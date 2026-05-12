from repository.base import BaseModelIdentifiable
from repository.base import TimestampedModelMixin
from repository.user.models.roles import UserRole


class UserModel(BaseModelIdentifiable, TimestampedModelMixin):
    username: str
    password: str

    name: str
    surname: str
    lastname: str

    role: UserRole

    def full_name(self) -> str:
        parts = [self.surname, self.name, self.lastname]
        text = ' '.join(p for p in parts if p).strip()
        return text if text else self.username
