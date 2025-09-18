import os, json, base64, io, threading, time
import pika
from PIL import Image
from typing import Any
from schemas.dto_ocr import OcrSchema
from typing import Optional
from core.config import settings

QUEUE_NAME = "image_queue"


def _connect():
    parameters = pika.URLParameters(settings.RABBITMQ_URL)

    parameters.heartbeat = 30
    parameters.blocked_connection_timeout = 300
    parameters.connection_attempts = 1
    parameters.retry_delay = 0

    return pika.BlockingConnection(parameters)


def start_consumer(
    model, stop_event: threading.Event, model_lock: Optional[threading.Lock] = None
):
    while not stop_event.is_set():
        try:
            print(f"[Consumer] Connecting to RabbitMQ at {settings.RABBITMQ_URL} ...")
            connection = _connect()
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.basic_qos(prefetch_count=1)

            def safe_infer(image):
                if model_lock is not None:
                    with model_lock:
                        return model(image, max_det=1, verbose=False)[0]
                else:
                    return model(image, max_det=1, verbose=False)[0]

            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    image_b64 = data.get("image_base64")
                    if not image_b64:
                        raise ValueError("image_base64 is missing")

                    image_data = base64.b64decode(image_b64)
                    image = Image.open(io.BytesIO(image_data)).convert("RGB")

                    result = safe_infer(image)
                    boxes = result.boxes

                    results = []
                    for i in range(len(boxes)):
                        results.append(
                            OcrSchema(
                                cls=float(boxes.cls[i]),
                                conf=float(boxes.conf[i]),
                                data=boxes.data[i].tolist(),
                                orig_shape=tuple(result.orig_shape),
                                xywh=boxes.xywh[i].tolist(),
                                xywhn=boxes.xywhn[i].tolist(),
                                xyxy=boxes.xyxy[i].tolist(),
                                xyxyn=boxes.xyxyn[i].tolist(),
                            )
                        )

                    response: Any = results[0].dict() if results else None

                    if properties and properties.reply_to:
                        ch.basic_publish(
                            exchange="",
                            routing_key=properties.reply_to,
                            properties=pika.BasicProperties(
                                correlation_id=properties.correlation_id,
                                delivery_mode=2,
                            ),
                            body=json.dumps(response),
                        )
                except Exception as e:
                    print(f"[Consumer] Error while processing message: {e}")
                finally:
                    ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(
                queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False
            )
            print("[Consumer] Waiting for messages...")
            while not stop_event.is_set():
                connection.process_data_events(time_limit=1)

            try:
                channel.stop_consuming()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass
            print("[Consumer] Stopped gracefully.")
            break

        except pika.exceptions.AMQPConnectionError as e:
            print(f"[Consumer] AMQPConnectionError: {e}. Retry in 5s ...")
            for _ in range(5):
                if stop_event.is_set():
                    break
                time.sleep(1)
        except Exception as e:
            print(f"[Consumer] Unexpected error: {e}. Retry in 5s ...")
            for _ in range(5):
                if stop_event.is_set():
                    break
                time.sleep(1)
