# Architecture Documentation

## Обзор проекта

Cinescope Autotests - это набор автоматизированных тестов для проверки функциональности сервиса Cinescope через API и UI.

## Структура проекта

```
cinescope-autotests/
├── tests/                      # Корневая директория тестов
│   ├── api/                    # API тесты
│   │   ├── test_auth.py
│   │   ├── test_create_movie.py
│   │   ├── test_delete_movie.py
│   │   ├── test_edit_movie.py
│   │   ├── test_get_movie_by_id.py
│   │   ├── test_get_movies.py
│   │   ├── test_genres.py
│   │   ├── test_mock_movie.py
│   │   ├── test_payments.py
│   │   ├── test_reviews.py
│   │   └── test_users.py
│   │
│   ├── ui/                     # UI тесты (Playwright)
│   │   ├── pages/             # Page Object модели
│   │   │   ├── base_page.py
│   │   │   ├── login_page.py
│   │   │   ├── main_page.py
│   │   │   ├── movie_details_page.py
│   │   │   ├── movies_page.py
│   │   │   ├── payment_page.py
│   │   │   ├── payment_success_page.py
│   │   │   └── register_page.py
│   │   ├── test_main_page.py
│   │   ├── test_movie_details_page.py
│   │   ├── test_movies_page.py
│   │   ├── test_payment_page.py
│   │   └── test_ui_auth.py
│   │
│   ├── clients/               # API клиенты
│   │   ├── api_manager.py    # Центральный менеджер API клиентов
│   │   ├── auth_api.py       # Клиент для аутентификации
│   │   ├── movies_api.py     # Клиент для работы с фильмами
│   │   ├── payment_api.py    # Клиент для платежей
│   │   └── users_api.py      # Клиент для работы с пользователями
│   │
│   ├── models/                # Pydantic модели
│   │   ├── movie_models.py   # Модели фильмов
│   │   ├── payment_models.py # Модели платежей
│   │   ├── request_models.py # Модели запросов
│   │   ├── response_models.py # Модели ответов
│   │   └── user_models.py    # Модели пользователей
│   │
│   ├── constants/             # Константы
│   │   ├── endpoints.py      # API эндпоинты
│   │   ├── log_messages.py   # Сообщения для логов
│   │   ├── payment_data.py   # Данные для платежей
│   │   ├── timeouts.py       # Таймауты
│   │   └── ui_data.py        # UI данные
│   │
│   ├── utils/                 # Утилиты
│   │   ├── data_generator.py # Генераторы тестовых данных
│   │   └── decorators.py     # Кастомные декораторы
│   │
│   ├── request/               # HTTP запросы
│   │   └── custom_requester.py # Базовый класс для HTTP запросов
│   │
│   ├── config.py              # Конфигурация (Pydantic Settings)
│   └── conftest.py            # Pytest фикстуры и хуки
│
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD
├── logs/                      # Логи тестов
├── allure-results/           # Результаты Allure
├── .env.example              # Пример переменных окружения
├── .editorconfig             # Конфигурация редактора
├── .gitattributes            # Git атрибуты
├── .gitignore                # Git игнор
├── .pre-commit-config.yaml   # Pre-commit hooks
├── ARCHITECTURE.md           # Этот файл
├── CONTRIBUTING.md           # Руководство для контрибьюторов
├── Makefile                  # Make команды
├── pyproject.toml            # Конфигурация проекта и инструментов
└── README.md                 # Основная документация
```

## Архитектурные слои

### 1. API Clients Layer

**Назначение**: Инкапсуляция логики взаимодействия с API

**Компоненты**:
- `CustomRequester`: Базовый класс для всех HTTP запросов
  - Интеграция с Allure (attachments)
  - Логирование запросов/ответов
  - Валидация статус-кодов

- `ApiManager`: Централизованное управление API клиентами
  - Инициализация всех API клиентов
  - Управление сессией requests
  - Связывание клиентов между собой

- Специализированные клиенты:
  - `AuthAPI`: Аутентификация (login, register, logout)
  - `MoviesAPI`: CRUD операции с фильмами
  - `PaymentAPI`: Платежи
  - `UsersAPI`: Управление пользователями

**Паттерны**:
- Composition over Inheritance
- Dependency Injection через session
- Type-safe responses с Union types

```python
type MovieResponse = Movie | ErrorResponse
```

### 2. Models Layer

**Назначение**: Валидация и типизация данных через Pydantic

**Особенности**:
- Строгая типизация всех полей
- Автоматическая валидация
- Алиасы для camelCase ↔ snake_case
- Enums для ограниченных значений (Location, GenreId)

**Примеры**:
```python
class Movie(BaseModel):
    id: int
    name: str
    location: Location
    genre_id: int = Field(alias="genreId")
```

### 3. Page Object Model (UI)

**Назначение**: Абстракция UI элементов и действий

**Структура**:
- `BasePage`: Базовый класс для всех страниц
  - Общие методы (open, is_url)
  - Управление page объектом Playwright

- Специализированные страницы:
  - Локаторы элементов
  - Методы взаимодействия
  - Проверки состояния

**Преимущества**:
- Изоляция изменений UI
- Переиспользование кода
- Читаемость тестов

### 4. Test Layer

**Структура тестов**:
```python
@allure.epic("Фильмы")
@allure.feature("Создание фильма")
class TestCreateMovie:
    @allure_test_details(...)
    def test_create_movie_success(self, admin_api_manager, movie_payload):
        # Arrange (фикстуры)
        # Act (действия через API clients)
        # Assert (проверки через pytest-check)
        pass
```

**Принципы**:
- Один тест = одна проверка
- Изоляция тестов (каждый тест независим)
- Fixtures для setup/teardown
- Allure декораторы для отчетности

## Управление зависимостями

### Runtime Dependencies
- `pytest`: Тестовый фреймворк
- `requests`: HTTP клиент
- `pydantic`: Валидация данных
- `playwright`: UI тестирование
- `allure-pytest`: Отчетность
- `faker`: Генерация тестовых данных

### Development Dependencies
- `ruff`: Линтер и форматтер
- `mypy`: Статическая проверка типов
- `bandit`: Проверка безопасности
- `pytest-cov`: Coverage
- `pytest-xdist`: Параллельное выполнение
- `pre-commit`: Git hooks

## Конфигурация

### Окружения

Конфигурация через Pydantic Settings (`tests/config.py`):
```python
class Settings(BaseSettings):
    base_url: str
    admin_email: str | None
    admin_password: str | None

    model_config = SettingsConfigDict(env_file=".env")
```

Поддержка переменных окружения:
- `.env` файл (локальная разработка)
- Environment variables (CI/CD)

### Pytest конфигурация

Настройки в `pyproject.toml`:
- Markers для категоризации тестов
- Logging конфигурация
- Allure integration

## CI/CD Pipeline

### Jobs

1. **Lint**: Проверка стиля кода (ruff)
2. **Type Check**: Статическая проверка типов (mypy)
3. **Security**: Проверка безопасности (bandit)
4. **API Tests**: Запуск API тестов с coverage

### Artifacts
- Coverage reports (HTML + XML)
- Allure results

## Логирование и Отчетность

### Логирование

**Уровни**:
- Console: INFO level
- File: INFO level (logs/tests.log)

**Формат**:
```
YYYY-MM-DD HH:MM:SS [LEVEL] Message (file.py:line)
```

**Особенности**:
- Curl команды для воспроизведения запросов
- Маскировка токенов авторизации
- Цветовое выделение в консоли

### Allure Report

**Структура**:
- Parent Suite: "Cinescope"
- Suite: "API" | "UI"
- Sub Suite: Автоматически по имени файла

**Attachments**:
- Request line
- Request body (JSON)
- Response body (JSON)
- Screenshots (для UI тестов при падении)

## Паттерны и Best Practices

### 1. Fixtures для изоляции тестов

```python
@pytest.fixture
def created_movie(admin_api_manager, movie_payload):
    movie = admin_api_manager.movies_api.create_movie(movie_payload)
    yield movie
    admin_api_manager.movies_api.delete_movie(movie.id)
```

### 2. Soft assertions

Использование `pytest-check` для множественных проверок:
```python
with allure.step("Проверка данных"):
    check.equal(movie.name, expected_name)
    check.equal(movie.price, expected_price)
```

### 3. Параметризация тестов

```python
@pytest.mark.parametrize("field,value", [
    ("name", 12345),
    ("price", "invalid"),
])
def test_invalid_field(self, field, value):
    # Test logic
    pass
```

### 4. Custom decorators

```python
@allure_test_details(
    story="История",
    title="Название теста",
    description="Описание",
    severity=allure.severity_level.CRITICAL,
)
```

## Безопасность

### Secrets Management
- Секреты в `.env` (не коммитится)
- GitHub Secrets для CI/CD
- Маскировка в логах

### Security Checks
- Bandit для поиска уязвимостей
- Pre-commit hook для проверки приватных ключей

## Масштабирование

### Параллельное выполнение

```bash
make test-parallel
# или
pytest -n auto
```

### Coverage

```bash
make test-cov
```

Отчет генерируется в `htmlcov/index.html`

## Дальнейшее развитие

### Возможные улучшения

1. **Test Data Management**
   - Фикстуры в JSON/YAML файлах
   - Factory pattern для создания данных

2. **Docker Integration**
   - Dockerfile для локального запуска
   - Docker Compose для зависимостей

3. **Load Testing**
   - Integration с Locust/k6
   - Performance тесты

4. **Contract Testing**
   - OpenAPI schema validation
   - Pact testing

5. **Visual Regression Testing**
   - Percy/Chromatic integration
   - Screenshot comparison

## Контакты и поддержка

При вопросах об архитектуре создавайте Issue на GitHub.
