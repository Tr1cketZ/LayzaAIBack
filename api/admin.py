from django.contrib import admin
from .models import Conteudo, Progresso, Avaliacao, PerfilUsuario
# Register your models here.
@admin.register(Conteudo)
class ConteudoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'tema', 'duracao_estimada', 'data_criacao', 'is_active')
    list_filter = ('tipo', 'tema', 'is_active')
    list_editable = ('is_active',)

@admin.register(Progresso)
class ProgressoAdmin(admin.ModelAdmin):
    list_display = ('user', 'conteudo', 'concluido', 'data_conclusao', 'desempenho')

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('user', 'conteudo', 'nota', 'comentario', 'data_avaliacao')

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'pref_visual', 'pref_auditivo', 'pref_leitura_escrita')