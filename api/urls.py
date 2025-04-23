from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('password-reset/', views.password_reset_request,name="password_reset_request"),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),

    path('me/', views.me),
    path('profile/', views.perfil_detail, name='perfil-detail'),
    path('profile/update/', views.perfil_update, name='perfil-update'),

    # Endpoints de Conteúdos
    path('conteudos/', views.conteudo_list, name='conteudo-list'),
    path('conteudos/create/', views.conteudo_create, name='conteudo-create'),
    path('conteudos/<int:pk>/', views.conteudo_detail, name='conteudo-detail'),
    path('conteudos/<int:pk>/update/', views.conteudo_update, name='conteudo-update'),
    path('conteudos/<int:pk>/delete/', views.conteudo_delete, name='conteudo-delete'),
    # Faltam endpoints para:
    # - Listar/atualizar/deletar usuários (admin)
    # - CRUD completo de avaliações
    # - CRUD completo de progresso
    # - CRUD completo de provas
]