
import os
import datetime as dt
from typing import List, Optional, Tuple

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, select, delete, update
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql+psycopg://botuser:botpass@db:5432/botdb"

Base = declarative_base()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class RequiredChat(Base):
    __tablename__ = "required_chats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat = Column(String(128), unique=True, nullable=False)
    url = Column(Text, nullable=True)
    label = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(64), unique=True, nullable=False)
    value = Column(Text, nullable=True)

def init_db():
    Base.metadata.create_all(engine)

def get_all_required() -> List[RequiredChat]:
    with SessionLocal() as s:
        return list(s.execute(select(RequiredChat).order_by(RequiredChat.id.asc())).scalars())

def add_required(chat: str, url: str, label: str) -> Tuple[bool, Optional[str]]:
    with SessionLocal() as s:
        if s.execute(select(RequiredChat).where(RequiredChat.chat == chat)).scalar():
            return False, "exists"
        rc = RequiredChat(chat=chat, url=url, label=label)
        s.add(rc)
        s.commit()
        return True, None

def delete_required_by_id(dbid: int) -> Tuple[bool, Optional[str], Optional[str]]:
    with SessionLocal() as s:
        row = s.get(RequiredChat, dbid)
        if not row:
            return False, None, None
        label, chat = row.label, row.chat
        s.delete(row)
        s.commit()
        return True, label, chat

def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    with SessionLocal() as s:
        row = s.execute(select(Setting).where(Setting.key == key)).scalar()
        return row.value if row else default

def set_setting(key: str, value: str):
    with SessionLocal() as s:
        row = s.execute(select(Setting).where(Setting.key == key)).scalar()
        if row:
            s.execute(update(Setting).where(Setting.key == key).values(value=value))
        else:
            s.add(Setting(key=key, value=value))
        s.commit()
