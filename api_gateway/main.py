# /api_gateway/main.py
import uvicorn
import httpx
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# --- Modelos de Dados (Validação de Entrada - Mitigação T-02) ---

class PerguntaUsuario(BaseModel):
    """ Modelo de entrada da pergunta do usuário """
    id_usuario: str  # ID para rastreabilidade (Mitigação T-05)
    texto_pergunta: str

class RespostaAgente(BaseModel):
    """ Modelo padronizado de resposta """
    id_pergunta: str
    texto_resposta: str
    fontes: list[str] = []


# --- Configuração do App ---
app = FastAPI(
    title="RAG-Café API Gateway (P1)",
    description="Ponto de entrada do sistema de suporte à cafeicultura."
)

# URL do nosso próximo microserviço (Agente 1).
# Usamos o nome do serviço que daremos no docker-compose.
URL_AGENTE_CLASSIFICADOR = "http://agente_classificador:8001/classificar"


# --- Endpoints ---

@app.get("/")
async def root():
    """ Endpoint de saúde do serviço """
    return {"status": "API Gateway está operacional"}


@app.post("/perguntar", response_model=RespostaAgente, status_code=status.HTTP_200_OK)
async def fazer_pergunta(pergunta: PerguntaUsuario):
    """
    Recebe a pergunta do usuário e a encaminha para o fluxo de IA.
    """
    print(f"Gateway (P1) [ID: {pergunta.id_usuario}]: Recebida pergunta: '{pergunta.texto_pergunta}'")

    # TODO (Passo 4.4): Substituir esta chamada HTTP direta por uma publicação no RabbitMQ.
    
    # Por enquanto (Passo 4.1), fazemos uma chamada HTTP síncrona para o Agente 1.
    try:
        async with httpx.AsyncClient() as client:
            # Encaminha a pergunta para o Agente 1
            response = await client.post(URL_AGENTE_CLASSIFICADOR, json=pergunta.dict())

            # Se o Agente 1 falhar, repassa o erro
            response.raise_for_status() 
            
            # (Simulação por enquanto) No futuro, o Agente 2 que retornará isso.
            # Por agora, apenas simulamos que o Agente 1 já nos deu a resposta final.
            # Vamos corrigir esse fluxo no Passo 4.4.
            
            # --- SIMULAÇÃO (será removido) ---
            # Vamos assumir que o Agente 1 já retorna a resposta final por enquanto.
            if response.status_code == 200:
                print(f"Gateway (P1): Resposta simulada recebida.")
                return RespostaAgente(
                    id_pergunta=pergunta.id_usuario,
                    texto_resposta="[SIMULAÇÃO] O Agente Classificador processou, mas a resposta final virá do Agente RAG.",
                    fontes=["passo_4.1"]
                )
            # --- FIM DA SIMULAÇÃO ---

    except httpx.RequestError as exc:
        # Erro de comunicação entre serviços
        print(f"Gateway (P1): Erro ao contatar Agente 1: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Serviço de classificação está indisponível: {exc}"
        )

    # (Este código não será alcançado na simulação atual, mas é o correto)
    # return response.json()


# --- Inicialização (para debug local) ---
if __name__ == "__main__":
    print("Iniciando API Gateway (P1) localmente em http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)