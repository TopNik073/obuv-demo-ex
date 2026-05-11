from repository.base.translator import BaseModelTranslator
from repository.user.models.postgres import UserORM
from repository.user.models.pydantic import UserModel


class UserModelTranslator(BaseModelTranslator):
    def to_db(self, model: UserModel) -> UserORM:
        return UserORM(**model.model_dump())

    def to_model(self, model: UserORM) -> UserModel:
        return UserModel.model_validate(model)
