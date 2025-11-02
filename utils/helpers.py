from config import settings


def is_admin(user_id: int) -> bool:
    admin_ids = settings.get_admin_ids()

    if not admin_ids:
        return False

    return user_id in admin_ids
