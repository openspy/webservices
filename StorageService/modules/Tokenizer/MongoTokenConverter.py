from modules.Tokenizer.Token import OperatorToken, OperandToken
from modules.Tokenizer.Token import StringToken, IntToken, VariableToken, EqualsOperand, AndOperand, OrOperand, LessOperand, LessEqualsOperand, GreaterOperand, GreaterEqualsOperand
class MongoToken():
    def __init__(self):
        pass
    def GetMongoDocument(self):
        return None
class MongoVariable(MongoToken):
    def __init__(self, name):
        self.name = name
    def GetMongoDocument(self):
        return "data.{}.value".format(self.name)
class MongoInt(MongoToken):
    def __init__(self, value):
        self.value = value
    def GetMongoDocument(self):
        return self.value
class MongoString(MongoToken):
    def __init__(self, value):
        self.value = value
    def GetMongoDocument(self):
        return self.value
class MongoEqualsOperator(MongoToken):
    def __init__(self, lvalue, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue
    def GetMongoDocument(self):
        return {self.lvalue.GetMongoDocument() : {"$eq":  self.rvalue.GetMongoDocument()}}
class MongoAndOperator(MongoToken):
    def __init__(self, lvalue, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue
    def GetMongoDocument(self):
        return {"$and": [self.lvalue.GetMongoDocument(), self.rvalue.GetMongoDocument()]}
class MongoOrOperator(MongoToken):
    def __init__(self, lvalue, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue
    def GetMongoDocument(self):
        return {"$or": [self.lvalue.GetMongoDocument(), self.rvalue.GetMongoDocument()]}
class MongoGreaterEqualsOperator(MongoToken):
    def __init__(self, lvalue, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue
    def GetMongoDocument(self):
        return {self.lvalue.GetMongoDocument() : {"$gte":  self.rvalue.GetMongoDocument()}}
class MongoGreaterOperator(MongoToken):
    def __init__(self, lvalue, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue
    def GetMongoDocument(self):
        return {self.lvalue.GetMongoDocument() : {"$gt":  self.rvalue.GetMongoDocument()}}
class MongoLessEqualsOperator(MongoToken):
    def __init__(self, lvalue, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue
    def GetMongoDocument(self):
        return {self.lvalue.GetMongoDocument() : {"$lte":  self.rvalue.GetMongoDocument()}}
class MongoLessOperator(MongoToken):
    def __init__(self, lvalue, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue
    def GetMongoDocument(self):
        return {self.lvalue.GetMongoDocument() : {"$lt":  self.rvalue.GetMongoDocument()}}

class MongoTokenConverter():
    def __init__(self):
        pass
    def ConvertValueToken(self, token):
        if isinstance(token, VariableToken):
            return MongoVariable(token.value)
        elif isinstance(token, IntToken):
            return MongoInt(token.value)
        elif isinstance(token, StringToken):
            return MongoString(token.value)

    def ConvertOperatorToken(self, token, value_stack):
        if isinstance(token, EqualsOperand):
            rvalue = value_stack.pop()
            lvalue = value_stack.pop()
            return MongoEqualsOperator(lvalue, rvalue)
        elif isinstance(token, AndOperand):
            rvalue = value_stack.pop()
            lvalue = value_stack.pop()
            return MongoAndOperator(lvalue, rvalue)
        elif isinstance(token, OrOperand):
            rvalue = value_stack.pop()
            lvalue = value_stack.pop()
            return MongoOrOperator(lvalue, rvalue)
        elif isinstance(token, LessOperand):
            rvalue = value_stack.pop()
            lvalue = value_stack.pop()
            return MongoLessOperator(lvalue, rvalue)
        elif isinstance(token, LessEqualsOperand):
            rvalue = value_stack.pop()
            lvalue = value_stack.pop()
            return MongoLessEqualsOperator(lvalue, rvalue)
        elif isinstance(token, GreaterOperand):
            rvalue = value_stack.pop()
            lvalue = value_stack.pop()
            return MongoGreaterOperator(lvalue, rvalue)
        elif isinstance(token, GreaterEqualsOperand):
            rvalue = value_stack.pop()
            lvalue = value_stack.pop()
            return MongoGreaterEqualsOperator(lvalue, rvalue)
        return None
    def ConvertTokenList(self, token_list):
        value_stack = []
        for token in token_list:
            if isinstance(token, OperandToken):
                value_stack.append(self.ConvertValueToken(token))
            elif isinstance(token, OperatorToken):
                operator_token = self.ConvertOperatorToken(token, value_stack)
                value_stack.append(operator_token)
                
        if len(value_stack) != 1:
            return None
        return value_stack[0]