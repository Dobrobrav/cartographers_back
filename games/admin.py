from django.contrib import admin
from .models import DiscoveryCardSQL, MonsterCardSQL, ShapeSQL, ObjectiveCardSQL

# Enum (choices) models:
# admin.site.register(EDiscoveryCardType)
# admin.site.register(ExchangeOrder)
# admin.site.register(EDiscoveryCardTerrain)
# admin.site.register(EFieldTerrain)
# admin.site.register(EShapeValue)

# Regular models:
admin.site.register(DiscoveryCardSQL)
admin.site.register(MonsterCardSQL)
admin.site.register(ShapeSQL)
admin.site.register(ObjectiveCardSQL)
