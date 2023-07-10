from cartographers_back.settings import R
from games.models import TerrainCardSQL, MonsterCardSQL, ObjectiveCardSQL, ShapeSQL
from redis import Redis

from games.redis.dao import MonsterCardDao, TerrainCardDao, ObjectiveCardDao, ShapeDaoRedis


def save_models_to_redis():
    _upload_terrain_cards(R)
    _upload_monster_cards(R)
    _upload_objective_cards(R)
    _upload_shapes(R)



def _upload_shapes(redis: Redis,
                   ) -> None:
    objective_cards_sql = ShapeSQL.objects.all()
    ShapeDaoRedis(redis).insert_sql_models(objective_cards_sql)


def _upload_objective_cards(redis: Redis,
                            ) -> None:
    dao = ObjectiveCardDao(redis)
    objective_cards_sql = ObjectiveCardSQL.objects.all()
    dao.insert_sql_models(objective_cards_sql)


def _upload_monster_cards(redis: Redis,
                          ) -> None:
    dao = MonsterCardDao(redis)
    cards = MonsterCardSQL.objects.select_related('shape').all()
    dao.insert_sql_models(cards)


def _upload_terrain_cards(redis: Redis,
                          ) -> None:
    terrain_cards = TerrainCardSQL.objects \
        .select_related('shape', 'additional_shape').all()

    TerrainCardDao(redis).insert_sql_models(terrain_cards)
