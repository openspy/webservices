from Token import OperatorToken, OperandToken
class RPNConverter():
    def __init__(self):
        pass
    def Convert(self, token_list):
        tokens = []
        operator_stack = []
        for token in token_list:
            if isinstance(token, OperandToken):
                tokens.append(token)
            elif isinstance(token, OperatorToken):
                while len(operator_stack) > 0 and isinstance(operator_stack[0], OperatorToken):
                    if operator_stack[0].GetPrecedence() >= token.GetPrecedence():
                        tokens.append(operator_stack[0])
                        operator_stack.pop(0)
                    else:
                        break
                operator_stack.insert(0, token)
        while len(operator_stack) > 0:
            tokens.append(operator_stack[0])
            operator_stack.pop(0)
        return tokens