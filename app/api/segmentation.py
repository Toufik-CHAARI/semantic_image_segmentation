import io
import time

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.schemas.responses import SegmentationResponse
from app.services.segmentation_service import SegmentationService

router = APIRouter()
segmentation_service = SegmentationService()


@router.post("/segment")
async def segment_image(file: UploadFile = File(...)):
    """API Image Segmentation Endpoint"""
    # check if file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # read file
        img_bytes = await file.read()

        # measure processing time
        start_time = time.time()

        # perform segmentation
        segmented_image_bytes, stats = segmentation_service.segment_image(img_bytes)

        processing_time = time.time() - start_time

        # return segmented image
        return StreamingResponse(
            io.BytesIO(segmented_image_bytes),
            media_type="image/png",
            headers={
                "X-Processing-Time": f"{processing_time:.3f}s",
                "X-Image-Stats": str(stats),
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during segmentation: {str(e)}"
        )


@router.post("/segment-with-stats")
async def segment_image_with_stats(file: UploadFile = File(...)):
    """API Image Segmentation Endpoint with detailed statistics"""
    # check if file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # read file
        img_bytes = await file.read()

        # measure processing time
        start_time = time.time()

        # perform segmentation
        segmented_image_bytes, stats = segmentation_service.segment_image(img_bytes)

        processing_time = time.time() - start_time

        # create response with statistics
        response = SegmentationResponse(
            message="Segmentation performed successfully",
            stats=stats,
            image_size=segmentation_service.IMG_SIZE,
            processing_time=processing_time,
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during segmentation: {str(e)}"
        )
