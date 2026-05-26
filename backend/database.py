from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./data/shortcuts.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    icon = Column(String, default="🔗")
    color = Column(String, default="#6366f1")
    order = Column(Integer, default=0)
    shortcuts = relationship("Shortcut", back_populates="category", cascade="all, delete")


class Shortcut(Base):
    __tablename__ = "shortcuts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String, default="")
    icon = Column(String, default="🌐")
    color = Column(String, default="#6366f1")
    order = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="shortcuts")


class Ebook(Base):
    __tablename__ = "ebooks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    size = Column(Integer, default=0)
    created_at = Column(String, default="")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    import os
    os.makedirs("data", exist_ok=True)
    os.makedirs("upload/ebook/epub", exist_ok=True)
    Base.metadata.create_all(bind=engine)
