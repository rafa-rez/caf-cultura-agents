# Visão Arquitetônica Inicial - RAG-Café (Pré-Modelagem de Ameaças)

Este documento descreve a arquitetura inicial do sistema **RAG-Café**, focando no fluxo de dados e na interação entre os componentes, *antes* da implementação de medidas de segurança.

---

## 1. Diagrama de Fluxo de Dados (DFD) - Nível 1

O diagrama abaixo ilustra os principais processos, fluxos de dados e armazenamentos do sistema.

```mermaid
graph TD
    %% Entidades Externas
    E_USUARIO[E1: Produtor/Usuário]

    %% Processos (Microserviços)
    subgraph "Limite de Confiança: Rede Local"
        P1_GATEWAY[P1: API Gateway]
        P2_AGENTE_CLF[P2: Agente Classificador (Local/Docker)]
        P3_AGENTE_RAG[P3: Agente Gerador RAG (Local/Docker)]
    end

    %% Armazenamento de Dados
    D1_VECTOR_STORE[D1: Banco de Dados Vetorial (Ex: ChromaDB)]
    D2_LLM_MODEL[D2: Modelo LLM Local (Ex: TinyLlama)]
    D3_CLF_MODEL[D3: Modelo Classificador Local (Ex: BERT-tiny)]

    %% Armazenamento (Comunicação A2A)
    D4_BROKER[D4: Message Broker (RabbitMQ)]

    %% Fluxos de Dados
    E_USUARIO -- 1. Pergunta (JSON) --> P1_GATEWAY
    P1_GATEWAY -- 2. Pergunta Bruta --> P2_AGENTE_CLF
    P2_AGENTE_CLF -- 3. Carrega Modelo --> D3_CLF_MODEL
    P2_AGENTE_CLF -- 4. Pergunta Classificada (Intenção + Entidades) --> D4_BROKER
    
    D4_BROKER -- 5. Evento (Pergunta Classificada) --> P3_AGENTE_RAG
    P3_AGENTE_RAG -- 6. Busca (Embeddings) --> D1_VECTOR_STORE
    D1_VECTOR_STORE -- 7. Contexto (Artigos Relevantes) --> P3_AGENTE_RAG
    P3_AGENTE_RAG -- 8. Carrega Modelo --> D2_LLM_MODEL
    P3_AGENTE_RAG -- 9. (Contexto + Pergunta) --> D2_LLM_MODEL
    D2_LLM_MODEL -- 10. Resposta Gerada --> P3_AGENTE_RAG
    
    P3_AGENTE_RAG -- 11. Resposta Final (JSON) --> P1_GATEWAY
    P1_GATEWAY -- 12. Resposta Final --> E_USUARIO
```

---

## 2. Descrição dos Componentes e Fluxos

### 2.1. Entidades Externas
**[E1] Produtor/Usuário:**  
Cliente que consome o sistema (pode ser um app frontend, Postman, etc.).

---

### 2.2. Processos (Microserviços)

**[P1] API Gateway (FastAPI):**  
- Ponto de entrada único do sistema *(Requisito API - 3 pts)*.  
- Recebe a pergunta do usuário (Fluxo 1).  
- Encaminha para o Agente Classificador (Fluxo 2).  
- Aguarda a resposta final (Fluxo 11) e a retorna ao usuário (Fluxo 12).

**[P2] Agente Classificador (FastAPI + Docker):**  
- Identifica a intenção do usuário *(Requisito IA Local/Docker - 7 pts)*.  
- Carrega o modelo local (Fluxo 3) para análise da pergunta.  
- Exemplo: “Como combater a broca-do-café?” → Intenção: *manejo_praga*, Entidade: *broca-do-café*.  
- Publica a pergunta enriquecida no Message Broker (Fluxo 4).

**[P3] Agente Gerador RAG (Python Worker + Docker):**  
- Responsável por gerar a resposta *(Requisito Mínimo 2 Agentes IA - 3 pts)*.  
- Consome a mensagem do Broker (Fluxo 5).  
- **RAG - Retrieval:** Busca documentos relevantes no Banco Vetorial (Fluxos 6, 7).  
- **RAG - Generation:** Monta o prompt (Contexto + Pergunta) e utiliza o LLM local (Fluxos 8, 9, 10).  
- Envia a resposta final de volta ao Gateway (Fluxo 11).

---

### 2.3. Armazenamento de Dados (Data Stores)

**[D1] Banco de Dados Vetorial (ChromaDB):**  
Armazena os embeddings (vetores) de artigos científicos e boletins sobre cafeicultura.

**[D2] Modelo LLM Local (TinyLlama / Flan-T5):**  
Modelo de linguagem que gera o texto da resposta (armazenado em disco e carregado pelo P3).

**[D3] Modelo Classificador Local (BERT-tiny):**  
Modelo de classificação de intenção (armazenado em disco e carregado pelo P2).

**[D4] Message Broker (RabbitMQ):**  
- Implementa comunicação A2A *(Requisito Extra - 4 pts)*.  
- Desacopla o Agente Classificador (rápido) do Agente RAG (mais demorado).

---

### 2.4. Limites de Confiança

O principal limite é a **Rede Local**, onde os microserviços são executados.  
A comunicação entre o **Usuário (externo)** e o **Gateway (interno)** é considerada a fronteira mais crítica.
