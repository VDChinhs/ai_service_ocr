from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from api import routers_ocr

from core.config import settings, resources
# from utils.file import is_model_path_exists, download_model_from_drive, create_folder
from utils.file import create_folder

import threading
from consumer import start_consumer

from paddleocr import PaddleOCR


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_folder("models")
    app.state.model = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        text_recognition_model_dir="models/PP-OCRv5_server_rec_infer",
    )
    yield
    # device = "cuda" if torch.cuda.is_available() else "cpu"
    # print("torch:", device)
    # if settings.TRITON_SERVER_URL == "" or True:
    #     model_title_block_exists = is_model_path_exists(
    #         resources.PATH_MODEL_TITLE_BLOCK
    #     )
    #     model_coordinates_exists = is_model_path_exists(
    #         resources.PATH_MODEL_COORDINATES
    #     )
    #     model_exists = model_title_block_exists and model_coordinates_exists
    #     print("Check Model Exists:", model_exists)
    #     down_model = False
    #     print("RABBITMQ_URL: ", settings.RABBITMQ_URL)

    #     if not model_exists:
    #         print("Download Model Title Block")
    #         down_model_title_block = download_model_from_drive(
    #             settings.FILE_MODEL_TITLE_BLOCK_ID, resources.PATH_MODEL_TITLE_BLOCK
    #         )
    #         down_model_coordinates = download_model_from_drive(
    #             settings.FILE_MODEL_COORDINATES_ID, resources.PATH_MODEL_COORDINATES
    #         )
    #         down_model = down_model_title_block and down_model_coordinates

    #     if model_exists or down_model:
    #         # app.state.model = YOLO(resources.PATH_MODEL_TITLE_BLOCK).to(device)
    #         app.state.model = YOLO(
    #             f"{settings.TRITON_SERVER_URL}/title_block", task="detect"
    #         )
    #         # app.state.model_coordinates = YOLO(resources.PATH_MODEL_COORDINATES).to(device)
    #         app.state.model_coordinates = YOLO(
    #             f"{settings.TRITON_SERVER_URL}/coordinates", task="detect"
    #         )
    #         print(
    #             f"[Startup] YOLO model {resources.PATH_MODEL_TITLE_BLOCK} loaded on {app.state.model.device}"
    #         )
    #         print(
    #             f"[Startup] YOLO model {resources.PATH_MODEL_COORDINATES} loaded on {app.state.model.device}"
    #         )

    #         app.state.model_lock = threading.Lock()

    #         if settings.RABBITMQ_URL.strip() == "":
    #             print("[Startup] RABBITMQ_URL is empty → Skipping RabbitMQ consumer.")
    #             app.state.stop_event = None
    #             app.state.consumer_thread = None

    #         else:
    #             app.state.stop_event = threading.Event()
    #             t = threading.Thread(
    #                 target=start_consumer,
    #                 args=(app.state.model, app.state.stop_event, app.state.model_lock),
    #                 daemon=True,
    #             )
    #             t.start()
    #             app.state.consumer_thread = t
    #             print("\n[Startup] RabbitMQ consumer started")
    #     else:
    #         app.state.model = None
    #         app.state.model_lock = None
    #         app.state.stop_event = None
    #         app.state.consumer_thread = None
    #         print("[Startup] Model not found. Skipping RabbitMQ consumer.")

    #     try:
    #         yield
    #     finally:
    #         if app.state.stop_event and app.state.consumer_thread:
    #             print("[Shutdown] Stopping consumer ...")
    #             app.state.stop_event.set()
    #             app.state.consumer_thread.join(timeout=5)
    #             print("[Shutdown] Done.")
    # else:
    #     yield


origins = ["*"]
app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.PROJECT_DESCRIPTION,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers_ocr.router, prefix="/ocr", tags=["OCR"])


@app.get("/")
def home():
    return {"message": "AI Services"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
