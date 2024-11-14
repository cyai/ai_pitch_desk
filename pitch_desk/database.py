# models.py
from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Pitch(Base):
    __tablename__ = "pitches"
    id = Column(Integer, primary_key=True, index=True)
    slide_no = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=False)
    audio_seq_no = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    audio_url = Column(Text, nullable=False)

    @classmethod
    async def save_pitch(cls, db_session: AsyncSession, pitch_data):
        new_pitch = cls(**pitch_data)
        db_session.add(new_pitch)
        await db_session.commit()
        return new_pitch

    @classmethod
    async def get_all_pitches(cls, db_session: AsyncSession):
        result = await db_session.execute(select(cls).order_by(cls.audio_seq_no.asc()))
        return result.scalars().all()

    @classmethod
    async def get_pitch_by_id(cls, db_session: AsyncSession, pitch_id):
        result = await db_session.execute(select(cls).filter(cls.id == pitch_id))
        return result.scalars().first()


# Create tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Usage example
# async def get_pitch():
#     async with SessionLocal() as session:
#         pitches = await Pitch.get_all_pitches(session)
#         return pitches
