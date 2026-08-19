import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, Project

MARKDOWN_EXT = (".md", ".markdown")
IGNORED_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".idea", ".vscode", "dist", "build"}

router = APIRouter(prefix="/projects", tags=["projects"])


def _to_fs_path(path: str) -> str:
    """Translate a Windows-style path (D:\\foo or D:/foo) to the equivalent WSL
    mount path (/mnt/d/foo) so the backend can access disks shared with Windows.
    Paths that are already POSIX-style are returned unchanged."""
    if len(path) >= 2 and path[1] == ":" and (path[0].isalpha()):
        drive = path[0].lower()
        rest = path[2:].replace("\\", "/").lstrip("/")
        return f"/mnt/{drive}/{rest}" if rest else f"/mnt/{drive}"
    return path


def _resolve_safe_path(project: Project, rel_path: str) -> str:
    """Resolve rel_path against the project's local_path, rejecting traversal outside of it."""
    base = os.path.realpath(_to_fs_path(project.local_path))
    target = os.path.realpath(os.path.join(base, rel_path or ""))
    if target != base and not target.startswith(base + os.sep):
        raise HTTPException(status_code=400, detail="Caminho inválido")
    return target


def _build_tree(dir_path: str, rel_path: str = "") -> dict:
    name = os.path.basename(dir_path) or dir_path
    node = {"name": name, "type": "dir", "path": rel_path, "children": []}
    try:
        entries = sorted(
            os.scandir(dir_path),
            key=lambda e: (e.is_file(), e.name.lower()),
        )
    except OSError:
        return node

    for entry in entries:
        entry_rel = f"{rel_path}/{entry.name}" if rel_path else entry.name
        if entry.is_dir(follow_symlinks=False):
            if entry.name in IGNORED_DIRS or entry.name.startswith("."):
                continue
            node["children"].append(_build_tree(entry.path, entry_rel))
        elif entry.is_file(follow_symlinks=False):
            if entry.name.lower().endswith(MARKDOWN_EXT):
                node["children"].append({"name": entry.name, "type": "file", "path": entry_rel})
    return node


class ProjectIn(BaseModel):
    name: str
    local_path: str
    description: str = ""


class FileIn(BaseModel):
    content: str


def _project_out(p: Project) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "local_path": p.local_path,
        "description": p.description or "",
        "created_at": p.created_at,
    }


@router.post("")
def create_project(data: ProjectIn, db: Session = Depends(get_db)):
    fs_path = _to_fs_path(data.local_path)
    if not os.path.isdir(fs_path):
        raise HTTPException(status_code=400, detail="Caminho não encontrado ou não é uma pasta")
    project = Project(
        name=data.name,
        local_path=data.local_path,
        description=data.description,
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_out(project)


@router.get("")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.id.desc()).all()
    return [_project_out(p) for p in projects]


@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return _project_out(project)


@router.put("/{project_id}")
def update_project(project_id: int, data: ProjectIn, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    if not os.path.isdir(_to_fs_path(data.local_path)):
        raise HTTPException(status_code=400, detail="Caminho não encontrado ou não é uma pasta")
    project.name = data.name
    project.local_path = data.local_path
    project.description = data.description
    db.commit()
    db.refresh(project)
    return _project_out(project)


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    db.delete(project)
    db.commit()
    return {"ok": True}


@router.get("/{project_id}/tree")
def get_tree(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    fs_path = _to_fs_path(project.local_path)
    if not os.path.isdir(fs_path):
        raise HTTPException(status_code=404, detail="Pasta do projeto não encontrada no disco")
    return _build_tree(fs_path)


@router.get("/{project_id}/file")
def read_file(project_id: int, path: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    if not path.lower().endswith(MARKDOWN_EXT):
        raise HTTPException(status_code=400, detail="Apenas arquivos .md podem ser abertos")
    file_path = _resolve_safe_path(project, path)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {
        "path": path,
        "content": content,
        "modified_at": datetime.utcfromtimestamp(os.path.getmtime(file_path)).isoformat(),
    }


@router.put("/{project_id}/file")
def write_file(project_id: int, path: str, data: FileIn, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    if not path.lower().endswith(MARKDOWN_EXT):
        raise HTTPException(status_code=400, detail="Apenas arquivos .md podem ser salvos")
    file_path = _resolve_safe_path(project, path)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data.content)
    return {
        "path": path,
        "modified_at": datetime.utcfromtimestamp(os.path.getmtime(file_path)).isoformat(),
    }
