class LogMessages:
    class General:
        SESSION_START = "[SESSION][START]"

    class Auth:
        ATTEMPT_LOGIN = "[AUTH][LOGIN_ATTEMPT] email={}"
        LOGIN_SUCCESS = "[AUTH][LOGIN_SUCCESS] email={}"

    class Movies:
        ATTEMPT_CREATE = "[MOVIE][CREATE_ATTEMPT] name={}"
        CREATE_SUCCESS = "[MOVIE][CREATE_SUCCESS] name={} movie_id={}"
        ATTEMPT_GET_BY_ID = "[MOVIE][GET_BY_ID_ATTEMPT] movie_id={}"
        GET_BY_ID_SUCCESS = "[MOVIE][GET_BY_ID_SUCCESS] name={} movie_id={}"
        ATTEMPT_DELETE = "[MOVIE][DELETE_ATTEMPT] movie_id={}"
        DELETE_SUCCESS = "[MOVIE][DELETE_SUCCESS] name={} movie_id={}"
        ATTEMPT_GET_LIST = "[MOVIE][LIST_ATTEMPT] params={}"
        ATTEMPT_GET_LIST_INVALID = "[MOVIE][LIST_INVALID_ATTEMPT] params={}"
        ATTEMPT_EDIT = "[MOVIE][EDIT_ATTEMPT] movie_id={}"
        EDIT_SUCCESS = "[MOVIE][EDIT_SUCCESS] name={} movie_id={}"
