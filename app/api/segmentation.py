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
    """Endpoint pour segmenter une image"""
    # Vérifier le type de fichier
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")

    try:
        # Lire le fichier
        img_bytes = await file.read()

        # Mesurer le temps de traitement
        start_time = time.time()

        # Effectuer la segmentation
        segmented_image_bytes, stats = segmentation_service.segment_image(img_bytes)

        processing_time = time.time() - start_time

        # Retourner l'image segmentée
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
            status_code=500, detail=f"Erreur lors de la segmentation: {str(e)}"
        )


@router.post("/segment-with-stats")
async def segment_image_with_stats(file: UploadFile = File(...)):
    """Endpoint pour segmenter une image avec statistiques détaillées"""
    # Vérifier le type de fichier
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")

    try:
        # Lire le fichier
        img_bytes = await file.read()

        # Mesurer le temps de traitement
        start_time = time.time()

        # Effectuer la segmentation
        segmented_image_bytes, stats = segmentation_service.segment_image(img_bytes)

        processing_time = time.time() - start_time

        # Créer la réponse avec statistiques
        response = SegmentationResponse(
            message="Segmentation effectuée avec succès",
            stats=stats,
            image_size=segmentation_service.IMG_SIZE,
            processing_time=processing_time,
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la segmentation: {str(e)}"
        )
