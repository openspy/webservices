	# // Competition system errors:
	# SCServiceResult_NO_ERROR = 0,
	# SCServiceResult_COULD_NOT_START,
	# SCServiceResult_COULD_NOT_JOIN,
	# SCServiceResult_COULD_NOT_LEAVE,

	# // Input validation errors:
	# SCServiceResult_PROFILE_ID_INVALID,
	# SCServiceResult_IP_INVALID,
	# SCServiceResult_ID_INVALID,
	# SCServiceResult_REPORT_INVALID,
	# SCServiceResult_AUTH_INVALID,

	# // System errors:
	# SCServiceResult_SERVER_ERROR,
	# SCServiceResult_DATABASE_ERROR,

	# // More input validation errors:
	# SCServiceResult_GAMEID_INVALID

class CompetitionException(Exception):
    result = 9
    pass
class InvalidCertificateException(CompetitionException):
    result = 8
    pass
class InvalidReportException(CompetitionException):
    result = 7
    pass