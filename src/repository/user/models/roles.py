from enum import StrEnum


class UserRole(StrEnum):
    """Роли учётных записей в БД (см. предметную область)."""

    client = 'client'
    manager = 'manager'
    admin = 'admin'


class ProductAction(StrEnum):
    read = 'read'
    read_with_filters = 'read_with_filters'
    create = 'create'
    update = 'update'
    delete = 'delete'
