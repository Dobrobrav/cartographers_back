from django.contrib import admin
from .models import MonsterCardSQL, ShapeSQL, ObjectiveCardSQL, SeasonCardSQL, TerrainCardSQL

admin.site.register(MonsterCardSQL)
admin.site.register(ShapeSQL)
admin.site.register(ObjectiveCardSQL)
admin.site.register(SeasonCardSQL)
admin.site.register(TerrainCardSQL)
