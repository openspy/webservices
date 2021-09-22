class SAKEException(Exception):
    result = "Unknown"
    pass
class RecordNotFoundException(SAKEException):
    result = "RecordNotFound"
    pass
class TableNotFoundException(SAKEException):
    #result = "TableNotFound"
    result = "RecordNotFound" #trick games into using it anyways
    pass
class LoginTicketInvalidException(SAKEException):
    result = "LoginTicketInvalid"
    pass