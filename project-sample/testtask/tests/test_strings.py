import unittest
from testtask.src.string_utils import reverse_string

class TestStrings(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(reverse_string('hello'), 'olleh')

if __name__ == '__main__':
    unittest.main()
