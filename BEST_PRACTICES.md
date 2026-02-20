# Best Practices & Recommendations

## Что уже внедрено ✅

### Code Quality
- ✅ Ruff для линтинга и форматирования
- ✅ mypy для статической проверки типов
- ✅ Bandit для проверки безопасности
- ✅ Pre-commit hooks
- ✅ EditorConfig для единообразного форматирования

### Testing
- ✅ pytest с современной конфигурацией
- ✅ pytest-cov для coverage
- ✅ pytest-xdist для параллельного выполнения
- ✅ Allure Report v3 для отчетности
- ✅ Изоляция тестов через fixtures

### Architecture
- ✅ Page Object Model для UI тестов
- ✅ API Clients с типизацией
- ✅ Pydantic модели для валидации
- ✅ Централизованная конфигурация

### DevOps
- ✅ GitHub Actions CI/CD
- ✅ Автоматические проверки в PR
- ✅ Coverage reporting
- ✅ Artifact uploads

## Дополнительные инструменты для внедрения

### 1. Mutation Testing 🧬

**Что**: Проверка качества тестов путем внесения мутаций в код

**Инструменты**:
- [mutmut](https://github.com/boxed/mutmut) - Python mutation testing
- [cosmic-ray](https://github.com/sixty-north/cosmic-ray) - Альтернатива

**Установка**:
```bash
# Добавить в pyproject.toml dev dependencies
"mutmut>=2.4.0"
```

**Использование**:
```bash
# Запуск mutation testing
mutmut run

# Просмотр результатов
mutmut results
mutmut html  # HTML отчет
```

**Конфигурация** (добавить в pyproject.toml):
```toml
[tool.mutmut]
paths_to_mutate = "tests/"
backup = false
runner = "pytest -x"
tests_dir = "tests/"
```

### 2. Property-Based Testing 🎲

**Что**: Генерация случайных входных данных для поиска граничных случаев

**Инструмент**: [Hypothesis](https://hypothesis.readthedocs.io/)

**Установка**:
```bash
# Добавить в dependencies
"hypothesis>=6.100.0"
```

**Пример использования**:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=100))
def test_movie_name_validation(movie_name):
    # Тест с автоматически сгенерированными данными
    payload = {"name": movie_name, ...}
    response = api.create_movie(payload)
    assert response.status_code in [201, 400]
```

### 3. Contract Testing 📋

**Что**: Проверка соответствия API контракту (OpenAPI/Swagger schema)

**Инструменты**:
- [schemathesis](https://github.com/schemathesis/schemathesis) - API testing
- [pact-python](https://github.com/pact-foundation/pact-python) - Consumer-driven contracts

**Установка Schemathesis**:
```bash
# Добавить в dev dependencies
"schemathesis>=3.28.0"
```

**Использование**:
```bash
# Тестирование по OpenAPI schema
schemathesis run https://api.cinescope.ru/openapi.json \
  --checks all \
  --hypothesis-max-examples=100
```

### 4. Load/Performance Testing ⚡

**Что**: Проверка производительности API под нагрузкой

**Инструменты**:
- [Locust](https://locust.io/) - Python-based load testing
- [k6](https://k6.io/) - JavaScript-based (можно интегрировать)

**Установка Locust**:
```bash
"locust>=2.23.0"
```

**Пример** (создать `tests/load/locustfile.py`):
```python
from locust import HttpUser, task, between

class CinescopeUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_movies(self):
        self.client.get("/api/movies")

    @task(3)  # 3x более частый
    def get_movie_by_id(self):
        self.client.get("/api/movies/1")
```

**Запуск**:
```bash
locust -f tests/load/locustfile.py --host=https://api.cinescope.ru
```

### 5. Visual Regression Testing 👁️

**Что**: Автоматическое сравнение скриншотов UI

**Инструменты**:
- [Percy](https://percy.io/) - Cloud-based (платный)
- [playwright-pytest](https://playwright.dev/python/docs/test-runners#visual-comparisons) - Встроенные возможности

**Пример с Playwright**:
```python
def test_movie_page_visual(page):
    page.goto("/movies/1")
    page.screenshot(path="screenshots/movie-page.png")
    # Сравнение с baseline
    expect(page).to_have_screenshot("movie-page.png")
```

### 6. API Mocking & Stubbing 🎭

**Что**: Моки для тестирования без реального API

**Инструменты**:
- [responses](https://github.com/getsentry/responses) - Mock requests
- [pytest-httpserver](https://pytest-httpserver.readthedocs.io/) - HTTP server в тестах
- [VCR.py](https://vcrpy.readthedocs.io/) - Запись/воспроизведение HTTP запросов

**Установка**:
```bash
"responses>=0.25.0"
"vcrpy>=6.0.0"
```

**Пример с responses**:
```python
import responses

@responses.activate
def test_movie_api_error():
    responses.add(
        responses.GET,
        "https://api.cinescope.ru/movies/1",
        json={"error": "Not found"},
        status=404
    )
    # Тест без реального API
```

### 7. Test Data Management 📊

**Рекомендации**:

**a) Factory Pattern**:
```python
# tests/factories.py
from dataclasses import dataclass
from faker import Faker

class MovieFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            "name": Faker().sentence(),
            "price": 100,
            "location": "MSK",
        }
        return {**defaults, **kwargs}
```

**b) JSON Fixtures**:
```python
# tests/fixtures/movies.json
{
  "valid_movie": {
    "name": "Test Movie",
    "price": 100
  },
  "invalid_movie": {
    "name": null
  }
}

# В тестах
import json
with open("tests/fixtures/movies.json") as f:
    test_data = json.load(f)
```

### 8. Code Coverage Badges 📈

**Добавить в README.md**:

```markdown
[![codecov](https://codecov.io/gh/nkrasdev/cinescope-autotests/branch/master/graph/badge.svg)](https://codecov.io/gh/nkrasdev/cinescope-autotests)
```

**Настройка codecov.io**:
1. Зарегистрироваться на codecov.io
2. Добавить в CI:
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
```

### 9. Dependency Management 🔐

**Dependabot** для автоматического обновления зависимостей:

Создать `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

**Safety** для проверки уязвимостей:
```bash
# Добавить в dev dependencies
"safety>=3.0.0"

# В CI
uv run safety check
```

### 10. Docker Integration 🐳

**Dockerfile для тестов**:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY tests/ tests/

# Install dependencies
RUN uv sync --dev

# Run tests
CMD ["uv", "run", "pytest"]
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  tests:
    build: .
    volumes:
      - ./tests:/app/tests
      - ./allure-results:/app/allure-results
    environment:
      - BASE_URL=${BASE_URL}
      - ADMIN_EMAIL=${ADMIN_EMAIL}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
```

### 11. Test Reporting Enhancements 📊

**a) pytest-html** для HTML отчетов:
```bash
"pytest-html>=4.1.0"

# Использование
pytest --html=report.html --self-contained-html
```

**b) pytest-json-report** для JSON отчетов:
```bash
"pytest-json-report>=1.5.0"

# Использование
pytest --json-report --json-report-file=report.json
```

### 12. Continuous Deployment 🚀

**a) Auto-deploy Allure Report**:

Добавить в CI job для деплоя Allure на GitHub Pages:
```yaml
- name: Deploy Allure Report
  if: always()
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./allure-report
```

**b) Test Results в Pull Request**:
```yaml
- name: Publish Test Results
  uses: EnricoMi/publish-unit-test-result-action@v2
  if: always()
  with:
    files: allure-results/**/*.xml
```

### 13. Monitoring & Observability 📈

**a) Test Analytics**:
- [TestRail](https://www.testrail.com/) - Test management
- [ReportPortal](https://reportportal.io/) - AI-powered test analytics

**b) Slack/Discord Notifications**:

Добавить в CI:
```yaml
- name: Slack Notification
  uses: 8398a7/action-slack@v3
  if: always()
  with:
    status: ${{ job.status }}
    text: "Test run completed: ${{ job.status }}"
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 14. Advanced Fixtures 🔧

**Параметризованные фикстуры**:
```python
@pytest.fixture(params=["MSK", "SPB"])
def movie_location(request):
    return request.param

def test_movie_in_different_locations(movie_location):
    # Тест запустится 2 раза с разными локациями
    pass
```

**Scope management**:
```python
@pytest.fixture(scope="session")
def db_connection():
    # Создается один раз за сессию
    conn = create_connection()
    yield conn
    conn.close()
```

### 15. AI/ML Testing Tools 🤖

**a) Auto-test generation**:
- [Pynguin](https://github.com/se2p/pynguin) - Automatic test generation

**b) Test maintenance**:
- [testmon](https://github.com/tarpas/pytest-testmon) - Запускать только затронутые тесты

```bash
"pytest-testmon>=2.1.0"

# Использование
pytest --testmon  # Только измененные тесты
```

## Roadmap внедрения

### Этап 1: Немедленно (уже сделано ✅)
- ✅ mypy
- ✅ bandit
- ✅ pytest-cov
- ✅ pytest-xdist
- ✅ pre-commit hooks

### Этап 2: Ближайшая перспектива (1-2 недели)
1. **pytest-testmon** - для оптимизации CI
2. **Dependabot** - автообновление зависимостей
3. **codecov.io** - coverage badges и отслеживание
4. **Docker integration** - для изоляции окружения

### Этап 3: Средняя перспектива (1 месяц)
1. **Hypothesis** - property-based testing для критичных тестов
2. **responses/VCR.py** - моки для стабильности
3. **Schemathesis** - contract testing
4. **Test data factories** - улучшение управления данными

### Этап 4: Долгосрочная перспектива (2-3 месяца)
1. **Locust** - load testing
2. **Visual regression** - для UI тестов
3. **mutmut** - mutation testing для качества тестов
4. **ReportPortal** - продвинутая аналитика

## Метрики успеха

Отслеживайте эти метрики для оценки качества:

1. **Code Coverage**: Цель > 80%
2. **Type Coverage** (mypy): Цель > 90%
3. **Test Execution Time**: < 5 минут для API тестов
4. **Flaky Tests**: < 1% от всех тестов
5. **CI Success Rate**: > 95%
6. **Mean Time To Detect (MTTD)**: < 1 день
7. **Mean Time To Resolve (MTTR)**: < 1 неделя

## Рекомендации по процессу

### 1. Test Review Checklist
- [ ] Тест изолирован и не зависит от других
- [ ] Используются type hints
- [ ] Есть Allure декораторы
- [ ] Cleanup в finally блоке
- [ ] Понятные имена и сообщения об ошибках
- [ ] Нет хардкода (используются fixtures/constants)

### 2. Code Review Checklist
- [ ] Проходят все CI проверки
- [ ] Coverage не упал
- [ ] Нет новых type errors
- [ ] Нет security issues
- [ ] Обновлена документация (если нужно)
- [ ] Следует существующим паттернам

### 3. Release Checklist
- [ ] Все тесты зеленые
- [ ] Нет известных flaky тестов
- [ ] Обновлен CHANGELOG
- [ ] Создан Git tag
- [ ] Allure report доступен

## Дополнительные ресурсы

### Документация
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python Testing Style Guide](https://blog.thea.codes/my-python-testing-style-guide/)
- [Google Testing Blog](https://testing.googleblog.com/)

### Книги
- "Python Testing with pytest" by Brian Okken
- "Unit Testing Principles, Practices, and Patterns" by Vladimir Khorikov
- "The Art of Software Testing" by Glenford J. Myers

### Курсы
- [Test Automation University](https://testautomationu.applitools.com/)
- [Udemy: Python Testing Masterclass](https://www.udemy.com/course/python-testing/)

## Заключение

Проект уже следует многим best practices. Внедрение дополнительных инструментов должно быть постепенным и основываться на реальных потребностях команды.

**Ключевые принципы**:
1. **Start Simple** - не внедряйте все сразу
2. **Measure Impact** - отслеживайте метрики
3. **Iterate** - постоянно улучшайте процесс
4. **Team Buy-in** - убедитесь, что команда понимает ценность

Удачи! 🚀
