import mimetypes
import os
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select, func
from models.role import Role
from models.user_role import UserRole
from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.document import Document, DocumentReviewUpdate, DocumentState, DocumentType
from models.interview import Interview
from schemas.document_schema import DocumentRead
from services.notification_service import create_notification

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "library")
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Tipos de documento obligatorios para aparecer en la vista de revisión
MANDATORY_DOC_TYPES = {
    DocumentType.id_document_front.value,
    DocumentType.id_document_back.value,
    DocumentType.grade_certificate.value,
    DocumentType.motivation_letter.value,
}

REVIEWER_ROLE_KEYWORDS = ("admin", "teacher", "profesor", "professor", "coordinator", "coordinador")


def _is_reviewer(role_name: str) -> bool:
    return any(r in role_name.lower() for r in REVIEWER_ROLE_KEYWORDS)


def _get_reviewer_user_ids(db: Session) -> list[int]:
    """Devuelve los IDs de todos los usuarios con rol de profesor o admin."""
    reviewer_role_ids = [
        r.id for r in db.exec(select(Role)).all()
        if _is_reviewer(r.name)
    ]
    if not reviewer_role_ids:
        return []
    return list(db.exec(
        select(UserRole.user_id).where(UserRole.role_id.in_(reviewer_role_ids))
    ).all())


def _student_has_all_mandatory_docs(db: Session, user_id: int) -> bool:
    """Devuelve True si el alumno tiene todos los documentos obligatorios subidos."""
    existing_types = set(db.exec(
        select(Document.document_type).where(Document.user_id == user_id)
    ).all())
    return MANDATORY_DOC_TYPES.issubset(existing_types)


@router.post("/upload", response_model=List[DocumentRead], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    id_type: Optional[str] = Form(None),
    id_document_front: Optional[UploadFile] = File(None),
    id_document_back: Optional[UploadFile] = File(None),
    grades_certificate: Optional[UploadFile] = File(None),
    motivation_letter: Optional[UploadFile] = File(None),
    language_certificate: Optional[UploadFile] = File(None),
    disability_certificate: Optional[UploadFile] = File(None),
    parental_authorization: Optional[UploadFile] = File(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    
    incoming_files = {
        DocumentType.id_document_front.value: id_document_front,
        DocumentType.id_document_back.value: id_document_back,
        DocumentType.grade_certificate.value: grades_certificate, 
        DocumentType.motivation_letter.value: motivation_letter,
        DocumentType.disability_certificate.value: disability_certificate,
        DocumentType.parental_authorization.value: parental_authorization,
        DocumentType.language_certificate.value: language_certificate
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

        is_calificable = doc_type in [
            DocumentType.grade_certificate.value, 
            DocumentType.motivation_letter.value,
            DocumentType.language_certificate.value
        ]

        existing = db.exec(
            select(Document).where(
                Document.user_id == current_user.id,
                Document.document_type == doc_type,
            )
        ).first()

        if existing:
            if existing.file_path and os.path.exists(existing.file_path):
                os.remove(existing.file_path)
            existing.name = original_name
            existing.file_path = file_path.replace("\\", "/")
            existing.state = DocumentState.pending
            existing.rejection_reason = None
            existing.grade = None
            db.add(existing)
            db.commit()
            db.refresh(existing)
            created.append(DocumentRead.model_validate(existing))
        else:
            document = Document(
                user_id=current_user.id,
                name=original_name,
                document_type=doc_type,
                calificable=is_calificable,
                file_path=file_path.replace("\\", "/"),
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            created.append(DocumentRead.model_validate(document))

    # Notificar a profesores/admins si el alumno acaba de completar todos los obligatorios
    if _student_has_all_mandatory_docs(db, current_user.id):
        student_name = f"{current_user.first_name} {current_user.last_name}"
        for reviewer_id in _get_reviewer_user_ids(db):
            create_notification(
                db=db,
                user_id=reviewer_id,
                message_key="docs_ready_for_review",
                notif_type="application_update",
                params={"student_name": student_name},
            )

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


@router.get("/pending")
def get_pending_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Devuelve la lista de alumnos con el conteo de documentos por estado. Solo profesor/admin."""
    role_id = db.exec(select(UserRole.role_id).where(UserRole.user_id == current_user.id)).first()
    role_name = db.exec(select(Role.name).where(Role.id == role_id)).first() or ""
    is_reviewer = any(
        r in role_name.lower()
        for r in ("admin", "teacher", "profesor", "professor", "coordinator", "coordinador")
    )
    if not is_reviewer:
        raise HTTPException(status_code=403, detail="Solo profesores y administradores pueden acceder.")

    # Obtener todos los alumnos que tienen al menos un documento
    student_role_ids = db.exec(
        select(Role.id).where(Role.name == "Student")
    ).all()
    student_user_ids = db.exec(
        select(UserRole.user_id).where(UserRole.role_id.in_(student_role_ids))
    ).all()

    if not student_user_ids:
        return []

    documents = db.exec(
        select(Document).where(Document.user_id.in_(student_user_ids))
    ).all()

    # Agrupar por user_id
    from collections import defaultdict
    doc_map: dict = defaultdict(lambda: {"pending": 0, "approved": 0, "rejected": 0, "total": 0, "types": set(), "mandatory_states": {}})
    for doc in documents:
        doc_map[doc.user_id][doc.state.value] += 1
        doc_map[doc.user_id]["total"] += 1
        doc_map[doc.user_id]["types"].add(doc.document_type)
        if doc.document_type in MANDATORY_DOC_TYPES:
            doc_map[doc.user_id]["mandatory_states"][doc.document_type] = doc.state.value

    # Solo incluir alumnos que tienen TODOS los documentos obligatorios subidos
    complete_user_ids = [
        uid for uid, counts in doc_map.items()
        if MANDATORY_DOC_TYPES.issubset(counts["types"])
    ]

    if not complete_user_ids:
        return []

    users = db.exec(
        select(User).where(User.id.in_(complete_user_ids))
    ).all()

    interviews = db.exec(
        select(Interview).where(Interview.user_id.in_(complete_user_ids))
    ).all()
    interview_map = {iv.user_id: iv for iv in interviews}

    result = []
    for user in users:
        counts = doc_map[user.id]
        mandatory_states = counts["mandatory_states"]
        all_approved = (
            set(mandatory_states.keys()) == MANDATORY_DOC_TYPES
            and all(v == "approved" for v in mandatory_states.values())
        )
        interview = interview_map.get(user.id)
        result.append({
            "user_id": user.id,
            "user_name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "pending": counts["pending"],
            "approved": counts["approved"],
            "rejected": counts["rejected"],
            "total": counts["total"],
            "all_approved": all_approved,
            "interview_grade": interview.grade if interview else None,
            "interview_status": interview.status if interview else "pending",
            "interview_rejection_reason": interview.rejection_reason if interview else None,
        })

    return sorted(result, key=lambda x: x["pending"], reverse=True)


@router.get("/{doc_id}/file")
def serve_document_file(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Sirve el archivo físico. Accesible por el propietario o por profesor/admin."""
    document = db.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")

    # Comprobar si el usuario es profesor o admin
    role_id = db.exec(select(UserRole.role_id).where(UserRole.user_id == current_user.id)).first()
    role_name = db.exec(select(Role.name).where(Role.id == role_id)).first() or ""
    is_reviewer = any(
        r in role_name.lower()
        for r in ("admin", "teacher", "profesor", "professor", "coordinator", "coordinador")
    )

    if document.user_id != current_user.id and not is_reviewer:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este archivo.")

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

@router.get("/user/{user_id}")
def get_user_documents(
    user_id: int,
    db: Session = Depends(get_session)
):
    rol_id = db.exec(select(UserRole.role_id).where(UserRole.user_id == user_id)).first()  
    rol = db.exec(select(Role.name).where(Role.id == rol_id)).first()
    if rol != "Student":
        raise HTTPException(status_code=401, detail="El usuario seleccionado no es un estudiante")

    documents = db.exec(
        select(Document).where(Document.user_id == user_id)
    ).all()
    return [DocumentRead.model_validate(d) for d in documents]


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


@router.patch("/{doc_id}/review")
def review_document(
    doc_id: int,
    review_data: DocumentReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    # Solo profesor/admin puede revisar
    role_id = db.exec(select(UserRole.role_id).where(UserRole.user_id == current_user.id)).first()
    role_name = db.exec(select(Role.name).where(Role.id == role_id)).first() or ""
    is_reviewer = any(
        r in role_name.lower()
        for r in ("admin", "teacher", "profesor", "professor", "coordinator", "coordinador")
    )
    if not is_reviewer:
        raise HTTPException(status_code=403, detail="Solo profesores y administradores pueden revisar documentos.")

    document = db.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")

    if review_data.state == DocumentState.pending:
        raise HTTPException(
            status_code=400,
            detail="El estado de revisión debe ser 'approved' o 'rejected'."
        )

    if review_data.state == DocumentState.rejected:
        if not review_data.rejection_reason or not review_data.rejection_reason.strip():
            raise HTTPException(
                status_code=400,
                detail="El motivo del rechazo es obligatorio al rechazar un documento."
            )

        document.rejection_reason = review_data.rejection_reason.strip()
        document.grade = None
        document.state = DocumentState.rejected
        db.add(document)
        db.commit()
        db.refresh(document)

        create_notification(
            db=db,
            user_id=document.user_id,
            message_key="doc_rejected",
            notif_type="application_update",
            params={"doc_type": document.name, "reason": document.rejection_reason},
        )

        from schemas.document_schema import DocumentRead
        return DocumentRead.model_validate(document)

    # approved
    document.rejection_reason = None
    if review_data.grade is not None:
        if review_data.grade < 1 or review_data.grade > 10:
            raise HTTPException(
                status_code=400,
                detail="La nota del documento debe ser un número del 1 al 10."
            )
        if not document.calificable:
            raise HTTPException(
                status_code=400,
                detail="El documento no es calificable, no debe tener nota."
            )
        document.grade = review_data.grade

    document.state = review_data.state
    db.add(document)
    db.commit()
    db.refresh(document)

    # Notificar al alumno del cambio de estado
    if review_data.state == DocumentState.approved:
        create_notification(
            db=db,
            user_id=document.user_id,
            message_key="doc_approved",
            notif_type="application_update",
            params={"doc_type": document.name},
        )
    else:
        create_notification(
            db=db,
            user_id=document.user_id,
            message_key="doc_rejected",
            notif_type="application_update",
            params={
                "doc_type": document.document_type,
                "reason": review_data.rejection_reason or "",
            },
        )

    return DocumentRead.model_validate(document)