FROM pytorch/pytorch:1.12.0-cuda11.3-cudnn8-devel

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./worker/ /app/

CMD ["celery", "-A", "worker", "worker", "--loglevel=info", "--pool=solo"]