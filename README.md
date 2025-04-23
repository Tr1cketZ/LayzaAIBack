# LayzaAI Backend

Backend da aplicação LayzaAI, um sistema de aprendizado personalizado para alunos do ensino médio.

## 📋 Descrição

O LayzaAI é um aplicativo móvel integrado com Inteligência Artificial para otimizar os estudos dos alunos do ensino médio. Este repositório contém o backend da aplicação, desenvolvido em Django e Django REST Framework.

## 🚀 Funcionalidades

- **Autenticação e Autorização**
  - Cadastro de usuários
  - Login com JWT
  - Recuperação de senha
  - Controle de acesso baseado em cargos

- **Perfis de Aprendizagem**
  - Preferências de aprendizado (visual, auditivo, leitura/escrita)
  - Personalização de perfil
  - Progresso individual

- **Conteúdos Educacionais**
  - CRUD de conteúdos (vídeos, textos, áudios)
  - Categorização por tema e tipo
  - Avaliação de conteúdos
  - Registro de progresso

- **Integração com IA**
  - API para comunicação com serviço de IA
  - Análise de perfil de aprendizado
  - Recomendações personalizadas

## 🛠️ Tecnologias

- Python 3.x
- Django 4.x
- Django REST Framework
- Django REST Framework SimpleJWT
- SQLite (desenvolvimento)
- PostgreSQL (produção)

## ⚙️ Requisitos

- Python 3.x
- pip
- virtualenv (recomendado)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/layza-ai-back.git
cd layza-ai-back
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Execute as migrações:
```bash
python manage.py migrate
```

6. Crie um superusuário:
```bash
python manage.py createsuperuser
```

7. Inicie o servidor:
```bash
python manage.py runserver
```

## 📚 Documentação da API

A documentação da API está disponível em `/swagger/` quando o servidor estiver rodando.

### Endpoints Principais

#### Autenticação ✅ Implementado
- `POST /api/auth/register/` - Cadastro de usuário
- `POST /api/auth/login/` - Login
- `POST /api/auth/password-reset/` - Recuperação de senha

#### Perfil ⚠️ Parcialmente Implementado
- `GET /api/profile/` - Visualizar perfil
- `PUT /api/profile/` - Atualizar preferências

#### Conteúdos ❌ Não Implementado
- `GET /api/contents/` - Listar conteúdos
- `POST /api/contents/` - Criar conteúdo (admin)
- `GET /api/contents/<id>/` - Detalhes do conteúdo
- `PUT /api/contents/<id>/` - Atualizar conteúdo (admin)
- `DELETE /api/contents/<id>/` - Deletar conteúdo (admin)

#### Avaliações ❌ Não Implementado
- `GET /api/ratings/` - Listar avaliações
- `POST /api/ratings/` - Criar avaliação
- `GET /api/ratings/<id>/` - Detalhes da avaliação
- `PUT /api/ratings/<id>/` - Atualizar avaliação
- `DELETE /api/ratings/<id>/` - Deletar avaliação

#### Progresso ❌ Não Implementado
- `GET /api/progress/` - Listar progresso
- `POST /api/progress/` - Registrar progresso
- `GET /api/progress/<id>/` - Detalhes do progresso
- `PUT /api/progress/<id>/` - Atualizar progresso

#### Prova ❌ Não Implementado
- `GET /api/provas/` - Listar provas
- `POST /api/provas/` - Criar prova
- `GET /api/provas/<id>/` - Detalhes da prova
- `PUT /api/provas/<id>/` - Atualizar prova
- `DELETE /api/provas/<id>/` - Deletar prova

#### Integração com IA ❌ Não Implementado
- `POST /api/ia/recomendacoes/` - Receber recomendações
- `POST /api/ia/analise/` - Enviar dados para análise
- `GET /api/ia/perfil/` - Obter análise do perfil

## 🔒 Segurança

- Autenticação via JWT
- Validação de senha forte
- Proteção contra ataques comuns
- Criptografia de dados sensíveis

## 📊 Estrutura do Projeto

```
layza-ai-back/
├── api/                    # Aplicação principal
│   ├── migrations/         # Migrações do banco de dados
│   ├── models.py          # Modelos do Django
│   ├── serializers.py     # Serializers da API
│   ├── views.py           # Views da API
│   └── urls.py            # URLs da API
├── config/                # Configurações do projeto
│   ├── settings.py        # Configurações
│   ├── urls.py           # URLs do projeto
│   └── wsgi.py           # WSGI config
├── requirements.txt       # Dependências
└── manage.py             # Script de gerenciamento
```

## 🧪 Testes

❌ Ainda não implementado. O plano de testes inclui:

- Testes unitários para modelos
- Testes de API para endpoints
- Testes de integração
- Testes de autenticação
- Testes de permissões

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- Aline Couto de Souza
- Bruno Martins de Abreu
- Riverton de Carvalho Oliveira
- Victor Behr Pereira Mendes

## 🙏 Agradecimentos

- Professores orientadores
- Faculdade Senac Palhoça
- Todos os contribuidores 