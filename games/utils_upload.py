import services.utils
from cartographers_back.settings import REDIS
from games.models import DiscoveryCardSQL, MonsterCardSQL, ObjectiveCardSQL, ShapeSQL, EShapeUnit
from redis import Redis

from games.redis.dao import MonsterCardDaoRedis, TerrainCardDaoRedis, ObjectiveCardDaoRedis, ShapeDaoRedis
from services.redis.models_base import get_enum_by_value


def save_models_to_redis():
    _upload_terrain_cards(REDIS)
    _upload_monster_cards(REDIS)
    _upload_objective_cards(REDIS)
    _upload_shapes(REDIS)


def _upload_shapes(redis: Redis,
                   ) -> None:
    objective_cards_sql = ShapeSQL.objects.all()
    ShapeDaoRedis(redis).insert_sql_models(objective_cards_sql)


def _upload_objective_cards(redis: Redis,
                            ) -> None:
    dao = ObjectiveCardDaoRedis(redis)
    objective_cards_sql = ObjectiveCardSQL.objects.all()
    dao.insert_sql_models(objective_cards_sql)


def _upload_monster_cards(redis: Redis,
                          ) -> None:
    dao = MonsterCardDaoRedis(redis)
    cards = MonsterCardSQL.objects.select_related('shape').all()
    dao.insert_sql_models(cards)


def _upload_terrain_cards(redis: Redis,
                          ) -> None:
    terrain_cards = DiscoveryCardSQL.objects \
        .select_related('shape', 'additional_shape').all()

    TerrainCardDaoRedis(redis).insert_sql_models(terrain_cards)
