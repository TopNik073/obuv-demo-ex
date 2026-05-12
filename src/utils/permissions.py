from repository.user.models.roles import ProductAction
from repository.user.models.roles import UserRole

_STORED_ROLES_PRODUCT: dict[UserRole, frozenset[ProductAction]] = {
    UserRole.client: frozenset({ProductAction.read}),
    UserRole.manager: frozenset(
        {
            ProductAction.read,
            ProductAction.read_with_filters,
        },
    ),
    UserRole.admin: frozenset(ProductAction),
}


def role_may_act_on_products(role: UserRole, action: ProductAction) -> bool:
    allowed = _STORED_ROLES_PRODUCT.get(role, frozenset())
    return action in allowed
