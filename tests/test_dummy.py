import unittest

from src.app import hello_world


class DummyTest(unittest.TestCase):
    def test(self):
        self.assertEqual(hello_world(), "Hello world!")


if __name__ == '__main__':
    unittest.main()
