# /agente_classificador/main.py
import uvicorn
from fastapi import FastAPI, status
from pydantic import BaseModel
import time

# --- Modelos de Dados ---
# O Agente 1 recebe exatamente o que o Gateway (P1) envia.

class PerguntaUsuario(BaseModel):
    """ Modelo de entrada (espelhado do Gateway) """
    id_usuario: str
    texto_pergunta: str

class RespostaAgente(BaseModel):
    """ 
    Modelo de resposta. 
    (ATENÇÃO: Este agente NÃO deveria retornar isso. 
    Isso é uma simulação temporária até o Passo 4.4)
    """
    id_pergunta: str
    texto_resposta: str
    fontes: list[str] = []


# --- Configuração do App ---
app = FastAPI(
    title="Agente Classificador (P2)",
    description="Microserviço de IA (Docker/Local) que classifica a intenção do usuário."
)

# --- Lógica de IA (Simulação) ---

def simular_classificacao(texto: str) -> tuple[str, list[str]]:
    """
    Simula o carregamento do modelo (D3_CLF_MODEL) e a classificação.
    No futuro, aqui entraria um modelo real (ex: BERT-tiny).
    """
    texto_lower = texto.lower()
    time.sleep(0.1) # Simula o tempo de processamento do modelo

    if "broca" in texto_lower or "praga" in texto_lower:
        return "manejo_praga", ["broca-do-cafe"]
    elif "doença" in texto_lower or "ferrugem" in texto_lower:
        return "manejo_doenca", ["ferrugem"]
    elif "preço" in texto_lower or "mercado" in texto_lower:
        return "cotacao", []
    else:
        return "desconhecido", []

# --- Endpoints ---

@app.get("/health")
async def health_check():
    """ Endpoint de saúde do serviço """
    return {"status": "Agente Classificador está operacional"}


@app.post("/classificar", status_code=status.HTTP_200_OK)
async def classificar_pergunta(pergunta: PerguntaUsuario):
    """
    Recebe a pergunta, simula a classificação e (temporariamente) retorna 
    uma resposta final.
    """
    print(f"Agente (P2) [ID: {pergunta.id_usuario}]: Recebida pergunta: '{pergunta.texto_pergunta}'")
    
    # 1. Simulação da Lógica de IA (o "cérebro" do P2)
    intencao, entidades = simular_classificacao(pergunta.texto_pergunta)
    
    print(f"Agente (P2) [ID: {pergunta.id_usuario}]: Classificado como -> Intenção: '{intencao}', Entidades: {entidades}")

    # TODO (Passo 4.4): 
    # A ação correta é:
    # 1. Montar um JSON {pergunta, intencao, entidades}
    # 2. Publicar no RabbitMQ
    # 3. Retornar status 202 (Accepted) para o Gateway.
    
    # --- SIMULAÇÃO (será removido) ---
    # Como o P3 e o Broker ainda não existem, vamos simular que o P2
    # já gera a resposta final (o que é ARQUITETURALMENTE INCORRETO,
    # mas necessário para testar o P1 e P2).
    
    resposta_simulada = RespostaAgente(
        id_pergunta=pergunta.id_usuario,
        texto_resposta=f"[SIMULAÇÃO P2] A intenção é '{intencao}'. O Agente RAG (P3) irá processar isso.",
        fontes=["passo_4.2", f"intencao:{intencao}"]
    )
    return resposta_simulada
    # --- FIM DA SIMULAÇÃO ---


# --- Inicialização ---
if __name__ == "__main__":
    print("Iniciando Agente Classificador (P2) localmente em http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)