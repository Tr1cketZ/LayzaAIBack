from django.urls import path

from . import views

urlpatterns = [
    # Endpoints de Autenticação
    path('register/', views.register),
    path('login/', views.login),
    path('password-reset/', views.password_reset_request,name="password_reset_request"),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/verify-code/', views.password_reset_verify_code, name='password_reset_verify_code'),

    # Endpoints de Perfil
    path('perfil/', views.me, name='perfil-completo'),
    path('perfil/update/', views.perfil_update_completo, name='perfil-update'),
    path('perfil/delete/', views.perfil_delete, name='perfil-delete'),

    # Endpoints de Conteúdos
    path('conteudos/', views.conteudo_list, name='conteudo-list'),
    path('conteudos/create/', views.conteudo_create, name='conteudo-create'),
    path('conteudos/<int:pk>/', views.conteudo_detail, name='conteudo-detail'),
    path('conteudos/<int:pk>/update/', views.conteudo_update, name='conteudo-update'),
    path('conteudos/<int:pk>/delete/', views.conteudo_delete, name='conteudo-delete'),

    # Endpoints de Provas
    path('provas/', views.prova_list, name='prova-list'),
    path('provas/create/', views.prova_create, name='prova-create'),
    path('provas/<int:pk>/', views.prova_detail, name='prova-detail'),
    path('provas/<int:pk>/update/', views.prova_update, name='prova-update'),
    path('provas/<int:pk>/delete/', views.prova_delete, name='prova-delete'),

    # Endpoints de Avaliações
    path('avaliacoes/', views.avaliacao_list, name='avaliacao-list'),
    path('avaliacoes/create/', views.avaliacao_create, name='avaliacao-create'),
    path('avaliacoes/<int:pk>/', views.avaliacao_detail, name='avaliacao-detail'),
    path('avaliacoes/<int:pk>/update/', views.avaliacao_update, name='avaliacao-update'),
    path('avaliacoes/<int:pk>/delete/', views.avaliacao_delete, name='avaliacao-delete'),

    # Faltam endpoints para:
    # - CRUD completo de avaliações
]