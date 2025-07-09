# Create your tests here.
from django.test import TestCase


class TestRandom(TestCase):
    def test_index(self):
        self.client.get("/")

        self.assertEqual(200, 200)
