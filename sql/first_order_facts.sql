--Copied from Looker
WITH nth_order AS (
	with line_item_filtered_orders as (
          select distinct
            lower(spree_orders.email) as email,
            spree_orders.id,
            spree_orders.completed_at

          from postgres_public.spree_line_items
          left join postgres_public.spree_variants
                    on spree_line_items.variant_id = spree_variants.id
          left join postgres_public.spree_products
                    on spree_variants.product_id = spree_products.id
          left join postgres_public.spree_orders
                    on spree_line_items.order_id = spree_orders.id

          where (spree_products.name not in ('the digital gift card', 'conditional insert', 'fedex delivery') or spree_products.name is null)

                and spree_orders.state = 'complete'
                and spree_orders.environment = 0

                and spree_line_items._fivetran_deleted = false
                and spree_variants._fivetran_deleted = false
                and spree_products._fivetran_deleted = false
                and spree_orders._fivetran_deleted = false
      )

      select
          line_item_filtered_orders.*,
          row_number() over (partition by lower(line_item_filtered_orders.email) order by line_item_filtered_orders.completed_at) as nth_order
      from line_item_filtered_orders
),
variant_facts AS (
	select
		  variant_id
		, listagg(case when option_type_id = 9 then name else null end,' | ') within group (order by option_values.name) as size
		, listagg(case when option_type_id = 2 then name else null end,' | ') within group (order by option_values.name) as color
		from POSTGRES_PUBLIC.SPREE_OPTION_VALUES_VARIANTS as option_values_variants
		left join POSTGRES_PUBLIC.SPREE_OPTION_VALUES as option_values on (option_values_variants."OPTION_VALUE_ID") = (option_values."ID") and (option_values."_FIVETRAN_DELETED") = false
		where (option_values_variants."_FIVETRAN_DELETED") = false
		group by 1
),
first_order_product_info AS (
	select distinct
        lower(orders."EMAIL") as email,
        products."NAME" as name,
        variant_facts."SIZE"  as size,
        variant_facts."COLOR" as color,
        product_map."DIVISION"  as division

      from POSTGRES_PUBLIC.SPREE_LINE_ITEMS  as line_items
      left join POSTGRES_PUBLIC.SPREE_ORDERS  as orders
                on (line_items."ORDER_ID") = (orders."ID")
                and (orders."_FIVETRAN_DELETED") = false
      left join POSTGRES_PUBLIC.SPREE_VARIANTS  as variants
                on (line_items."VARIANT_ID") = (variants."ID")
                and (variants."_FIVETRAN_DELETED") = false
      left join POSTGRES_PUBLIC.SPREE_PRODUCTS  as products
                on (variants."PRODUCT_ID") = (products."ID")
                and (products."_FIVETRAN_DELETED") = false
      left join nth_order as nth_order
                on (orders."ID") = (nth_order."ID")
      left join variant_facts as variant_facts
                on (variants."ID") = (variant_facts."VARIANT_ID")
      left join MERCH.PRODUCT_MAP as product_map
                on (left((variants."SKU"), 6)) = (product_map."STYLE_CODE")

      where orders."STATE" = 'complete'
            and (products."NAME"  not in ('conditional insert', 'the digital gift card','fedex delivery') or products."NAME" is null)
            and line_items."_FIVETRAN_DELETED" = false
            and orders."ENVIRONMENT" = 0
			and nth_order.nth_order = 1
)
select
    fi.email,
    listagg(distinct division, '|') within group (order by division) as first_order_division
from first_order_product_info fi
group by 1
order by 1
