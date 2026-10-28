from wedding.modules.identity.adapters.http.schemas import CurrentUserOut
from wedding.modules.identity.application.dto import CurrentUser


def to_current_user_out(user: CurrentUser) -> CurrentUserOut:
    return CurrentUserOut.model_validate(
        {"user_id": user.user_id, "username": user.username, "profile": user.profile}
    )
