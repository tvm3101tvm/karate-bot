from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Technique(Base):
    __tablename__ = 'techniques'
    id = Column(Integer, primary_key=True)
    name_ru = Column(String(100))
    name_ja = Column(String(100))
    category = Column(String(50))   # stance, block, punch, kick, kihon, kata
    description = Column(Text, default='')
    video_path = Column(String(200))   # file_id видео
    gif_path = Column(String(200))     # file_id GIF
    audio_path = Column(String(200), default='')   # file_id аудио/голосового сообщения

class UserProgress(Base):
    __tablename__ = 'user_progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    technique_id = Column(Integer)
    last_shown = Column(DateTime, default=datetime.utcnow)
    correct_streak = Column(Integer, default=0)
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)

# Создаём таблицы, если их нет
Base.metadata.create_all(engine)

def get_techniques_by_category(category):
    session = Session()
    techs = session.query(Technique).filter_by(category=category).all()
    session.close()
    return techs

def get_technique_by_id(tech_id):
    session = Session()
    tech = session.query(Technique).get(tech_id)
    session.close()
    return tech

def update_progress(user_id, technique_id, correct):
    session = Session()
    prog = session.query(UserProgress).filter_by(user_id=user_id, technique_id=technique_id).first()
    if not prog:
        prog = UserProgress(
            user_id=user_id,
            technique_id=technique_id,
            total_attempts=0,
            correct_attempts=0,
            correct_streak=0,
            last_shown=datetime.utcnow()
        )
        session.add(prog)
    else:
        # Если по какой-то причине поля оказались None (например, старая запись), инициализируем их
        if prog.total_attempts is None:
            prog.total_attempts = 0
        if prog.correct_attempts is None:
            prog.correct_attempts = 0
        if prog.correct_streak is None:
            prog.correct_streak = 0

    prog.last_shown = datetime.utcnow()
    prog.total_attempts += 1
    if correct:
        prog.correct_attempts += 1
        prog.correct_streak += 1
    else:
        prog.correct_streak = 0
    session.commit()
    session.close()