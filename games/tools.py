import redis
from rest_framework.utils import json

from games.models import DiscoveryCardSQL, MonsterCardSQL
from redis import Redis

from games.redis.dao import MonsterCardDaoRedis


def save_models_to_redis():
    client = redis.Redis(host='redis',
                         port=6379,
                         db=0)
    _save_discovery_cards(client)
    _save_monster_cards_to_redis(client)


def _save_monster_cards_to_redis(redis_client: Redis,
                                 ) -> None:
    dao = MonsterCardDaoRedis(redis_client)
    # TODO: add select_related!!
    cards = MonsterCardSQL.objects.all()
    dao.insert_sql_model_many(cards)


def _save_discovery_cards(redis_client: Redis,
                          ) -> None:
    cards = DiscoveryCardSQL.objects \
        .select_related('shape', 'additional_shape') \
        .all()

    for card in cards:
        _save_card_to_redis(card, redis_client)


def _save_card_to_redis(card: DiscoveryCardSQL,
                        r: Redis,
                        ) -> None:
    redis_format_card = _convert_card(card)
    r.hset(name=f"discovery_card:{card.id}",
           mapping=redis_format_card)


def _convert_card(card: DiscoveryCardSQL,
                  ) -> dict[str, str]:
    if card.card_type == 'ruins':
        redis_card = {
            'name': card.name,
            'image_url': card.image.url,
            'card_type': card.card_type,
        }
        return redis_card

    redis_card = {
        'name': card.name,
        'image_url': card.image.url,
        'card_type': card.card_type,
        'terrain': card.terrain,
        'shape': json.dumps({
            'shape_str': card.shape.shape_str,
            'gives_coin': card.shape.gives_coin,
        }),
        'season_points': card.season_points,
    }

    if card.additional_shape:
        redis_card['additional_shape'] = json.dumps({
            'shape_str': card.additional_shape.shape_str,
            'gives_coin': card.additional_shape.gives_coin,
        })

    if card.additional_terrain:
        redis_card['additional_terrain'] = card.additional_terrain

    return redis_card