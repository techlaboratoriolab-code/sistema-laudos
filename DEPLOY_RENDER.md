# Deploy no Render - Sistema de Laudos (Automação Hiago)

## 🚀 Por que Render é Melhor que Vercel para Flask?

- ✅ **Suporte nativo para Python/Flask** - Sem configurações complicadas
- ✅ **Sem timeout de 10 segundos** - Aplicações podem rodar por mais tempo
- ✅ **Logs em tempo real** - Fácil de debugar
- ✅ **Deploy automático do GitHub** - Push e deploy automático
- ✅ **Grátis para começar** - Plano free generoso

---

## 📋 Pré-requisitos

1. Conta no [Render.com](https://render.com) (gratuita)
2. Repositório no GitHub
3. Arquivo CSV de contatos configurado

---

## 🎯 Passo a Passo - Deploy no Render

### 1. Preparar o Repositório (JÁ FEITO ✅)

Os seguintes arquivos já estão configurados:
- ✅ `automacao_hiago.py` - Aplicação Flask
- ✅ `requirements.txt` - Dependências Python
- ✅ `render.yaml` - Configuração do Render
- ✅ `contatos_envio.csv` - Arquivo de contatos (você precisa editar com dados reais)

### 2. Configurar o CSV de Contatos

Edite o arquivo `contatos_envio.csv` com seus dados reais:

```csv
LocalOrigem,NumeroWhatsApp
NOME_LOCAL_1,5511999999999@c.us
NOME_LOCAL_2,5511888888888@c.us
```

**IMPORTANTE**:
- O `LocalOrigem` deve corresponder EXATAMENTE ao nome que vem da API do laboratório
- Os números devem terminar com `@c.us`
- Não deve haver espaços nos números

### 3. Fazer Push para o GitHub

```bash
git add .
git commit -m "Configurar para deploy no Render"
git push origin main
```

### 4. Criar Serviço no Render

#### Opção A: Deploy Automático (RECOMENDADO)

1. Acesse [https://render.com](https://render.com)
2. Faça login ou crie uma conta
3. Clique em **"New +"** → **"Web Service"**
4. Conecte seu repositório do GitHub
5. Selecione o repositório: `techlaboratoriolab-code/sistema-laudos`
6. O Render detectará automaticamente as configurações do `render.yaml`
7. Clique em **"Create Web Service"**

#### Opção B: Configuração Manual

Se o `render.yaml` não for detectado:

1. **Name**: `sistema-laudos`
2. **Environment**: `Python 3`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn automacao_hiago:app`
5. **Instance Type**: `Free`

### 5. Configurar Variáveis de Ambiente (Opcional)

As variáveis já estão no `render.yaml`, mas você pode sobrescrevê-las no painel:

- `WAHA_URL` = `https://automacaolab.ngrok.dev/api/sendFile`
- `WAHA_SESSION` = `bot-whatsapp`
- `WAHA_API_KEY` = `43092119c8b54d82ae07a0d694125ee`
- `CSV_CONTATOS` = `contatos_envio.csv`

### 6. Aguardar o Deploy

O Render irá:
1. Clonar seu repositório
2. Instalar as dependências do `requirements.txt`
3. Iniciar a aplicação com gunicorn
4. Fornecer uma URL pública (ex: `https://sistema-laudos.onrender.com`)

⏱️ Tempo médio: 2-5 minutos

---

## 🔍 Testar a Aplicação

### Teste 1: Verificar Status

Acesse:
```
https://seu-app.onrender.com/api/status
```

Deve retornar:
```json
{
  "status": "online",
  "contatos_carregados": 2,
  "locais": ["NOME_LOCAL_1", "NOME_LOCAL_2"],
  "waha_url": "https://automacaolab.ngrok.dev/api/sendFile",
  "csv_path": "contatos_envio.csv"
}
```

### Teste 2: Acessar Interface

Acesse:
```
https://seu-app.onrender.com
```

Você verá a interface web do sistema.

### Teste 3: Processar um Laudo

1. Digite um código de requisição válido
2. Clique em "Processar Laudo"
3. Verifique os logs

---

## 📊 Monitoramento e Logs

### Ver Logs em Tempo Real

1. No painel do Render, clique no seu serviço
2. Vá na aba **"Logs"**
3. Você verá todos os logs da aplicação em tempo real

### Comandos Úteis de Log

Os logs mostrarão:
- ✅ Carregamento de contatos do CSV
- ✅ Requisições recebidas
- ✅ Chamadas à API do laboratório
- ✅ Envios via WAHA
- ❌ Erros e exceções

---

## 🔧 Troubleshooting

### Erro: "Application failed to start"

**Causa**: Problema nas dependências ou código

**Solução**: Verifique os logs no Render para ver o erro específico

### Erro: "CSV não encontrado"

**Causa**: Arquivo CSV não está no repositório

**Solução**:
```bash
git add contatos_envio.csv
git commit -m "Adicionar CSV de contatos"
git push origin main
```

### Erro: "Nenhum destinatário encontrado"

**Causa**: O `LocalOrigem` no CSV não corresponde ao da API

**Solução**:
1. Teste uma requisição e veja nos logs qual é o `LocalOrigem` retornado
2. Edite o CSV com o nome EXATO
3. Faça commit e push

### WAHA não está enviando

**Causa**: URL do ngrok pode ter expirado ou WAHA está offline

**Solução**:
1. Verifique se o ngrok está rodando
2. Atualize a variável de ambiente `WAHA_URL` no Render
3. Ou configure uma URL permanente do WAHA

---

## 🔄 Re-deploy e Atualizações

### Deploy Automático

Toda vez que você fizer `git push`, o Render fará deploy automático.

### Deploy Manual

No painel do Render:
1. Clique em **"Manual Deploy"** → **"Deploy latest commit"**

### Rollback

Se algo der errado:
1. No painel, vá em **"Events"**
2. Clique em **"Rollback"** para voltar ao deploy anterior

---

## 💰 Planos e Limites

### Plano Free (Grátis)

- ✅ 750 horas/mês de runtime
- ✅ 512 MB RAM
- ✅ Deploy automático
- ⚠️ Aplicação "hiberna" após 15 minutos de inatividade
- ⚠️ Primeira requisição pode levar ~1 minuto para "acordar"

### Como Evitar a Hibernação

Use um serviço de ping (ex: UptimeRobot, Cron-Job.org) para fazer requisições a cada 10 minutos:
```
GET https://seu-app.onrender.com/api/status
```

---

## 📚 Arquivos do Projeto

```
sistema-laudos/
├── automacao_hiago.py       # Aplicação Flask principal
├── requirements.txt          # Dependências Python
├── render.yaml              # Configuração do Render
├── contatos_envio.csv       # Contatos por local de origem
├── templates/
│   └── index.html          # Interface web
└── DEPLOY_RENDER.md        # Este arquivo
```

---

## 🆘 Suporte

### Logs do Render
Acesse: Dashboard → Seu Serviço → Logs

### Documentação do Render
- [Python Quickstart](https://render.com/docs/deploy-flask)
- [Environment Variables](https://render.com/docs/environment-variables)

### Problemas com o Código
Verifique os logs no Render para mensagens de erro detalhadas.

---

## ✅ Checklist Pós-Deploy

- [ ] Aplicação está "Live" no Render
- [ ] `/api/status` retorna status online
- [ ] Interface web carrega corretamente
- [ ] CSV foi carregado (verificar em `/api/status`)
- [ ] Teste com código de requisição real
- [ ] WAHA está acessível e respondendo
- [ ] Configurar ping externo (opcional)

---

## 🎉 Pronto!

Seu sistema está no ar e pronto para uso!

URL da aplicação: `https://sistema-laudos.onrender.com` (ou o nome que você escolheu)
