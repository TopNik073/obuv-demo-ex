from repository.base.translator import BaseModelTranslator
from repository.order.models.postgres import OrderItemORM
from repository.order.models.postgres import OrderORM
from repository.order.models.pydantic import OrderItemModel
from repository.order.models.pydantic import OrderModel
from repository.order.models.status import OrderStatus


class OrderModelTranslator(BaseModelTranslator):
    def to_db(self, model: OrderModel) -> OrderORM:
        orm = OrderORM(
            customer_id=model.customer_id,
            status=model.status.value,
            total_amount=model.total_amount,
        )
        if model.id is not None:
            orm.id = model.id
        for item in model.items:
            iorm = OrderItemORM(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            if item.id is not None:
                iorm.id = item.id
            orm.items.append(iorm)
        return orm

    def to_model(self, model: OrderORM) -> OrderModel:
        return OrderModel(
            id=model.id,
            customer_id=model.customer_id,
            status=OrderStatus(model.status),
            total_amount=model.total_amount,
            items=[
                OrderItemModel(
                    id=i.id,
                    product_id=i.product_id,
                    quantity=i.quantity,
                    unit_price=i.unit_price,
                )
                for i in model.items
            ],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
