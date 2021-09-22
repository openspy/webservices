import unittest
from TokenParser import TokenParser

class TestStringMethods(unittest.TestCase):

    def test_single_variable(self):
        parser = TokenParser()
        result = parser.ParseTokens("filename")
        self.assertEqual(1, len(result))


#if __name__ == '__main__':
    #unittest.main()
parser = TokenParser()
result = parser.ParseTokens("ownerid=333 AND filename=='MPStorage'")