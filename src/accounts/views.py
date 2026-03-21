from django.shortcuts import render
from accounts.serializers import CreateUserSerializer
from accounts.services import UserService
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


@extend_schema(
    request=CreateUserSerializer,
    responses={
        201: {"message": "User created successfully"},
        400: CreateUserSerializer,
    },
)
class RegisterUserView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        data = CreateUserSerializer(data=request.data)
        if data.is_valid():
            user = UserService().create_user(data.validated_data)
            return Response({"message": "User created successfully"}, status=201)
        return Response(data.errors, status=400)
