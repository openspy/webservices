from enum import Enum
from Token import StringToken, IntToken, VariableToken, EqualsOperand, AndOperand, OrOperand, GreaterEqualsOperand, GreaterOperand, LessEqualsOperand, LessOperand
class ParserState(Enum):
    READ_VALUE = 1 #beginning, prior to any detection
    READ_VARIABLE = 2
    READ_INT = 3
    READ_STRING = 4
    READ_OPERAND = 5

class TokenType(Enum):
    TOKEN_TYPE_STRING = 1
    TOKEN_TYPE_INT = 2
    TOKEN_TYPE_VARIABLE = 3
    TOKEN_TYPE_EQUALS = 4
    TOKEN_TYPE_AND = 5
    TOKEN_TYPE_OR = 6

    TOKEN_TYPE_GREATER = 7
    TOKEN_TYPE_GREATER_EQUAL = 8
    TOKEN_TYPE_LESS = 9
    TOKEN_TYPE_LESS_EQUAL = 10


class TokenParser():
    state = ParserState.READ_VALUE
    
    skip_len = 0
    read_accumulator = ""
    token_list = []
    in_escape_sequence = False
    def isVariableChar(self, c, start):
        if c == None: return False
        if start:
            return c.isalpha()
        return c.isalnum() or c in "_"
    def isIntChar(self, c):
        if c == None: return False
        return c.isnumeric()
       

    def TryReadOperand(self, string):
        result = {}
        operand_map = {
            "==": TokenType.TOKEN_TYPE_EQUALS,
            "=": TokenType.TOKEN_TYPE_EQUALS,
            "&&": TokenType.TOKEN_TYPE_AND,
            "and": TokenType.TOKEN_TYPE_AND,
            "||": TokenType.TOKEN_TYPE_OR,
            "or": TokenType.TOKEN_TYPE_OR,
            ">=": TokenType.TOKEN_TYPE_GREATER_EQUAL,
            ">": TokenType.TOKEN_TYPE_GREATER,
            "<=": TokenType.TOKEN_TYPE_LESS_EQUAL,
            "<": TokenType.TOKEN_TYPE_LESS,
        }
        for item in operand_map:
            item_len = len(item)
            if string[:item_len].lower() == item.lower():
                result["operand"] = operand_map[item]
                result["len"] = item_len
                return result
        return None
    def CreateToken(self, token_value, parser_state):
        if parser_state == ParserState.READ_VARIABLE:
            operand_read = self.TryReadOperand(token_value)
            if operand_read != None:
                return self.CreateOperandToken(operand_read["operand"])
            return VariableToken(token_value)
        if parser_state == ParserState.READ_INT:
            return IntToken(int(token_value))
        if parser_state == ParserState.READ_STRING:
            return StringToken(token_value)
        return None
    def CreateOperandToken(self, tokentype):
        if tokentype == TokenType.TOKEN_TYPE_EQUALS:
            return EqualsOperand()
        elif tokentype == TokenType.TOKEN_TYPE_AND:
            return AndOperand()
        elif tokentype == TokenType.TOKEN_TYPE_OR:
            return OrOperand()
        elif tokentype == TokenType.TOKEN_TYPE_GREATER:
            return GreaterOperand()
        elif tokentype == TokenType.TOKEN_TYPE_GREATER_EQUAL:
            return GreaterEqualsOperand()
        elif tokentype == TokenType.TOKEN_TYPE_LESS:
            return LessOperand()
        elif tokentype == TokenType.TOKEN_TYPE_LESS_EQUAL:
            return LessEqualsOperand()
        return None
    def HandleChar(self, c):
        if c == None:
            self.read_accumulator = self.read_accumulator.strip()
            token = self.CreateToken(self.read_accumulator, self.state)
            self.token_list.append(token)
            self.state = ParserState.READ_VALUE            
            return False
        if self.state == ParserState.READ_VALUE:
            if self.isVariableChar(c, True):
                self.state = ParserState.READ_VARIABLE
            if self.isIntChar(c):
                self.state = ParserState.READ_INT
            if c == '\'' or c == '\"':
                self.state = ParserState.READ_STRING
                return True
            if c == ' ': #skip space between values
                return True 
        if self.state == ParserState.READ_STRING:
            if c == '\'' or c == '\"':
                self.skip_len += 1
                return False 
        if self.state == ParserState.READ_INT:
            if not c.isnumeric():
                return False
        
        if self.state == ParserState.READ_VARIABLE:
            if not self.isVariableChar(c, False):
                return False

        self.read_accumulator += c
        return True
    def ReadSingleToken(self, string):
        self.read_accumulator = ""
        operand_read = self.TryReadOperand(string)
        if operand_read != None:
            operand = self.CreateOperandToken(operand_read["operand"])
            self.token_list.append(operand)
            return operand_read["len"]

        self.skip_len = 0
        for c in string:
            if not self.HandleChar(c):
                break
            self.skip_len += 1
        self.HandleChar(None) #signal end
        return self.skip_len

    def ParseTokens(self, token_string):
        current_token_string = token_string
        skip_len = 0
        while current_token_string != None and len(current_token_string) > 0:            
            skip_len = self.ReadSingleToken(current_token_string)
            current_token_string = current_token_string[skip_len:]
        return self.token_list
