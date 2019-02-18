with distinct_to_email as (
    select distinct
        lower(o.email) as email,
        e.distinct_id
    from postgres_public.spree_orders o
        inner join mixpanel.event e
            on e.properties:order_number::string = o.number
    where o.email is not null
),
events as (
    select
        coalesce(lower(e.email), dte.email) as email,
        case when trim(e.OS) in ('Windows Mobile', 'BlackBerry', 'Android', 'Windows Phone', 'iOS')
                then 'mobile'
             else 'desktop'
        end as platform,
        to_timestamp_ntz(time) as time,
        e.name
    from mixpanel.event e
        left join distinct_to_email dte
            on dte.distinct_id = e.distinct_id
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
)
select
    *
from events
where email is not null
    and email in (%(users)s)
