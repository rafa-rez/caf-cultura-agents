# /agente_rag/main.py
import pika
import time
import json
import sys
import os

host_broker = os.environ.get('BROKER_HOST', 'localhost')
broker_user = os.environ.get('BROKER_USER', 'guest')
broker_pass = os.environ.get('BROKER_PASS', 'guest')
credenciais = pika.PlainCredentials(broker_user, broker_pass)

# --- SIMULAÇÃO DA LÓGICA RAG (D1 e D2) ---
# (A mesma do Passo 4.3)
def simular_carregamento_banco_vetorial(intencao: str, entidades: list[str]) -> str:
    print(f"[P3-RAG] (D1-Retrieve): Buscando contexto para Intenção='{intencao}', Entidades={entidades}")
    time.sleep(0.2) # Simula I/O do banco (D1)
    
    conhecimento = {
        "manejo_praga": "Segundo a Embrapa, o controle da broca-do-café (Hypothenemus hampei) deve ser feito com monitoramento constante e controle biológico.",
        "manejo_doenca": "A ferrugem (Hemileia vastatrix) é controlada com fungicidas cúpricos e variedades resistentes, conforme boletim técnico da UFLA.",
        "cotacao": "O mercado de café arábica fechou em alta na bolsa de NY."
    }
    
    return conhecimento.get(intencao, "Nenhum contexto encontrado para esta intenção.")

def simular_geracao_llm_local(contexto: str, pergunta: str) -> str:
    print(f"[P3-RAG] (D2-Generate): Gerando resposta com LLM local...")
    time.sleep(0.5) # Simula o processamento pesado do LLM (D2)
    
    resposta_gerada = f"Resposta: {contexto}"
    fontes = ["Artigo Simulado (Embrapa/UFLA)"]
    return resposta_gerada, fontes

# --- LÓGICA DO WORKER (Consumidor RabbitMQ) ---

# Nomes das filas (consistência)
FILA_ENTRADA_P3 = "q_rag_processar"   # P2 -> P3

def main():
    host_broker = os.environ.get('BROKER_HOST', 'localhost')
    
    while True: # Loop de reconexão
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host_broker, port=5672, credentials=credenciais)
            )
            channel = connection.channel()

            # Declara a fila que este agente vai consumir (de onde P2 envia)
            channel.queue_declare(queue=FILA_ENTRADA_P3, durable=True)

            print(f"[P3-RAG] Conectado ao RabbitMQ em '{host_broker}'.")
            print(f"[P3-RAG] Aguardando mensagens em '{FILA_ENTRADA_P3}'...")

            def callback(ch, method, properties, body):
                """ Processa a mensagem recebida do P2 """
                try:
                    dados = json.loads(body)
                    id_usuario = dados.get('id_usuario', 'ID_NULO')
                    pergunta = dados.get('texto_pergunta', '')
                    intencao = dados.get('intencao', 'desconhecido')
                    
                    print(f"\n[P3-RAG] [ID: {id_usuario}]: Mensagem recebida de P2. Intenção='{intencao}'")

                    # 1. Lógica de IA (P3 - RAG)
                    contexto = simular_carregamento_banco_vetorial(intencao, [])
                    resposta_texto, resposta_fontes = simular_geracao_llm_local(contexto, pergunta)
                    
                    print(f"[P3-RAG] [ID: {id_usuario}]: Resposta final gerada.")
                    
                    # 2. Prepara a resposta final (para P1)
                    mensagem_resposta = {
                        "id_pergunta": id_usuario,
                        "texto_resposta": resposta_texto,
                        "fontes": resposta_fontes
                    }

                    # 3. Publica a resposta de volta para o P1
                    # (properties.reply_to é a fila que o P1 criou e está ouvindo)
                    channel.basic_publish(
                        exchange='',
                        routing_key=properties.reply_to,
                        properties=pika.BasicProperties(
                            correlation_id=properties.correlation_id
                        ),
                        body=json.dumps(mensagem_resposta)
                    )
                    
                    print(f"[P3-RAG] [ID: {id_usuario}]: Resposta final enviada para '{properties.reply_to}'.")

                    ch.basic_ack(delivery_tag=method.delivery_tag)

                except json.JSONDecodeError:
                    print("[P3-RAG] Erro: Mensagem recebida não é um JSON válido.")
                except Exception as e:
                    print(f"[P3-RAG] Erro inesperado: {e}")

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=FILA_ENTRADA_P3, on_message_callback=callback)
            
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"[P3-RAG] Erro de conexão ({e}). Tentando novamente em 5s...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("[P3-RAG] Desligando...")
            sys.exit(0)

if __name__ == '__main__':
    main()