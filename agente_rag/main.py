# /agente_rag/main.py
import pika
import time
import json
import sys

# --- SIMULAÇÃO DA LÓGICA RAG (D1 e D2) ---

def simular_carregamento_banco_vetorial(intencao: str, entidades: list[str]) -> str:
    """
    Simula a busca no ChromaDB (D1).
    (D1 - Retrieval)
    """
    print(f"[P3-RAG] (D1-Retrieve): Buscando contexto para Intenção='{intencao}', Entidades={entidades}")
    time.sleep(0.2) # Simula I/O do banco
    
    # Base de conhecimento simulada
    conhecimento = {
        "manejo_praga": "Segundo a Embrapa, o controle da broca-do-café (Hypothenemus hampei) deve ser feito com monitoramento constante e controle biológico.",
        "manejo_doenca": "A ferrugem (Hemileia vastatrix) é controlada com fungicidas cúpricos e variedades resistentes, conforme boletim técnico da UFLA.",
        "cotacao": "O mercado de café arábica fechou em alta na bolsa de NY."
    }
    
    return conhecimento.get(intencao, "Nenhum contexto encontrado para esta intenção.")

def simular_geracao_llm_local(contexto: str, pergunta: str) -> str:
    """
    Simula o carregamento do LLM (D2 - TinyLlama/Flan-T5) e a geração.
    (D2 - Generation)
    """
    print(f"[P3-RAG] (D2-Generate): Gerando resposta com LLM local...")
    time.sleep(0.5) # Simula o processamento pesado do LLM
    
    # O LLM "funde" o contexto e a pergunta
    resposta_gerada = f"Resposta: {contexto} (Fonte: Artigo Simulado 1.0)"
    return resposta_gerada

# --- LÓGICA DO WORKER (Consumidor RabbitMQ) ---

def processar_pergunta(corpo_mensagem: bytes):
    """
    Função principal do agente P3: RAG (Retrieval-Augmented Generation).
    """
    try:
        dados = json.loads(corpo_mensagem)
        id_usuario = dados.get('id_usuario', 'ID_NULO')
        pergunta = dados.get('texto_pergunta', '')
        intencao = dados.get('intencao', 'desconhecido')
        entidades = dados.get('entidades', [])
        
        print(f"\n[P3-RAG] [ID: {id_usuario}]: Pergunta recebida da fila. Intenção='{intencao}'")

        # 1. Retrieval (RAG - Parte 1)
        contexto_recuperado = simular_carregamento_banco_vetorial(intencao, entidades)
        
        # 2. Generation (RAG - Parte 2)
        resposta_final = simular_geracao_llm_local(contexto_recuperado, pergunta)
        
        print(f"[P3-RAG] [ID: {id_usuario}]: Resposta final gerada.")
        
        # TODO (Passo 4.4): Publicar a resposta final na fila 'q_respostas'
        # para o Gateway (P1) consumir.
        
        print(f"[P3-RAG] [ID: {id_usuario}]: (Simulação) Resposta seria enviada para 'q_respostas': {resposta_final}")

    except json.JSONDecodeError:
        print("[P3-RAG] Erro: Mensagem recebida não é um JSON válido.")
    except Exception as e:
        print(f"[P3-RAG] Erro inesperado ao processar: {e}")

def main():
    """ Função principal que conecta ao RabbitMQ e consome a fila. """
    
    # TODO (Passo 4.4): Mover 'rabbitmq' para variável de ambiente
    host_broker = 'rabbitmq'
    
    # Loop de reconexão
    tentativas_conexao = 0
    while tentativas_conexao < 10:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host_broker, port=5672)
            )
            channel = connection.channel()

            # Declara a fila que este agente vai consumir (de onde P2 vai enviar)
            # TODO (Passo 4.4): Definir nome da fila (ex: 'q_rag')
            nome_fila = 'q_rag_simulada' 
            channel.queue_declare(queue=nome_fila, durable=True)

            print(f"[P3-RAG] Conectado ao RabbitMQ. Aguardando mensagens na fila '{nome_fila}'...")
            
            def callback(ch, method, properties, body):
                """ Função chamada quando uma mensagem é recebida """
                processar_pergunta(body)
                ch.basic_ack(delivery_tag=method.delivery_tag) # Confirma o recebimento

            channel.basic_qos(prefetch_count=1) # Processa uma mensagem por vez
            channel.basic_consume(queue=nome_fila, on_message_callback=callback)
            
            # Inicia o consumo (bloqueante)
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"[P3-RAG] Erro ao conectar no RabbitMQ ({e}). Tentando novamente em 5s...")
            tentativas_conexao += 1
            time.sleep(5)
        except KeyboardInterrupt:
            print("[P3-RAG] Desligando...")
            sys.exit(0)

if __name__ == '__main__':
    main()