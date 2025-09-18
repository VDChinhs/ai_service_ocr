from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from schemas.dto_ocr import OcrSchema
from services.services_ocr import infer_image_from_base64

from schemas.dto_image import ImageBase64Input

from utils.validate import safe_jsonify

router = APIRouter()


@router.post("", response_model=OcrSchema)
async def ocr_image(request: Request, payload: ImageBase64Input):
    if request.app.state.model is None:
        return None
    result = infer_image_from_base64(payload, request)
    return JSONResponse(content=safe_jsonify(result))
