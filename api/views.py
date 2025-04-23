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
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
        try:
            user = User.objects.get(email=email)
            reset_token = PasswordResetToken.objects.filter(user=user, code=code).first()
            
            if not reset_token:
                return Response(
                    {"code": "Código de verificação inválido."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if not reset_token.is_valid():
                return Response(
                    {"code": "Este código expirou. Solicite um novo."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            reset_token.delete()
            
            return Response(
                {"message": "Senha redefinida com sucesso."},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {"email": "Email não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['GET'],
    operation_description="Retorna o perfil do usuário autenticado",
    tags=["Perfil"],
    responses={200: PerfilUsuarioSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_detail(request):
    try:
        perfil = PerfilUsuario.objects.get(user=request.user)
        serializer = PerfilUsuarioSerializer(perfil)
        return Response(serializer.data)
    except PerfilUsuario.DoesNotExist:
        # Se o perfil não existe, cria um com preferências padrão
        perfil = PerfilUsuario.objects.create(user=request.user)
        serializer = PerfilUsuarioSerializer(perfil)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    methods=['PUT', 'PATCH'],
    operation_description="Atualiza as preferências de aprendizado do usuário",
    request_body=PerfilUsuarioUpdateSerializer,
    tags=["Perfil"],
    responses={200: PerfilUsuarioSerializer}
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def perfil_update(request):
    try:
        perfil = PerfilUsuario.objects.get(user=request.user)
    except PerfilUsuario.DoesNotExist:
        perfil = PerfilUsuario.objects.create(user=request.user)

    serializer = PerfilUsuarioUpdateSerializer(
        perfil, 
        data=request.data,
        partial=request.method == 'PATCH'
    )

    if serializer.is_valid():
        # Valida se pelo menos uma preferência está selecionada
        if not any([
            serializer.validated_data.get('pref_visual', perfil.pref_visual),
            serializer.validated_data.get('pref_auditivo', perfil.pref_auditivo),
            serializer.validated_data.get('pref_leitura_escrita', perfil.pref_leitura_escrita)
        ]):
            return Response(
                {"detail": "Selecione pelo menos uma preferência de aprendizado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        return Response(PerfilUsuarioSerializer(perfil).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['GET'],
    operation_description="Lista todos os conteúdos disponíveis",
    tags=["Conteúdos"],
    responses={200: ConteudoSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conteudo_list(request):
    conteudos = Conteudo.objects.all()
    serializer = ConteudoSerializer(conteudos, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    methods=['POST'],
    operation_description="Cria um novo conteúdo",
    request_body=ConteudoSerializer,
    tags=["Conteúdos"],
    responses={201: ConteudoSerializer}
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def conteudo_create(request):
    serializer = ConteudoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['GET'],
    operation_description="Retorna os detalhes de um conteúdo específico",
    tags=["Conteúdos"],
    responses={200: ConteudoSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conteudo_detail(request, pk):
    try:
        conteudo = Conteudo.objects.get(pk=pk)
    except Conteudo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ConteudoSerializer(conteudo)
    return Response(serializer.data)

@swagger_auto_schema(
    methods=['PUT'],
    operation_description="Atualiza um conteúdo existente",
    request_body=ConteudoSerializer,
    tags=["Conteúdos"],
    responses={200: ConteudoSerializer}
)
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def conteudo_update(request, pk):
    try:
        conteudo = Conteudo.objects.get(pk=pk)
    except Conteudo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ConteudoSerializer(conteudo, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['DELETE'],
    operation_description="Deleta um conteúdo",
    tags=["Conteúdos"],
    responses={204: "No Content"}
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def conteudo_delete(request, pk):
    try:
        conteudo = Conteudo.objects.get(pk=pk)
    except Conteudo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    conteudo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)