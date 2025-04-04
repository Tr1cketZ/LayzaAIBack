from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conteudo, Progresso, Avaliacao, PerfilUsuario, PasswordResetToken	
import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['is_staff']  # Apenas admin pode alterar

class UserCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
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
        fields = ['email', 'password', 'first_name', 'last_name']
    def validate_password(self, value):
            if not re.search(r'[A-Z]', value):
                raise serializers.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
            if not re.search(r'[a-z]', value):
                raise serializers.ValidationError("A senha deve conter pelo menos uma letra minúscula.")
            if not re.search(r'[0-9]', value):
                raise serializers.ValidationError("A senha deve conter pelo menos um número.")
            return value
    def create(self, validated_data):
        if not validated_data['email']:
            raise serializers.ValidationError('O campo email é obrigatório.')
        username = validated_data['first_name']+"."+validated_data['last_name']
        base_username = username.lower()
        counter = 1
        if User.objects.filter(username=username.lower()).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user = User.objects.create_user(
            username=username.lower(),
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
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

class ProgressoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    conteudo = ConteudoSerializer(read_only=True)
    conteudo_id = serializers.PrimaryKeyRelatedField(
        queryset=Conteudo.objects.all(), source='conteudo', write_only=True
    )

    class Meta:
        model = Progresso
        fields = ['id', 'user', 'conteudo', 'conteudo_id', 'concluido', 'data_conclusao', 'desempenho']
        read_only_fields = ['user']

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
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            'required': 'A senha é obrigatória.',
            'min_length': 'A senha deve ter pelo menos 8 caracteres.'
        }
    )

    def validate_password(self, value):
        # Validar a senha conforme RF03
        if not (re.search(r'[A-Z]', value) and 
                re.search(r'[a-z]', value) and 
                re.search(r'[0-9]', value)):
            raise serializers.ValidationError(
                "A senha deve ter pelo menos 8 caracteres, com uma letra maiúscula, uma minúscula e um número."
            )
        return value
    
