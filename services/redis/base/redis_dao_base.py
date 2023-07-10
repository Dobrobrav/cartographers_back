from typing import Iterable, Callable, Generator, Any, TypeVar, Optional, MutableSequence

from django.db.models import Model
from redis.client import Redis

import services.utils
from services import utils
from services.redis.base.key_schemas_base import IKeySchema

from services.redis.base.converters_base import BaseRedisConverter, DictModel, HashModel, BaseFullConverter
from services.redis.base.models_base import DataClassModel
import random

T = TypeVar('T')


class DaoBase:
    _key_schema: IKeySchema
    _redis: Redis
    _model_class: DataClassModel

    def __init__(self,
                 redis_client: Redis,
                 ) -> None:
        self._redis = redis_client

    def get_all_ids(self) -> Generator:
        ids_key = self._key_schema.ids_key
        ids = (int(id) for id in self._redis.smembers(ids_key))
        return ids

    @staticmethod
    def _pick_card_id(card_ids: MutableSequence[int],
                      ) -> int:
        random_card_id = random.choice(card_ids)
        card_ids.remove(random_card_id)
        return random_card_id

    def _fetch_model_attr(self,
                          model_id: int,
                          field_name: str,
                          converter: Callable[[bytes], T] = services.utils.deserialize,
                          ) -> Optional[T]:
        key = self._key_schema.get_hash_key(model_id)
        response = self._redis.hget(key, field_name)
        return None if response == b'' else converter(response)

    def _set_model_attr(self,
                        model_id: int,
                        field_name: str,
                        value: T,
                        converter: Callable[[T], Any] = utils.serialize,
                        ) -> None:
        key = self._key_schema.get_hash_key(model_id)
        self._redis.hset(key, field_name, converter(value))

    def _fetch_hash_models(self,
                           ids: Iterable[int],
                           ) -> list[HashModel]:
        hash_models = [
            self._fetch_hash_model(id)
            for id in ids
        ]
        return hash_models

    def _fetch_hash_model(self,
                          model_id: int,
                          ) -> HashModel:
        hash_key = self._key_schema.get_hash_key(model_id)
        hash_model = self._redis.hgetall(hash_key)
        return hash_model

    def delete_by_id(self,
                     id: int,
                     ) -> None:
        ids_key = self._key_schema.ids_key
        self._redis.srem(ids_key, id)

    def _get_all_ids(self) -> set[int]:
        all_ids_hash = self._key_schema.ids_key
        all_ids = {int(id) for id in self._redis.smembers(all_ids_hash)}
        print(all_ids)
        return all_ids

    @staticmethod
    def _get_ids_for_page(all_ids: Iterable[int],
                          page: int,
                          limit: int,
                          ) -> list[int]:
        start_id = (page - 1) * limit + 1
        end_id = start_id + limit - 1
        ids = sorted(all_ids)[start_id - 1:end_id]
        print(ids)
        return ids

    def _insert_many(self,
                     models: Iterable[Model | DataClassModel],
                     dumper: Callable[[Model | DataClassModel], DictModel],
                     ) -> list[DictModel]:
        hash_models = [
            self._insert_single(model, dumper)
            for model in models
        ]
        return hash_models

    def _insert_single(self,
                       model: Model | DataClassModel,
                       dumper: Callable[[Model | DataClassModel], DictModel],
                       ) -> DictModel:
        hash_key = self._key_schema.get_hash_key(id=model.id)
        # these actually should be a transaction
        dict_model = dumper(model)
        self._redis.hset(hash_key, mapping=dict_model)
        self._insert_id(model.id)
        return dict_model

    def _gen_new_id(self) -> int:
        ids = self._get_ids()
        id = self._gen_id(ids)
        self._insert_id(id)

        return id

    def _insert_id(self,
                   id: int,
                   ) -> None:
        ids_key = self._key_schema.ids_key
        self._redis.sadd(ids_key, id)

    def _get_ids(self) -> set[int]:
        ids_key = self._key_schema.ids_key
        ids = {int(id) for id in self._redis.smembers(ids_key)}
        return ids

    def _gen_new_ids(self,
                     quantity: int,
                     ) -> list[int]:
        ids = [self._gen_new_id() for _ in range(quantity)]
        return ids

    @staticmethod
    def _gen_id(ids: set[int]) -> int:
        new_id = 1  # start with the lowest possible ID value

        while new_id in ids:
            new_id += 1  # increment the ID until an available one is found

        return new_id

    def fetch_hash_value(self,
                         key: str,
                         field_name: str | int,
                         converter: Callable[[bytes], T]
                         ) -> Optional[T]:
        print(key)
        response = self._redis.hget(key, field_name)
        return response and converter(response)  # assign None or converter


class DaoRedis(DaoBase):
    _converter: BaseRedisConverter

    def fetch_dc_models(self,
                        model_ids: Iterable[int],
                        ) -> list[DataClassModel]:
        redis_models = [
            self.fetch_dc_model(id)
            for id in model_ids
        ]
        return redis_models

    def fetch_dc_model(self,
                       model_id: int,
                       ) -> DataClassModel:
        hash_model = self._fetch_hash_model(model_id)
        dc_model = self._converter.hash_model_to_dc_model(hash_model)
        return dc_model

    def insert_dc_models(self,
                         models: Iterable[DataClassModel],
                         ) -> list[DictModel]:
        dict_models = [
            self.insert_dc_model(model)
            for model in models
        ]
        return dict_models

    def insert_dc_model(self,
                        model: DataClassModel,
                        ) -> DictModel:
        dict_model = self._insert_single(
            model, dumper=self._converter.dc_model_to_dict_model
        )
        return dict_model


class DaoFull(DaoRedis):
    _converter: BaseFullConverter

    def insert_sql_models(self,
                          models: Iterable[Model],
                          ) -> list[DictModel]:
        hash_models = [
            self._insert_single(
                model, dumper=self._converter.sql_model_to_dict_model
            )
            for model in models
        ]
        return hash_models

    def insert_sql_model(self,
                         model: Model,
                         ) -> DictModel:
        hash_model = self._insert_single(
            model, dumper=self._converter.sql_model_to_dict_model
        )
        return hash_model
