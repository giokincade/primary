with events as(
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
        end as event
    from mixpanel.event e
    where e.time between %(start)s and %(end)s
),
days as(
    select
        day,
        event,
        count(distinct distinct_id) as daily_users
    from events
    group by 1, 2
)
select
    event,
    avg(daily_users) as avg_daily_users
from days
group by 1
order by 1
