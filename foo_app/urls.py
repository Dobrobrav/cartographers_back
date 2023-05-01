from django.urls import path

from .views import set_view, get_view

urlpatterns = [
    path('set_url/<str:key>/<str:value>', set_view),
    path('get_url/<str:key>/', get_view),
]
