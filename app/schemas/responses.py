from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str

class InfoResponse(BaseModel):
    name: str
    version: str
    description: str
    model_info: Dict[str, Any]
    endpoints: list[str]

class SegmentationStats(BaseModel):
    pixel_count: int = Field(ge=0)
    percentage: float = Field(ge=0.0, le=100.0)

class SegmentationResponse(BaseModel):
    message: str
    stats: Dict[str, SegmentationStats]
    image_size: tuple[int, int]
    processing_time: float = Field(ge=0.0)
    
    @field_validator('image_size')
    @classmethod
    def validate_image_size(cls, v):
        if v[0] <= 0 or v[1] <= 0:
            raise ValueError('Image size must be positive')
        return v
