# BusinessAIprocessing

Репозиторий для взаимодействия с моделями искусственного интеллекта в рамках обработки запросов для бизнеса

## Для запуска локально

```
docker compose -f docker-compose.yaml up
```

### Для запуска в виртуальном окружении

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHON_PROFILE=development
python3 businessAiProcessing.py

```
Интерфейс отладки промптов - http://localhost:7777/debug

### Проверка на тестовых данных

```
docker compose -f docker-compose.yaml up
В интерфейсе отладки промптов - http://localhost:7777/debug раздел "Тестовые данные" - "Загрузить тестовые данные"
```