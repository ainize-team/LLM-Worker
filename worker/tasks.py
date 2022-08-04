import json
from datetime import datetime
from typing import Dict

import pytz
import torch
from celery.signals import celeryd_init
from loguru import logger

from config import model_settings
from enums import ResponseStatusEnum
from ml_model import LargeLanguageModel
from payloads.response import TextGenerationResponse
from utils import clear_memory
from worker import app, redis


llm = LargeLanguageModel()


@celeryd_init.connect
def load_model(**kwargs):
    logger.info("Start loading model...")
    llm.load_model(model_settings.model_path, model_settings.use_fast_tokenizer)
    logger.info("Loading model is done!")


@app.task(name="generate")
def generate(task_id: str, data: Dict) -> None:
    now = datetime.utcnow().replace(tzinfo=pytz.utc).timestamp()
    response = TextGenerationResponse(status=ResponseStatusEnum.ASSIGNED, updated_at=now)
    redis.set(task_id, json.dumps(dict(response)))
    inputs = {
        "inputs": llm.tokenizer.encode(data["prompt"], return_tensors="pt").cuda()
        if torch.cuda.is_available()
        else llm.tokenizer.encode(data["prompt"], return_tensors="pt"),
        "max_new_tokens": data["max_new_tokens"],
        "do_sample": data["do_sample"],
        "early_stopping": data["early_stopping"],
        "num_beams": data["num_beams"],
        "temperature": data["temperature"],
        "top_k": data["top_k"],
        "top_p": data["top_p"],
        "no_repeat_ngram_size": data["no_repeat_ngram_size"],
        "num_return_sequences": data["num_return_sequences"],
    }
    if inputs["max_new_tokens"] + inputs["inputs"].shape[-1] > model_settings.model_max_length:
        logger.warning("too long prompt")
        new_max_new_tokens = model_settings.model_max_length - inputs["inputs"].shape[-1]
        if new_max_new_tokens <= 0:
            del inputs
            redis.set(task_id, json.dumps({"status_code": 422, "message": "too long prompt"}))
            return
        else:
            logger.warning(f"Change max_new_tokens to {new_max_new_tokens}")
            inputs["max_new_tokens"] = new_max_new_tokens
    error_flag = False
    try:
        generated_ids = llm.model.generate(**inputs)
        response.result = llm.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        del generated_ids
    except ValueError as e:
        redis.set(task_id, json.dumps({"status_code": 422, "message": str(e)}))
        error_flag = True
    except Exception as e:
        redis.set(task_id, json.dumps({"status_code": 500, "message": str(e)}))
        error_flag = True
    finally:
        del inputs
        clear_memory()
    if error_flag:
        pass
    else:
        now = datetime.utcnow().replace(tzinfo=pytz.utc).timestamp()
        response.updated_at = now
        response.status = ResponseStatusEnum.COMPLETED
        logger.info(f"task_id: {task_id}, gen result: {response.result}")
        redis.set(task_id, json.dumps(dict(response)))
