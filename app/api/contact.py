import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import ContactRequest, ContactResponse
from app.services.contact_service import contact_service
from app.db.db import get_db
from app.db.repositories import rate_limit_repo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["contact"])


@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=201,
    summary="Отправить форму обратной связи",
    description=(
        "Принимает данные из формы обратной связи, выполняет AI-анализ"
        " и отправляет email-уведомления."
    ),
    responses={
        429: {"description": "Превышен лимит запросов"},
        422: {"description": "Ошибка валидации данных"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def create_contact(
    contact: ContactRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ContactResponse:
    client_ip = getattr(request.state, "client_ip", "unknown")

    is_limited = await rate_limit_repo.check_and_record(db, client_ip)
    if is_limited:
        raise HTTPException(status_code=429, detail="Превышен лимит запросов")

    result = await contact_service.process(
        db,
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        comment=contact.comment,
        ip_address=client_ip,
    )

    return ContactResponse(**result)
