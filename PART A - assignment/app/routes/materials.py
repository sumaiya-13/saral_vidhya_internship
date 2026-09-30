import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Material, User
from app.schemas import MaterialResponse, QuizResponse
from app.services.ocr import extract_text_from_pdf
from app.services.llm import generate_summary, generate_quiz

router = APIRouter(prefix="/materials", tags=["Materials"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_owned_material(material_id: int, user: User, db: Session) -> Material:
    material = (
        db.query(Material)
        .filter(Material.id == material_id, Material.owner_id == user.id)
        .first()
    )
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material

@router.post("/upload", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def upload_material(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    safe_name = f"{uuid.uuid4().hex}_{os.path.basename(file.filename or 'material.pdf')}"
    path = os.path.join(UPLOAD_DIR, safe_name)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text_from_pdf(path)
    except Exception as exc:
        os.remove(path)
        raise HTTPException(status_code=500, detail=f"PDF/OCR processing failed: {exc}")

    material = Material(
        filename=file.filename or "material.pdf",
        file_path=path,
        extracted_text=extracted_text,
        owner_id=current_user.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    return material

@router.post("/{material_id}/summary", response_model=MaterialResponse)
def summarize_material(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    material = get_owned_material(material_id, current_user, db)

    if not material.extracted_text:
        raise HTTPException(status_code=400, detail="No extracted text available")

    try:
        material.summary = generate_summary(material.extracted_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {exc}")

    db.commit()
    db.refresh(material)
    return material

@router.post("/{material_id}/quiz", response_model=QuizResponse)
def quiz_material(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    material = get_owned_material(material_id, current_user, db)

    if not material.extracted_text:
        raise HTTPException(status_code=400, detail="No extracted text available")

    try:
        material.quiz = generate_quiz(material.extracted_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {exc}")

    db.commit()
    db.refresh(material)

    return {"id": material.id, "filename": material.filename, "quiz": material.quiz}
