from pydantic import BaseModel, Field

class ImageBase64Input(BaseModel):
    image_base64: str = Field(..., description="Input image in base64 format")
    text_det_thresh: float = Field(
        0.1, description="Confidence threshold for text detection"
    )
    text_rec_score_thresh: float = Field(
        0.8, description="Confidence threshold for text recognition"
    )
