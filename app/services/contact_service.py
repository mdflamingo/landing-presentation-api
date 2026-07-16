import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_service import ai_service
from app.services.email_service import email_service
from app.db.repositories import contact_repo
logger = logging.getLogger(__name__)


class ContactService:
    async def process(
        self,
        db: AsyncSession,
        *,
        name: str,
        email: str,
        phone: str,
        comment: str,
        ip_address: str | None = None,
    ) -> dict:
        request_id = str(uuid.uuid4())[:8]

        logger.info("Processing contact request %s from %s", request_id, email)

        analysis = ai_service.analyze(name, comment)
        logger.info(
            "AI analysis for %s: sentiment=%s, category=%s",
            request_id,
            analysis.sentiment,
            analysis.category,
        )

        email_service.send_owner_notification(
            name=name,
            email=email,
            phone=phone,
            comment=comment,
            request_id=request_id,
            sentiment=analysis.sentiment,
            category=analysis.category,
            ai_response=analysis.suggested_response,
        )
        email_service.send_user_copy(name=name, email=email, comment=comment)

        await contact_repo.create(
            db,
            request_id=request_id,
            name=name,
            email=email,
            phone=phone,
            comment=comment,
            ip_address=ip_address,
            ai_sentiment=analysis.sentiment,
            ai_category=analysis.category,
            ai_response=analysis.suggested_response,
        )

        logger.info("Contact request %s processed successfully", request_id)

        return {
            "request_id": request_id,
            "success": True,
            "message": "Ваше обращение успешно отправлено. Мы свяжемся с вами в ближайшее время.",
            "ai_sentiment": analysis.sentiment,
            "ai_response": analysis.suggested_response,
            "ai_category": analysis.category,
        }


contact_service = ContactService()
