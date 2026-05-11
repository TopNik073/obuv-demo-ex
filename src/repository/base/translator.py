from abc import ABC, abstractmethod

from repository.base.models import BaseModelIdentifiable, BaseORM


class BaseModelTranslator(ABC):
    @abstractmethod
    def to_db(self, model: BaseModelIdentifiable) -> BaseORM:
        raise NotImplementedError

    @abstractmethod
    def to_model(self, model: BaseORM) -> BaseModelIdentifiable:
        raise NotImplementedError
