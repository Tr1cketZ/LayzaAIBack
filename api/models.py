# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    pref_visual = models.BooleanField(default=False)
    pref_auditivo = models.BooleanField(default=False)
    pref_leitura_escrita = models.BooleanField(default=False)

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Conteudo(models.Model):
    TIPO_CHOICES = [
        ('Vídeo', 'Vídeo'),
        ('Texto', 'Texto'),
        ('Áudio', 'Áudio'),
    ]
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    tema = models.CharField(max_length=100)
    url = models.URLField()
    duracao_estimada = models.IntegerField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Avaliacao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conteudo = models.ForeignKey(Conteudo, on_delete=models.CASCADE)
    nota = models.CharField(max_length=10)
    comentario = models.TextField(null=True, blank=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação de {self.user.username} para {self.conteudo.titulo}"

class Progresso(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conteudo = models.ForeignKey(Conteudo, on_delete=models.CASCADE)
    concluido = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    desempenho = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Progresso de {self.user.username} em {self.conteudo.titulo}"

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at

    def __str__(self):
        return f"Token para {self.user.email}"