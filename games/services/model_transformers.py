from abc import ABC, abstractmethod
from typing import TypeAlias

from games.services.redis_models import RedisModel, MonsterCard

ModelHash: TypeAlias = dict[str, str]


class ModelTransformer(ABC):
    @abstractmethod
    def dump(self,
             model: RedisModel,
             ) -> ModelHash:
        pass

    @abstractmethod
    def load(self,
             redis_hash: ModelHash,
             ) -> RedisModel:
        pass


class MonsterCardTransformer(ModelTransformer):
    def dump(self,
             model: MonsterCard,
             ) -> ModelHash:
        monster_card_hash = {
            'id': model.id,
            'name': model.name,
            'image_url': model.image_url,
            'shape': model.shape,
            'exchange_order': model.exchange_order,
        }
        return monster_card_hash

    def load(self,
             model_hash: ModelHash,
             ) -> MonsterCard:
        card = MonsterCard(
            id=int(model_hash['id']),
            name=model_hash['name'],
            image_url=model_hash['image_url'],
            shape=model_hash['shape'],
            exchange_order=model_hash['exchange_order'],
        )
        return card
