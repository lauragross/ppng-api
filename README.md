# ppng-api

API Flask para cálculo e análise da Provisão de Prêmios Não Ganhos (PPNG) de contratos de resseguro. Desenvolvida como parte do MVP do curso de Desenvolvimento Full Stack Básico da PUC-Rio.

---

## Objetivo

Automatizar o cálculo da PPNG com base em dados de emissão de contratos de resseguro, armazenar os resultados em banco de dados SQLite, permitir análise via HTML e integração com uma interface SPA (front-end).

---

## Funcionalidades

- Definição da data base para o cálculo da PPNG
- Cálculo da PPNG e variação cambial da PPNG
- Armazenamento da base completa
- Análise dos resultados via página HTML renderizada pela API
- Barra de progresso atualizada dinamicamente
- Documentação interativa via Swagger

---

## Tecnologias utilizadas

- Python 3.x
- Flask
- Flasgger (Swagger)
- SQLite
- Pandas
- JSON / HTML

---

## Estrutura do projeto

```
ppng-api/
├── app.py                    # Script principal com as rotas Flask
├── database.py              # Importação da base Parquet
├── models.py                # Funções de cálculo da PPNG
├── utils.py                 # Funções auxiliares (progresso, data)
├── ppng_progresso.json      # Controle da barra de progresso
├── data_base.txt            # Armazena a data base do cálculo
├── requirements.txt         # Lista de dependências
├── templates/
│   └── analise_ppng.html    # Página HTML com a análise da PPNG
├── ppng-api.db              # Banco de dados SQLite
```

---

## Como instalar e rodar a API

### 1. Clone o repositório:

```bash
git clone https://github.com/lauragross/ppng-api.git
cd ppng-api
```

### 2. Crie e ative o ambiente virtual (opcional, recomendado):

```bash
python -m venv venv
.venv\Scripts\Activate.ps1        # PowerShell
# ou
venv\Scripts\activate.bat        # CMD
```

### 3. Instale as dependências:

```bash
pip install -r requirements.txt
```

### 4. Inicie a API:

```bash
python app.py
```

### 5. Acesse a documentação no navegador:

```
http://127.0.0.1:5000/apidocs/
```

---

## Integração com o front-end

A API foi projetada para ser consumida pela SPA contida no repositório [ppng-frontend](https://github.com/seu_usuario/ppng-frontend). O front consome as rotas via `fetch()`.

---

## Desenvolvido por

Laura Gross Lorenzi  
PUC-Rio • MVP - Desenvolvimento Full Stack Básico