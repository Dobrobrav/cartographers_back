from typing import Iterable, Callable

from django.db.models import Model
from redis.client import Redis

from services.redis.key_schemas_base import IKeySchema

from .model_transformers_base import BaseModelTransformer, DictModel, HashModel
from .redis_models_base import RedisModel


class DaoRedis:
    _key_schema: IKeySchema
    _transformer: BaseModelTransformer
    _redis: Redis
    _model_id: int

    def __init__(self,
                 redis_client: Redis,
                 ) -> None:
        self._redis = redis_client

    def fetch_hash_models(self,
                          ids: Iterable[int],
                          ) -> list[HashModel]:
        hash_models = [
            self.fetch_hash_model(id)
            for id in ids
        ]
        return hash_models

    def fetch_hash_model(self,
                         model_id: int,
                         ) -> HashModel:
        hash_key = self._key_schema.get_hash_key(model_id)
        hash_model = self._redis.hgetall(hash_key)
        return hash_model

    def fetch_redis_models(self,
                           model_ids: Iterable[int],
                           ) -> list[RedisModel]:
        redis_models = [
            self.fetch_redis_model(id)
            for id in model_ids
        ]
        return redis_models

    def fetch_redis_model(self,
                          model_id: int,
                          ) -> RedisModel:
        hash_model = self.fetch_hash_model(model_id)
        redis_model = self._transformer. \
            hash_model_to_redis_model(hash_model)
        return redis_model

    def fetch_dict_models(self,
                          model_ids: Iterable[int],
                          ) -> list[DictModel]:
        dict_models = [
            self.fetch_dict_model(model_id)
            for model_id in model_ids
        ]
        return dict_models

    def fetch_dict_model(self,
                         model_id: int,
                         ) -> DictModel:
        hash_model = self.fetch_hash_model(model_id)
        dict_model = self._transformer. \
            hash_model_to_dict_model(hash_model)

        return dict_model

    def delete_by_id(self,
                     id: int,
                     ) -> None:
        ids_key = self._key_schema.get_ids_key()
        self._redis.srem(ids_key, id)

    def _get_all_ids(self) -> set[int]:
        all_ids_hash = self._key_schema.get_ids_key()
        all_ids = {int(id) for id in self._redis.smembers(all_ids_hash)}
        return all_ids

    # TODO: implement this

    @staticmethod
    def _get_ids_for_page(all_ids: Iterable[int],
                          page: int,
                          limit: int,
                          ) -> list[int]:
        start = (page - 1) * limit + 1
        end = start + limit
        ids = sorted(all_ids)[start:end]
        return ids

    def _insert_many(self,
                     models: Iterable[Model | RedisModel],
                     dumper: Callable[[Model | RedisModel], DictModel],
                     ) -> list[DictModel]:
        hash_models = [
            self._insert_single(model, dumper)
            for model in models
        ]
        return hash_models

    def _insert_single(self,
                       model: Model | RedisModel,
                       dumper: Callable[[Model | RedisModel], DictModel],
                       ) -> DictModel:
        hash_key = self._key_schema.get_hash_key(id=model.id)
        ids_key = self._key_schema.get_ids_key()
        # these actually should be a transaction
        hash_model = dumper(model)
        self._redis.hset(hash_key, mapping=hash_model)
        self._redis.sadd(ids_key, model.id)
        return hash_model

    def _gen_new_id(self) -> int:
        ids = self._get_ids()
        id = self._gen_id(ids)
        return id

    def _get_ids(self) -> set[int]:
        ids_key = self._key_schema.get_ids_key()
        ids = {int(id) for id in self._redis.smembers(ids_key)}
        return ids

    @staticmethod
    def _gen_id(ids: set[int]) -> int:
        new_id = 1  # start with the lowest possible ID value

        while new_id in ids:
            new_id += 1  # increment the ID until an available one is found

        return new_id


class DaoRedisRedis(DaoRedis):

    def insert_redis_models(self,
                            models: Iterable[RedisModel],
                            ) -> list[DictModel]:
        model_hashes = [
            self.insert_redis_model(model)
            for model in models
        ]
        return model_hashes

    def insert_redis_model(self,
                           model: RedisModel,
                           ) -> DictModel:
        model_hash = self._insert_single(
            model, dumper=self._transformer.redis_model_to_dict_model
        )
        return model_hash


class DaoRedisSQL(DaoRedis):
    def insert_sql_models(self,
                          models: Iterable[Model],
                          ) -> list[DictModel]:
        model_hashes = [
            self._insert_single(
                model, dumper=self._transformer.sql_model_to_dict_model
            )
            for model in models
        ]
        return model_hashes

    def insert_sql_model(self,
                         model: Model,
                         ) -> DictModel:
        hash_model = self._insert_single(
            model, dumper=self._transformer.sql_model_to_dict_model
        )
        return hash_model
