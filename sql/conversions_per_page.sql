with orders as  (
    select
        o.id as order_id,
        max(to_timestamp_ntz(o.completed_at)) as order_completed_at,
        max(o.number) as order_number,
        max(lower(o.email)) as email
    from postgres_public.spree_orders o
    where  o._fivetran_deleted = false
        and o.state = 'complete'
        and o.environment = 0
        and o.completed_at is not null
    group by 1
),
email_to_distinct_raw as (
    select
        lower(o.email) as email,
        e.distinct_id
    from orders o
        inner join mixpanel.event e
            on e.properties:order_number::string = o.order_number
    where o.email is not null

    union all

    select
        lower(e.email) as email,
        e.distinct_id
    from mixpanel.event e
),
orders_with_distinct_ids as (
    select
        o.order_id,
        etd.distinct_id,
        max(o.order_completed_at) as order_completed_at
    from orders o
        inner join email_to_distinct_raw etd
            on etd.email = o.email
    group by 1, 2
),
line_items_with_distinct_ids as (
    select
        o.order_id,
        o.order_completed_at,
        o.distinct_id,
        v.product_id
    from orders_with_distinct_ids o
        inner join postgres_public.spree_line_items li
            on li.order_id = o.order_id
        inner join postgres_public.spree_variants v
            on v.id = li.variant_id
),
events as (
    select
        e.distinct_id,
        to_timestamp_ntz(date_trunc('day', time)) as day,
        case when e.name in ('products.show', 'Product viewed') then 'product'
             when e.name in ('Line items added') then 'bag'
             when e.name in ('products.index') then 'product_list'
             when e.name in ('home', 'viewedHomepage') then 'home'
             when e.name in ('Started Checkout Process') then 'checkout_start'
             when e.name in ('Checkout completed') then 'checkout'
             else 'other'
        end as event,
        case when exists(select 1
                         from orders_with_distinct_ids o
                         where o.distinct_id = e.distinct_id
                            and o.order_completed_at < e.time) then 1.0
             else 0.0
        end as prior_transaction,
        case when exists(select 1
                         from line_items_with_distinct_ids o
                         where o.distinct_id = e.distinct_id
                            and o.order_completed_at < e.time
                            and o.product_id = e.properties:product_id::int) then 1.0
                else 0.0
        end as prior_transaction_same_product
    from mixpanel.event e
    where e.time between %(start)s and %(end)s
        and e.name in (
            'Product viewed',
            'products.show',
            'products.index',
            'home',
            'viewedHomepage',
            'Started Checkout Process',
            'Checkout completed',
            'Line items added'
        )
),
user_day_event_counts as (
    select
        distinct_id,
        day,
        event,
        'all_users' as segment,
        count(1) as event_count
    from events
    group by 1, 2, 3

    union all

    select
        distinct_id,
        day,
        event,
        max(case when e.prior_transaction > 0 then 'prior_transaction'
             else 'no_prior_transaction'
        end) as segment,
        count(1) as event_count
    from events e
    group by 1, 2, 3

    union all

    select
        distinct_id,
        day,
        event,
        max(case when e.prior_transaction_same_product > 0 then 'prior_transaction_same_product'
             else 'no_prior_transaction_with_same_product'
        end) as segment,
        count(1) as event_count
    from events e
    where e.event = 'product'
    group by 1, 2, 3

),
traffic_and_conversion_per_day as (
    select
        ude.day,
        ude.event,
        ude.segment,
        count(distinct ude.distinct_id) as daily_users,
        count(distinct conversions.distinct_id) as daily_converting_users
    from user_day_event_counts ude
        left join user_day_event_counts conversions
            on conversions.distinct_id = ude.distinct_id
                and conversions.day = ude.day
                    and conversions.event = 'checkout'
    group by 1, 2, 3
),
traffic_and_conversion as (
    select
        event,
        segment,
        avg(daily_users) as avg_daily_users,
        avg(daily_converting_users) as avg_daily_converting_users,
        count(1) as days_counted,
        avg_daily_converting_users / avg_daily_users as avg_user_conversion_rate
    from traffic_and_conversion_per_day
    group by 1, 2
    order by 1, 2
)
select *
from traffic_and_conversion
