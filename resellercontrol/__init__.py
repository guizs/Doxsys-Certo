from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import timedelta
from credenciais import dbname, dbusr, dbpwd, doxenv
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import os

# pip install mysql-connector-python
# import mysql

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['APPLICATION_ROOT'] = ''
app.static_url_path = '/static'
app.config['FORCE_PREFIX'] = ''

# Detecta ambiente
#ENV = os.environ.get("DOXSYS_ENV", "development")

# # Configura prefixo para ambiente de produção
# if ENV == "production":
#     # Produção com prefixo /doxsys
#     app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
#     app.config['APPLICATION_ROOT'] = '/doxsys'
#     app.config['FORCE_PREFIX'] = '/doxsys'
#     app.static_url_path = '/doxsys/static'
#
# else:
#     # Desenvolvimento sem prefixo
#     app.config['APPLICATION_ROOT'] = '/'
#     app.config['FORCE_PREFIX'] = ''

# Files
APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # refers to application_top
app.config['APP_STATIC'] = os.path.join(APP_ROOT, 'static')
# APP_STATIC = os.path.join(APP_ROOT, 'static')

# Para gerar a chave, abrir o Python no terminal:
# >>> import secrets
# >>> secrets.token_hex(16)
app.config['SECRET_KEY'] = 'd2253c2de975b2fc23f66a28d96720a5'
# csrf = CSRFProtect(app)  # Proteção CSRF ativada
# O CSRF Token pode falhar se as sessões do Flask não estiverem funcionando corretamente. Certifique-se de que as sessões estão ativadas:
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True

# CONEXÃO AO MYSQL - Mudar crenciais para Produção
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'+dbusr+':'+dbpwd+'@localhost:3306/' + dbname
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'false'
# app.config['SQLALCHEMY_ECHO'] = 1

if doxenv == 'production':
    app.config['SESSION_COOKIE_PATH'] = '/doxsys'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
else:
    # Ambiente de desenvolvimento: cookies padrão
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Variables
# app.config['MONTH'] = '08-2023'

# TIMEOUT USER
app.permanent_session_lifetime = timedelta(minutes=180)

database = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-info'

app.config['VERSION'] = 'v2025.15.07b'

from resellercontrol import routes

# Envelopa a aplicação com DispatcherMiddleware para funcionar sob o prefixo /doxsys
original_app = app
if doxenv == 'production':
    app = DispatcherMiddleware(None, {
        '/doxsys': original_app
    })

__all__ = ['app', 'original_app', 'database']

# MAIN
# git add .
# git commit -am 'v2025.15.07b - 18/07/2025 - MRR & ARR report arrumado!'
# git push
# SE QUISER VOLTAR UM COMMIT PARA A WORKSTATION:
# git log --oneline
# git reset --hard def5678  -> trocar esse código pelo commit desejado
# HISTÓRICO DE VERSÕES
# 'v2025.15.06 - 14/07/2025 - Weekly-Digest & colored home_msg'
# 'v2025.15.05 - 19/06/2025 - Ajustes na landing page e no módulo de versões'
# 'v2025.15.04 - 18/06/2025 - Armazena landing page access e Criação do módulo de versões'
# 'v2025.15.02 - 09/06/2025 - Criação do relatório Comercial totalizando as apresentações.'
# 'v2025.15.01 - 09/06/2025 - Inclusão da data de apresentação (pipeedit), dropdown usr e outros ajustes.'
# 'v2025.14.23 - 05/06/2025 - Tradução do espanhol com MyMemory Translated.'
# 'v2025.14.22 - 04/06/2025 - Correção de texto com LanguageTool.'
# 'v2025.14.21 - 03/06/2025 - Tratamento para ignorar msgs de grupo no Whatsapp.'
# 'v2025.14.20 - 02/06/2025 - Ajustes nos status das mensagens do Whatsapp.'
# 'v2025.14.19 - 28/05/2025 - Arrumado o dashboard.css o favicon.ico e a chamada no home.html'
# 'v2025.14.18 - 27/05/2025 - Whatsapp - Webhooks adicionais.'
# 'v2025.14.17 - 26/05/2025 - Whatsapp - Sales & Support.'
# 'v2025.14.16 - 23/05/2025 - Whatsapp - Nova interface.'
# 'v2025.14.15 - 23/05/2025 - Whatsapp - Novos testes com Instância do Suporte.'
# 'v2025.14.13 - 22/05/2025 - Whatsapp - Testes com Instância do Suporte.'
# 'v2025.14.12 - 19/05/2025 - DispatcherMiddleware para /doxsys.'
# 'v2025.14.11 - 14/05/2025 - Inclusão do prefix nas rotas e teste whatsapp.'
# 'v2025.14.10 - 14/05/2025 - Teste whatsapp.'
# 'v2025.14.09 - 07/05/2025 - Calculo do bonus técnico.'
# 'v2025.14.08 - 07/05/2025 - Finalização do relatório técnico.'
# 'v2025.14.07 - 25/04/2025 - Criação de relatório técnico.'
# 'v2025.14.06 - 23/04/2025 - Ajustes mostrar arquivo da proposta e botão voltar em algumas telas.'
# 'v2025.14.05 - 22/04/2025 - Inclusão de accesslevel no KBFAQ - conserto.'
# 'v2025.14.03 - 19/04/2025 - Criação do KBFAQ e arquivo de proposta.'
# 'v2025.14.02 - 04/04/2025 - Ajustes no form de edição do financeiro.'
# 'v2025.14.01 - 03/04/2025 - Gráfico de barras do financeiro.'
# 'v2024.13.03 - 31/10/2024 - Lista de cliente com contrato para novo projeto'
# 'v2024.13.02 - 25/10/2024 - Envio de emails - contracts digest'
# 'v2024.13.01 - 23/10/2024 - Envio de emails - pipeline digest'
# 'v2024.12.42 - 13/09/2024 - resultado.count() - relatorios mailing/pipeline'
# 'v2024.12.41 - 21/06/2024 - Formatação da busca do CNPJ no receitaws'
# 'v2024.12.40 - 21/06/2024 - Inclusão da busca do CNPJ no receitaws'
# 'v2024.12.39 - 07/05/2024 - Ajuste na data HOJE para FinancClose'
# 'v2024.12.38 - 01/04/2024 - Acerto na coluna de USER em Equipamentos'
# 'v2024.12.37 - 18/03/2024 - API CALL Inclusão da funcionalidade'
# 'v2024.12.36 - 05/03/2024 - Pipeline - ajuste na apresentação'
# 'v2024.12.35 - 29/02/2024 - Pipeline+Busca - agora busca em tudo'
# 'v2024.12.34 - 27/02/2024 - Mudança no RelatRealiz (Busca) e nos Links'
# 'v2024.12.33 - 01/02/2024 - Modulo Equipamentos'
# 'v2024.12.32 - 18/01/2024 - Serviços(revenda) incluído no report da W3K'
# 'v2023.12.31 - 05/01/2024 - fix week'
# 'v2023.12.30 - 12/12/2023 - fix DataHoje'
# 'v2023.12.28 - 10/11/2023 - Backlog em Propostas'
# 'v2023.12.27 - 18/10/2023 - Mais variáveis "session[]"'
# 'v2023.12.26 - 12/10/2023 - Implementado session['MESATL']'
# 'v2023.12.25 - 12/10/2023 - CHART.JS Inclusão de gráficos'
# 'v2023.12.24 - 07/10/2023 - bugfix Sigla do usuário'
# 'v2023.12.23 - 06/09/2023 - Novos botões para Nova Oportunidade e Nova Proposta'
# 'v2023.12.22 - 24/08/2023 - fix Vendedor no Pipeline'
# 'v2023.12.21 - 22/08/2023 - class globaldata substituiu app.config[MONTH]'
# 'v2023.12.20 - 21/08/2023 - fix HOME with app.config[MONTH]'
# 'v2023.12.19 - 17/08/2023 - Adjusts Client (colors)'
# 'v2023.12.18 - 14/08/2023 - Minor adjustment e Week Number'
# 'v2023.12.17 - 10/08/2023 - Fix Add Proposta e Inicialização de variáveis globais'
# version = 'v2023.12.16 - 08/08/2023 - Sigla do usuário e Reativação de contato'
# version = 'v2023.12.15 - 04/08/2023 - AJustes nos forms financ e relatprop'
# version = 'v2023.12.14 - 03/08/2023 - AJustes nos forms e relatprop'
# version = 'v2023.12.13 - 01/08/2023 - PROPOSTAS refeito e Relatorio COMERCIAL - v2'
# version = 'v2023.12.12 - 31/07/2023 - Relatorio COMERCIAL'
# version = 'v2023.12.11 - 30/07/2023 - Modais de Pipeline e Contrato em CLIENTE'
# version = 'v2023.12.10' - 26/07/2023 - Inclusão dos campos pipeline.LINKEXT e contato.MAILING'
# version = 'v2023.12.03' - 26/07/2023 - PIPELINE - Melhoria na usabilidade;
# version = 'v2023.12.02' - 25/07/2023 - PIPELINE - Ajustes;
# version = 'v2023.12.01' - 25/07/2023 - PIPELINE - Módulo criado, Dados Migrados;
# version = 'v2023.11.01' - 22/07/2023 - Migração dos contatos e clientes do CRM antigo;
# version = 'v2023.10.15' - 18/07/2023 - Ajuste nos botões de edição e deleção nas páginas de cliente e usuários;
# version = 'v2023.10.14' - 17/07/2023 - Ajuste na abertura e fechamento do sidebar, na página financeiro e na visualização mobile;
# version = 'v2023.10.13' - 11/07/2023 - Ajuste de tamanho dos formulários nas páginas de relatórios;
# version = 'v2023.10.12' - 30/06/2023 - Ajuste de tamanho e esçamento das tabelas;
# version = 'v2023.10.11' - 28/06/2023 - Ajustes e bugfix nos relatórios;
# version = 'v2023.10.9' - 20/06/2023 - MesFim p/ RelatForn;
# version = 'v2023.10.8' - 13/06/2023 - teste branch html;
# version = 'v2023.10.7' - dd/06/2023 - Usr=doxsys;
# version = 'v2023.10.6' - 29/05/2023 - Acerto no progresso percentual dos projetos e ordenação dos projetos
# version = 'v2023.10.5' - 24/05/2023 - incluído o nome do Vendedor nos Contratos
# version = 'v2023.10.4' - 27/04/2023 - desligando socketIO, teste de lentidão
# version = 'v2023.10.3' - 13/04/2023 - add new list-value ListaOpcoesDB
# version = 'v2023.10.2' - 28/02/2023 - timezone adjust & user timeout
# version = 'v2023.10.1' - 15/02/2023 - Log actions estendido e relatório Users Log criado
# version = 'v2022.9.5' - 22/12/2022 - Log Actions implementado
# version = 'v2022.9.4' - 15/12/2022 - Vendedor e Notas em Propostas
# version = 'v2022.9.3' - 14/12/2022 - Status e edição de Propostas
# version = 'v2022.9.1' - 06/12/2022 - Production - Financ com FATURADO
# version = 'v0.8.9.dev' - 04/12/2022 - VariablesDB, AddSaldo & Currency
# version = 'v0.8.8.dev' - 02/12/2022 - VariablesDB and AddSaldo
# version = 'v0.8.6.dev' - 01/12/2022 - Ajustes
# version = 'v0.8.5.dev' - 29/11/2022 - Previsão Financeiro SALDO
# version = 'v0.8.4.dev' - 29/11/2022 - Relatorio Financeiro PAGOS
# version = 'v0.8.3.dev' - 28/11/2022 - Eventos repetidos no Financeiro
# version = 'v0.8.2.dev' - 23/11/2022 - Relat com Previsão e Mergem EBITDA
# version = 'v0.7.7.dev' - 19/11/2022 - Conserto Relatório W3K - acerto p/ dez
# version = 'v0.7.6.dev' - 19/11/2022 - Conserto Relatório W3K
# version = 'v0.7.5.dev' - 19/11/2022 - Conserto em DTFIM do finaceiro, agora trata ano bissexto
# version = 'v0.7.4.dev' - 18/11/2022 - Ajustes no Financeiro e Relatórios
# version = 'v0.7.3.dev' - 16/11/2022 - Ajustes no Financeiro e Colapso do menu
# version = 'v0.7.2.dev' - 15/11/2022 - Financeiro com dados e opções de listas
# version = 'v0.7.1.dev' - 10/11/2022 - Contratos OrderBy Valid, Inclusão do Financeiro
# version = 'v0.6.3.dev' - 07/11/2022 - Msg de Alerta p/ Nivel da Credencial, aumento do Notas da Credencial para 1024 e bug fix em Propostas
# version = 'v0.6.2.dev' - 03/11/2022 - Chg Modulo Credenciais - Nivel 2 deu pau na inclusao
# version = "v0.6.1.dev" - 02/11/2022 - Inclusão do módulo de Credenciais
# version = "v0.5.20.dev" - 01/11/2022 - Inclusão das horas para controle do BackLog no módulo de Projetos
# version = "v0.5.18.dev" - 28/10/2022 - Alterações em links.html e ajustes em Propostas incluindo o modal para addprop

# Versioning
# Segundo o Semantic Versioning:
#
# O primeiro número indica que o sistema tem mudanças que o torna incompatível com versões anteriores;
# O segundo número indica que o sistema tem mudanças compatíveis com versões anteriores, dentro do primeiro número;
# O terceiro número indica que o sistema tem mudanças menores, como correções de bugs e funcionalidades que não prejudicam a compatibilidade com versões anteriores.
# Estado pode ser Alpha, Beta, dev, stable
