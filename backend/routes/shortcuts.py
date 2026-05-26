from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, Shortcut

router = APIRouter(prefix="/shortcuts", tags=["shortcuts"])


class ShortcutIn(BaseModel):
    name: str
    url: str
    description: str = ""
    icon: str = "🌐"
    color: str = "#6366f1"
    order: int = 0
    category_id: int


class ShortcutOut(ShortcutIn):
    id: int
    model_config = {"from_attributes": True}


@router.get("/", response_model=list[ShortcutOut])
def list_shortcuts(category_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Shortcut)
    if category_id:
        q = q.filter(Shortcut.category_id == category_id)
    return q.order_by(Shortcut.order).all()


@router.post("/", response_model=ShortcutOut)
def create_shortcut(data: ShortcutIn, db: Session = Depends(get_db)):
    s = Shortcut(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.put("/{sid}", response_model=ShortcutOut)
def update_shortcut(sid: int, data: ShortcutIn, db: Session = Depends(get_db)):
    s = db.get(Shortcut, sid)
    if not s:
        raise HTTPException(404, "Not found")
    for k, v in data.model_dump().items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{sid}")
def delete_shortcut(sid: int, db: Session = Depends(get_db)):
    s = db.get(Shortcut, sid)
    if not s:
        raise HTTPException(404, "Not found")
    db.delete(s)
    db.commit()
    return {"ok": True}
