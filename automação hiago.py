import requests
import json
import base64
import os
import csv
import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# --- INICIALIZAÇÃO DO FLASK ---
app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÕES GERAIS ---
API_URL = "https://lab.aplis.inf.br/api/integracao.php"
API_USERNAME = "api.lab"
API_PASSWORD = "nintendo64"
API_HEADERS = {"Content-Type": "application/json"}

# --- CONFIGURAÇÕES DO WAHA (VERIFIQUE AQUI) ---
WAHA_URL = "http://localhost:4000/api/sendFile"
WAHA_SESSION = "bot-whatsapp"
WAHA_API_KEY = "450759cbecc9440ea2e6574b2e175353"

# --- CONFIGURAÇÕES DE MENSAGEM E ARQUIVO (EDITÁVEL) ---
MENSAGEM_PADRAO_TEMPLATE = "Olá! Segue em anexo o laudo de {nome_paciente} (Requisição: {cod_requisicao})."

NOME_ARQUIVO_SAIDA = "nome_paciente"

# --- CONFIGURAÇÃO DO ARQUIVO DE CONTATOS ---
CAMINHO_CSV_CONTATOS = "Números de confiança LAB.csv"

# --- FUNÇÕES AUXILIARES ---

def carregar_contatos_csv(caminho_arquivo):
    """Lê um arquivo CSV, valida os números e retorna um dicionário de contatos."""
    contatos = {}
    print(f"Tentando carregar contatos do arquivo: {caminho_arquivo}")
    try:
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_completo = os.path.join(diretorio_atual, caminho_arquivo)
        
        with open(caminho_completo, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if 'LocalOrigem' not in reader.fieldnames or 'NumeroWhatsApp' not in reader.fieldnames:
                print("!!! ERRO DE CABEÇALHO !!! O CSV deve ter as colunas 'LocalOrigem' e 'NumeroWhatsApp'.")
                return {}

            for i, row in enumerate(reader, 2):
                local = row.get('LocalOrigem', '').strip()
                numero = row.get('NumeroWhatsApp', '').strip()
                
                if local and numero:
                    if numero.endswith('@c.us') and ' ' not in numero:
                        if local not in contatos:
                            contatos[local] = []
                        contatos[local].append(numero)
                    else:
                        print(f"!!! AVISO !!! Número em formato inválido na linha {i} do CSV e foi ignorado: '{numero}'")

        print(f"Sucesso! {len(contatos)} locais de origem carregados do CSV.")
        return contatos
    except FileNotFoundError:
        print(f"!!! ATENÇÃO !!! Arquivo de contatos '{caminho_completo}' não encontrado.")
        return {}
    except Exception as e:
        print(f"!!! ERRO !!! Falha ao ler o arquivo CSV de contatos: {e}")
        return {}

def fazer_requisicao_api(cmd, cod_req):
    """Função para buscar dados na API do laboratório."""
    payload = {"ver": 1, "cmd": cmd, "dat": {"codRequisicao": cod_req.strip()}}
    try:
        response = requests.post(API_URL, auth=(API_USERNAME, API_PASSWORD), headers=API_HEADERS, data=json.dumps(payload), timeout=30)
        response.raise_for_status()
        resposta_json = response.json()
        if resposta_json.get("dat") and resposta_json["dat"].get("sucesso") == 1:
            return {"status": "success", "data": resposta_json["dat"]}
        else:
            msg_erro = resposta_json.get('dat', {}).get('msg', 'Mensagem de erro não encontrada.')
            return {"status": "error", "message": f"Falha na API do lab ao buscar '{cmd}': {msg_erro}"}
    except Exception as e:
        return {"status": "error", "message": f"Erro de conexão com a API do lab: {e}"}

def enviar_pdf_waha(pdf_base64_data, nome_arquivo, destinatario, mensagem):
    """
    Função para enviar um arquivo PDF via WAHA usando um payload JSON.
    Usa uma estratégia "fire and forget" para lidar com a lentidão do servidor WAHA.
    """
    headers = {'Content-Type': 'application/json'}
    if 'WAHA_API_KEY' in globals() and WAHA_API_KEY:
        headers['X-Api-Key'] = WAHA_API_KEY

    payload = {
        "chatId": destinatario, "caption": mensagem,
        "file": {"filename": nome_arquivo, "mimetype": "application/pdf", "data": pdf_base64_data},
        "session": WAHA_SESSION
    }
    try:
        # --- ESTRATÉGIA "FIRE AND FORGET" ---
        # Enviamos a requisição com um timeout muito curto (2 segundos).
        # A intenção é apenas despachar os dados para o WAHA e não esperar
        # pelo processamento completo, que está a causar o timeout.
        print(f"Disparando requisição para {destinatario} (estratégia 'fire and forget')...")
        requests.post(WAHA_URL, headers=headers, json=payload, timeout=2)
        
        # Se chegarmos aqui, o WAHA respondeu muito rápido (improvável, mas possível)
        return {"status": "success", "message": f"Requisição enviada para {destinatario}. WAHA respondeu inesperadamente rápido."}
    
    except requests.exceptions.Timeout:
        # Este é o resultado ESPERADO. O timeout acontece, mas os dados já foram enviados.
        # Assumimos que o WAHA irá processar o pedido em segundo plano.
        return {"status": "success", "message": f"Requisição enviada para {destinatario}. Assumindo sucesso (WAHA processará em segundo plano)."}
    
    except requests.exceptions.ConnectionError as e:
        return {"status": "error", "message": f"Erro de Conexão com o WAHA. Verifique se o servidor está rodando em '{WAHA_URL}'. Detalhes: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Erro inesperado ao conectar com o WAHA: {e}"}


# --- CARREGAMENTO INICIAL DOS CONTATOS ---
CONTATOS_CARREGADOS = carregar_contatos_csv(CAMINHO_CSV_CONTATOS)

# --- ROTAS DA API FLASK ---
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "online"})

@app.route('/api/processar', methods=['POST'])
def processar_endpoint():
    log_execucao = []
    data = request.get_json()
    if not data or 'codRequisicao' not in data:
        return jsonify({"status": "error", "message": "O campo 'codRequisicao' é obrigatório."}), 400

    cod_requisicao = data['codRequisicao']
    log_execucao.append(f"Iniciando processamento para a requisição: {cod_requisicao}")

    resultado_api = fazer_requisicao_api("requisicaoResultado", cod_requisicao)
    if resultado_api['status'] == 'error':
        log_execucao.append(resultado_api['message'])
        return jsonify({"status": "error", "log": log_execucao}), 500
    
    dados_resultado = resultado_api['data']
    nome_paciente = dados_resultado.get('paciente', {}).get('nome', 'Paciente')
    local_origem_api = dados_resultado.get('localOrigem', {}).get('nome')
    log_execucao.append(f"Paciente: {nome_paciente}, Local de Origem: {local_origem_api}")

    laudo_api = fazer_requisicao_api("requisicaoLaudo", cod_requisicao)
    if laudo_api['status'] == 'error':
        log_execucao.append(laudo_api['message'])
        return jsonify({"status": "error", "log": log_execucao}), 500

    pdf_base64 = laudo_api['data'].get('laudoPDF')
    if not pdf_base64:
        log_execucao.append("AVISO: 'laudoPDF' não encontrado na resposta.")
        return jsonify({"status": "error", "log": log_execucao}), 404
    
    log_execucao.append("Laudo em Base64 obtido com sucesso.")

    destinatarios = CONTATOS_CARREGADOS.get(local_origem_api, [])
    log_execucao.append(f"Contatos encontrados para '{local_origem_api}': {destinatarios}")

    if not destinatarios:
        log_execucao.append(f"AVISO: Nenhum destinatário válido encontrado para '{local_origem_api}'.")
    else:
        log_execucao.append(f"Disparando laudo para {len(destinatarios)} contato(s)...")
        mensagem_final = MENSAGEM_PADRAO_TEMPLATE.format(nome_paciente=nome_paciente, cod_requisicao=cod_requisicao.strip())
        for contato in destinatarios:
            resultado_envio = enviar_pdf_waha(pdf_base64, nome_paciente, contato, mensagem_final)
            log_execucao.append(f"[{contato}]: {resultado_envio['message']}")
    
    return jsonify({
        "status": "success", 
        "log": log_execucao,
        "paciente": nome_paciente,
        "requisicao": cod_requisicao.strip()
    }), 200

# --- EXECUÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 2806))
    app.run(host='0.0.0.0', port=port, debug=True)

