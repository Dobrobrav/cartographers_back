from django.contrib import admin
from .models import *

# Enum (choices) models:
# admin.site.register(EDiscoveryCardType)
# admin.site.register(ExchangeOrder)
# admin.site.register(EDiscoveryCardTerrain)
# admin.site.register(EFieldTerrain)
# admin.site.register(EShapeValue)

# Regular models:
admin.site.register(DiscoveryCard)
admin.site.register(MonsterCard)
admin.site.register(Shape)
