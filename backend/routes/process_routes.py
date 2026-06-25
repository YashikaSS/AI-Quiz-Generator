from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.crud import (
    get_job,
    update_job,
    update_job_results
)

from backend.services.transcription_service import transcribe_audio
from backend.services.summary_service import generate_summary
from backend.services.notes_service import generate_notes
from backend.services.quiz_service import generate_quiz
from backend.services.pdf_service import process_pdf_file

router = APIRouter()


@router.post("/process/{job_id}")
def process_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = get_job(db, job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    update_job(
        db,
        job_id,
        status="Processing"
    )

    try:

        # -------------------------
        # YouTube Processing
        # -------------------------
        if job.source_type.lower() == "youtube":

            transcript_data = transcribe_audio(
                job.audio_path
            )

            text = transcript_data["text"]
            transcript = transcript_data["text"]
            transcript_path = transcript_data["transcript_path"]
            language = transcript_data["language"]

        # -------------------------
        # PDF Processing
        # -------------------------
        elif job.source_type.lower() == "pdf":

            pdf_data = process_pdf_file(
                job.source_path
            )

            text = pdf_data["text"]

            transcript = text
            transcript_path = ""
            language = "N/A"

        else:

            raise HTTPException(
                status_code=400,
                detail="Unsupported source type."
            )

    except Exception as e:

        update_job(
            db,
            job_id,
            status="Failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    # Summary
    summary = generate_summary(text)

    # Notes
    notes = generate_notes(text)

    # Quiz
    quiz = generate_quiz(text)

    if quiz is None:

        update_job(
            db,
            job_id,
            status="Failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Quiz generation failed."
        )

    # Save results
    update_job_results(
        db=db,
        job_id=job_id,
        transcript=transcript,
        transcript_path=transcript_path,
        language=language,
        summary=summary,
        notes=notes,
        quiz=quiz.model_dump()
    )

    return {
        "message": "Processing Completed",
        "job_id": job_id,
        "summary": summary,
        "notes": notes,
        "quiz": quiz
    }