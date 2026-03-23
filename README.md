# CineReserve API 🍿

Uma API RESTful robusta desenvolvida com Django REST Framework para gerenciamento e reserva de ingressos de cinema. O sistema foi desenhado para lidar com cenários reais e complexos, como concorrência na reserva de assentos, transações seguras, tarefas assíncronas em background e limites de taxa de requisições.

---

## 🚀 Principais Funcionalidades

Este projeto implementa 7 casos de uso principais solicitados na construção do sistema:

1. **Autenticação e Usuários**: Gerenciamento de acessos seguros.
2. **Filmes e Gêneros**: Listagem e organização do catálogo do cinema.
3. **Salas e Sessões (Showtimes)**: Mapeamento de exibições baseadas em horários e salas (Theaters).
4. **Visualização do Mapa de Assentos (`CASE 4`)**: Endpoint para listar os assentos e seus respectivos status de ocupação (Livre, Reservado, Comprado) para uma sessão em tempo real.
5. **Bloqueio e Reserva Temporária (`CASE 5`)**: Utilização do Redis para _Distributed Locking_, prevenindo condições de corrida (Race Conditions) ao tentar reservar o mesmo assento. Os bloqueios expiram nativamente ou através de workers.
6. **Checkout Transacional e Geração de Bilhetes (`CASE 6`)**: Processo seguro que consolida a transação envolvendo o banco de dados (atomicidade), remove o _lock_ do Redis, gera os registros de `Order` e `Ticket`, e dispara o envio de e-mails em _background_.
7. **Portal "Meus Ingressos" (`CASE 7`)**: Histórico de compras com filtros integrados e paginação para o usuário final otimizado no banco de dados.

### 🛡️ Proteções Adicionais

- **Filas e Assincronismo**: Funcionalidades assíncronas operadas via **Celery** (Liberação caduca de assentos e envio de Confirmação de pedidos por e-mail).
- **Rate Limiting (Throttling)**: Endpoints críticos (como Checkout e Reserva de Assentos) contam com proteções contra abusos em rajada (bursts), scrapers e scalpers usando as classes do DRF e cache.
- **Seed do Banco**: Script acionado via `manage.py seed` para provisionamento rápido de um ambiente de desenvolvimento limpo com fakes e simulações completas.
- **Testes (Unitários & Integração)**: Cobertura extensiva fazendo mocks das chamadas Redis e dos serviços Celery (via APIClient e mock patchs).
- **CI/CD Automatizado**: Workflow do GitHub Actions para testar cada comitês com containers _postgres_ e _redis_.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Framework Web:** Django & Django REST Framework (DRF)
- **Banco de Dados:** PostgreSQL
- **Cache, Filas & Locks:** Redis
- **Background Tasks:** Celery e Celery Beat
- **Gerenciador de Pacotes:** Poetry
- **Orquestração de Containers:** Docker & Docker Compose
- **Outros:** Flower (para monitoramento do Celery)

---

## ⚙️ Como Executar o Projeto Localmente

A melhor e mais robusta maneira de rodar o cenário em ambiente de desenvolvimento é utilizar o Docker Compose configurado no repositório.

### 📌 Pré-Requisitos

- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 🚀 Subindo a aplicação com Docker

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/pedrohcdsouza/CineReserve-API.git
   cd CineReserve-API
   ```

2. **Copie as variáveis de ambiente:**
   Se certifique de ter um arquivo `.env` na raiz do projeto contendo as declarações exigidas pelo `docker-compose.yml`. Você pode criá-lo:

   ```env
   # Exemplo do arquivo .env
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=cinereserve_db
   DB_PORT=5432
   ```

3. **Construa e inicie os containers:**
   O `docker-compose` irá inicializar o Banco de Dados, o Redis, o Backend (API), os Celery Workers, Celery Beat e o Flower de monitoramento:

   ```bash
   docker-compose up --build
   ```

   > Observação: O contêiner de `backend` já possui em seu comando padrão de inicialização a execução do `migrate` automático.

4. **Popule o Banco de Dados (Seed Inicial):**
   Com os containeres rodando, numa nova aba do terminal e crie dados fake para testes:
   ```bash
   docker-compose exec backend poetry run python src/manage.py seed
   ```
   Serão recriados filmes, cinemas, usuários e exibições.

### 🌐 Serviços Disponíveis no final do processo

- **API Web (Backend):** `http://localhost:8000/`
- **Painel Celery Flower (Monitoramento de Tarefas):** `http://localhost:5555/`

---

## 🧪 Como Rodar as Suítes de Testes

Os testes são configurados para cobrir cenários normais e isolados usando mocks para dependências externas. Para executá-los em seu ambiente virtual do Poetry ou via contêiner do Docker:

**Pelo Docker:**

```bash
docker-compose exec backend poetry run python src/manage.py test accounts movie showtime order
```

**Rodando fora do docker (Requer Poetry instalado):**
Certifique-se que o Redis local e o Postgres estejam respondendo nas portas definidas nas suas variáveis de ambiente de teste.

```bash
poetry run python src/manage.py test
```

---

## 📚 Estrutura da API / Apps Principais

A api está dividida de forma limpa em apps do django:

1. `accounts/`: Autenticações e Usuário;
2. `movie/`: Modelagem de Filmes (Movies) e Cinemas (Theaters);
3. `showtime/`: Responsável pelas sessões, mapeamento do status dos assentos via agregação/redis (`CASE 4`) e processamento das reservas (`CASE 5`);
4. `order/`: Processamento seguro do carrinho/checkout (`CASE 6`) e da visualização de compras passadas do usuário (`CASE 7`);
5. `core/`: Configurações centralizadas, settings de Celery, etc;
6. `base/`: Utilitários gerais e o comando de seed (`seed.py`).
