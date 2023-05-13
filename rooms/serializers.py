from rest_framework import serializers


class RoomSerializer(serializers.Serializer):
    name = serializers.CharField()
    max_players = serializers.IntegerField()
    admin_id = serializers.IntegerField()
    current_users = serializers.IntegerField()
