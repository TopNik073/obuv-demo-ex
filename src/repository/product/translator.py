from repository.base import BaseModelTranslator
from repository.product.models.orm import ProductORM
from repository.product.models.pydantic import ProductModel


class ProductModelTranslator(BaseModelTranslator):
    def to_db(self, model: ProductModel) -> ProductORM:
        data = model.model_dump()
        for key in ('id', 'created_at', 'updated_at'):
            if data.get(key) is None:
                data.pop(key, None)
        return ProductORM(**data)

    def to_model(self, model: ProductORM) -> ProductModel:
        return ProductModel.model_validate(model)
