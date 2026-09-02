from .models import User


class UserCustomAuthenticatedBackend:
    def get_user(self, user_id):


        return (
            User.objects
            .select_related("store")
            .prefetch_related("colleague_with_store")
            .get(pk=user_id)
        )