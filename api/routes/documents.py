import mimetypes
import os
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.document import Document, DocumentReviewUpdate, DocumentState
from schemas.document_schema import DocumentRead

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "library")
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload", response_model=List[DocumentRead], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    id_type: Optional[str] = Form(None),
    id_document_front: Optional[UploadFile] = File(None),
    id_document_back: Optional[UploadFile] = File(None),
    grades_certificate: Optional[UploadFile] = File(None),
    cover_letter: Optional[UploadFile] = File(None),
    disability_certificate: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    incoming_files = {
        "id_document_front": id_document_front,
        "id_document_back": id_document_back,
        "grades_certificate": grades_certificate,
        "cover_letter": cover_letter,
        "disability_certificate": disability_certificate,
    }

    user_dir = os.path.join(UPLOAD_DIR, current_user.rodne_cislo.replace("/", "_"))
    os.makedirs(user_dir, exist_ok=True)

    created = []
    for doc_type, upload in incoming_files.items():
        if upload is None:
            continue

        if upload.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Archivo '{upload.filename}': tipo no permitido. Solo PNG, JPEG y PDF.",
            )

        contents = await upload.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Archivo '{upload.filename}' supera el límite de 10MB.",
            )

        original_name = upload.filename or "file"
        unique_filename = f"{uuid.uuid4().hex}_{original_name}"
        file_path = os.path.join(user_dir, unique_filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        # Si ya existe un documento del mismo tipo para este usuario, sobreescribir
        existing = db.exec(
            select(Document).where(
                Document.user_id == current_user.id,
                Document.document_type == doc_type,
            )
        ).first()

        if existing:
            # Borrar el archivo antiguo del disco si existe
            if existing.file_path and os.path.exists(existing.file_path):
                os.remove(existing.file_path)
            existing.name = original_name
            existing.file_path = file_path.replace("\\", "/")
            db.add(existing)
            db.commit()
            db.refresh(existing)
            created.append(DocumentRead.model_validate(existing))
        else:
            document = Document(
                user_id=current_user.id,
                name=original_name,
                document_type=doc_type,
                file_path=file_path.replace("\\", "/"),
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            created.append(DocumentRead.model_validate(document))

    return created


@router.get("", response_model=List[DocumentRead])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    documents = db.exec(
        select(Document).where(Document.user_id == current_user.id)
    ).all()
    return [DocumentRead.model_validate(d) for d in documents]


@router.get("/{doc_id}/file")
def serve_document_file(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Sirve el archivo físico de un documento. Solo accesible por su propietario."""
    document = db.get(Document, doc_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")
    if not document.file_path or not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor.")

    mime_type, _ = mimetypes.guess_type(document.file_path)
    return FileResponse(
        path=document.file_path,
        media_type=mime_type or "application/octet-stream",
        filename=document.name,
    )


@router.get("/{doc_id}", response_model=DocumentRead)
def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    document = db.get(Document, doc_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")
    return DocumentRead.model_validate(document)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    document = db.get(Document, doc_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")

    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()

@router.patch("/{doc_id}/review", response_model=Document)
def review_document(
    doc_id: int,
    review_data: DocumentReviewUpdate,
    db: Session = Depends(get_session)
):
    document = db.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")
    
    if review_data.state == DocumentState.pending:
        raise HTTPException(
            status_code=400, 
            detail="El estado de revisión debe ser 'approved' o 'rejected'."
        )
    
    document.state = review_data.state

    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document