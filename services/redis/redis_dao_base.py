from typing import Iterable, Callable

from django.db.models import Model
from redis.client import Redis

from services.redis.key_schemas_base import IKeySchema

from .model_transformers_base import ITransformer, ModelDict, ModelHash
from .redis_models_base import RedisModel


class DaoRedis:
    _key_schema: IKeySchema
    _transformer: ITransformer
    _redis: Redis

    def __init__(self,
                 redis_client: Redis,
                 ) -> None:
        self._redis = redis_client

    def get_page(self,
                 page: int,
                 limit: int,
                 ) -> list[RedisModel]:
        all_ids = self._get_all_ids()
        ids_for_page = self._get_ids_for_page(all_ids, page, limit)
        hashes = self.fetch_hashes(ids_for_page)
        models = self._transformer.hashes_to_models(hashes)
        return models

    # TODO: fix all that shit about bytes models and hashes!!
    def fetch_hashes(self,
                     ids: Iterable[int],
                     ) -> list[ModelHash]:
        hashes = [
            self.fetch_hash(id)
            for id in ids
        ]
        return hashes

    def fetch_hash(self,
                   model_id: int,
                   ) -> ModelHash:
        hash_key = self._key_schema.get_hash_key(model_id)
        hash = self._redis.hgetall(hash_key)
        return hash

    def fetch_models(self,
                     model_ids: Iterable[int],
                     ) -> list[RedisModel]:
        models = [
            self.fetch_model(id)
            for id in model_ids
        ]
        return models

    def fetch_model(self,
                    model_id: int,
                    ) -> RedisModel:
        hash = self.fetch_hash(model_id)
        return self._transformer.hash_to_model(hash)

    def _get_all_ids(self) -> set[int]:
        all_ids_hash = self._key_schema.get_ids_key()
        all_ids = {int(id) for id in self._redis.smembers(all_ids_hash)}
        return all_ids

    @staticmethod
    def _get_ids_for_page(all_ids: Iterable[int],
                          page: int,
                          limit: int,
                          ) -> list[int]:
        start = (page - 1) * limit + 1
        end = start + limit
        ids = sorted(all_ids)[start:end]
        return ids

    def _insert_single(self,
                       model: Model | RedisModel,
                       dumper: Callable[[Model | RedisModel], ModelDict],
                       ) -> ModelDict:
        hash_key = self._key_schema.get_hash_key(id=model.id)
        ids_key = self._key_schema.get_ids_key()
        # these actually should be a transaction
        model_hash = dumper(model)
        self._redis.hset(hash_key, mapping=model_hash)
        self._redis.sadd(ids_key, model.id)
        return model_hash

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
                            ) -> list[ModelDict]:
        model_hashes = [
            self._insert_single(
                obj, dumper=self._transformer.redis_model_to_dict
            )
            for obj in models
        ]
        return model_hashes

    def insert_redis_model(self,
                           model: RedisModel,
                           ) -> ModelDict:
        model_hash = self._insert_single(
            model, dumper=self._transformer.redis_model_to_dict
        )

        return model_hash


class DaoRedisSQL(DaoRedis):
    def insert_sql_models(self,
                          models: Iterable[Model],
                          ) -> list[ModelDict]:
        model_hashes = [
            self._insert_single(
                model, dumper=self._transformer.sql_model_to_dict
            )
            for model in models
        ]
        return model_hashes

    def insert_sql_model(self,
                         model: Model,
                         ) -> ModelDict:
        model_hash = self._insert_single(
            model, dumper=self._transformer.sql_model_to_dict
        )
        return model_hash
