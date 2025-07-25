# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import os

class PerfilUsuario(models.Model):
    SERIE_CHOICES = [
        ('1º Ano', '1º Ano'),
        ('2º Ano', '2º Ano'),
        ('3º Ano', '3º Ano'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    pref_visual = models.BooleanField(default=False)
    pref_auditivo = models.BooleanField(default=False)
    pref_leitura_escrita = models.BooleanField(default=False)
    serie_atual = models.CharField(max_length=10, choices=SERIE_CHOICES, blank=True, null=True)
    fotoPerfil = models.ImageField(upload_to='images/fotos_perfil/', null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Conteudo(models.Model):
    TIPO_CHOICES = [
        ('Vídeo', 'Vídeo'),
        ('Texto', 'Texto'),
        ('Áudio', 'Áudio'),
    ]
    TEMA_CHOICES = [
        ('Matemática', 'Matemática'),
        ('Português', 'Português'),
        ('História', 'História'),
        ('Geografia', 'Geografia'),
        ('Inglês', 'Inglês'),
    ]
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    tema = models.CharField(max_length=100, choices=TEMA_CHOICES)
    url = models.URLField()
    duracao_estimada = models.IntegerField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo
    
class Prova(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    data = models.DateField()
    foto = models.ImageField(upload_to='images/provas/', null=True, blank=True)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
    def delete(self, *args, **kwargs):
        if self.foto and os.path.exists(self.foto.path):
            os.remove(self.foto.path)
        super().delete(*args, **kwargs)
    
class Avaliacao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conteudo = models.ForeignKey(Conteudo, on_delete=models.CASCADE)
    nota = models.CharField(max_length=10,blank=True)
    comentario = models.TextField(null=True, blank=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação de {self.user.username} para {self.conteudo.titulo}"

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True, default=00000)
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