import os
import uuid
import zipfile
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from database import get_db, Ebook

CONTENT_TYPES = {
    "html":  "text/html; charset=utf-8",
    "xhtml": "text/html; charset=utf-8",
    "css":   "text/css",
    "js":    "application/javascript",
    "png":   "image/png",
    "jpg":   "image/jpeg",
    "jpeg":  "image/jpeg",
    "gif":   "image/gif",
    "svg":   "image/svg+xml",
    "ttf":   "font/ttf",
    "otf":   "font/otf",
    "woff":  "font/woff",
    "woff2": "font/woff2",
    "xml":   "application/xml",
    "opf":   "application/oebps-package+xml",
    "ncx":   "application/x-dtbncx+xml",
    "webp":  "image/webp",
}

UPLOAD_DIR = "upload/ebook/epub"

router = APIRouter(prefix="/ebooks", tags=["ebooks"])


@router.post("/upload")
async def upload_epub(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".epub"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .epub são permitidos")

    content = await file.read()
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.epub"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    ebook = Ebook(
        title=os.path.splitext(file.filename)[0],
        filename=filename,
        original_name=file.filename,
        size=len(content),
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(ebook)
    db.commit()
    db.refresh(ebook)
    return {
        "id": ebook.id,
        "title": ebook.title,
        "original_name": ebook.original_name,
        "size": ebook.size,
        "created_at": ebook.created_at,
    }


@router.get("/")
def list_ebooks(db: Session = Depends(get_db)):
    ebooks = db.query(Ebook).order_by(Ebook.id.desc()).all()
    return [
        {
            "id": e.id,
            "title": e.title,
            "original_name": e.original_name,
            "size": e.size,
            "created_at": e.created_at,
        }
        for e in ebooks
    ]


@router.get("/{ebook_id}/book.epub")
def serve_epub(ebook_id: int, db: Session = Depends(get_db)):
    ebook = db.query(Ebook).filter(Ebook.id == ebook_id).first()
    if not ebook:
        raise HTTPException(status_code=404, detail="Ebook não encontrado")
    file_path = os.path.join(UPLOAD_DIR, ebook.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(
        file_path,
        media_type="application/epub+zip",
        filename=ebook.original_name,
        headers={"Access-Control-Allow-Origin": "*"},
    )


@router.get("/{ebook_id}/epub/{resource_path:path}")
def serve_epub_resource(ebook_id: int, resource_path: str, db: Session = Depends(get_db)):
    """Serve individual resources from inside the epub zip (used by epubjs directory mode)."""
    ebook = db.query(Ebook).filter(Ebook.id == ebook_id).first()
    if not ebook:
        raise HTTPException(status_code=404, detail="Ebook não encontrado")

    zip_path = os.path.join(UPLOAD_DIR, ebook.filename)

    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Arquivo epub não encontrado no servidor")

    try:
        with zipfile.ZipFile(zip_path) as z:
            content = z.read(resource_path)
    except KeyError:
        # Recurso opcional ausente no epub — retorna vazio para não interromper o epubjs
        return Response(content=b"", status_code=200)
    except (zipfile.BadZipFile, Exception):
        raise HTTPException(status_code=422, detail="Arquivo epub inválido ou corrompido")

    ext = resource_path.rsplit(".", 1)[-1].lower() if "." in resource_path else ""
    media_type = CONTENT_TYPES.get(ext, "application/octet-stream")

    return Response(
        content=content,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.delete("/{ebook_id}")
def delete_ebook(ebook_id: int, db: Session = Depends(get_db)):
    ebook = db.query(Ebook).filter(Ebook.id == ebook_id).first()
    if not ebook:
        raise HTTPException(status_code=404, detail="Ebook não encontrado")
    file_path = os.path.join(UPLOAD_DIR, ebook.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.delete(ebook)
    db.commit()
    return {"ok": True}
