from typing import List
from pydantic import BaseModel, Field

class OcrSchema(BaseModel):
    rec_texts: List[str] = Field(..., description="List of recognized OCR texts")
    rec_boxes: List[List[int]] = Field(
        ..., description="List of bounding boxes, each in format [x1, y1, x2, y2]"
    )
    rec_scores: List[float] = Field(
        ..., description="List of confidence scores for each recognized text"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "rec_texts": [
                    "A",
                    "B",
                    "C"
                ],
                "rec_boxes": [
                    [10, 10, 10, 10],
                    [10, 10, 10, 10],
                    [10, 10, 10, 10]
                ],
                "rec_scores": [
                    0.99,
                    0.99,
                    0.99
                ]
            }
        }
