from unittest.mock import patch

from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django_fakeredis import fakeredis
from djoser.conf import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.utils import json

from cartographers_back.settings import R
from rooms.redis.dao import RoomDao


class RoomsAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user',
                                             password='test_password')
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()
        redis_patcher = patch('rooms.views.REDIS', fakeredis.FakeRedis)
        self.redis = redis_patcher.start()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_room(self):
        url = reverse('room')
        data = {
            'name': 'foo_room',
            'password': '123',
            'max_players': 5,
        }

        # Make the API request to create a room
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)  # Assuming a successful creation returns 201

        # Retrieve the room data from Redis
        room_id = response.data.get('id')
        redis_key = f'rooms:{room_id}'
        redis_data = self.redis.get(redis_key)  # Assuming the data stored in Redis is a JSON string

        # Compare the initial data with the Redis data
        self.assertIsNotNone(redis_data)  # Ensure data is present in Redis
        redis_data = json.loads(redis_data)  # Convert Redis data from JSON string to Python dict

        self.assertEqual(data['name'], redis_data['name'])
        self.assertEqual(data['max_players'], redis_data['max_players'])
        self.assertEqual(self.user.id, redis_data['max_players'])
        self.assertTrue(check_password(data['password'], redis_data['password']))
