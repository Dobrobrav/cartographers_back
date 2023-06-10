from django.test import TestCase
from ..models import ShapeSQL


class ShapeSQLTest(TestCase):
    @staticmethod
    def create(shape_str: str,
               gives_coin: bool,
               ) -> ShapeSQL:
        return ShapeSQL.objects.create(shape_str=shape_str,
                                       gives_coin=gives_coin)

    def test_creation(self) -> None:
        shape = self.create(shape_str='111 011 001', gives_coin=True)
        self.assertTrue(isinstance(shape, ShapeSQL))
