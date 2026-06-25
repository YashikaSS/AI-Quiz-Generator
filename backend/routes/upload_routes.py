from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.crud import create_job, update_job

from backend.models.schemas import JobCreate

from backend.services.youtube_service import process_youtube_url
from backend.services.pdf_service import process_pdf_file

router = APIRouter()


@router.post("/upload")
def upload_source(
    job: JobCreate,
    db: Session = Depends(get_db)
):

    # Create Job
    new_job = create_job(
        db,
        job.source_type,
        job.source_path
    )

    try:

        if job.source_type.lower() == "youtube":

            result = process_youtube_url(
                job.source_path
            )

            update_job(
                db,
                new_job.id,
                video_id=result["video_id"],
                title=result["title"],
                duration_seconds=result["duration_seconds"],
                audio_path=result["audio_path"],
                status="Uploaded"
            )

        elif job.source_type.lower() == "pdf":

            result = process_pdf_file(
                job.source_path
            )

            update_job(
                db,
                new_job.id,
                status="Uploaded"
            )

        else:

            raise HTTPException(
                status_code=400,
                detail="Invalid source type"
            )

        return {
            "job_id": new_job.id,
            "status": "Uploaded",
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )