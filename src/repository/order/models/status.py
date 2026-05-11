from enum import StrEnum


class OrderStatus(StrEnum):
    pending = 'pending'
    confirmed = 'confirmed'
    cancelled = 'cancelled'
