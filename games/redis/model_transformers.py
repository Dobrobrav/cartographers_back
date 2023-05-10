from games.models import MonsterCardSQL
from games.redis.models import MonsterCardRedis
from services.model_transformers_base import ITransformer, ModelHash


class MonsterCardTransformer(ITransformer):
    @staticmethod
    def dump_redis_model(model: MonsterCardRedis,
                         ) -> ModelHash:
        monster_card_hash = {
            'id': model.id,
            'name': model.name,
            'image_url': model.image_url,
            'shape': model.shape,
            'exchange_order': model.exchange_order,
        }
        return monster_card_hash

    @staticmethod
    def dump_sql_model(model: MonsterCardSQL,
                       ) -> ModelHash:
        monster_card_hash = {
            'id': model.pk,
            'name': model.name,
            'image_url': model.image.url,
            'shape': model.shape.shape_str,
            'exchange_order': model.exchange_order,
        }
        return monster_card_hash

    @staticmethod
    def load_redis_model(model_hash: ModelHash,
                         ) -> MonsterCardRedis:
        card = MonsterCardRedis(
            id=int(model_hash['id']),
            name=model_hash['name'],
            image_url=model_hash['image_url'],
            shape=model_hash['shape'],
            exchange_order=model_hash['exchange_order'],
        )
        return card
