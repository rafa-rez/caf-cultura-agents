# /agente_classificador/main.py
import pika
import time
import json
import sys
import os

# --- Lógica de IA (Simulação - P2) ---
# (A mesma do Passo 4.2)
def simular_classificacao(texto: str) -> tuple[str, list[str]]:
    texto_lower = texto.lower()
    time.sleep(0.1) # Simula o tempo de processamento do modelo (D3)

    if "broca" in texto_lower or "praga" in texto_lower:
        return "manejo_praga", ["broca-do-cafe"]
    elif "doença" in texto_lower or "ferrugem" in texto_lower:
        return "manejo_doenca", ["ferrugem"]
    elif "preço" in texto_lower or "mercado" in texto_lower:
        return "cotacao", []
    else:
        return "desconhecido", []

# --- Lógica do Worker (RabbitMQ) ---

# Nomes das filas (consistência)
FILA_ENTRADA_P2 = "q_perguntas"      # P1 -> P2
FILA_SAIDA_P2 = "q_rag_processar"   # P2 -> P3

def main():
    host_broker = os.environ.get('BROKER_HOST', 'localhost')
    
    while True: # Loop de reconexão
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host_broker, port=5672)
            )
            channel = connection.channel()

            # Declara a fila que este agente consome (P1 envia para cá)
            channel.queue_declare(queue=FILA_ENTRADA_P2, durable=True)
            # Declara a fila que este agente publica (P3 consome daqui)
            channel.queue_declare(queue=FILA_SAIDA_P2, durable=True)

            print(f"[P2-Classificador] Conectado ao RabbitMQ em '{host_broker}'.")
            print(f"[P2-Classificador] Aguardando mensagens em '{FILA_ENTRADA_P2}'...")

            def callback(ch, method, properties, body):
                """ Processa a mensagem recebida do P1 """
                try:
                    dados = json.loads(body)
                    id_usuario = dados.get('id_usuario', 'ID_NULO')
                    pergunta = dados.get('texto_pergunta', '')
                    
                    print(f"\n[P2-Classificador] [ID: {id_usuario}]: Pergunta recebida: '{pergunta}'")
                    
                    # 1. Lógica de IA (P2)
                    intencao, entidades = simular_classificacao(pergunta)
                    print(f"[P2-Classificador] [ID: {id_usuario}]: Classificado como -> Intenção: '{intencao}'")

                    # 2. Prepara a próxima mensagem (para P3)
                    mensagem_para_p3 = {
                        "id_usuario": id_usuario,
                        "texto_pergunta": pergunta,
                        "intencao": intencao,
                        "entidades": entidades,
                        # Passa adiante as propriedades de roteamento (ex: reply_to)
                        "correlation_id": properties.correlation_id,
                        "reply_to": properties.reply_to
                    }
                    
                    # 3. Publica no P3
                    channel.basic_publish(
                        exchange='',
                        routing_key=FILA_SAIDA_P2, # Envia para a fila do RAG
                        body=json.dumps(mensagem_para_p3),
                        properties=pika.BasicProperties(
                            delivery_mode=2, # Torna a mensagem persistente
                            correlation_id=properties.correlation_id,
                            reply_to=properties.reply_to
                        )
                    )
                    
                    print(f"[P2-Classificador] [ID: {id_usuario}]: Mensagem enriquecida enviada para '{FILA_SAIDA_P2}'.")
                    
                    # Confirma que a mensagem foi processada
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                except json.JSONDecodeError:
                    print("[P2-Classificador] Erro: Mensagem recebida não é um JSON válido.")
                except Exception as e:
                    print(f"[P2-Classificador] Erro inesperado: {e}")

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=FILA_ENTRADA_P2, on_message_callback=callback)
            
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"[P2-Classificador] Erro de conexão ({e}). Tentando novamente em 5s...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("[P2-Classificador] Desligando...")
            sys.exit(0)

if __name__ == '__main__':
    main()