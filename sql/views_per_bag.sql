with event_counts as (
    select
        e.distinct_id,
        to_timestamp_ntz(date_trunc('day', time)) as day,
        case when e.name in ('products.show', 'Product viewed') then 'product'
             when e.name in ('Line items added') then 'bag'
             else 'other'
        end as event,
        count(1) as event_count
    from mixpanel.event e
    where e.time between %(start)s and %(end)s
        and e.name in (
            'Product viewed',
            'products.show',
            'Line items added'
        )
    group by 1, 2, 3
),
pivoted as (
    select
        *
    from event_counts pivot(sum(event_count) for event in ('product', 'bag', 'other'))
)
select
    distinct_id,
    day,
    pivoted."'product'" as product,
    pivoted."'bag'" as bag,
    case when pivoted."'bag'" > 0.0 then 1.0
         else 0.0
   end as bag_indicator
from pivoted
