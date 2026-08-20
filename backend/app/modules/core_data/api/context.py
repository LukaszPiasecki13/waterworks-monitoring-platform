"""Current-user environment context API."""

from fastapi import APIRouter, Depends

from app.modules.core_data.dependencies import get_user_context_service
from app.modules.core_data.models import User
from app.modules.core_data.schemas.context import UserContextResponse
from app.modules.core_data.services.context import UserContextService
from app.modules.security.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me/context", response_model=UserContextResponse)
def get_my_context(
    user: User = Depends(get_current_user),
    service: UserContextService = Depends(get_user_context_service),
) -> UserContextResponse:
    """Environments (organizations + platform) available to the current user."""
    return service.get_context(user)
