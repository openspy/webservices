from modules.ResponseCode import ResponseCodes
class AuthServiceException(Exception):
    response_code = ResponseCodes.LOGIN_RESPONSE_SERVER_ERROR
class MissingParameterException(AuthServiceException):
    response_code = ResponseCodes.LOGIN_RESPONSE_SERVER_ERROR
class InvalidCredentialsException(AuthServiceException):
    response_code = ResponseCodes.LOGIN_RESPONSE_INVALID_PASSWORD
class InvalidProfileException(AuthServiceException):
    response_code = ResponseCodes.LOGIN_RESPONSE_INVALID_PROFILE
class UserNotFoundException(AuthServiceException):
    response_code = ResponseCodes.LOGIN_RESPONSE_USER_NOT_FOUND