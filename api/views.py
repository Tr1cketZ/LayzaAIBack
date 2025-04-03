from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import PasswordResetToken
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
# Create your views here.
@swagger_auto_schema(
    methods=['POST'],
    request_body= UserCreateSerializer,
    tags=["token"],
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
    request_body= PasswordResetRequestSerializer,
    tags=["token"],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # Criar token temporário
        token = PasswordResetToken.objects.create(user=user)
        
        # Gerar link de recuperação
        reset_url = request.build_absolute_uri(
            reverse('password_reset_request') + f'?token={token.token}'
        )
        
        # Enviar email
        subject = "Recuperação de Senha - Layza"
        message = f"""
        Olá {user.first_name},

        Você solicitou a recuperação de senha. Clique no link abaixo para redefinir sua senha:
        {reset_url}

        Este link é válido por 15 minutos. Se você não solicitou isso, ignore este email.

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
            {"message": "Email de recuperação enviado com sucesso."},
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=PasswordResetConfirmSerializer,
    tags=["token"],
    responses={
        200: 'Senha redefinida com sucesso.',
        400: 'Erro na validação do token ou senha.'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        reset_token = serializer.validated_data['reset_token']
        user = reset_token.user
        
        # Alterar a senha
        user.set_password(serializer.validated_data['password'])
        user.save()
        
        # Invalidar o token após uso
        reset_token.delete()
        
        return Response(
            {"message": "Senha redefinida com sucesso."},
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)