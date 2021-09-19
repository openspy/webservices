class SAKEException(Exception):
    result = "Unknown"
    pass
class RecordNotFoundException(SAKEException):
    result = "RecordNotFound"
    pass
class TableNotFoundException(SAKEException):
    result = "TableNotFound"
    pass
class LoginTicketInvalidException(SAKEException):
    result = "LoginTicketInvalid"
    pass