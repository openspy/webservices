#values
class ValueToken():
    value = None
    def __init__(self):
        pass
class IntToken():
    def __init__(self, value):
        self.value = value
class StringToken():
    def __init__(self, value):
        print("StringToken: {}\n".format(value))
        self.value = value
class VariableToken():
    def __init__(self, value):
        print("VariableToken: {}\n".format(value))
        self.value = value


#operands
class OperandToken():
    def __init__(self):
        pass
class AndOperand(OperandToken):
    def __init__(self):
        pass
class OrOperand(OperandToken):
    def __init__(self):
        pass
class EqualsOperand(OperandToken):
    def __init__(self):
        pass