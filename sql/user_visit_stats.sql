with distinct_to_email as (
    select distinct
        lower(o.email) as email,
        e.distinct_id
    from postgres_public.spree_orders o
        inner join mixpanel.event e
            on e.properties:order_number::string = o.number
    where o.email is not null
),
indexed_transactions as (
    select
        o.id as order_id,
        lower(o.email) as email,
        o.completed_at,
        row_number() over (partition by o.email order by o.completed_at) as user_transaction_index
    from postgres_public.spree_orders o
    where o.environment = 0
        and o.completed_at is not null
),
time_between_transactions as (
    select
        one.email,
        avg(datediff('day', one.completed_at, two.completed_at)) as avg_days_between_orders,
        min(datediff('day', one.completed_at, two.completed_at)) as min_days_between_orders,
        max(datediff('day', one.completed_at, two.completed_at)) as max_days_between_orders
    from indexed_transactions one
        inner join indexed_transactions two
            on one.email = two.email
                and one.user_transaction_index + 1 = two.user_transaction_index
    group by 1
),
visit_days as (
    select
        coalesce(lower(e.email), dte.email) as email,
        date_trunc('day', time) as visit_day
    from mixpanel.event e
        left join distinct_to_email dte
            on dte.distinct_id = e.distinct_id
    group by 1, 2
),
visit_days_indexed as (
    select
        *,
        row_number() over (partition by email order by visit_day) as user_visit_index
    from visit_days
),
time_between_visits as (
    select
        one.email,
        avg(datediff('day', one.visit_day, two.visit_day)) as avg_days_between_visits,
        min(datediff('day', one.visit_day, two.visit_day)) as min_days_between_visits,
        max(datediff('day', one.visit_day, two.visit_day)) as max_days_between_visits
    from visit_days_indexed one
        inner join visit_days_indexed two
            on one.email = two.email
                and one.user_visit_index + 1 = two.user_visit_index
    group by 1
),
users as(
    select
        coalesce(lower(e.email), dte.email) as email,
        to_timestamp_ntz(min(time)) as min_visit_time,
        to_timestamp_ntz(max(time)) as max_visit_time,
        count(distinct date_trunc('day', time)) as visit_days
    from mixpanel.event e
        left join distinct_to_email dte
            on dte.distinct_id = e.distinct_id
    group by 1
),
with_retained_days as(
  select
        *,
        datediff('day', min_visit_time, max_visit_time) as days_retained,
        days_retained * 1.0 / visit_days as days_retained_per_visit
  from users
)
select
    r.email,
    r.min_visit_time,
    r.max_visit_time,
    r.visit_days,
    r.days_retained,
    r.days_retained_per_visit,
    tbt.avg_days_between_orders,
    tbt.min_days_between_orders,
    tbt.max_days_between_orders,
    tbv.avg_days_between_visits,
    tbv.min_days_between_visits,
    tbv.max_days_between_visits
from with_retained_days r
    left join time_between_transactions tbt
        on tbt.email = r.email
    left join time_between_visits tbv
        on tbv.email = r.email
