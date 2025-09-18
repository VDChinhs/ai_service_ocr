import base64
import io
from PIL import Image
from fastapi import Request

from schemas.dto_image import ImageBase64Input

import numpy as np


def infer_image_from_base64(payload: ImageBase64Input, request: Request):
    try:
        image_data = base64.b64decode(payload.image_base64)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        w, h = image.size
        max_dim = 4000
        if max(w, h) > max_dim:
            if w >= h:
                new_w = max_dim
                new_h = int(h * (max_dim / w))
            else:
                new_h = max_dim
                new_w = int(w * (max_dim / h))
            image = image.resize((new_w, new_h), Image.LANCZOS)
        image_np = np.array(image)
        model = request.app.state.model
        results = model.predict(
            image_np,
            text_det_thresh=payload.text_det_thresh,
            text_rec_score_thresh=payload.text_rec_score_thresh,
        )
        obj = {}
        for res in results:
            obj["rec_texts"] = res.get("rec_texts")
            obj["rec_boxes"] = res.get("rec_boxes")
            obj["rec_scores"] = res.get("rec_scores")
        return obj
    except:
        return None
