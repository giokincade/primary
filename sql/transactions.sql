--mostly Copied from Looker
with preorders as  (
    select
        o.id as order_id,
        max(lower(email)) as email,
        max(to_timestamp_ntz(o.completed_at)) as order_completed_at,
        max(o.number) as order_number,
        max(o.item_total) as item_total,
        max(o.user_id) as user_id,
        max(o.adjustment_total) as adjustment_total
    from postgres_public.spree_orders o
    where  o._fivetran_deleted = false
        and o.state = 'complete'
        and o.environment = 0
        and o.email not like '%primary.com%'
        and o.completed_at is not null
    group by 1
),
numbered as (
    select
        *,
        row_number() over (partition by email order by order_completed_at) as order_index,
        case when user_id is null then 1.0 else 0.0 end as is_guest
    from preorders
),
variant_facts AS (
    select
        variant_id,
        listagg(case when option_type_id = 9 then name else null end,' | ')
            within group (order by option_values.name) as size,
        listagg(case when option_type_id = 2 then name else null end,' | ')
            within group (order by option_values.name) as color
    from POSTGRES_PUBLIC.SPREE_OPTION_VALUES_VARIANTS as option_values_variants
        left join POSTGRES_PUBLIC.SPREE_OPTION_VALUES as option_values
            on (option_values_variants."OPTION_VALUE_ID") = (option_values."ID") and (option_values."_FIVETRAN_DELETED") = false
    where (option_values_variants."_FIVETRAN_DELETED") = false
    group by 1
),
line_items as (
    select
        li.variant_id,
        li.order_id as order_id,
        max(o.email) as email,
        max(o.is_guest) as is_guest,
        max(o.adjustment_total) as order_adjustment_total,
        max(o.order_number) as order_number,
        max(p.id) as product_id,
        max(o.order_completed_at) as order_completed_at,
        max(o.item_total) as item_total,
        max(o.order_index) as order_index,
        max(to_timestamp_ntz(li.created_at)) as line_item_created_at,
        max(li.price) as price,
        max(li.quantity) as quantity,
        max(li.cost_price) as total,
        max(vf.size) as size,
        max(vf.color) as color,
        max(case
            when p.name ilike '%sale%' or p.name ilike '%clearance%' then 1.0
            else 0.0
        end) as is_sale_item
    from postgres_public.spree_line_items li
        left join postgres_public.spree_variants
                on li.variant_id = spree_variants.id
        left join postgres_public.spree_products p
                on spree_variants.product_id = p.id
        inner join numbered o
                on li.order_id = o.order_id
        left join variant_facts vf
            on vf.variant_id = li.variant_id
    where (
            p.name not in ('the digital gift card', 'conditional insert', 'fedex delivery')
                or p.name is null
        )
        and li._fivetran_deleted = false
        and spree_variants._fivetran_deleted = false
        and p._fivetran_deleted = false
    group by 1,2
),
orders as (
    select
        order_id,
        max(email) as email,
        max(is_guest) as is_guest,
        max(order_number) as order_number,
        max(order_index) as order_index,
        max(order_completed_at) as order_completed_at,
        min(line_item_created_at) as min_line_item_created_at,
        max(line_item_created_at) as max_line_item_created_at,
        sum(quantity) as units,
        count(distinct product_id) as products,
        count(1) as line_items,
        max(item_total) as item_total,
        max(order_adjustment_total) as adjustment_total,
        max(is_sale_item) as has_sale_item,
        sum(case
            when is_sale_item > 0.0 then item_total
            else 0.0
        end) as sale_total
    from line_items
    group by 1
),
common_line_items as (
    select
        new.order_id,
        count(distinct new.product_id) as common_products,
        sum(new.quantity) as common_units,
        sum(price) as common_total
    from line_items new
    where exists(
        select 1
        from line_items old
        where new.email = old.email
            and new.order_id != old.order_id
            and new.product_id = old.product_id
            and new.order_index > old.order_index
    )
    group by 1
)
select
    o.*,
    coalesce(cli.common_products, 0.0) as common_products,
    coalesce(cli.common_units, 0.0) as common_units,
    coalesce(cli.common_total, 0.0) as common_total
from orders o
    left join common_line_items cli
        on o.order_id = cli.order_id
