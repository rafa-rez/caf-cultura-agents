# Modelagem de Ameaças - RAG-Café (STRIDE)

Este documento analisa a arquitetura inicial (definida em `ARQUITETURA_INICIAL.md`) usando a metodologia STRIDE para identificar e priorizar riscos de segurança.

## 1. DFD de Referência (Simplificado)

(Referência ao DFD da Fase 2: Usuário -> P1:Gateway -> P2:Agente1 -> D4:Broker -> P3:Agente2 -> D1:BDVetorial -> P1 -> Usuário)

## 2. Matriz de Risco (Priorização)

Usaremos a seguinte matriz para calcular a pontuação de risco (Risco = Impacto x Probabilidade):

| Impacto / Probabilidade | Baixa (5) | Média (10) | Alta (15) |
| :--- | :--- | :--- | :--- |
| **Baixo (5)** | 25 | 50 | 75 |
| **Médio (10)** | 50 | 100 | 150 |
| **Alto (15)** | 75 | 150 | 225 |

## 3. Análise e Documentação de Ameaças (STRIDE)

A tabela a seguir detalha as ameaças identificadas para cada elemento-chave do sistema.

| ID | Elemento Afetado | Categoria STRIDE | Descrição da Ameaça | Impacto (5/10/15) | Probabilidade (5/10/15) | Risco (Pts) | Medida de Mitigação Proposta | Risco Residual |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T-01** | **P1: API Gateway** | **D**enial of **S**ervice (DoS) | Um atacante (externo) inunda o P1 com milhares de requisições, esgotando recursos e tornando o sistema indisponível para usuários legítimos. | 15 (Alto) | 10 (Médio) | 150 | Implementar **Rate Limiting** (limitação de taxa) no Gateway (ex: 10 reqs/min por IP). | 50 (Baixo) |
| **T-02** | **Fluxo 1 (Usuário -> P1)** | **T**ampering (Manipulação) | Um atacante envia uma "Pergunta" maliciosa (ex: JSON malformado, *Prompt Injection*) para tentar manipular o Agente 2 (P3) ou causar falhas no P2. | 10 (Médio) | 15 (Alta) | 150 | Implementar **Validação de Schema (Pydantic)** rigorosa na entrada do P1 e **Sanitização de Entrada** (limpar *inputs*) antes de enviar aos agentes. | 50 (Baixo) |
| **T-03** | **Fluxo 12 (P1 -> Usuário)** | **I**nformation **D**isclosure (Divulgação) | A comunicação entre o Usuário e o Gateway não é criptografada (HTTP). Um atacante (Man-in-the-Middle) captura a resposta, expondo dados (ex: recomendações técnicas). | 10 (Médio) | 10 (Médio) | 100 | Forçar o uso de **HTTPS (SSL/TLS)** no API Gateway para criptografar todo o tráfego. | 25 (Baixo) |
| **T-04** | **P1: API Gateway** | **S**poofing (Falsificação) | Um atacante externo envia requisições ao P1 fingindo ser um usuário legítimo. Sem autenticação, o Gateway trata todas as requisições como válidas. | 10 (Médio) | 15 (Alta) | 150 | Implementar **Autenticação baseada em API Key** no *header* da requisição. O Gateway só processará requisições com uma chave válida. | 25 (Baixo) |
| **T-05** | **P1, P2, P3** | **R**epudiation (Repúdio) | Um usuário (ou um agente) executa uma ação (ex: uma pergunta que causa falha) e não há registro. O administrador não consegue rastrear a causa da falha ou o que foi perguntado. | 5 (Baixo) | 15 (Alta) | 75 | Implementar **Logging (Registro de Auditoria)** centralizado. Cada serviço (P1, P2, P3) deve logar eventos-chave (recebimento, processamento, erro) com *timestamps*. | 25 (Baixo) |
| **T-06** | **D4: Message Broker** | **S**poofing (Falsificação) | Um microserviço não autorizado (ex: um "Agente 4" malicioso na mesma rede Docker) conecta-se ao Broker e publica mensagens falsas na fila do P3, envenenando os dados. | 15 (Alto) | 5 (Baixa) | 75 | Configurar **Autenticação no RabbitMQ** (usuário/senha). P2 e P3 devem usar credenciais específicas para se conectarem ao Broker. | 25 (Baixo) |
| **T-07** | **P3: Agente RAG** | **E**levation of **P**rivilege (Elevação) | Um atacante, via *Prompt Injection* (T-02), induz o LLM (D2) a executar ações não previstas, como tentar ler arquivos do sistema (se o agente tiver permissão) em vez de responder. | 15 (Alto) | 5 (Baixa) | 75 | **1.** Rodar o container do P3 com o **mínimo de privilégios** (usuário *non-root*). **2.** Implementar **Prompt Engineering defensivo** (ex: "Responda apenas com base no contexto..."). | 25 (Baixo) |
| **T-08** | **D1: Banco Vetorial** | **I**nformation **D**isclosure (Divulgação) | Um atacante ganha acesso à rede e lê diretamente o D1, roubando os artigos e dados de pesquisa (que podem ser sensíveis ou proprietários) que alimentam o RAG. | 10 (Médio) | 5 (Baixa) | 50 | **Criptografia em Repouso (at-rest)** se o ChromaDB (ou similar) suportar, e **Controle de Acesso** estrito (ex: firewall de rede interna) permitindo acesso apenas do P3. | 25 (Baixo) |