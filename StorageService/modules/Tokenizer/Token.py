#values
class OperandToken():
    value = None
    def __init__(self):
        pass
class IntToken(OperandToken):
    def __init__(self, value):
        self.value = value
class StringToken(OperandToken):
    def __init__(self, value):
        self.value = value
class VariableToken(OperandToken):
    def __init__(self, value):
        self.value = value


#operands
class OperatorToken():
    precedence = 0
    def __init__(self):
        self.precedence = 0
        pass
    def GetPrecedence(self):
        return self.precedence
class AndOperand(OperatorToken):
    def __init__(self):
        self.precedence = 2
        pass
class OrOperand(OperatorToken):
    def __init__(self):
        self.precedence = 1
        pass
class EqualsOperand(OperatorToken):
    def __init__(self):
        self.precedence = 3
        pass
class LessOperand(OperatorToken):
    def __init__(self):
        self.precedence = 3
        pass
class LessEqualsOperand(OperatorToken):
    def __init__(self):
        self.precedence = 3
        pass
class GreaterOperand(OperatorToken):
    def __init__(self):
        self.precedence = 3
        pass
class GreaterEqualsOperand(OperatorToken):
    def __init__(self):
        self.precedence = 3
        pass