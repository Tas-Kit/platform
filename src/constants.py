class ROLE(object):
    OWNER = 10
    ADMIN = 5
    STANDARD = 0


class ERROR_CODE():
    APP_NOT_FIND = 0
    NOT_HAVE_APP = 1
    USER_NOT_FIND = 2
    TOBJECT_NOT_FIND = 3
    UNABLE_TO_DECRYPT = 4
    USER_NOT_MATCH = 5
    KEY_EXPIRED = 6
    UNSUPPORTED_DATA_TYPE = 7
    NEO4J_PUSH_FAILURE = 8
    NO_WRITE_PERMISSION = 9
    ID_NOT_MATCH = 10
    NEO4J_DATABASE_ERROR = 11
    PLATFORM_ROOT_KEY_IS_NONE = 12
    REQUIRE_HIHGER_PERMISSION = 13
    UNABLE_TO_SHARE_APP = 14
    NO_READ_PERMISSION = 15
