from datetime import date, datetime

from lib.viz import Colors


class Enum:

    @classmethod
    def ALL(cls):
        thing = cls()
        attrs = [getattr(thing, attr) for attr in dir(thing) if "__" not in attr]
        return [a for a in attrs if not callable(a)]

    @classmethod
    def indicator(cls, col: str) -> str:
        return col + "_indicator"


class TransactionColumns(Enum):
    ORDER_ID = "order_id"
    ORDER_NUMBER = "order_number"
    ORDER_INDEX = "order_index"
    ORDER_INDEX_BUCKET = "order_index_bucket"
    EMAIL = "email"
    ORDER_COMPLETED_AT = "order_completed_at"
    ORDER_DATE = "order_date"
    ORDER_MONTH = "order_month"
    MIN_LINE_ITEM_CREATED_AT = "min_line_item_created_at"
    MAX_LINE_ITEM_CREATED_AT = "max_line_item_created_at"
    UNITS = "units"
    PRODUCTS = "products"
    LINE_ITEMS = "line_items"
    ITEM_TOTAL = "item_total"
    COMMON_PRODUCTS = "common_products"
    COMMON_UNITS = "common_units"
    COMMON_TOTAL = "common_total"
    COMMON_PRODUCTS_RATIO = "common_products_ratio"
    COMMON_UNITS_RATIO = "common_units_ratio"
    COMMON_TOTAL_RATIO = "common_total_ratio"
    DISCOUNT_PERCENTAGE = "discount_percentage"
    ADJUSTMENT_TOTAL = "adjustment_total"
    IS_GUEST = "is_guest"
    HAS_SALE_ITEM = "has_sale_item"
    IS_REPEAT = "is_repeat"

    @classmethod
    def types(cls):
        return {
            cls.ORDER_ID: int,
            cls.ORDER_NUMBER: str,
            cls.ORDER_INDEX: float,
            cls.EMAIL: str,
            cls.ADJUSTMENT_TOTAL: float,
            cls.DISCOUNT_PERCENTAGE: float,
            cls.IS_GUEST: float,
            cls.ORDER_COMPLETED_AT: datetime,
            cls.MIN_LINE_ITEM_CREATED_AT: datetime,
            cls.MAX_LINE_ITEM_CREATED_AT: datetime,
            cls.UNITS: float,
            cls.PRODUCTS: float,
            cls.LINE_ITEMS: float,
            cls.ITEM_TOTAL: float,
            cls.COMMON_PRODUCTS: float,
            cls.COMMON_UNITS: float,
            cls.COMMON_TOTAL: float,
            cls.HAS_SALE_ITEM: float,
        }


class EventColumns(Enum):
    EMAIL = "email"
    NAME = "name"
    TIME = "time"
    PLATFORM = "platform"

    @classmethod
    def types(cls):
        return {cls.EMAIL: str, cls.NAME: str, cls.PLATFORM: str, cls.TIME: datetime}


class Events(Enum):
    PDP = "pdp"
    PLP = "plp"
    BAG = "add_to_bag"
    CHECKOUT = "checkout"
    CHECKOUT_START = "checkout_start"
    HOME = "home"

    @classmethod
    def palette(cls):
        return {
            cls.HOME: Colors.YELLOW_LIGHT,
            cls.PLP: Colors.PINK_LIGHT,
            cls.PDP: Colors.PINK_MEDIUM,
            cls.BAG: Colors.GREEN_LIGHT,
            cls.CHECKOUT_START: Colors.GREEN_MEDIUM,
            cls.CHECKOUT: Colors.GREEN_DARK,
        }


class UserColumns(Enum):
    EMAIL = "email"
    FIRST_ORDER_DATE = "first_order_date"
    FIRST_ORDER_MONTH = "first_order_month"
    FIRST_ORDER_COLORS = "first_order_colors"
    FIRST_ORDER_DIVISION = "first_order_division"
    LIFETIME_GPR = "lifetime_gpr"
    LIFETIME_ORDERS = "lifetime_orders"
    LIFETIME_UNITS = "lifetime_units"
    LIFETIME_ORDERS_DECILE = "lifetime_orders_decile"
    DAYS = "days"
    DAYS_RETAINED = "days_retained"
    DAYS_RETAINED_PER_VISIT = "days_retained_per_visit"
    ORDER_FREQUENCY = "order_frequency"
    MIN_VISIT_TIME = "min_visit_time"
    MAX_VISIT_TIME = "max_visit_time"
    VISIT_DAYS = "visit_days"
    AVG_DAYS_BETWEEN_ORDERS = "avg_days_between_orders"
    MIN_DAYS_BETWEEN_ORDERS = "min_days_between_orders"
    MAX_DAYS_BETWEEN_ORDERS = "max_days_between_orders"
    AVG_DAYS_BETWEEN_VISITS = "avg_days_between_visits"
    MIN_DAYS_BETWEEN_VISITS = "min_days_between_visits"
    MAX_DAYS_BETWEEN_VISITS = "max_days_between_visits"
    IS_PILOT_BOX_BUYER = "is_pilot_box_buyer"

    @classmethod
    def types(cls):
        return {
            cls.EMAIL: str,
            cls.FIRST_ORDER_DATE: date,
            cls.FIRST_ORDER_COLORS: str,
            cls.LIFETIME_GPR: float,
            cls.LIFETIME_ORDERS: int,
            cls.LIFETIME_UNITS: int,
            cls.DAYS_RETAINED_PER_VISIT: float,
            cls.ORDER_FREQUENCY: float,
            cls.AVG_DAYS_BETWEEN_ORDERS: float,
            cls.MIN_DAYS_BETWEEN_ORDERS: float,
            cls.MAX_DAYS_BETWEEN_ORDERS: float,
            cls.AVG_DAYS_BETWEEN_VISITS: float,
            cls.MIN_DAYS_BETWEEN_VISITS: float,
            cls.MAX_DAYS_BETWEEN_VISITS: float,
            cls.IS_PILOT_BOX_BUYER: int
        }
