from typing import Callable, Iterable

from rest_framework.utils import json

from games.models import DiscoveryCard, MonsterCard
from redis import Redis

from games.services.redis_dao import MonsterCardDaoRedis


def save_monster_cards_to_redis(redis_client: Redis,
                                ) -> None:
    dao = MonsterCardDaoRedis(redis_client)
    monster_card_hashes = (
        MonsterCard.to_model_hash(card)
        for card in MonsterCard.objects.all()
    )
    dao.insert_many(monster_card_hashes)


def save_discovery_cards_to_redis(r: Redis,
                                  ) -> None:
    cards = DiscoveryCard.objects \
        .select_related('shape', 'additional_shape') \
        .all()

    for card in cards:
        _save_card_to_redis(card, r)


def _save_card_to_redis(card: DiscoveryCard,
                        r: Redis,
                        ) -> None:
    redis_format_card = _convert_card(card)
    r.hset(name=f"discovery_card:{card.id}",
           mapping=redis_format_card)


def _convert_card(card: DiscoveryCard,
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
