from django.contrib.auth.models import User


class UserService:

    def create_user(self, data):

        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
        )
        return user
