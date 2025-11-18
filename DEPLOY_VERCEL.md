# Deploy no Vercel - Sistema de Laudos (Automação Hiago)

## Arquivos Configurados

Este projeto está configurado para deploy no Vercel com os seguintes arquivos:

- `automacao_hiago.py` - Aplicação Flask principal
- `wsgi.py` - Ponto de entrada para o Vercel
- `vercel.json` - Configuração de rotas do Vercel
- `requirements.txt` - Dependências Python
- `templates/index.html` - Interface web
- `Números de confiança LAB.csv` - Arquivo de contatos

## Pré-requisitos

1. Conta no GitHub
2. Conta no Vercel
3. Arquivo CSV de contatos no repositório

## Passos para Deploy

### 1. Fazer Push para o GitHub

```bash
git add .
git commit -m "Adicionar automação Hiago para deploy no Vercel"
git push origin main
```

### 2. Configurar Variáveis de Ambiente no Vercel

No painel do Vercel, configure as seguintes variáveis de ambiente:

- `WAHA_URL` - URL do servidor WAHA (ex: http://seu-servidor:4000/api/sendFile)
- `WAHA_SESSION` - Nome da sessão WAHA (ex: bot-whatsapp)
- `WAHA_API_KEY` - Chave de API do WAHA (ex: 450759cbecc9440ea2e6574b2e175353)

**Importante**: Se você estiver usando WAHA no localhost, será necessário expor o servidor com ngrok ou similar, ou usar uma instância WAHA hospedada na nuvem.

### 3. Deploy no Vercel

#### Opção A: Via Dashboard do Vercel

1. Acesse [vercel.com](https://vercel.com)
2. Clique em "New Project"
3. Importe o repositório do GitHub
4. Configure as variáveis de ambiente
5. Clique em "Deploy"

#### Opção B: Via CLI do Vercel

```bash
npm i -g vercel
vercel login
vercel --prod
```

### 4. Verificar o Deploy

Após o deploy, acesse a URL fornecida pelo Vercel. Você deverá ver a interface web.

Endpoints disponíveis:
- `GET /` - Interface web
- `GET /api/status` - Status da aplicação
- `POST /api/processar` - Processar laudo

## Estrutura de Arquivos

```
sistema-laudos/
├── automacao_hiago.py          # Aplicação Flask principal
├── wsgi.py                      # Ponto de entrada Vercel
├── vercel.json                  # Configuração Vercel
├── requirements.txt             # Dependências Python
├── Números de confiança LAB.csv # Contatos por local de origem
└── templates/
    └── index.html              # Interface web
```

## Arquivo CSV de Contatos

O arquivo `Números de confiança LAB.csv` deve ter o seguinte formato:

```csv
LocalOrigem,NumeroWhatsApp
HOSPITAL XYZ,5511999999999@c.us
CLINICA ABC,5511888888888@c.us
```

**Importante**:
- Os números devem terminar com `@c.us`
- Não deve haver espaços no número
- O cabeçalho deve ser exatamente `LocalOrigem,NumeroWhatsApp`

## Configuração do WAHA

### Opção 1: WAHA Local com ngrok

Se você está rodando WAHA localmente, use ngrok para expor:

```bash
ngrok http 4000
```

Depois configure a variável `WAHA_URL` no Vercel com a URL do ngrok:
```
https://seu-id.ngrok.io/api/sendFile
```

### Opção 2: WAHA Hospedado

Recomendado hospedar o WAHA em um servidor cloud (Railway, Render, etc.) e usar a URL pública.

## Teste da Aplicação

### Teste via Interface Web

1. Acesse a URL do Vercel
2. Digite um código de requisição
3. Clique em "Processar Laudo"
4. Verifique os logs

### Teste via API

```bash
curl -X POST https://seu-app.vercel.app/api/processar \
  -H "Content-Type: application/json" \
  -d '{"codRequisicao": "0202042034005"}'
```

## Troubleshooting

### Erro: Template não encontrado

Certifique-se que a pasta `templates` está no repositório e contém o `index.html`.

### Erro: CSV não encontrado

Verifique se o arquivo `Números de confiança LAB.csv` está na raiz do projeto.

### Erro: WAHA timeout

- Verifique se a URL do WAHA está correta
- Confirme que o WAHA está acessível publicamente
- Verifique se a API key está correta

### Erro: Nenhum destinatário encontrado

- Verifique se o LocalOrigem no CSV corresponde ao retornado pela API
- Confira se os números estão no formato correto (`@c.us`)

## Limitações do Vercel

- Timeout máximo de 10 segundos para funções serverless
- Não mantém estado entre requisições
- Arquivos estáticos não podem ser modificados em runtime

## Logs e Monitoramento

Acesse os logs no dashboard do Vercel em:
```
https://vercel.com/seu-usuario/seu-projeto/logs
```

## Suporte

Para problemas relacionados ao:
- **Vercel**: Consulte a [documentação oficial](https://vercel.com/docs)
- **WAHA**: Consulte o [repositório do WAHA](https://github.com/devlikeapro/waha)
- **API Lab**: Contate o administrador do laboratório
