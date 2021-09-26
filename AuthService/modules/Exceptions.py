from modules.ResponseCode import ResponseCodes
class AuthServiceException(Exception):
    response_code = ResponseCodes.LOGIN_RESPONSE_SERVER_ERROR
class MissingParameterException(AuthServiceException):
    result = ResponseCodes.LOGIN_RESPONSE_SERVER_ERROR
class InvalidCredentialsException(AuthServiceException):
    results = ResponseCodes.LOGIN_RESPONSE_INVALID_PASSWORD
class InvalidProfileException(AuthServiceException):
    results = ResponseCodes.LOGIN_RESPONSE_INVALID_PROFILE
class UserNotFoundException(AuthServiceException):
    results = ResponseCodes.LOGIN_RESPONSE_USER_NOT_FOUND