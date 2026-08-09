# International Delivery Service

FastAPI-сервис для регистрации посылок и асинхронного расчёта стоимости доставки.

## Stack

FastAPI, PostgreSQL, Async SQLAlchemy, Redis, RabbitMQ, Docker Compose, Loguru, Prometheus, Grafana, Pytest, Ruff, mypy.

## Main Features

- создание и просмотр посылок;
- асинхронный расчёт стоимости доставки;
- кэширование курса USD/RUB в Redis;
- HTTP idempotency;
- Transactional Outbox;
- RabbitMQ publisher/consumer;
- логирование через Loguru;
- Prometheus-метрики и Grafana.

## Architecture

Приложение разделено на Router → Service → Repository и построено по принципам слоистой архитектуры.

Для управления транзакциями используется Unit of Work.

При создании посылки одновременно создаётся OutboxEvent. Отдельный publisher отправляет событие в RabbitMQ, после чего consumer запускает расчёт стоимости доставки.

Redis используется для кэширования курса валют и уменьшения количества запросов к внешнему API.

## Monitoring

Приложение отдаёт метрики через:

`/metrics`

Prometheus собирает метрики, а Grafana используется для отображения:

- HTTP Requests per Second;
- P95 Request Latency;
- HTTP 5xx Errors.

Также логируются HTTP-запросы, бизнес-события и работа RabbitMQ.

## Testing

Проект покрыт unit и integration тестами, включая полный сценарий:

`создание посылки → Outbox → RabbitMQ → Consumer → расчёт стоимости`

Текущее состояние:

`23 tests passed`

## Run

1. Создать рабочий конфиг:

```bash
cp config.yaml.example config.yaml
```

2. Запустить сервисы:

```bash
docker compose up -d
```

3. Применить миграции:

```bash
make migrate
```

4. Заполнить таблицу типов посылок:

```bash
docker compose exec app /app/.venv/bin/python -m delivery_service.database.seed
```

## Useful Links

- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- RabbitMQ Management: http://localhost:15672

## Challenges

В ходе разработки пришлось решить несколько практических задач:

- обеспечить надёжную публикацию событий через Transactional Outbox;
- организовать асинхронную обработку расчёта стоимости через RabbitMQ;
- обеспечить идемпотентность создания посылок;
- настроить кэширование внешнего API через Redis с fallback при недоступности Redis;
- разделить ответственность между Service, Repository и Unit of Work;
- настроить интеграционные тесты с PostgreSQL, Redis и RabbitMQ;
- настроить логирование, Prometheus и Grafana в Docker Compose.

## Checks

```bash
make check
```

Команда запускает форматирование, линтер, mypy и тесты.