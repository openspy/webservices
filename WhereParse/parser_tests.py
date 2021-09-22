import unittest
from TokenParser import TokenParser
from MongoTokenConverter import MongoTokenConverter
from RPNConverter import RPNConverter

class TestStringMethods(unittest.TestCase):

    def test_single_variable(self):
        parser = TokenParser()
        result = parser.ParseTokens("filename")
        self.assertEqual(1, len(result))


#if __name__ == '__main__':
    #unittest.main()
parser = TokenParser()
#result = parser.ParseTokens("ownerid=333 AND filename=='MPStorage'")
result = parser.ParseTokens("ownerid>333 AND filename=='test' OR test==1")

rpnConverter = RPNConverter()
result = rpnConverter.Convert(result)

mongoConverter = MongoTokenConverter()

result = mongoConverter.ConvertTokenList(result)
print("mongo query: {}\n".format(result.GetMongoDocument()))