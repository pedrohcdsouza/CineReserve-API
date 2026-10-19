from django.test import SimpleTestCase
from unittest.mock import patch
from accounts.serializers import CreateUserSerializer
from accounts.services import UserService


class CreateUserSerializerUnitTests(SimpleTestCase):
    def test_valid_data(self):
        serializer = CreateUserSerializer(
            data={"username": "pedro", "email": "pedro@mail.com", "password": "12345678"}
        )
        self.assertTrue(serializer.is_valid())

    def test_rejects_short_password_and_invalid_email(self):
        serializer = CreateUserSerializer(
            data={"username": "pedro", "email": "not-an-email", "password": "123"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)
        self.assertIn("email", serializer.errors)


class UserServiceUnitTests(SimpleTestCase):
    @patch("accounts.services.User.objects.create_user")
    def test_create_user(self, mock_create_user):
        data = {"username": "pedro", "email": "pedro@mail.com", "password": "12345678"}

        user = UserService().create_user(data)

        mock_create_user.assert_called_once_with(
            username="pedro", email="pedro@mail.com", password="12345678"
        )
        self.assertEqual(user, mock_create_user.return_value)
