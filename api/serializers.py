from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conteudo, Progresso, Avaliacao, PerfilUsuario

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['is_staff']  # Apenas admin pode alterar

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        if not validated_data['email']:
            raise serializers.ValidationError('O campo email é obrigatório.')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
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