import random
import string
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import PasswordResetToken
from django.core.mail import send_mail
from django.conf import settings
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser

# Create your views here.


# region Auth
@swagger_auto_schema(
    methods=["POST"],
    request_body=UserCreateSerializer,
    tags=["Auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=["POST"],
    request_body=LoginSerializer,
    tags=["Auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validate(request.data), status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=["POST"],
    request_body=PasswordResetRequestSerializer,
    tags=["Auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            # Gerar código de 6 dígitos
            code = "".join(random.choices(string.digits, k=6))
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
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Email não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=["POST"],
    request_body=PasswordResetConfirmSerializer,
    tags=["Auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        try:
            user = User.objects.get(email=email)
            reset_token = PasswordResetToken.objects.filter(
                user=user, code=code
            ).first()

            if not reset_token:
                return Response(
                    {"code": "Código de verificação inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not reset_token.is_valid():
                return Response(
                    {"code": "Este código expirou. Solicite um novo."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(serializer.validated_data["new_password"])
            user.save()
            reset_token.delete()

            return Response(
                {"message": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"email": "Email não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=["POST"],
    request_body=CodeVerificationSerializer,
    tags=["Auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_verify_code(request):
    serializer = CodeVerificationSerializer(data=request.data)
    if serializer.is_valid():
        code = serializer.validated_data["code"]
        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"email": "Email não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )
        if not PasswordResetToken.objects.filter(user=user, code=code).exists():
            return Response(
                {"code": "Código de verificação inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"message": "Código verificado com sucesso."}, status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# endregion


# region Perfil
@swagger_auto_schema(
    methods=["GET"],
    tags=["Perfil"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    methods=["PUT", "PATCH"],
    operation_description="Atualiza os dados do usuário e perfil",
    manual_parameters=[
        openapi.Parameter("username", openapi.IN_FORM, type=openapi.TYPE_STRING),
        openapi.Parameter("email", openapi.IN_FORM, type=openapi.TYPE_STRING),
        openapi.Parameter("pref_visual", openapi.IN_FORM, type=openapi.TYPE_BOOLEAN),
        openapi.Parameter("pref_auditivo", openapi.IN_FORM, type=openapi.TYPE_BOOLEAN),
        openapi.Parameter(
            "pref_leitura_escrita", openapi.IN_FORM, type=openapi.TYPE_BOOLEAN
        ),
        openapi.Parameter(
            "serie_atual", openapi.IN_FORM, type=openapi.TYPE_STRING,enum=[
                "1º Ano",
                "2º Ano",
                "3º Ano",
            ]
        ),
        openapi.Parameter("foto_perfil", openapi.IN_FORM, type=openapi.TYPE_FILE),
    ],
    consumes=["multipart/form-data"],
    responses={200: UserSerializer},
    tags=["Perfil"],
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def perfil_update_completo(request):
    try:
        user = request.user
        perfil = PerfilUsuario.objects.get_or_create(user=user)[0]

        # Atualiza tudo via serializer (ele já trata PerfilUsuario)
        user_serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=request.method == "PATCH",
        )

        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except PerfilUsuario.DoesNotExist:
        return Response(
            {"detail": "Perfil não encontrado"}, status=status.HTTP_404_NOT_FOUND
        )


@swagger_auto_schema(
    methods=["DELETE"],
    operation_description="Desativa a conta do usuário (deleção lógica)",
    tags=["Perfil"],
    responses={204: "No Content"},
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def perfil_delete(request):
    try:
        user = request.user
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response(
            {"detail": "Erro ao desativar conta"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# endregion


# region Conteúdos
@swagger_auto_schema(
    methods=["GET"],
    operation_description="Lista todos os conteúdos disponíveis",
    tags=["Conteúdos"],
    responses={200: ConteudoSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conteudo_list(request):
    conteudos = Conteudo.objects.filter(is_active=True)
    serializer = ConteudoSerializer(conteudos, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    methods=["POST"],
    operation_description="Cria um novo conteúdo \n Tipos: 'Vídeo', 'Áudio', 'Texto'",
    request_body=ConteudoSerializer,
    tags=["Conteúdos"],
    responses={201: ConteudoSerializer},
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def conteudo_create(request):
    serializer = ConteudoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=["GET"],
    operation_description="Retorna os detalhes de um conteúdo específico",
    tags=["Conteúdos"],
    responses={200: ConteudoSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conteudo_detail(request, pk):
    try:
        conteudo = Conteudo.objects.get(pk=pk, is_active=True)
    except Conteudo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ConteudoSerializer(conteudo)
    return Response(serializer.data)


@swagger_auto_schema(
    methods=["PUT"],
    operation_description="Atualiza um conteúdo existente",
    request_body=ConteudoSerializer,
    tags=["Conteúdos"],
    responses={200: ConteudoSerializer},
)
@api_view(["PUT"])
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
    methods=["DELETE"],
    operation_description="Deleta um conteúdo",
    tags=["Conteúdos"],
    responses={204: "No Content"},
)
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def conteudo_delete(request, pk):
    try:
        conteudo = Conteudo.objects.get(pk=pk)
    except Conteudo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    conteudo.is_active = False
    conteudo.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


# endregion


# region Provas
@swagger_auto_schema(
    methods=["GET"],
    operation_description="Lista todas as provas do usuário autenticado",
    tags=["Provas"],
    responses={200: ProvaSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def prova_list(request):
    provas = Prova.objects.filter(usuario=request.user)
    serializer = ProvaSerializer(provas, many=True, context={"request": request})
    return Response(serializer.data)


@swagger_auto_schema(
    method="post",
    operation_description="Cria uma nova prova",
    manual_parameters=[
        openapi.Parameter(
            "titulo", openapi.IN_FORM, type=openapi.TYPE_STRING, required=True
        ),
        openapi.Parameter(
            "data",
            openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            required=True,
        ),
        openapi.Parameter(
            "foto", openapi.IN_FORM, type=openapi.TYPE_FILE, required=False
        ),
        openapi.Parameter(
            "descricao", openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
        ),
    ],
    tags=["Provas"],
    responses={201: ProvaSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def prova_create(request):
    serializer = ProvaSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=["GET"],
    operation_description="Retorna os detalhes de uma prova específica",
    tags=["Provas"],
    responses={200: ProvaSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def prova_detail(request, pk):
    try:
        prova = Prova.objects.get(pk=pk, usuario=request.user)
    except Prova.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ProvaSerializer(prova, context={"request": request})
    return Response(serializer.data)


@swagger_auto_schema(
    methods=["PUT", "PATCH"],
    operation_description="Atualiza uma prova existente",
    manual_parameters=[
        openapi.Parameter(
            "titulo", openapi.IN_FORM, type=openapi.TYPE_STRING, required=True
        ),
        openapi.Parameter(
            "data",
            openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            required=True,
        ),
        openapi.Parameter(
            "foto", openapi.IN_FORM, type=openapi.TYPE_FILE, required=False
        ),
        openapi.Parameter(
            "descricao", openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
        ),
    ],
    tags=["Provas"],
    responses={200: ProvaSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def prova_update(request, pk):
    try:
        prova = Prova.objects.get(pk=pk, usuario=request.user)
    except Prova.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ProvaSerializer(
        prova,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request},
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=["DELETE"],
    operation_description="Deleta uma prova",
    tags=["Provas"],
    responses={204: "No Content"},
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def prova_delete(request, pk):
    try:
        prova = Prova.objects.get(pk=pk, usuario=request.user)
    except Prova.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    prova.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# endregion


# region Avaliações
@swagger_auto_schema(
    methods=["GET"],
    operation_description="Lista avaliações do usuário autenticado, com filtros por tema",
    tags=["Avaliações"],
    responses={200: AvaliacaoSerializer(many=True)},
    manual_parameters=[
        openapi.Parameter(
            "tema",
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="Filtrar por tema (e.g., Matemática)",
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def avaliacao_list(request):
    queryset = Avaliacao.objects.filter(user=request.user).select_related("conteudo")
    tema = request.query_params.get("tema")
    if tema:
        queryset = queryset.filter(conteudo__tema=tema)
    queryset = queryset.order_by("-data_avaliacao")
    serializer = AvaliacaoSerializer(queryset, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    methods=["GET"],
    operation_description="Retorna detalhes de uma avaliação",
    tags=["Avaliações"],
    responses={200: AvaliacaoSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def avaliacao_detail(request, pk):
    try:
        if request.user.is_staff:
            avaliacao = Avaliacao.objects.get(pk=pk)
        else:
            avaliacao = Avaliacao.objects.get(pk=pk, user=request.user)
        serializer = AvaliacaoSerializer(avaliacao)
        return Response(serializer.data)
    except Avaliacao.DoesNotExist:
        return Response(
            {"detail": "Avaliação não encontrada"}, status=status.HTTP_404_NOT_FOUND
        )


@swagger_auto_schema(
    methods=["POST"],
    operation_description="Cria uma nova avaliação para um conteúdo",
    request_body=AvaliacaoSerializer,
    tags=["Avaliações"],
    responses={201: AvaliacaoSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def avaliacao_create(request):
    serializer = AvaliacaoSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=["PUT", "PATCH"],
    operation_description="Atualiza uma avaliação",
    request_body=AvaliacaoSerializer,
    tags=["Avaliações"],
    responses={200: AvaliacaoSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def avaliacao_update(request, pk):
    try:
        if request.user.is_staff:
            avaliacao = Avaliacao.objects.get(pk=pk)
        else:
            avaliacao = Avaliacao.objects.get(pk=pk, user=request.user)
        serializer = AvaliacaoSerializer(
            avaliacao, data=request.data, partial=request.method == "PATCH"
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Avaliacao.DoesNotExist:
        return Response(
            {"detail": "Avaliação não encontrada"}, status=status.HTTP_404_NOT_FOUND
        )


@swagger_auto_schema(
    methods=["DELETE"],
    operation_description="Deleta uma avaliação",
    tags=["Avaliações"],
    responses={204: "No Content"},
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def avaliacao_delete(request, pk):
    try:
        if request.user.is_staff:
            avaliacao = Avaliacao.objects.get(pk=pk)
        else:
            avaliacao = Avaliacao.objects.get(pk=pk, user=request.user)
        avaliacao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Avaliacao.DoesNotExist:
        return Response(
            {"detail": "Avaliação não encontrada"}, status=status.HTTP_404_NOT_FOUND
        )


# endregion
