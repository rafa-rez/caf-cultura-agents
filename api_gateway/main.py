# /api_gateway/main.py
import uvicorn
import pika
import json
import uuid
import os
from fastapi import FastAPI, HTTPException, status, Request
from pydantic import BaseModel
from contextlib import AbstractContextManager
from fastapi.security import APIKeyHeader
from fastapi import Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


BROKER_USER = os.environ.get('BROKER_USER', 'guest')
BROKER_PASS = os.environ.get('BROKER_PASS', 'guest')
CREDENCIAIS = pika.PlainCredentials(BROKER_USER, BROKER_PASS)

# --- Modelos de Dados (Validação T-02) ---

class PerguntaUsuario(BaseModel):
    texto_pergunta: str

class RespostaAgente(BaseModel):
    id_pergunta: str
    texto_resposta: str
    fontes: list[str]

# --- Configuração do App ---
app = FastAPI(
    title="RAG-Café API Gateway (P1)",
    description="Ponto de entrada do sistema. Comunicação A2A via RabbitMQ."
)

# Configuração do Rate Limiter (Mitigação T-01)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Chave de API (Mitigação T-04)
# Em produção, isso viria de uma variável de ambiente
API_KEY_VALIDA = "cafe_seguro_UFLA_2025" 
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def validar_api_key(key: str = Depends(api_key_header)):
    """ Validador de dependência para a API Key """
    if not key or key != API_KEY_VALIDA:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API (X-API-Key) inválida ou ausente."
        )
    return True

# --- Gerenciador de Conexão RabbitMQ (Boa Prática) ---
# Vamos manter uma conexão/canal por requisição para segurança em threads

BROKER_HOST = os.environ.get('BROKER_HOST', 'localhost')
FILA_SAIDA_P1 = "q_perguntas" # P1 -> P2

class RabbitMQClient(AbstractContextManager):
    """
    Gerencia a conexão e o canal do RabbitMQ para o padrão RPC.
    """
    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue_name = None
        self.correlation_id = None
        self.response = None
        
    def __enter__(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=BROKER_HOST, port=5672, credentials=CREDENCIAIS)
            )
            self.channel = self.connection.channel()
            
            # Declara a fila de resposta (exclusiva e anônima)
            result = self.channel.queue_declare(queue='', exclusive=True)
            self.callback_queue_name = result.method.queue
            
            # Prepara o consumo da fila de resposta
            self.channel.basic_consume(
                queue=self.callback_queue_name,
                on_message_callback=self.on_response_callback,
                auto_ack=True
            )
            return self
            
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[P1-Gateway] Erro ao conectar no RabbitMQ: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Broker de mensagens indisponível."
            )
            
    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            
    def on_response_callback(self, ch, method, props, body):
        # Verifica se é a resposta da nossa requisição
        if self.correlation_id == props.correlation_id:
            self.response = body

    def call_rpc(self, mensagem_body: dict) -> dict:
        """ Executa a chamada RPC (Publica e Espera) """
        if not self.channel or not self.connection:
            raise HTTPException(status_code=503, detail="Conexão com Broker não estabelecida.")
            
        self.correlation_id = str(uuid.uuid4())
        
        # Publica a mensagem na fila do P2
        self.channel.basic_publish(
            exchange='',
            routing_key=FILA_SAIDA_P1,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue_name,
                correlation_id=self.correlation_id,
                delivery_mode=2 # Persistente
            ),
            body=json.dumps(mensagem_body)
        )
        
        print(f"[P1-Gateway] [ID: {self.correlation_id}]: Mensagem publicada em '{FILA_SAIDA_P1}'. Aguardando resposta em '{self.callback_queue_name}'...")
        
        # Espera pela resposta (com timeout)
        timeout_segundos = 15 # Timeout para o fluxo P2->P3->P1
        start_time = pika.compat.time.time()
        
        while self.response is None:
            # Processa eventos do RabbitMQ (espera pela resposta)
            self.connection.process_data_events(time_limit=1)
            
            if pika.compat.time.time() - start_time > timeout_segundos:
                print(f"[P1-Gateway] [ID: {self.correlation_id}]: Timeout esperando resposta.")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT, 
                    detail="Tempo limite da requisição de IA excedido. O processamento pode estar demorando."
                )

        print(f"[P1-Gateway] [ID: {self.correlation_id}]: Resposta recebida.")
        return json.loads(self.response)

# --- Endpoints ---

@app.get("/")
async def root():
    return {"status": "API Gateway está operacional (Modo A2A/RPC)"}


@app.post("/perguntar", response_model=RespostaAgente, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def fazer_pergunta(pergunta: PerguntaUsuario, request: Request, key_valida: bool = Depends(validar_api_key)):
    """
    Recebe a pergunta, envia para o fluxo A2A (P2->P3) via RabbitMQ 
    e aguarda a resposta (Padrão RPC).
    """
    
    # (Mitigação T-04: API Key - será adicionada na Fase 5)
    # (Mitigação T-01: Rate Limit - será adicionada na Fase 5)
    
    # (Mitigação T-02: Validação) - O Pydantic (PerguntaUsuario) já faz isso.
    
    id_req = str(uuid.uuid4()) # ID único para esta transação (Mitigação T-05)
    print(f"\n[P1-Gateway] [ID: {id_req}]: Nova requisição /perguntar de {request.client.host}")
    
    mensagem_para_p2 = {
        "id_usuario": id_req, # Usamos o ID da requisição como rastreador
        "texto_pergunta": pergunta.texto_pergunta
    }

    try:
        # Usa o gerenciador de contexto para a chamada RPC
        with RabbitMQClient() as rpc_client:
            resposta_json = rpc_client.call_rpc(mensagem_para_p2)
        
        # Valida a resposta recebida do P3
        # (Isso garante que P3 não envie dados malformados)
        return RespostaAgente(**resposta_json)

    except HTTPException as e:
        # Repassa exceções HTTP (Timeout, Broker indisponível)
        raise e
    except Exception as e:
        # Erro genérico
        print(f"[P1-Gateway] [ID: {id_req}]: Erro inesperado no fluxo RPC: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no processamento da requisição.")

# --- Inicialização ---
if __name__ == "__main__":
    print(f"Iniciando API Gateway (P1) localmente em http://localhost:8000")
    print(f"Tentando conectar ao Broker em: {BROKER_HOST}")
    uvicorn.run(app, host="0.0.0.0", port=8000)