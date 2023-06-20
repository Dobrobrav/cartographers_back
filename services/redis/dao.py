from typing import Sequence

from django.contrib.auth.models import User

from services.redis.dict_models import UserPretty
from services.redis.key_schemas import UserKeySchema
from services.redis.converters import UserConverter
from services.redis.base.redis_dao_base import DaoFull


class UserDaoRedis(DaoFull):
    _key_schema = UserKeySchema()
    _converter = UserConverter()

    def get_users_pretty(self,
                         user_ids: Sequence[int],
                         users_readiness: dict[int, bool],
                         ) -> list[UserPretty]:
        sql_users = list(User.objects.filter(id__in=user_ids))

        users_pretty = self._Converter.sql_users_to_pretty_users(
            sql_users, users_readiness.values()
        )
        return users_pretty

    # TODO: где все же должны быть эти методы (выше) и кто должен менять готовность
