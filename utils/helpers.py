from config import settings


def is_admin(user_id: int) -> bool:
    admin_ids = settings.get_admin_ids()
    return bool(admin_ids) and user_id in admin_ids
