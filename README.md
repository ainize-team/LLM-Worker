# LLM-Worker

Serving Large Language Model Using FastAPI and Celery

## For Developers

### 1. install dev package.

```shell
pip install -r requirements-dev.txt
```

### 2. install pre-commit.

```shell
pre-commit install
```

### 3. Running the Celery worker server with RabbitMQ(as Broker), Redis(as Backend).
#### Running RabbitMQ server using Docker
```shell
docker run -d --name rabbitmq -p 5672:5672 -p 8080:15672 --restart=unless-stopped rabbitmq:3.9.21-management
```

#### Setting RabbitMQ, Redis configuration.
```python
# worker/configs/config.py
class CeleryWorkerSettings(BaseSettings):
    worker_name: str = "Celery Worker"
    broker_uri: str = "ampq://<user>:<password>@<hostname>:<port>/<vhost>"
    backend_uri: str = "redis://:<password>@<hostname>:<port>/<db>"
```

#### Running the Celery worker server
```shell
cd worker
celery -A worker worker -P solo -l info
```

#### Test Sample code
```python
from celery.result import AsyncResult
from celery_tasks.tasks import generate

task = generate.delay({
    "prompt": "Hello", 
    "max_new_tokens": 16, 
    "do_sample": True, 
    "early_stopping": False, 
    "num_beams": 1, 
    "temperature": 1.0, 
    "top_k": 50, 
    "top_p": 1.0, 
    "no_repeat_ngram_size": 0, 
    "num_return_sequences": 1
})
# Check task status result
print(task.ready())
# Get task result
print(task.get())
```
