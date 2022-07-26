# LLM-Worker

Serving Large Language Model Using FastAPI and Celery

## For Developers

1. install dev package.

```shell
pip install -r requirements-dev.txt
```

2. install pre-commit.

```shell
pre-commit install
```

3. Running the Celery worker server(Not Docker)
```shell
cd worker
celery -A worker worker -P solo -l info
```
