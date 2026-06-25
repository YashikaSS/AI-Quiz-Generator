import json
from backend.models.db_models import Job


def create_job(db, source_type, source_path):
    job = Job(
        source_type=source_type,
        source_path=source_path,
        status="Pending"
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def get_job(db, job_id):
    return db.query(Job).filter(Job.id == job_id).first()


def update_job(db, job_id, **kwargs):
    job = get_job(db, job_id)

    if not job:
        return None

    for key, value in kwargs.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)

    return job


def update_job_results(
    db,
    job_id,
    transcript,
    transcript_path,
    language,
    summary,
    notes,
    quiz
):
    job = get_job(db, job_id)

    if not job:
        return None

    job.transcript = transcript
    job.transcript_path = transcript_path
    job.language = language

    job.summary = summary

    # Store notes as JSON string
    job.notes = json.dumps(notes)

    # Store quiz as JSON string
    job.quiz = json.dumps(quiz)

    job.status = "Completed"

    db.commit()
    db.refresh(job)

    return job