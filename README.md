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

#### Running Redis server using Docker
```
docker run --name redis -d -p 6379:6379 redis
```
- Want to control Redis
  - `sudo apt install redis-tools` in local shell

### 3-1. in local

#### Setting RabbitMQ, Redis configuration.
```python
# worker/config.py
class CeleryWorkerSettings(BaseSettings):
    worker_name: str = "Celery Worker"
    broker_uri: str = "ampq://<user>:<password>@<hostname>:<port>/<vhost>"
    backend_uri: str = "Auto Generate"


class RedisSettings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = Field(
        default=6379,
        ge=0,
        le=65535,
    )
    redis_db: int = Field(
        default=0,
        ge=0,
        le=15,
    )
    redis_password: str = ""
```
- Auto generate `backend_uri`. Just fill `RedisSettings` 

#### Running the Celery worker server
```shell
git clone https://github.com/ainize-team/LLM-Worker.git
cd LLM-Worker/worker
cd worker
celery -A worker worker -P solo -l info
```

#### Test Celery Worker
```python
from celery.result import AsyncResult
from tasks import generate

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

# Get task result
print(task.get())
```

### 3-2. Using docker
#### Build docker file
```
git clone https://github.com/ainize-team/LLM-Worker.git
cd LLM-Worker
docker build -t celery-llm .
```

#### Run docker container
```
docker run -d --name {worker_container_name} 
--gpus='"device=0,1,2,3,4,5,6,7"' -e USE_FAST_TOKENIZER=False
-e BROKER_URI={broker_uri} -e REDIS_HOST=<redis_hostname> 
-e REDIS_PORT=<redis_port> -e REDIS_DB=<redis_db> 
-e REDIS_PASSWORD=<redis_password> -v {local-path}:/model 
celery-llm
```

#### Test with FastAPI
- Check our [LLM-FastAPI](https://github.com/ainize-team/LLM-FastAPI) Repo.