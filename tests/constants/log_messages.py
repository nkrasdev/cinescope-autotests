class LogMessages:
    class General:
        SESSION_START = "=" * 20 + " Test session started " + "=" * 20

    class Auth:
        ATTEMPT_LOGIN = "Попытка логина для пользователя {}"
        LOGIN_SUCCESS = "Пользователь {} успешно вошел в систему."

    class Movies:
        ATTEMPT_CREATE = "Попытка создания фильма с названием '{}'"
        CREATE_SUCCESS = "Фильм '{}' (ID: {}) успешно создан."
        ATTEMPT_GET_BY_ID = "Попытка получения фильма по ID {}"
        GET_BY_ID_SUCCESS = "Фильм '{}' (ID: {}) успешно получен."
        ATTEMPT_DELETE = "Попытка удаления фильма с ID {}"
        DELETE_SUCCESS = "Фильм '{}' (ID: {}) успешно удален."
        ATTEMPT_GET_LIST = "Попытка получения списка фильмов с параметрами: {}"
        ATTEMPT_GET_LIST_INVALID = "Попытка получения списка фильмов с невалидными параметрами: {}"
        ATTEMPT_EDIT = "Попытка редактирования фильма с ID {}"
        EDIT_SUCCESS = "Фильм '{}' (ID: {}) успешно отредактирован."
