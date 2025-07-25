from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conteudo, Avaliacao, PerfilUsuario, Prova
from rest_framework_simplejwt.tokens import RefreshToken
import re
from django.contrib.auth import authenticate
class UserSerializer(serializers.ModelSerializer):
    pref_visual = serializers.BooleanField(source='perfilusuario.pref_visual', read_only=True)
    pref_auditivo = serializers.BooleanField(source='perfilusuario.pref_auditivo', read_only=True)
    pref_leitura_escrita = serializers.BooleanField(source='perfilusuario.pref_leitura_escrita', read_only=True)
    serie_atual = serializers.CharField(source='perfilusuario.serie_atual', read_only=True)
    foto_perfil = serializers.ImageField(source='perfilusuario.fotoPerfil')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'pref_visual', 'pref_auditivo', 'pref_leitura_escrita', 'serie_atual', 'foto_perfil']
        read_only_fields = ['is_staff']  # Apenas admin pode alterar

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            raise serializers.ValidationError("Email e senha obrigatórios.")
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("Email ou senha incorretos.")
        if not user.is_active:
            raise serializers.ValidationError("Conta desativada.")
        authenticated_user = authenticate(username=user.username,password=password)
        if not authenticated_user:
            raise serializers.ValidationError("Email ou senha incorretos.")
        refresh = RefreshToken.for_user(authenticated_user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            'invalid': 'Insira um email válido, como exemplo@dominio.com',
            'blank': 'O email não pode estar em branco.',
            'required': 'O email é obrigatório.'
        }
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            'blank': 'A senha não pode estar em branco.',
            'required': 'A senha é obrigatória.',
            'min_length': 'A senha deve ter pelo menos 8 caracteres.'
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está cadastrado.")
        if '@' not in value or '.' not in value.split('@')[-1]:
            raise serializers.ValidationError("Insira um email válido, como exemplo@dominio.com")
        return value

    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra minúscula.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um número.")
        return value

    def create(self, validated_data):

        # Cria o usuário
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        user.set_password(validated_data['password'])
        user.save()

        # Cria o perfil do usuário
        PerfilUsuario.objects.create(user=user)

        return user

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PerfilUsuario
        fields = ['user', 'pref_visual', 'pref_auditivo', 'pref_leitura_escrita']

    def create(self, validated_data):
        # Vincula ao usuário logado
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class PerfilUsuarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ['pref_visual', 'pref_auditivo', 'pref_leitura_escrita']

class ConteudoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conteudo
        fields = ['id', 'titulo', 'tipo', 'tema', 'url', 'duracao_estimada', 'data_criacao']
        read_only_fields = ['data_criacao']

class AvaliacaoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    conteudo = ConteudoSerializer(read_only=True)
    conteudo_id = serializers.PrimaryKeyRelatedField(
        queryset=Conteudo.objects.all(), source='conteudo', write_only=True
    )

    class Meta:
        model = Avaliacao
        fields = ['id', 'user', 'conteudo', 'conteudo_id', 'nota', 'comentario', 'data_avaliacao']
        read_only_fields = ['user', 'data_avaliacao']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            'blank': 'O email não pode estar em branco.',
            'required': 'O email é obrigatório.',
            'invalid': 'Insira um email válido, como exemplo@dominio.com'
        }
    )

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email não encontrado.")
        return value
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            'blank': 'A senha não pode estar em branco.',
            'required': 'A senha é obrigatória.',
            'min_length': 'A senha deve ter pelo menos 8 caracteres.'
        }
    )
    code = serializers.CharField(
        write_only=True,
        min_length=6,
        max_length=6,
        error_messages={
            'blank': 'O código não pode estar em branco.',
            'required': 'O código é obrigatório.',
            'min_length': 'O código deve ter pelo menos 6 caracteres.',
            'max_length': 'O código deve ter no máximo 6 caracteres.'
        }
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'blank': 'O email não pode estar em branco.',
            'required': 'O email é obrigatório.',
            'invalid': 'Insira um email válido, como exemplo@dominio.com'
        }
    )
    def validate_new_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra minúscula.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um número.")
        return value

class CodeVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(
        write_only=True,
        min_length=6,
        max_length=6,
        error_messages={
            'blank': 'O código não pode estar em branco.',
            'required': 'O código é obrigatório.',
            'min_length': 'O código deve ter pelo menos 6 caracteres.',
            'max_length': 'O código deve ter no máximo 6 caracteres.'
        }
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'blank': 'O email não pode estar em branco.',
            'required': 'O email é obrigatório.',
            'invalid': 'Insira um email válido, como exemplo@dominio.com'
        }
    )

class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        error_messages={
            'invalid': 'Insira um email válido, como exemplo@dominio.com',
            'blank': 'O email não pode estar em branco.'
        }
    )
    pref_visual = serializers.BooleanField(required=False)
    pref_auditivo = serializers.BooleanField(required=False)
    pref_leitura_escrita = serializers.BooleanField(required=False)
    foto_perfil = serializers.ImageField(
        source='perfilusuario.fotoPerfil',
        required=False,
        allow_null=True,
        error_messages={
            'invalid': 'Formato de imagem inválido. Use JPG, PNG ou GIF.',
        }
    )
    serie_atual = serializers.CharField(
        source='perfilusuario.serie_atual',
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'pref_visual', 'pref_auditivo', 'pref_leitura_escrita', 'foto_perfil', 'serie_atual']
        extra_kwargs = {
            'email': {'required': False},
            'username': {'required': False}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Este email já está cadastrado.")
        if '@' not in value or '.' not in value.split('@')[-1]:
            raise serializers.ValidationError("Insira um email válido, como exemplo@dominio.com")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value

    def update(self, instance, validated_data):
        # Extrai dados do perfil se existirem
        perfil_data = validated_data.pop('perfilusuario', {})

        # Atualiza o usuário
        user = super().update(instance, validated_data)

        # Atualiza o perfil se houver dados
        if perfil_data:
            try:
                perfil = user.perfilusuario
                # Se for enviada uma nova foto, exclui a antiga
                if 'fotoPerfil' in perfil_data and perfil.fotoPerfil:
                    nova_foto = perfil_data.get('fotoPerfil')
                    if nova_foto and hasattr(perfil.fotoPerfil, 'path') and perfil.fotoPerfil.path != nova_foto:
                        perfil.fotoPerfil.delete(save=False)
                for key, value in perfil_data.items():
                    if value is not None:
                        setattr(perfil, key, value)
                perfil.save()
            except PerfilUsuario.DoesNotExist:
                # Se o perfil não existe, cria um novo
                PerfilUsuario.objects.create(user=user, **perfil_data)

        return user

class ProvaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prova
        fields = ['id','titulo', 'data', 'foto', 'descricao', 'criado_em']
        read_only_fields = ['criado_em']

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)

