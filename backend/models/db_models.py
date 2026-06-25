from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text

Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    source_type = Column(String(50))
    source_path = Column(Text)

    status = Column(String(50), default="Pending")

    video_id = Column(String(100))
    title = Column(Text)
    duration_seconds = Column(Integer)

    audio_path = Column(Text)

    transcript = Column(Text)
    transcript_path = Column(Text)
    language = Column(String(20))

    summary = Column(Text)
    notes = Column(Text)

    quiz = Column(Text)