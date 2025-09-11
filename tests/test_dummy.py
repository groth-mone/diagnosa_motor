from django.test import TestCase

class DummyTest(TestCase):
    def test_always_passes(self):
        self.assertEqual(1 + 1, 2)
