# 💼 Portal de Vagas Inteligente - LabBD

Projeto desenvolvido para a disciplina de Laboratório de Banco de Dados.
O sistema é um portal completo de recrutamento que conecta candidatos e empresas, utilizando **MongoDB Atlas** na nuvem e algoritmos de busca para facilitar o "match" entre currículos e vagas.

## 👥 Integrantes do Grupo
* **Angelo Mesquita Higgins Azevedo dos Santos**
* **Eugênio Mesquita Higgins Azevedo dos Santos**
* **Henrique de Oliveira Gomes Sanches**
* **Vitor Rolisola**

## 🛠 Tecnologias e Arquitetura

* **Frontend & Backend:** [Streamlit](https://streamlit.io/) (Python)
* **Banco de Dados:** [MongoDB Atlas](https://www.mongodb.com/atlas) (NoSQL/Documentos)
* **Visualização de Dados:** Plotly & Pandas
* **Hospedagem (Deploy):** Streamlit Cloud

## ⚙️ Funcionalidades Implementadas

### 1. 👤 Para Candidatos
* **Cadastro de Currículo:** Formulário completo salvando dados estruturados no MongoDB.
* **Aplicação:** Visualização de vagas e botão de candidatura.

### 2. 🏢 Para Empregadores
* **Gestão de Vagas:** Cadastro de novas oportunidades com requisitos, salário e local.
* **Banco de Vagas:** Visualização e atualização das vagas publicadas.

### 3. ⚙️ Perfil Administrador
* **Login Seguro:** Acesso restrito via autenticação.
* **Dashboard Gerencial:** Gráficos interativos (Plotly) mostrando distribuição de vagas.
* **Visão Global:** Tabelas completas de todos os candidatos e vagas cadastrados no sistema.

### 4. 🤖 Busca Inteligente (Diferencial)
* **Sistema de Busca:** Implementação de lógica de busca por palavras-chave (Keyword Search) que simula um RAG (Retrieval-Augmented Generation).
* **Flexibilidade:** Permite alternar a busca entre "Vagas" e "Candidatos".

## 🧠 Matching e Algoritmo de Busca (Full Text Search)

Para atender ao requisito de matching automático entre candidatos e vagas, utilizamos o recurso nativo de **Text Indexes** do MongoDB.

**Como funciona o Score:**
1. Criamos índices de texto nos campos principais (`skills`, `titulo`, `requisitos`, `descricao`).
2. As consultas utilizam o operador `$text` e `$search`.
3. O MongoDB calcula automaticamente um **Score de Relevância** (`$meta: "textScore"`) para cada documento.
4. Os resultados são apresentados ordenados do maior score para o menor, garantindo que os resultados mais pertinentes apareçam no topo.

**Login e senha do administrador**

Login: admin
Senha: 123

**Código da Query (Exemplo):**
````python
db.collection.find(
    {"$text": {"$search": "python sql"}},
    {"score": {"$meta": "textScore"}}
).sort([("score", {"$meta": "textScore"})])