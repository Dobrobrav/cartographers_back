from typing import Iterable

from games.services.dao_base import Dao
from games.services.key_schemas import MonsterCardKeySchema
from games.services.model_transformers import MonsterCardTransformer
from games.services.redis_models import MonsterCard
from redis.client import Redis


class MonsterCardDaoRedis(Dao):
    _redis: Redis
    _key_schema = MonsterCardKeySchema()
    _transformer = MonsterCardTransformer()

    def __init__(self,
                 redis_client: Redis,
                 ) -> None:
        self._redis = redis_client

    def insert(self,
               redis_model: MonsterCard,
               ) -> None:
        hash_key = self._key_schema.get_hash_key(redis_model.id)
        ids_key = self._key_schema.get_ids_key()
        # this actually should be a transaction
        self._redis.hset(hash_key,
                         mapping=self._transformer.dump(redis_model))
        self._redis.sadd(ids_key, hash_key)

    def insert_many(self,
                    redis_models: Iterable[MonsterCard],
                    ) -> None:
        for model in redis_models:
            self.insert(model)

    def fetch_by_id(self,
                    model_id: int,
                    ) -> MonsterCard:
        hash_key = self._key_schema.get_hash_key(model_id)
        model_hash = self._redis.hgetall(hash_key)
        return self._transformer.load(model_hash)

    def fetch_all(self) -> set[MonsterCard]:
        ids_key = self._key_schema.get_ids_key()
        monster_card_hashes = (
            self._redis.hgetall(hash_key)
            for hash_key in self._redis.smembers(ids_key)
        )
        monster_cards = {
            self._transformer.load(card)
            for card in monster_card_hashes
        }
        return monster_cards
