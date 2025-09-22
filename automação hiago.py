import requests
import json
import base64
import os
import csv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# --- INICIALIZAÇÃO DO FLASK ---
app = Flask(__name__)
CORS(app)  # Apenas para permitir requisições da interface web

# --- CONFIGURAÇÕES GERAIS ---
API_URL = "https://lab.aplis.inf.br/api/integracao.php"
API_USERNAME = "api.lab"
API_PASSWORD = "nintendo64"
API_HEADERS = {"Content-Type": "application/json"}

# --- CONFIGURAÇÕES DO WAHA (VERIFIQUE AQUI) ---
WAHA_URL = "http://localhost:9000/api/sendFile"
WAHA_SESSION = "testano" # NOME DA SESSÃO EXIGIDO PELA SUA API
# WAHA_API_KEY = "SUA_CHAVE_DE_API_AQUI"

# --- CONFIGURAÇÕES DE MENSAGEM E ARQUIVO (EDITÁVEL) ---
NOME_ARQUIVO_SAIDA = "Laudo Médico.pdf"
MENSAGEM_PADRAO_TEMPLATE = "Olá! Segue em anexo o laudo de {nome_paciente} (Requisição: {cod_requisicao})."

# --- CONFIGURAÇÃO DO ARQUIVO DE CONTATOS ---
CAMINHO_CSV_CONTATOS = r"C:\Users\Windows 11\Desktop\sistema-laudos\Números de confiança LAB.csv"

# --- CONFIGURAÇÕES DE CONTATOS (PARA TESTE) ---
# Dicionário de contatos para usar a 'lista_teste' enquanto o CSV é ajustado.
#CONTATOS_POR_ORIGEM = #{
   # "lista_teste": [
     #   "556192127911@c.us",
     #   "55685925152@c.us"#
  #  ],
   # "DR. GUIDO SILVA GARCIA FREIRE": [
      #  "NUMERO_ESPECIFICO_DO_GUIDO@c.us"
 #   ],
#}#

# --- FUNÇÕES AUXILIARES (LÓGICA DA APLICAÇÃO) ---

def carregar_contatos_csv(caminho_arquivo):
    """Lê um arquivo CSV e retorna um dicionário de contatos por local de origem."""
    contatos = {}
    print(f"Tentando carregar contatos do arquivo: {caminho_arquivo}")
    try:
        with open(caminho_arquivo, mode='r', encoding='utf-8') as infile:
            primeira_linha = infile.readline().strip()
            print(f"DEBUG: Cabeçalho encontrado no CSV: '{primeira_linha}'")
            infile.seek(0)
            
            reader = csv.DictReader(infile)
            
            if 'LocalOrigem' not in reader.fieldnames or 'NumeroWhatsApp' not in reader.fieldnames:
                print("!!! ERRO DE CABEÇALHO !!! O arquivo CSV deve conter exatamente as colunas 'LocalOrigem' e 'NumeroWhatsApp'.")
                return {}

            for row in reader:
                local = row.get('LocalOrigem')
                numero = row.get('NumeroWhatsApp')
                
                if local and numero:
                    if local not in contatos:
                        contatos[local] = []
                    contatos[local].append(numero)

        print(f"Sucesso! {len(contatos)} locais de origem carregados do CSV.")
        return contatos
    except FileNotFoundError:
        print(f"!!! ATENÇÃO !!! Arquivo de contatos não encontrado em: {caminho_arquivo}")
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
    """Função para enviar um arquivo PDF via WAHA usando um payload JSON."""
    headers = {'Content-Type': 'application/json'}
    if 'WAHA_API_KEY' in globals() and WAHA_API_KEY:
        headers['X-Api-Key'] = WAHA_API_KEY

    payload = {
        "chatId": destinatario, "caption": mensagem,
        "file": {"filename": nome_arquivo, "mimetype": "application/pdf", "data": pdf_base64_data},
        "session": WAHA_SESSION
    }
    try:
        response = requests.post(WAHA_URL, headers=headers, json=payload, timeout=60)
        if response.status_code in [200, 201]:
            return {"status": "success", "message": f"PDF enviado para {destinatario}."}
        else:
            return {"status": "error", "message": f"WAHA retornou status {response.status_code} para {destinatario}. Resposta: {response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"Erro de conexão com o WAHA: {e}"}

# --- CARREGAMENTO INICIAL DOS CONTATOS ---
CONTATOS_CARREGADOS = carregar_contatos_csv(CAMINHO_CSV_CONTATOS)

# --- ROTAS ---

# Rota para interface web
@app.route('/')
def index():
    return render_template('index.html')

# --- ROTA DA API FLASK ---
@app.route('/api/processar', methods=['POST'])
def processar_endpoint():
    """Endpoint principal que recebe o código da requisição e executa o fluxo."""
    log_execucao = []
    
    data = request.get_json()
    if not data or 'codRequisicao' not in data:
        return jsonify({"status": "error", "message": "O campo 'codRequisicao' é obrigatório no corpo da requisição."}), 400

    cod_requisicao = data['codRequisicao']
    log_execucao.append(f"Iniciando processamento para a requisição: {cod_requisicao}")

    # 1. Buscar dados do resultado
    resultado_api = fazer_requisicao_api("requisicaoResultado", cod_requisicao)
    if resultado_api['status'] == 'error':
        log_execucao.append(resultado_api['message'])
        return jsonify({"status": "error", "log": log_execucao}), 500
    
    dados_resultado = resultado_api['data']
    nome_paciente = dados_resultado.get('paciente', {}).get('nome', 'Paciente')
    local_origem_api = dados_resultado.get('localOrigem', {}).get('nome')
    log_execucao.append(f"Paciente: {nome_paciente}, Local de Origem: {local_origem_api}")

    # 2. Buscar dados do laudo
    laudo_api = fazer_requisicao_api("requisicaoLaudo", cod_requisicao)
    if laudo_api['status'] == 'error':
        log_execucao.append(laudo_api['message'])
        return jsonify({"status": "error", "log": log_execucao}), 500

    pdf_base64 = laudo_api['data'].get('laudoPDF')
    if not pdf_base64:
        log_execucao.append("AVISO: O campo 'laudoPDF' não foi encontrado na resposta da API.")
        return jsonify({"status": "error", "log": log_execucao}), 404
    
    log_execucao.append("Laudo em Base64 obtido com sucesso.")

    # 3. Lógica de envio usando contatos
    # Para alternar entre CSV e lista de teste, comente uma linha e descomente a outra.
    
    # Lógica 1: Usar o arquivo CSV para encontrar o contato pelo Local de Origem (ATIVADO)
    destinatarios = CONTATOS_CARREGADOS.get(local_origem_api, []) 
    
    # Lógica 2: Usar uma lista de teste fixa (DESATIVADO)
    # destinatarios = CONTATOS_POR_ORIGEM.get("lista_teste", []) 

    if not destinatarios:
        log_execucao.append(f"AVISO: Nenhum destinatário encontrado para o local '{local_origem_api}'.")
    else:
        log_execucao.append(f"Disparando laudo para {len(destinatarios)} contato(s) da lista de teste...")
        mensagem_final = MENSAGEM_PADRAO_TEMPLATE.format(
            nome_paciente=nome_paciente,
            cod_requisicao=cod_requisicao.strip()
        )
        for contato in destinatarios:
            resultado_envio = enviar_pdf_waha(pdf_base64, NOME_ARQUIVO_SAIDA, contato, mensagem_final)
            log_execucao.append(f"[{contato}]: {resultado_envio['message']}")

    return jsonify({"status": "success", "log": log_execucao, "paciente": nome_paciente, "requisicao": cod_requisicao}), 200

# Rota simples para status
@app.route('/api/status')
def status():
    return jsonify({"status": "online"})

# --- EXECUÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)