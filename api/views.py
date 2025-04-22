import random
import string
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import PasswordResetToken
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from drf_yasg import openapi


@swagger_auto_schema(
    methods=['GET'],
    tags=["Auth"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
# Create your views here.
@swagger_auto_schema(
    methods=['POST'],
    request_body= UserCreateSerializer,
    tags=["Auth"],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['POST'],
    request_body= LoginSerializer,
    tags=["Auth"],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validate(request.data), status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['POST'],
    request_body= PasswordResetRequestSerializer,
    tags=["Auth"],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            # Gerar código de 6 dígitos
            code = ''.join(random.choices(string.digits, k=6))
            # Criar token com código
            PasswordResetToken.objects.create(user=user, code=code)
            
            # Enviar email com código
            subject = "Recuperação de Senha - Layza"
            message = f"""
            Olá {user.first_name or user.username},

            Você solicitou a recuperação de senha. Use o código abaixo para redefinir sua senha:
            Código: {code}

            Este código é válido por 15 minutos. Se você não solicitou isso, ignore este email.

            Equipe Layza
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response(
                {"message": "Código de recuperação enviado com sucesso."},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Email não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@swagger_auto_schema(
    methods=['POST'],
    request_body=PasswordResetConfirmSerializer,
    tags=["Auth"],
    manual_parameters=[
        openapi.Parameter(
            'token',
            openapi.IN_QUERY,
            description="Token de recuperação de senha",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    token = request.GET.get('token')
    if not token:
        return Response(
            {"token": "O token é obrigatório na URL."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token.is_valid():
            return Response(
                {"token": "Este link expirou. Solicite um novo."},
                status=status.HTTP_400_BAD_REQUEST
            )
    except PasswordResetToken.DoesNotExist:
        return Response(
            {"token": "Token inválido."},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        user = reset_token.user
        user.set_password(serializer.validated_data['password'])
        user.save()
        reset_token.delete()
        
        return Response(
            {"message": "Senha redefinida com sucesso."},
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)