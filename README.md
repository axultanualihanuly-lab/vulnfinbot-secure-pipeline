# vulnfinbot-secure-pipeline
# vulnfinbot-secure-pipeline

Учебный проект: безопасный CI/CD-пайплайн для Flask-приложения **Mini-VulnFinBot** (финансовый чат-бот с двумя эндпоинтами). Пайплайн на GitHub Actions автоматически запускает тесты и сканеры безопасности при каждом push в `main` и каждом pull request.

## Приложение

| Эндпоинт | Метод | Описание |
|---|---|---|
| `/health` | GET | Проверка работоспособности, возвращает `{"status": "healthy"}` |
| `/api/chat` | POST | Принимает `{"message": "..."}`, возвращает ответ бота |

Защитные меры: проверка типа и длины сообщения (до 1000 символов), лимит размера тела запроса (16 КБ), единые JSON-ответы об ошибках без раскрытия внутренностей, отсутствие логирования текста сообщений, заголовки безопасности, `debug=False`.

## Структура проекта

```
app/                 код приложения (Flask)
tests/               pytest-тесты, AI-тесты безопасности, генератор отчёта
security/semgrep/    собственные правила Semgrep
reports/             отчёты
.github/workflows/   security-pipeline.yml
Dockerfile
run.py
requirements.txt
```

## Пайплайн (`.github/workflows/security-pipeline.yml`)

| Этап | Инструмент | Что проверяет | Отчёт |
|---|---|---|---|
| Тесты | pytest | функциональность, заголовки безопасности | вывод в логе |
| SAST | Bandit | небезопасные конструкции Python | `bandit-report.json` |
| SAST | Semgrep (свои правила) | `eval`, `shell=True`, `debug=True` | `semgrep-report.json` |
| SCA | pip-audit | уязвимости зависимостей | `dependency-report.json` |
| Контейнер | Docker + Trivy | уязвимости образа | `trivy-report.json` |
| DAST | OWASP ZAP baseline | запущенное приложение | `zap-report.json` |
| AI-безопасность | `tests/test_ai_security.py` | prompt injection, раскрытие секретов и др. | `ai-security-report.md` |

Все отчёты собираются в артефакт запуска **`vulnfinbot-security-reports`** (вкладка Actions, раздел Artifacts).

## Запуск локально

```bash
python -m venv venv
venv\Scripts\activate        # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python -m pytest -v
python run.py                # http://localhost:5000/health
```

Docker (если установлен):

```bash
docker build -t vulnfinbot .
docker run -p 5000:5000 vulnfinbot
```

## Результаты

### Исправления по отчётам

- **Trivy:** найдены уязвимости (CVE) в пакете `setuptools` внутри образа. Исправлено обновлением в `Dockerfile`.
- **ZAP:** найдены два предупреждения. Исправлено добавлением заголовков безопасности в `app/__init__.py`, проверяется тестом `tests/test_headers.py`.
- ### Исправления по отчётам

- **Trivy:** первый скан образа нашёл уязвимости (CVE) в пакете `setuptools`, который попал в образ вместе с базовым образом Python. Исправлено в `Dockerfile` обновлением `setuptools` до безопасной версии. Повторный скан показал, что у Python-пакетов находок нет.
- **ZAP baseline:** первый скан запущенного приложения выдал два предупреждения об отсутствующих заголовках безопасности. Исправлено добавлением заголовков в ответы приложения (`app/__init__.py`). Наличие заголовков проверяет тест `tests/test_headers.py`. Повторный скан показал, что оба предупреждения исчезли.
- **pip-audit:** уязвимых зависимостей в `requirements.txt` не найдено.

### Проверка работы сканеров (ветка `test/vulnerable-demo`)

Чтобы убедиться, что сканеры реально находят проблемы, в отдельной ветке был добавлен файл `app/insecure_demo.py` с намеренно небезопасным кодом (в `main` он не вливался, Pull Request #1 закрыт без слияния).

| | Bandit | Semgrep |
|---|---|---|
| С небезопасным кодом | 5 находок: B404 (импорт subprocess, LOW), B105 (хардкод пароля, LOW), B307 (`eval`, MEDIUM), B602 (`shell=True`, HIGH), B201 (`debug=True`, HIGH) | 3 находки: `python-eval-usage`, `subprocess-shell-true`, `flask-debug-true` |
| После удаления файла | 0 | 0 |

Semgrep не нашёл захардкоженный пароль, потому что для него нет собственного правила. Bandit его ловит встроенным правилом B105. Сканеры дополняют друг друга.

### Тесты

`python -m pytest -q`: 17 passed, 1 skipped (пропущен тест, требующий реальной LLM).

## Ограничения

- - AI-тесты в CI работают на mock-модели, чтобы пайплайн не зависел от API-ключа и не тратил деньги. Mock проверяет защитный код приложения: валидацию входа, фильтрацию ответов, непопадание секретов в ответ и логи. Реальную устойчивость модели к prompt injection mock не показывает: для этого нужен тест на настоящей LLM, который пропускается без ключа (отсюда `1 skipped`).
- DAST проверяет только два эндпоинта.
- Пайплайн не блокирует слияние при находках: отчёты сохраняются, решение принимает человек.

## Секреты

В репозитории нет ключей и паролей. API-ключи (если используются) хранятся в GitHub Secrets и локально в `.env`, который указан в `.gitignore`.
