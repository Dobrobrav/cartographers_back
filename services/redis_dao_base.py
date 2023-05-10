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

    @abstractmethod
    def insert_redis_model_many(self,
                                objects: Iterable[RedisModel],
                                ) -> None:
        pass

    @abstractmethod
    def insert_redis_model_single(self,
                                  obj: RedisModel,
                                  ) -> None:
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
                                objects: Iterable[RedisModel],
                                ) -> None:
        for obj in objects:
            self._insert_single(
                obj, dumper=self._transformer.dump_redis_model)

    def insert_redis_model_single(self,
                                  obj: RedisModel,
                                  ) -> None:
        self._insert_single(
            obj, dumper=self._transformer.dump_sql_model)

    def insert_sql_model_many(self,
                              objects: Iterable[Model],
                              ) -> None:
        for obj in objects:
            self._insert_single(
                obj, dumper=self._transformer.dump_sql_model)

    def insert_sql_model_single(self,
                                obj: Model,
                                ) -> None:
        self._insert_single(
            obj, dumper=self._transformer.dump_sql_model)

    def _insert_single(self,
                       obj: Model | RedisModel,
                       dumper: Callable[[Model | RedisModel], ModelHash],
                       ) -> None:
        hash_key = self._key_schema.get_hash_key(id=obj.id)
        ids_key = self._key_schema.get_ids_key()
        # these actually should be a transaction
        self._redis.hset(hash_key, mapping=dumper(obj))
        self._redis.sadd(ids_key, hash_key)

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
