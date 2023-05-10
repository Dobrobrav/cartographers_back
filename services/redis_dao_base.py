from typing import Iterable, Callable

from django.db.models import Model
from redis.client import Redis

from .key_schemas_base import KeySchema
from abc import ABC, abstractmethod

from .model_transformers_base import ITransformer, ModelHash
from .redis_models_base import RedisModel


class Dao(ABC):
    _key_schema: KeySchema
    _transformer: ITransformer
    _model: type[RedisModel]

    @abstractmethod
    def insert_redis_model_many(self,
                                objects: Iterable[RedisModel],
                                ) -> list[RedisModel]:
        pass

    @abstractmethod
    def insert_redis_model_single(self,
                                  obj: RedisModel,
                                  ) -> RedisModel:
        pass

    @abstractmethod
    def fetch_by_id(self, model_id: int) -> RedisModel:
        pass

    @abstractmethod
    def fetch_all(self) -> set[RedisModel]:
        pass

    @abstractmethod
    def insert_sql_model_many(self,
                              objects: Iterable[Model],
                              ) -> None:
        pass

    @abstractmethod
    def insert_sql_model_single(self,
                                obj: Model,
                                ) -> None:
        pass


class DaoRedis(Dao):
    _redis: Redis

    def __init__(self,
                 redis_client: Redis,
                 ) -> None:
        self._redis = redis_client

    def insert_redis_model_many(self,
                                redis_models: Iterable[RedisModel],
                                ) -> list[ModelHash]:
        model_hashes = [
            self._insert_single(
                obj, dumper=self._transformer.dump_redis_model)
            for obj in redis_models
        ]
        return model_hashes

    def insert_redis_model_single(self,
                                  model: RedisModel,
                                  ) -> ModelHash:
        model_hash = self._insert_single(
            model, dumper=self._transformer.dump_sql_model)

        return model_hash

    def insert_sql_model_many(self,
                              models: Iterable[Model],
                              ) -> list[ModelHash]:
        model_hashes = [
            self._insert_single(
                model, dumper=self._transformer.dump_sql_model)
            for model in models
        ]
        return model_hashes

    def insert_sql_model_single(self,
                                model: Model,
                                ) -> ModelHash:
        model_hash = self._insert_single(
            model, dumper=self._transformer.dump_sql_model)

        return model_hash

    def _insert_single(self,
                       model: Model | RedisModel,
                       dumper: Callable[[Model | RedisModel], ModelHash],
                       ) -> ModelHash:
        hash_key = self._key_schema.get_hash_key(id=model.id)
        ids_key = self._key_schema.get_ids_key()
        # these actually should be a transaction
        model_hash = dumper(model)
        self._redis.hset(hash_key, mapping=model_hash)
        self._redis.sadd(ids_key, hash_key)

        return model_hash

    def fetch_by_id(self,
                    model_id: int,
                    ) -> RedisModel:
        hash_key = self._key_schema.get_hash_key(model_id)
        model_hash = self._redis.hgetall(hash_key)
        return self._transformer.load_redis_model(model_hash)

    def fetch_all(self) -> set[RedisModel]:
        ids_key = self._key_schema.get_ids_key()
        monster_card_hashes = (
            self._redis.hgetall(hash_key)
            for hash_key in self._redis.smembers(ids_key)
        )
        monster_cards = {
            self._transformer.load_redis_model(card)
            for card in monster_card_hashes
        }
        return monster_cards

    def _gen_new_id(self) -> int:
        ids = self._get_ids()
        id = self._gen_id(ids)
        return id

    @staticmethod
    def _gen_id(ids: set[int]) -> int:
        new_id = 1  # start with the lowest possible ID value

        while new_id in ids:
            new_id += 1  # increment the ID until an available one is found

        return new_id

    def _get_ids(self) -> set[int]:
        ids_key = self._key_schema.get_ids_key()
        ids = {int(id) for id in self._redis.smembers(ids_key)}
        return ids
