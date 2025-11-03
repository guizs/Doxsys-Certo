from flask import render_template, flash, redirect, url_for, request, session, make_response
from sqlalchemy import and_, or_, desc
#from sqlalchemy import not_, join, func
from sqlalchemy.sql import func
#from sqlalchemy.sql import literal_column
#from sqlalchemy.orm import aliased, joinedload
from collections import defaultdict
from resellercontrol import app, bcrypt, database
from resellercontrol.forms import FormLogin, FormEditarConta, FormCriarConta, FormAddProp, FormEditarPessoal, FormFinancScope, \
                                  FormEditarCliente, FormEditarContato, FormEditarContrato, FormEditarProjeto, FormFinancEdit, \
                                  FormEditarCredencial, FormFinancClose, FormFinancResult, FormFinancRealiz, FormAddSaldo, \
                                  FormEditCfg, FormUsersScope, FormAddLstOpc, FormSearchCli, FormEditarPipeline, FormSearchCont, \
                                  FormPipelineScope, FormRelatScope, FormRelatProp, FormEditarEquiptos, FormApiCall, FormFinancCfcs, \
                                  FormEditarKBFaq, FormScopeTecn, FormVersionEdit
from resellercontrol.models import usuario, ClientesDB, ContatoDB, PropostasDB, PessoalDB, FinancDB, LogDB, EquiptosDB, MsgDB, WebAccessDB,\
                                   ContratosDB, ListaOpcoesDB, ProjetosDB, CredencialDB, SaldoDB, ConfigDB, PipelineDB, KBFaqDB, VersionDB

from credenciais import doxenv, sender_email, sender_password, send_smtp_srv, \
                        ZAPI_CLIENT, ZAPI_INSTANCE_SUPP, ZAPI_TOKEN_SUPP, ZAPI_INSTANCE_SALES, ZAPI_TOKEN_SALES
from flask_login import login_user, logout_user, current_user, login_required
from datetime import date, time, datetime, timedelta
from dateutil.relativedelta import relativedelta
from urllib.parse import urljoin
from decimal import Decimal
# from time import strftime, strptime
# from zoneinfo import ZoneInfo
import json, pytz, os, re, locale
#import openai
import language_tool_python
from textwrap import dedent
import requests  # for API_CALL
import pandas as pd  # for API_CALL
# from flask_socketio import SocketIO, emit, disconnect
import smtplib, logging, traceback, base64, socket
from logging.handlers import TimedRotatingFileHandler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from werkzeug.utils import secure_filename

app_bp = Blueprint('app_bp', __name__)
whatsapp_bp = Blueprint('whatsapp_bp', __name__, url_prefix='/whatsapp')
# ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_SUPP}/token/{ZAPI_TOKEN_SUPP}/send-text"

# VARIÁVEIS GLOBAIS
# Configurações por tipo de mídia
MEDIA_CONFIGS = {
    'image': {
        'endpoint': '/send-image',
        'allowed_extensions': {'.jpg', '.jpeg', '.png', '.gif'},
        'mime_types': {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        },
        'payload_key': 'image'
    },
    'video': {
        'endpoint': '/send-video',
        'allowed_extensions': {'.mp4', '.mov', '.avi'},
        'mime_types': {
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo'
        },
        'payload_key': 'video'
    },
    'audio': {
        'endpoint': '/send-audio',
        'allowed_extensions': {'.mp3', '.ogg', '.wav'},
        'mime_types': {
            '.mp3': 'audio/mpeg',
            '.ogg': 'audio/ogg',
            '.wav': 'audio/wav'
        },
        'payload_key': 'audio'
    },
    'document': {
        'endpoint': '/send-document',
        'allowed_extensions': {'.pdf', '.xlsx', '.xls', '.doc', '.docx', '.ppt', '.pptx'},
        'mime_types': {
            '.pdf': 'application/pdf',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        },
        'payload_key': 'document'
    }
}

# Cria dicionário de extensão para tipo de mídia
EXTENSION_TO_MEDIA_TYPE = {}
for media_type, config in MEDIA_CONFIGS.items():
    for ext in config['allowed_extensions']:
        EXTENSION_TO_MEDIA_TYPE[ext] = media_type

MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB em bytes
UP_FOLDER = 'uploads'
DN_FOLDER = 'dnloads'
WA_FOLDER = 'whatsapp'
UPLOAD_FOLDER = os.path.join(WA_FOLDER, UP_FOLDER)
DNLOAD_FOLDER = os.path.join(WA_FOLDER, DN_FOLDER)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DNLOAD_FOLDER, exist_ok=True)
# Prefixo para usar nas chamadas para diferenciar ambiente de produção e de desenvolvimento
prefix = app.config.get('FORCE_PREFIX', '')  # Nâo deu certo, estou usando a variável doxenv

# socketio = SocketIO(app)

# Configuração do arquivo de log e URL
if doxenv == 'production':
    DXSURL = "https://www.doxsg.com/doxsys"
    # logging.basicConfig(filename='doxsys_log.txt', level=logging.ERROR, # logging.INFO,
    #                 format='%(asctime)s - %(levelname)s - %(message)s')

    # Diretório e nome do log
    log_dir = ""
    # os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "doxsys_log.txt")
    # Cria o handler de log rotativo por dia (1 backup por dia, manter 7 dias)
    handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8")
    handler.suffix = "%Y-%m-%d"  # adiciona a data no nome do log, ex: doxsys_log.txt.2025-05-22
    # Formato do log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # Aplica ao logger root
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # ou DEBUG para testes
    logger.addHandler(handler)
else:
    DXSURL = "http://127.0.0.1:5000"

# Usuários conectados
connected_users = set()
# Connected Users
# @socketio.on('connect')
# def handle_connect():
#     connected_users.add(request.sid)
#     # print(f"User {request.sid} connected. Total connected users: {len(connected_users)}")

# @socketio.on('disconnect')
# def handle_disconnect():
#     connected_users.remove(request.sid)
#     # print(f"User {request.sid} disconnected. Total connected users: {len(connected_users)}")

# - Número de linhas por listagem em tela
# em Propostas listamos (maxLines * 1.5) e no Financeiro a lista tem (maxLines * 15)
maxLines = 20
# DATAS
# - DATA DE HOJE
hoje = date.today()
hoje_formatado = hoje.strftime('%d/%m/%Y')
week = "{:02d}".format(hoje.isocalendar().week)
wyear = 'W'+(str(hoje.year))[2:] + week
data_atual = '{:02d}/{:02d}/{:02d}'.format(hoje.day, hoje.month, hoje.year)
mes_atual = '{:02d}-{:04d}'.format(hoje.month, hoje.year)
local_tz = datetime.now().astimezone().tzinfo
# # localdt = datetime.strptime(datetime.now(),"%H%M%S")
original_timezone = pytz.timezone('America/Sao_Paulo')

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error("🚨 Erro não tratado:")
    logging.error(traceback.format_exc())
    return "Erro interno do servidor", 500

# TIMEOUT USER
@app.before_request
def make_session_permanent():
    session.permanent = True

# - PARA PEGAR O IP DA DOX
def get_ip_from_hostname(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.gaierror as e:
        return None

# - IP DO USUÁRIO
def getusrip():
    if request.headers.getlist("X-Forwarded-For"):
        ipadr = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ipadr = request.remote_addr
    return request.environ.get('HTTP_X_REAL_IP', ipadr)

# - Dados do Usuário
def getusrnam(usr_id):
    usrdata = usuario.query.get(usr_id)
    return (usrdata.username)

# - Dados do Cliente
def getclient(cli_id):
    cliedtng = ClientesDB.query.get(cli_id)
    clidata = cliedtng.nomecliente + ' - ' + cliedtng.unidade
    return (clidata)

# LOG ACTION
def log_action(module, function, action):
    if current_user.is_authenticated and current_user.is_active:
        log_db = LogDB.query.order_by(LogDB.idlog.desc()).first()
        if (log_db.idusuario != current_user.id) or (log_db.acao != action):
            logact = LogDB(idusuario=current_user.id, datahora=datetime.now(), modulo=module, funcao=function, acao=action)
            database.session.add(logact)
            database.session.commit()
    # elif current_user.is_anonymous:
    else:
        logact = LogDB(idusuario=0, datahora=datetime.now(), modulo=module, funcao=function, acao=action)
        database.session.add(logact)
        database.session.commit()
    return 0

def listar_logins_por_ip(ipdox, data):
    inicio_dia = datetime.combine(data, time.min)
    fim_dia = datetime.combine(data, time.max)
    logs_login_hoje = LogDB.query.filter(
        LogDB.datahora >= inicio_dia,
        LogDB.datahora <= fim_dia,
        LogDB.modulo == 'usuarios',
        LogDB.funcao == 'login'
    ).order_by(LogDB.datahora.asc()).all()  # ordena por datahora ascendente
    usuarios_no_escritorio = []
    usuarios_fora_do_escritorio = []
    logins_registrados = {}  # chave = email, valor = (username, horario)
    for log in logs_login_hoje:
        email_match = re.search(r"Login:\s*([\w\.\-@]+)", log.acao)
        ip_match = re.search(r"IP:(\d+\.\d+\.\d+\.\d+)", log.acao)
        if not email_match or not ip_match:
            continue
        email = email_match.group(1)
        ipuser = ip_match.group(1)
        # Ignora se já registramos esse email
        if email in logins_registrados:
            continue
        usuario_encontrado = usuario.query.filter_by(email=email).first()
        if not usuario_encontrado:
            continue
        horario_login = log.datahora.strftime("%H:%M:%S")
        info = (usuario_encontrado.username, horario_login)
        logins_registrados[email] = info  # registra o primeiro login
        if ipuser == ipdox:
            usuarios_no_escritorio.append(info)
        else:
            usuarios_fora_do_escritorio.append(info)
    return usuarios_no_escritorio, usuarios_fora_do_escritorio

def is_adm5():
    return current_user.access >= 5

def is_ctl4():
    return current_user.access >= 4

def is_usr3():
    return current_user.access >= 3

def is_usr2():
    return current_user.access >= 2

def is_usr1():
    return current_user.access >= 1

# HOME PAGE
@app.route(f'{prefix}/')
def home():
    # inicializadatas()
    hoje = date.today()
    # hoje_formatado = hoje.strftime('%d/%m/%Y')
    week = "{:02d}".format(hoje.isocalendar().week)
    local_tz = datetime.now().astimezone().tzinfo
    original_timezone = pytz.timezone('America/Sao_Paulo')
    localtime = datetime.now().time().strftime("%H:%M")
    europe_tz = pytz.timezone('Europe/Paris')
    europetime = datetime.now(europe_tz).time().strftime("%H:%M")
    taiwan_tz = pytz.timezone('Asia/Taipei')
    taiwantime = datetime.now(taiwan_tz).time().strftime("%H:%M")
    # session["HOJE"] = hoje.isoformat()
    session["HOJE"] = hoje.strftime('%d/%m/%Y')
    session["WEEK"] = week
    session["WYEAR"] = 'W'+(str(hoje.year))[2:] + week
    session["LOCAL_TZ"] = 'America/Sao_Paulo'
    session["LOCALTIME"] = localtime
    session["EUROPE_TZ"] = 'Europe/Berlin'
    session["EUROPETIME"] = europetime
    session["TAIWAN_TZ"] = 'Asia/Taipei'
    session["TAIWANTIME"] = taiwantime

    ipdox = get_ip_from_hostname("doxsg.synology.me")
    users_in, users_out = listar_logins_por_ip(ipdox,date.today())

    # Ler comentários no arquivo static/home_msg.txt
    aviso = []
    with open(os.path.join(current_app.config['APP_STATIC'], 'home_msg.txt'), 'r', encoding="utf-8") as f:
        for line in f:
            if line[0:1] != '#':   # Retira as linhas comentadas
                aviso.append(line)

    return render_template('home.html', app=app, ipadr=getusrip(), ipdox=ipdox, users_in=users_in, users_out=users_out,hoje=data_atual, wyear=session["WYEAR"], connected_users=connected_users, aviso=aviso)

def pipeline_digest():
    usrlst = usuario.query.filter(usuario.access > 0).order_by(usuario.username.asc())
    for usrpipe in usrlst:
        listaactiv = database.session.query(PipelineDB, ClientesDB, usuario).select_from(PipelineDB).join(ClientesDB).join(
            usuario, usuario.id == PipelineDB.vendedor).filter(
            and_(PipelineDB.active == 1, PipelineDB.status == 'Ativo', PipelineDB.vendedor == usrpipe.id, PipelineDB.dtacao <= date.today())).order_by(PipelineDB.dtacao.desc()).all()
        if listaactiv:    # SOMENTE PARA TESTES -> and usrpipe.email == 'julio.paulino@doxsg.com':
            send_email_pipe(usrpipe.email, usrpipe.username, usrpipe.sigla, listaactiv)

def send_email_pipe(to_email, username, sigla, list):
    # sender_email = "admin@doxsg.com"
    # sender_password = "idom vkjq vclu ftwd"

    # Criar mensagem de e-mail
    message = MIMEMultipart("related")
    message["From"] = sender_email
    message["To"] = to_email
    # message["Cc"] = sender_email
    message["Subject"] = f"DOXSYS [{sigla}] - Digest diário do pipeline"

    # Gerar o HTML da tabela do pipeline
    pipeline_list = "<table border='1' cellpadding='5' cellspacing='0'>"
    pipeline_list += "<thead><tr><th>Cliente</th><th>Data Ação</th><th>Ação</th><th>Produto</th><th>Oportunidade</th></tr></thead><tbody>"
    for item in list:
        pipeline_list += (f"<tr><td>{item.ClientesDB.nomecliente}</td><td>{item.PipelineDB.dtacao.day:02d}/{item.PipelineDB.dtacao.month:02d}/{item.PipelineDB.dtacao.year}</td><td>{item.PipelineDB.acao}</td><td>{item.PipelineDB.produto}</td><td>{item.PipelineDB.oportunidade}</td></tr>")
    pipeline_list += "</tbody></table>"

    # Renderizar o template HTML e passar o valor de 'username'
    body = render_template('email_pipedigest.html', username=username, pipeline_list=pipeline_list)

    # Anexar corpo HTML ao e-mail
    message.attach(MIMEText(body, "html"))

    # Anexar a imagem (logomarca)
    logomarca = current_app.config['APP_STATIC'] + '/logo300x58.gif'
    with open(logomarca, 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header("Content-ID", "<logo_dox>")
        message.attach(img)

    # Enviar e-mail via Gmail SMTP
    try:
        server = smtplib.SMTP(send_smtp_srv, 587)
        server.starttls()  # Usar TLS
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())
        server.close()
        # logging.info(f'E-mail enviado com sucesso para {to_email} com {str(len(lista))} itens na lista!')
        log_action('pipeline', 'digest', 'Usr:' + to_email + ' Itens:' + str(len(list)))
        # print(f'E-mail enviado com sucesso para {to_email} com {str(len(lista))} clientes na lista!')
        # flash(f'E-mail enviado com sucesso para {to_email}', 'alert - success')
    except Exception as e:
        logging.error(f'Erro ao enviar e-mail para {to_email}: {str(e)}')
        # print(f'Erro ao enviar e-mail: {str(e)}')
        # flash(f'Erro ao enviar e-mail: {str(e)}', 'alert-danger')

def contracts_digest():
    usrlst = usuario.query.filter(and_(usuario.access > 0, (or_(usuario.role.like('%CT%'),usuario.role.like('%CM%'))))).order_by(usuario.username.asc()).all()
    hoje30 = date.today() + timedelta(days=30)
    contratos_vencidos = ContratosDB.query.filter(and_(ContratosDB.validadecontrato <= date.today(), ContratosDB.status == 'Ativo')).order_by(ContratosDB.validadecontrato.asc()).all()
    contratos_a_vencer = ContratosDB.query.filter(and_(ContratosDB.validadecontrato > date.today(), ContratosDB.validadecontrato <= hoje30, ContratosDB.status == 'Ativo')).order_by(ContratosDB.validadecontrato.asc()).all()
    for usr in usrlst:
        send_email_contracts(usr.email,usr.username,usr.sigla,contratos_vencidos,contratos_a_vencer)

def send_email_contracts(to_email, username, sigla, list_vencidos, list_a_vencer):
    # sender_email = "admin@doxsg.com"
    # sender_password = "idom vkjq vclu ftwd"

    # Criar mensagem de e-mail
    message = MIMEMultipart("related")
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = f"DOXSYS [{sigla}] - Vencimento de contratos"

    # Gerar o HTML da tabela do pipeline
    contracts_list_venc = "<table border='1' cellpadding='5' cellspacing='0'>"
    contracts_list_venc += "<thead><tr><th>Cliente</th><th>Unidade</th><th>Validade</th><th>Produto</th><th>Duração</th><th>Frequência</th></tr></thead><tbody>"
    for item in list_vencidos:
        contracts_list_venc += (f"<tr><td>{item.nomecliente}</td><td>{item.unidade}</td><td>{item.validadecontrato.day:02d}/{item.validadecontrato.month:02d}/{item.validadecontrato.year}</td><td>{item.produto}</td><td>{item.duracaocontrato}</td><td>{item.fatfrequencia}</td></tr>")
    contracts_list_venc += "</tbody></table>"

    contracts_lst_a_venc = "<table border='1' cellpadding='5' cellspacing='0'>"
    contracts_lst_a_venc += "<thead><tr><th>Cliente</th><th>Unidade</th><th>Validade</th><th>Produto</th><th>Duração</th><th>Frequência</th></tr></thead><tbody>"
    for item in list_a_vencer:
        contracts_lst_a_venc += (
            f"<tr><td>{item.nomecliente}</td><td>{item.unidade}</td><td>{item.validadecontrato.day:02d}/{item.validadecontrato.month:02d}/{item.validadecontrato.year}</td><td>{item.produto}</td><td>{item.duracaocontrato}</td><td>{item.fatfrequencia}</td></tr>")
    contracts_lst_a_venc += "</tbody></table>"

    # Renderizar o template HTML e passar o valor de 'username'
    body = render_template('email_contractdigest.html', username=username, contracts_list_venc=contracts_list_venc, contracts_lst_a_venc=contracts_lst_a_venc)

    # Anexar corpo HTML ao e-mail
    message.attach(MIMEText(body, "html"))

    # Anexar a imagem (logomarca)
    logomarca = current_app.config['APP_STATIC'] + '/logo300x58.gif'
    with open(logomarca, 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header("Content-ID", "<logo_dox>")
        message.attach(img)

    # Enviar e-mail via Gmail SMTP
    try:
        server = smtplib.SMTP(send_smtp_srv, 587)
        server.starttls()  # Usar TLS
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())
        server.close()
        log_action('contratos', 'digest', 'Usr:' + to_email + ' Itens:' + str(len(list_vencidos))+ '/' + str(len(list_a_vencer)))
    except Exception as e:
        logging.error(f'Erro ao enviar e-mail para {to_email}: {str(e)}')

    return jsonify({"status": "ok", "msg": "Email de contratos enviado!"}), 200

def send_email_zapi_disconnected(disconnected_info):
    # sender_email = "admin@doxsg.com"
    # sender_password = "idom vkjq vclu ftwd"
    to_email = "admin@doxsg.com"

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = f"⚠️ Instância Z-API {disconnected_info.instance_id} foi desconectada"

    corpo = f"""
    <html>
        <body>
            <p>Uma instância do Z-API foi desconectada:</p>
            <br><p>🔍 Detalhes:</p>
            <p><strong>Instância:</strong> {disconnected_info['instance_id']}</p>
            <p><strong>Dispositivo:</strong> {disconnected_info['device']}</p>
            <p><strong>Motivo:</strong> {disconnected_info['reason']}</p>
            <p><strong>Data/Hora:</strong> {disconnected_info['timestamp']}</p>
        </body>
    </html>
    """

    message.attach(MIMEText(corpo, "html"))

    try:
        server = smtplib.SMTP(send_smtp_srv, 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())
        server.close()
        logging.info(f"E-mail de desconexão enviado para {to_email}")
    except Exception as e:
        logging.error(f"Erro ao enviar e-mail de desconexão: {str(e)}")

    return jsonify({"status": "ok", "msg": "Email de alerta de desconexão Z-API enviado!"}), 200

@app.route(f'{prefix}/lp/<eml>,<fon>,<usr>', methods=['GET'])
def landing_page(eml,fon,usr):
    # Dados que podem ser obtidos da requisição
    user_agent = request.headers.get('User-Agent')
    remote_addr = request.remote_addr
    referrer = request.referrer
    accept_language = request.headers.get('Accept-Language')
    host = request.host
    full_path = request.full_path
    method = request.method
    args = request.args  # Parâmetros da query string
    # request.cookies # Se houver cookies enviados pelo navegador do usuário

    to_email = eml
    if fon:
        telefone = fon
        if len(telefone) >= 10:
            if usr:
                whatsapp_lp(telefone, f'{usr} acessou de {remote_addr} e quer informações!')
    else:
        telefone = 'Fone não fornecido!'

    # sender_email = "admin@doxsg.com"
    # sender_password = "idom vkjq vclu ftwd"

    wbaccs = WebAccessDB(
        datahora=datetime.now(),
        usr_email=(usr or 'Não disponível')[0:31],
        user_agent=(user_agent or 'Não disponível')[0:95],
        ipaddr=(remote_addr or 'Não disponível')[0:63],
        referrer=(referrer or 'Não disponível')[0:255],
        language=(accept_language or 'Não disponível')[0:63],
        host=(host or 'Não disponível')[0:31],
        full_path=(full_path or 'Não disponível')[0:255],
        httpmethod=(method or 'Não disponível')[0:15],
        querystr=(args or 'Nenhum')[0:255],
        notify=(telefone or '')[0:15])
    database.session.add(wbaccs)
    database.session.commit()

   # Criar mensagem de e-mail
    message = MIMEMultipart("related")
    message["From"] = "DOX WebSite<"+sender_email+">"
    message["To"] = to_email
    # message["Cc"] = sender_email
    message["Subject"] = f"DOXSYS [{usr}] - Acesso ao site da DOX"

    body = dedent(f"""
               <html>
                  <body>
                       <p>Usuário acessou a landing page com os seguintes dados:</p>
                       <ul>
                           <li><b>Email (informado):</b> {usr}</li>
                           <li><b>User-Agent (Navegador/Sistema Operacional):</b> {user_agent if user_agent else 'Não disponível'}</li>
                           <li><b>Endereço IP:</b> {remote_addr if remote_addr else 'Não disponível'}</li>
                           <li><b>Referência (Página Anterior):</b> {referrer if referrer else 'Não disponível'}</li>
                           <li><b>Idioma Preferencial:</b> {accept_language if accept_language else 'Não disponível'}</li>
                           <li><b>Host Acessado:</b> {host if host else 'Não disponível'}</li>
                           <li><b>Caminho Completo da URL:</b> {full_path if full_path else 'Não disponível'}</li>
                           <li><b>Método HTTP:</b> {method if method else 'Não disponível'}</li>
                           <li><b>Parâmetros da Query String:</b> {args if args else 'Nenhum'}</li>
                           <li><b>WA:</b> {telefone}</li>
                       </ul>
                       <br>
                       <p><b>DOXSYS</b></p>
                       <br>
                   </body>
               </html> """)

    # Anexar corpo HTML ao e-mail
    message.attach(MIMEText(body, "html"))

    # Anexar a imagem (logomarca)
    logomarca = current_app.config['APP_STATIC'] + '/logo300x58.gif'
    with open(logomarca, 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header("Content-ID", "<logo_dox>")
        message.attach(img)

    # Enviar e-mail via Gmail SMTP
    try:
        server = smtplib.SMTP(send_smtp_srv, 587)
        server.starttls()  # Usar TLS
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())
        server.close()
    except Exception as e:
        logging.error(f'Erro ao enviar e-mail de teste {to_email}: {str(e)}')

    return '', 204 # No Content

def whatsapp_lp(telefone, message):
    instzapi = 'Sales11970847098'
    ZAPI_INSTANCE = ZAPI_INSTANCE_SALES
    ZAPI_TOKEN = ZAPI_TOKEN_SALES
    usr_resp = 36 # Luciana

    phone = normalize_phone(telefone)

    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_CLIENT
    }
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
    payload = {
        "phone": phone,
        "message": '*DOX SG Ltda*: '+message
    }
    msg_salva = message
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        logging.error(f'Erro ao enviar whatsapp da landing page p/ {telefone}')

    return response.status_code

@app.route(f'{prefix}/ajustes', methods=['GET', 'POST'])
def ajustes():
    if current_user.access >= 4:
        form_addsaldo = FormAddSaldo()
        form_addsaldo.conta.data = 'ITAU-1669-390146'
        saldodb = SaldoDB.query.order_by(SaldoDB.idsaldo.desc()).first()
        form_addsaldo.saldo.data = saldodb.saldo
        form_addsaldo.aplic.data = saldodb.aplic
        form_addsaldo.variac.data = 0
        if form_addsaldo.validate_on_submit() and 'botao_submit_addsaldo' in request.form:
            contaform = request.form.get("conta")
            saldoform = request.form.get("saldo")
            aplicform = request.form.get("aplic")
            variaform = request.form.get("variac")
            obserform = request.form.get("observacao")
            if contaform and saldoform != saldodb.saldo:
                saldo = SaldoDB(idusuario=current_user.id, data=date.today(), conta=contaform,
                                saldo=saldoform, aplic=aplicform, variac=variaform, observacao=obserform)
                database.session.add(saldo)
                database.session.commit()
                flash(f'Saldo para {form_addsaldo.conta.data} adicionado com sucesso!', 'alert-success')
                log_action('home', 'addsaldo','Saldo:' + saldoform + ' Aplic:' + aplicform)
                return redirect(url_for('relatorios', mesatl=session['MESATL']))
            else:
                flash(f'Dados insuficientes! Preencha todos os valores.', 'alert-danger')

        form_addlstopc = FormAddLstOpc()
        # list/set - Remove os valores duplicados da lista
        form_addlstopc.lst.choices = list(set([(s.lst) for s in ListaOpcoesDB.query.all()]))
        form_addlstopc.lst.data = 'ClientForn'
        if form_addlstopc.validate_on_submit() and 'botao_submit_addlstopc' in request.form:
            lstform = request.form.get("lst")
            optform = request.form.get("opt")
            msgform = request.form.get("msg")
            cliforn = ListaOpcoesDB(lst=lstform, opt=optform, msg=msgform)
            database.session.add(cliforn)
            database.session.commit()
            flash(f'Incluido um {lstform} valor {optform} na lista de opções!', 'alert-success')
            log_action('home', 'addoptlst', 'Lista:' + lstform + ' Opção:' + optform + ' Msg:' + msgform)
            return redirect(url_for('relatorios', mesatl=session['MESATL']))

        variables = ConfigDB.query.order_by(ConfigDB.var.asc())
        lista_opcoes = ListaOpcoesDB.query.order_by(ListaOpcoesDB.lst.asc(), ListaOpcoesDB.opt.asc()).all()
    else:
        abort(403)
    return render_template('ajustes.html', variables=variables, form_addsaldo=form_addsaldo, form_addlstopc=form_addlstopc, lstopc=lista_opcoes)


@app.route(f'{prefix}/ajustedt,<idvar>', methods=['GET', 'POST'])
@login_required
def ajustedt(idvar):
    if current_user.access >= 4:
        variables = ConfigDB.query.order_by(ConfigDB.var.asc())
        form_varsedit = FormEditCfg()
        if idvar != '0':
            variable = ConfigDB.query.get(int(idvar))
            varname = variable.var
        else:
            variable = None
            varname = None

        form_varsedit.variable.data = variable.var
        form_varsedit.varvalue.data = variable.valor

        if form_varsedit.validate_on_submit() and 'botao_submit_editcfg' in request.form:
            variable.idusuario = current_user.id
            variable.dtalter = date.today()
            # variable.var = request.form.get('variable')
            variable.valor = request.form.get('varvalue')
            # database.session.add(variable)
            database.session.commit()
            flash(f'Variável {variable.var} alterada com sucesso!', 'alert-success')
            log_action('home', 'ajustes', 'Var:'+variable.var+' Valor:'+variable.valor)
            return redirect(url_for('ajustes'))
    else:
        abort(403)
    return render_template('ajustedt.html', idvar=idvar, varname=varname, form_varsedit=form_varsedit)

@app.route(f'{prefix}/doxsg')
def doxsg():
    if current_user.access >= 1:
        return render_template('doxsg.html')
    return render_template('home.html')

# Armazenar o cliente visto na lista de clientes visualizados pelo usuário
def include_hist(clnt):
    user = usuario.query.get(current_user.id)
    new_historico = []
    if user.cli_hist:
        historico = json.loads(user.cli_hist)
    else:
        historico = []

    try:
        achou = historico.index(clnt)
    except ValueError:
        new_historico.append(clnt)
        n = 0
        if len(historico) > 0:
                for item in historico:
                     n += 1
                     if n < 35 and n <= len(historico):
                         new_historico.append(item)
        user.cli_hist = json.dumps(new_historico)
        database.session.commit()
    return

@app.route(f'{prefix}/cliente/<cli_id>')
@login_required
def cliente(cli_id):
    cliente = ClientesDB.query.get(cli_id)
    if cliente:
        if cliente.idcliente:
            include_hist(cliente.idcliente)  # Armazenar o cliente visto na lista de clientes visualizados pelo usuário
            contatos = ContatoDB.query.filter(and_(ContatoDB.idcliente==cli_id, ContatoDB.active==1)).order_by(ContatoDB.nomecontato.asc())
            contat_del = ContatoDB.query.filter(and_(ContatoDB.idcliente == cli_id, ContatoDB.active == 0)).order_by(ContatoDB.nomecontato.asc())
            pipeline = PipelineDB.query.filter(and_(PipelineDB.idcliente==cli_id, PipelineDB.active==1))
            # contratos = ContratosDB.query.filter(and_(ContratosDB.status=='Ativo', ContratosDB.idcliente==cli_id))
            contratos = ContratosDB.query.filter(ContratosDB.idcliente == cli_id).order_by(ContratosDB.idcontrato.desc())
            propostas = PropostasDB.query.filter(PropostasDB.idcliente == cli_id).order_by(PropostasDB.idproposta.desc())
            return render_template('cliente.html', cliente=cliente, contatos=contatos, contat_del=contat_del, pipeline=pipeline, contratos=contratos, propostas=propostas)
    return

@app.route(f'{prefix}/clientes')
@login_required
def clientes():
    page = request.args.get('page', 1, type=int)
    Search = request.args.get('Search')
    clientes = ClientesDB.query.filter_by(active=1)
    if Search:
        clientes = clientes.filter(or_(ClientesDB.nomecliente.contains(Search), ClientesDB.unidade.contains(Search),
                                       ClientesDB.municipio.contains(Search), ClientesDB.cnpj.contains(Search)))
        # clientes = clientes.order_by(ClientesDB.nomecliente.asc()).paginate(page=page, per_page=maxLines)
    else:
        user = usuario.query.get(current_user.id) # Recupera a lista de clientes visualizados
        if user.cli_hist:
            historico = json.loads(user.cli_hist)
            cli0 = historico[0]
            if len(historico) == 1:
                pycommand = "clientes.filter(ClientesDB.idcliente == " +str(cli0) + " )"
            else:
                pycommand = "clientes.filter(or_"
                for cli in historico:
                    if cli == cli0:
                        pycommand = pycommand + "(ClientesDB.idcliente == " + str(cli)
                    else:
                        pycommand = pycommand + ",ClientesDB.idcliente == " + str(cli)
                pycommand = pycommand + "))"
            clientes = eval(pycommand)

    clientes = clientes.order_by(ClientesDB.nomecliente.asc()).paginate(page=page, per_page=maxLines*2)

    # link_to_pipeline = 'http://crm.doxsg.com.br/dox/pipeline/Add.asp?Acao=A&Id='
    # link_to_cadastro = 'http://crm.doxsg.com.br/dox/cadastro/Contato.asp?Cliente='
    log_action('clientes', 'clientes', 'Listagem de clientes.')
    return render_template('clientes.html', clientes=clientes, Search=Search)

@app.route(f'{prefix}/advsearch', methods=['GET', 'POST'])
@login_required
def advsearch():
    page = request.args.get('page', 1, type=int)
    Search = request.args.get('Search')
    form_search_cli = FormSearchCli()
    form_search_cont = FormSearchCont()
    resultcli = []
    resultcont = []

    #TODO INCLUIR STATUS
    if form_search_cli.validate_on_submit() and 'botao_submit_search_cli' in request.form:
        resultcli = database.session.query(ClientesDB).filter(and_(ClientesDB.active == 1,
             ClientesDB.nomecliente.contains(form_search_cli.nomecliente.data),
             ClientesDB.unidade.contains(form_search_cli.unidade.data),
             ClientesDB.razaosocial.contains(form_search_cli.razaosocial.data),
             ClientesDB.cnpj.contains(form_search_cli.cnpj.data),
             ClientesDB.inscrmunicipal.contains(form_search_cli.inscrmunicipal.data),
             ClientesDB.inscrestadual.contains(form_search_cli.inscrestadual.data),
             ClientesDB.municipio.contains(form_search_cli.municipio.data),
             ClientesDB.estado.contains(form_search_cli.estado.data),
             ClientesDB.pais.contains(form_search_cli.pais.data),
             ClientesDB.cep.contains(form_search_cli.cep.data),
             ClientesDB.endereco.contains(form_search_cli.endereco.data),
             ClientesDB.complemento.contains(form_search_cli.complemento.data),
             ClientesDB.telefone.contains(form_search_cli.telefone.data),
             ClientesDB.emailnfe.contains(form_search_cli.emailnfe.data),
             ClientesDB.website.contains(form_search_cli.website.data),
             ClientesDB.observacao.contains(form_search_cli.observacao.data)
            ))
        resultcli = resultcli.order_by(ClientesDB.nomecliente.asc()).paginate(page=page, per_page=maxLines*50)

    if form_search_cont.validate_on_submit() and 'botao_submit_search_cont' in request.form:
        resultcont = database.session.query(ClientesDB, ContatoDB) \
            .join(ContatoDB, ClientesDB.idcliente == ContatoDB.idcliente) \
            .filter(and_(ContatoDB.active == 1,
              ContatoDB.nomecontato.contains(form_search_cont.nomecontato.data),
              ContatoDB.mobile.contains(form_search_cont.mobile.data),
              ContatoDB.phone.contains(form_search_cont.phone.data),
              ContatoDB.email.contains(form_search_cont.email.data),
              ContatoDB.bizrole.contains(form_search_cont.bizrole.data),
              ContatoDB.departamento.contains(form_search_cont.departamento.data),
              ContatoDB.cargo.contains(form_search_cont.cargo.data),
              ContatoDB.observacao.contains(form_search_cont.observacao.data)
            ))
        resultcont = resultcont.order_by(ClientesDB.nomecliente.asc()).paginate(page=page, per_page=maxLines*50)

    return render_template('advsearch.html', resultcli=resultcli, resultcont=resultcont, form_search_cli=form_search_cli, form_search_cont=form_search_cont, Search=Search)

@app.route(f'{prefix}/links')
def links():
    return render_template('links.html')

@app.route(f'{prefix}/users')
@login_required
def users():
    usuarios = usuario.query.filter(usuario.access > 0).order_by(usuario.username.asc())
    usrnoaccess = usuario.query.filter(usuario.access == 0).order_by(usuario.username.asc())
    log_action('usuarios', 'users', 'Listagem de usuários')
    return render_template('users.html', usuarios=usuarios, usrnoaccess=usrnoaccess)

@app.route(f'{prefix}/usredit/<user_id>', methods=['GET', 'POST'])
@login_required
def usredit(user_id):
    usredtng = usuario.query.get(user_id)
    form_editarconta = FormEditarConta()
    form_editarconta.username.data = usredtng.username
    form_editarconta.sigla.data = usredtng.sigla
    form_editarconta.role.data = usredtng.role
    form_editarconta.email.data = usredtng.email
    form_editarconta.mobile.data = usredtng.mobile
    form_editarconta.phone.data = usredtng.phone
    form_editarconta.access.data = usredtng.access
    senha_crypt = usredtng.senha
    if form_editarconta.validate_on_submit() and 'botao_submit_editarconta' in request.form:
        if request.form.get('senha') != '':
            senha_crypt = bcrypt.generate_password_hash(request.form.get('senha'))
            flash('Senha alterada!', 'alert-success')
        usredtng.username = request.form.get('username')
        usredtng.sigla = request.form.get('sigla')
        usredtng.role = request.form.get('role')
        usredtng.email = request.form.get('email')
        usredtng.mobile = request.form.get('mobile')
        usredtng.phone = request.form.get('phone')
        usredtng.senha = senha_crypt
        usredtng.access = request.form.get('access')
        database.session.commit()
        flash(f'Dados editados para o e-mail {form_editarconta.email.data}', 'alert-success')
        log_action('usuarios', 'usredit', 'User:' + form_editarconta.email.data + ' editado.')
        return redirect(url_for('users'))
        #editou conta com sucesso
    return render_template('usredit.html', form_editarconta=form_editarconta)

@app.route(f'{prefix}/contedit/<cont_id>', methods=['GET', 'POST'])
@login_required
def contedit(cont_id):
    if current_user.access >= 3:
        form_editarcontato = FormEditarContato()
        contato = ContatoDB.query.get(cont_id)
        cli_id = contato.idcliente
        form_editarcontato.emphasis.data = contato.emphasis
        form_editarcontato.mailing.data = contato.mailing
        form_editarcontato.nomecontato.data = contato.nomecontato
        form_editarcontato.mobile.data = contato.mobile
        form_editarcontato.phone.data = contato.phone
        form_editarcontato.email.data = contato.email
        form_editarcontato.departamento.data = contato.departamento
        form_editarcontato.cargo.data = contato.cargo
        form_editarcontato.bizrole.data = contato.bizrole
        form_editarcontato.observacao.data = contato.observacao
        if form_editarcontato.validate_on_submit() and 'botao_submit_editarcontato' in request.form:
            contato.idcliente = cli_id
            if request.form.get('emphasis'):
                contato.emphasis = 1
            else:
                contato.emphasis = 0
            if request.form.get('mailing'):
                contato.mailing = 1
            else:
                contato.mailing = 0
            contato.idusuario = current_user.id
            contato.dtalter = date.today()
            contato.nomecontato = request.form.get('nomecontato')
            contato.mobile = request.form.get('mobile')
            contato.phone = request.form.get('phone')
            contato.email = request.form.get('email')
            contato.departamento = request.form.get('departamento')
            contato.cargo = request.form.get('cargo')
            contato.bizrole = request.form.get('bizrole')
            contato.observacao = request.form.get('observacao')
            database.session.commit()
            flash(f'Dados do contato {contato.nomecontato} editados com sucesso!', 'alert-success')
            log_action('contatos', 'contedit', 'Contato:' + contato.nomecontato + ' editado.')
            return redirect(url_for('cliente', cli_id=cli_id))
    else:
        abort(403)
    return render_template('contedit.html', form_editarcontato=form_editarcontato)


@app.route(f'{prefix}/contdel/<cont_id>/excluir', methods=['GET', 'POST'])
@login_required
def contdel(cont_id):
    if current_user.access >= 5:
        contact = ContatoDB.query.get(cont_id)
        cli_id = contact.idcliente
        database.session.delete(contact)
        database.session.commit()
        flash('Contato '+contact.nomecontato+' excluido com sucesso!', 'alert-danger')
        log_action('contatos', 'excluir', 'Contato:' + contact.nomecontato + ' excluido.')
        return redirect(url_for('cliente', cli_id=cli_id))
    else:
        abort(403)

@app.route(f'{prefix}/contactv/<cont_id>/ativar', methods=['GET', 'POST'])
@login_required
def contactv(cont_id):
    if current_user.access >= 5:
        contact = ContatoDB.query.get(cont_id)
        cli_id = contact.idcliente
        contact.active = 1
        database.session.commit()
        flash('Contato '+contact.nomecontato+' re-ativado com sucesso!', 'alert-danger')
        log_action('contatos', 'ativar', 'Contato:' + contact.nomecontato + ' re-ativado.')
        return redirect(url_for('cliente', cli_id=cli_id))
    else:
        abort(403)

@app.route(f'{prefix}/contadd/<cli_id>', methods=['GET', 'POST'])
@login_required
def contadd(cli_id):
    form_editarcontato = FormEditarContato()
    if form_editarcontato.validate_on_submit() and 'botao_submit_editarcontato' in request.form:
        if form_editarcontato.emphasis.data:
            enfatiz = 1
        else:
            enfatiz = 0
        if form_editarcontato.mailing.data:
            correio = 1
        else:
            correio = 0
        contato = ContatoDB(idcliente=cli_id, active=1, emphasis=enfatiz, mailing=correio, nomecontato=form_editarcontato.nomecontato.data,
                            mobile=form_editarcontato.mobile.data, idusuario=current_user.id, dtalter=date.today(),
                            phone=form_editarcontato.phone.data, email=form_editarcontato.email.data, bizrole=form_editarcontato.bizrole.data,
                            departamento=form_editarcontato.departamento.data, cargo=form_editarcontato.cargo.data,
                            observacao=form_editarcontato.observacao.data)
        database.session.add(contato)
        database.session.commit()
        flash(f'Contato {contato.nomecontato} criado com sucesso!', 'alert-success')
        log_action('contatos', 'contadd', 'Contato:' + contato.nomecontato + ' adicionado.')
        return redirect(url_for('cliente', cli_id=cli_id))
    return render_template('contedit.html', form_editarcontato=form_editarcontato)

@app.route(f'{prefix}/cliedit/<cli_id>', methods=['GET', 'POST'])
@login_required
def cliedit(cli_id):
    if current_user.access >= 3:
        form_editarcliente = FormEditarCliente()
        cliente = ClientesDB.query.get(cli_id)
        include_hist(cliente.idcliente)  # Armazenar o cliente visto na lista de clientes visualizados pelo usuário
        form_editarcliente.status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusCli')]
        if cliente.status:
            form_editarcliente.status.data = cliente.status
        else:
            form_editarcliente.status.data = "Prospect"
        form_editarcliente.nomecliente.data = cliente.nomecliente
        if cliente.unidade:
            form_editarcliente.unidade.data = cliente.unidade
        else:
            form_editarcliente.unidade.data = 'Matriz'
        form_editarcliente.razaosocial.data = cliente.razaosocial
        form_editarcliente.cnpj.data = cliente.cnpj
        form_editarcliente.inscrmunicipal.data = cliente.inscrmunicipal
        form_editarcliente.inscrestadual.data = cliente.inscrestadual
        form_editarcliente.municipio.data = cliente.municipio
        form_editarcliente.estado.data = cliente.estado
        form_editarcliente.pais.data = cliente.pais
        form_editarcliente.endereco.data = cliente.endereco
        form_editarcliente.complemento.data = cliente.complemento
        form_editarcliente.cep.data = cliente.cep
        form_editarcliente.telefone.data = cliente.telefone
        form_editarcliente.emailnfe.data = cliente.emailnfe
        form_editarcliente.linkcadastro.data = cliente.linkcadastro
        form_editarcliente.linkpipeline.data = cliente.linkpipeline
        form_editarcliente.website.data = cliente.website
        form_editarcliente.observacao.data = cliente.observacao
        if form_editarcliente.validate_on_submit() and 'botao_submit_editarcliente' in request.form:
            cliente.status = form_editarcliente.status.raw_data,
            cliente.idusuario = current_user.id
            cliente.dtalter = date.today()
            cliente.nomecliente = request.form.get('nomecliente')
            cliente.unidade = request.form.get('unidade')
            cliente.razaosocial = request.form.get('razaosocial')
            cliente.cnpj = request.form.get('cnpj')
            cliente.inscrmunicipal = request.form.get('inscrmunicipal')
            cliente.inscrestadual = request.form.get('inscrestadual')
            cliente.municipio = request.form.get('municipio')
            cliente.estado = request.form.get('estado')
            cliente.pais = request.form.get('pais')
            cliente.endereco = request.form.get('endereco')
            cliente.complemento = request.form.get('complemento')
            cliente.cep = request.form.get('cep')
            cliente.telefone = request.form.get('telefone')
            cliente.emailnfe = request.form.get('emailnfe')
            cliente.linkcadastro = request.form.get('linkcadastro')
            cliente.linkpipeline = request.form.get('linkpipeline')
            cliente.website = request.form.get('website')
            cliente.observacao = request.form.get('observacao')
            database.session.commit()
            flash(f'Dados do cliente {cliente.nomecliente} editados com sucesso!', 'alert-success')
            log_action('clientes', 'cliedit', 'Cliente:' + cliente.nomecliente + ' editado.')
            return redirect(url_for('clientes'))
    else:
        abort(403)
    return render_template('cliedit.html', form_editarcliente=form_editarcliente, cliente=cliente)

@app.route(f'{prefix}/proxy_cnpj/<cnpj>', methods=['GET'])
def proxy_cnpj(cnpj):
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    # response = requests.get(f'https://www.receitaws.com.br/v1/cnpj/{cnpj_limpo}')
    #return jsonify(response.json())
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; DOXSYS/1.0; +https://www.doxsg.com)'}
        response = requests.get(f'https://www.receitaws.com.br/v1/cnpj/{cnpj_limpo}', headers=headers, timeout=10)
        data = response.json()
        if 'status' in data and data['status'] == 'ERROR':
            return jsonify({'erro': f"Erro na consulta ao CNPJ: {data.get('message', 'Desconhecido')}"}), 400
        return jsonify(data)
    except Exception as e:
        return jsonify({'erro': f"Erro ao buscar dados do CNPJ: {str(e)}"}), 500


@app.route(f'{prefix}/fipe/<placa>', methods=['GET'])
def fipe(placa):
    placa_limpa = re.sub(r'[^a-zA-Z0-9]', '', placa).upper()
    url = f"https://placafipe.com/placa/{placa_limpa}"
    html = f"""
    <html>
    <head><title>Redirecionando...</title></head>
    <body>
      <script>
        window.open("{url}", "_blank", "width=800,height=600");
        window.location.href = "/";  // redireciona a página atual para home (ou feche se quiser)
      </script>
      <p>Se não foi redirecionado automaticamente, <a href="{url}" target="_blank">clique aqui</a>.</p>
    </body>
    </html>
    """
    # html = f"""
    #     <html>
    #     <head><title>Abrindo consulta da placa</title></head>
    #     <body>
    #       <script>
    #         window.open("{url}", "_blank", "width=800,height=600");
    #       </script>
    #       <p>A consulta da placa abriu em uma nova janela. Se nada aconteceu, <a href="{url}" target="_blank">clique aqui</a>.</p>
    #     </body>
    #     </html>
    #     """
    return render_template_string(html)

@app.route(f'{prefix}/cliadd', methods=['GET', 'POST'])
@login_required
def cliadd():
    form_editarcliente = FormEditarCliente()
    cliente = {"cliente": [{"nomecliente": "Cliente"}, {"unidade": "Unidade"}]}
    form_editarcliente.status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusCli')]
    if form_editarcliente.validate_on_submit() and 'botao_submit_editarcliente' in request.form:
        unid = form_editarcliente.unidade.data
        if not unid:
            unid = 'Matriz'
        cliente = ClientesDB(nomecliente=form_editarcliente.nomecliente.data, active=1, unidade=unid,
                               idusuario=current_user.id, dtalter=date.today(),
                               razaosocial=form_editarcliente.razaosocial.data, cnpj=form_editarcliente.cnpj.data, status=form_editarcliente.status.raw_data,
                               inscrmunicipal=form_editarcliente.inscrmunicipal.data, inscrestadual=form_editarcliente.inscrestadual.data,
                               municipio=form_editarcliente.municipio.data, estado=form_editarcliente.estado.data, pais=form_editarcliente.pais.data,
                               endereco=form_editarcliente.endereco.data, complemento=form_editarcliente.complemento.data, cep=form_editarcliente.cep.data,
                               telefone=form_editarcliente.telefone.data, emailnfe=form_editarcliente.emailnfe.data,
                               linkcadastro=form_editarcliente.linkcadastro.data, linkpipeline=form_editarcliente.linkpipeline.data,
                               website=form_editarcliente.website.data, observacao=form_editarcliente.observacao.data)
        database.session.add(cliente)
        database.session.commit()
        cliente = ClientesDB.query.order_by(ClientesDB.idcliente.desc()).first()
        include_hist(cliente.idcliente)  # Armazenar o cliente visto na lista de clientes visualizados pelo usuário
        flash(f'Cliente {cliente.nomecliente} criado com sucesso!', 'alert-success')
        log_action('clientes', 'cliadd', 'Cliente:' + cliente.nomecliente + ' adicionado.')
        return redirect(url_for('clientes'))
    return render_template('cliedit.html', form_editarcliente=form_editarcliente, cliente=cliente)

@app.route(f'{prefix}/kbfaq', methods=['GET', 'POST'])
@login_required
def kbfaq():
    page = request.args.get('page', 1, type=int)
    Search = request.args.get('Search')

    if Search:
        kbfaqs = (database.session.query(KBFaqDB).filter
                  (and_(current_user.access >= KBFaqDB.accesslevel),
                        (or_(KBFaqDB.categoria.contains(Search),KBFaqDB.titulo.contains(Search),KBFaqDB.descricao.contains(Search)))
                  )
                 )
        log_action('kbfaq', 'kbfaq', 'KBFaq search: (' + Search + ')')
    else:
        kbfaqs = database.session.query(KBFaqDB).filter(KBFaqDB.active == 1, current_user.access >= KBFaqDB.accesslevel)
        log_action('kbfaq', 'kbfaq', 'KBFaq listagem.')

    kbfaqs = kbfaqs.order_by(KBFaqDB.categoria.asc(), KBFaqDB.titulo.asc()).paginate(page=page, per_page=(maxLines*1.5))

    return render_template('kbfaq.html', kbfaqs=kbfaqs, Search=Search)

@app.route(f'{prefix}/kbfaqedt/<int:id>', methods=['GET', 'POST'])
@login_required
def kbfaqedt(id):
    form_kbfaq = FormEditarKBFaq()
    form_kbfaq.categoria.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='KBFaqCategor')]

    if id == 0:  # novo registro
        registro = KBFaqDB(active=1, dtcriac=date.today(), accesslevel=current_user.access)
        form_kbfaq.accesslevel.data = current_user.access
    else: # editar registro existente
        registro = KBFaqDB.query.get(id)
        form_kbfaq.accesslevel.data = registro.accesslevel
        form_kbfaq.categoria.data = registro.categoria
        form_kbfaq.titulo.data = registro.titulo
        form_kbfaq.descricao.data = registro.descricao

    if form_kbfaq.validate_on_submit() and 'botao_submit_editar_kbfaq' in request.form:
        registro.accesslevel = request.form.get('accesslevel')
        registro.categoria = request.form.get('categoria')
        registro.titulo = request.form.get('titulo')
        registro.descricao = request.form.get('descricao')
        registro.idusuario=current_user.id
        registro.dtalter = date.today()
        if not registro.accesslevel:
            registro.accesslevel = current_user.access
        if id == 0:
            database.session.add(registro)
            flash(f'KBFaq Categoria: {registro.categoria}, criado com sucesso!', 'alert-success')
            log_action('kbfaq', 'kbfaqadd', 'KBFaq Categor:' + registro.categoria + ' criado.')
        else:
            flash(f'KBFaq {registro.idkbfaq}. Categoria: {registro.categoria}, editado com sucesso!', 'alert-success')
            log_action('kbfaq', 'kbfaqedt', 'KBFaq:' + str(registro.idkbfaq) + ' editado.')

        database.session.commit()
        return redirect(url_for('kbfaq'))

    return render_template('kbfaqedt.html', kbfaq=registro, form_kbfaq=form_kbfaq)

@app.route(f'{prefix}/kbfaqdel/<int:id>')
@login_required
def kbfaqdel(id):
    if current_user.access > 3:
        registro = KBFaqDB.query.get(id)
        # database.session.delete(registro)
        registro.active = 0
        database.session.commit()
        flash(f'KBFaq {registro.idkbfaq}. Categoria: {registro.categoria}, apagado!', 'alert-success')
        log_action('kbfaq', 'kbfaqdel', 'KBFaq:' + str(registro.idkbfaq) + ' desativado.')
        return redirect(url_for('kbfaq'))
    else:
        abort(403)


@app.route(f'{prefix}/propostas/<orderby>', methods=['GET', 'POST'])
@login_required
def propostas(orderby):
    ordem = orderby
    form_addprop = FormAddProp()
    page = request.args.get('page', 1, type=int)
    Search = request.args.get('Search')

    form_addprop.status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusPrp')]
    form_addprop.status.data = 'Aberta'

    if Search:
        propostas = database.session.query(PropostasDB).filter(or_(PropostasDB.status.contains(Search),
                                                                   PropostasDB.vendedor.contains(Search),
                                                                   PropostasDB.nomecliente.contains(Search),
                                                                   PropostasDB.descricao.contains(Search)))
    else:
        propostas = database.session.query(PropostasDB).filter(PropostasDB.idproposta > 0)

    if ordem == 'c':
        propostas = propostas.order_by(PropostasDB.nomecliente.asc()).paginate(page=page, per_page=(maxLines*1.5))
    else:
        propostas = propostas.order_by(PropostasDB.idproposta.desc()).paginate(page=page, per_page=(maxLines*1.5))

    if form_addprop.validate_on_submit() and 'botao_submit_addprop' in request.form:
        if form_addprop.nomecliente.data and form_addprop.descricao.data:
            proposta = PropostasDB(status=form_addprop.status.raw_data,
                                idusuario=current_user.id,
                                dtalter=date.today(),
                                vendedor=form_addprop.vendedor.data,
                                nomecliente=form_addprop.nomecliente.data,
                                descricao=form_addprop.descricao.data,
                                arquivo=form_addprop.arquivo.data,
                                notas=form_addprop.notas.data,
                                dataprop=date.today())
            database.session.add(proposta)
            database.session.commit()
            flash(f'Proposta para {proposta.nomecliente} criada com sucesso!', 'alert-success')
            log_action('propostas', 'propadd', 'Proposta para:' + proposta.nomecliente + ' adicionada.')
            return redirect(url_for('propostas', orderby=ordem))

    return render_template('propostas.html', propostas=propostas, form_addprop=form_addprop, orderby=ordem, Search=Search)

@app.route(f'{prefix}/propadd/<idpipe>', methods=['GET', 'POST'])
@login_required
def propadd(idpipe):
        idprop = ''
        form_editprop = FormAddProp()
        pipeline = PipelineDB.query.get(idpipe)
        cliente = ClientesDB.query.get(pipeline.idcliente)
        vendor = usuario.query.get(pipeline.vendedor)

        form_editprop.status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusPrp')]
        form_editprop.status.data = 'Aberta'
        # usrlst = usuario.query.order_by(usuario.username.asc())
        # TODO PEGAR SOMENTE USUARIOS ATIVOS
        # form_editprop.idvendor.choices = [(s.id, s.username) for s in usrlst]
        form_editprop.idvendor.choices = [(s.id, s.username) for s in
               usuario.query.filter(or_(usuario.role.contains('VD'),usuario.role.contains('IS'),usuario.role.contains('CM')),usuario.access > 0)
               .order_by(usuario.username.asc())]
        form_editprop.idvendor.data = vendor.id
        form_editprop.vlrsoft.data = 0
        form_editprop.vlrserv.data = 0
        form_editprop.horasprev.data = 0
        form_editprop.periodo.data = 0
        form_editprop.descricao.data = 'PROP / CR0'
        form_editprop.arquivo.data = 'C:\\DOX-COML\\CLIENTES\\'

        if form_editprop.validate_on_submit() and 'botao_submit_addprop' in request.form:
            clnt = cliente.nomecliente + ' - ' + cliente.unidade
            clnt = clnt[0:44]
            proposta = PropostasDB(status=form_editprop.status.raw_data,
                                   idusuario=current_user.id,
                                   dtalter=date.today(),
                                   idvendor = vendor.id,
                                   vendedor = vendor.username,
                                   idpipeline = pipeline.idpipeline,
                                   nomecliente = clnt,
                                   idcliente = cliente.idcliente,
                                   dtprovavel = form_editprop.dtprovavel.data,
                                   forecast = form_editprop.forecast.data,
                                   vlrsoft = request.form.get('vlrsoft'),
                                   vlrserv = request.form.get('vlrserv'),
                                   horasprev = request.form.get('horasprev'),
                                   periodo = request.form.get('periodo'),
                                   renovac = form_editprop.renovac.data,
                                   descricao=request.form.get('descricao'),
                                   arquivo=request.form.get('arquivo'),
                                   notas=form_editprop.notas.data,
                                   dataprop=date.today())

            database.session.add(proposta)
            database.session.commit()
            flash(f'Proposta para {cliente.nomecliente} editada com sucesso!', 'alert-success')
            log_action('propostas', 'propadd',
                       'Proposta p/ op ' + idpipe + ' cliente:' + cliente.nomecliente + ' adicionada.')
            return redirect(url_for('propostas', orderby='n'))

        return render_template('propedit.html', form_editprop=form_editprop, idprop=idprop, cliente=cliente, vendor=vendor)

@app.route(f'{prefix}/propedit/<idprop>', methods=['GET', 'POST'])
@login_required
def propedit(idprop):
    form_editprop = FormAddProp()
    proposta = PropostasDB.query.get(idprop)
    pipeline = PipelineDB.query.get(proposta.idpipeline)
    cliente = ClientesDB.query.get(proposta.idcliente)
    form_editprop.status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusPrp')]
    form_editprop.status.data = proposta.status
    form_editprop.descricao.data = proposta.descricao
    form_editprop.arquivo.data = proposta.arquivo
    form_editprop.notas.data = proposta.notas
    # usrlst = usuario.query.order_by(usuario.username.asc())
    # TODO PEGAR SOMENTE USUARIOS ATIVOS
    # form_editprop.idvendor.choices = [(s.id, s.username) for s in usrlst]
    form_editprop.idvendor.choices = [(s.id, s.username) for s in
                                      usuario.query.filter(or_(usuario.role.contains('VD'), usuario.role.contains('IS'),
                                      usuario.role.contains('CM')), usuario.access > 0).order_by(usuario.username.asc())]
    form_editprop.idvendor.data = str(proposta.idvendor)
    if proposta.dtprovavel:
        form_editprop.dtprovavel.data = proposta.dtprovavel
    else:
        form_editprop.dtprovavel.data = date.today() + timedelta(days=30)
    form_editprop.forecast.data = proposta.forecast
    form_editprop.vlrsoft.data = proposta.vlrsoft
    form_editprop.vlrserv.data = proposta.vlrserv
    form_editprop.horasprev.data = proposta.horasprev
    form_editprop.periodo.data = proposta.periodo
    form_editprop.renovac.data = proposta.renovac

    if form_editprop.validate_on_submit() and 'botao_submit_addprop' in request.form:
        vendor = usuario.query.get(int(request.form.get('idvendor')))
        proposta.status = form_editprop.status.raw_data
        proposta.idusuario = current_user.id
        proposta.dtalter = date.today()
        proposta.idvendor = vendor.id
        proposta.vendedor = vendor.username
        proposta.dtprovavel = request.form.get('dtprovavel')
        proposta.forecast = request.form.get('forecast')
        proposta.vlrsoft = request.form.get('vlrsoft')
        proposta.vlrserv = request.form.get('vlrserv')
        proposta.horasprev = request.form.get('horasprev')
        proposta.periodo = request.form.get('periodo')
        if request.form.get('renovac'):
            proposta.renovac = 1
        else:
            proposta.renovac = 0
        proposta.descricao = request.form.get('descricao')
        proposta.arquivo = request.form.get('arquivo')
        proposta.notas = request.form.get('notas')
        database.session.commit()
        flash(f'Proposta para {proposta.nomecliente} editada com sucesso!', 'alert-success')
        log_action('propostas', 'propedit', 'Proposta ' + idprop + ' para:' + proposta.nomecliente + ' editada.')
        return redirect(url_for('propostas', orderby='n'))

    return render_template('propedit.html', form_editprop=form_editprop, idprop=idprop, proposta=proposta, cliente=cliente, pipeline=pipeline)

@app.route(f'{prefix}/login', methods=['GET', 'POST'])
def login():
    ipadr = getusrip()
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    # DEBUG DO FORM LOGIN
    # print("Form Login validado?", form_login.validate_on_submit())
    # print("Erros no Form Login:", form_login.errors)

    if 'botao_submit_login' in request.form and form_login.validate_on_submit():
        utilizador = usuario.query.filter_by(email=form_login.email.data).first()
        if utilizador and bcrypt.check_password_hash(utilizador.senha, form_login.senha.data):
            login_user(utilizador, remember=form_login.lembrar_dados.data)
            # handle_connect()
            flash(f'Login feito com sucesso no e-mail {form_login.email.data}', 'alert-success')
            log_action('usuarios', 'login', 'Login: ' + form_login.email.data + ' (OK!). IP:' + ipadr)
            session['MESATL'] = '{:02d}-{:02d}'.format(hoje.month, hoje.year)
            session['MESFIM'] = '{:02d}-{:02d}'.format(hoje.month, hoje.year)
            param_next = request.args.get('next')
            if param_next:
                return redirect(param_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Falha no login. E-mail ou senha incorretos!', 'alert-danger')
            log_action('usuarios', 'login', 'IP:' + ipadr + ' FAIL: ' + form_login.email.data + ' (não entrou).')
            return redirect(url_for('home'))
            # redirecionar para a home page

    # DEBUG DO FORM CRIAR_CONTA
    # print("Form Criar Conta validado?", form_criarconta.validate_on_submit())
    # print("Erros no Form Criar Conta:", form_criarconta.errors)

    if 'botao_submit_criarconta' in request.form and form_criarconta.validate_on_submit():
        senha_crypt = bcrypt.generate_password_hash(form_criarconta.senha.data)
        utilizador = usuario(username=form_criarconta.username.data,
                             email=form_criarconta.email.data,
                             sigla=form_criarconta.username.data[:3].upper(),
                             mobile=form_criarconta.mobile.data,
                             phone=form_criarconta.phone.data,
                             senha=senha_crypt,
                             access=0)
        database.session.add(utilizador)
        database.session.commit()
        flash(f'Conta criada para o e-mail {form_criarconta.email.data}', 'alert-success')
        log_action('usuarios', 'usradd','Conta ' + utilizador.username + '(' + utilizador.email + ') criada.')
        return redirect(url_for('home'))
        #criou conta com sucesso

    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)

@app.route(f'{prefix}/sair')
@login_required
def sair():
    ipadr = getusrip()
    log_action('usuarios', 'logout', 'Usuario fez logout. IP:' + ipadr)
    log_action('usuarios', 'logout', '')
    # handle_disconnect()
    logout_user()
    flash('Logout feito com sucesso!', 'alert-success')
    return redirect(url_for('home'))


@app.route(f'{prefix}/users/<user_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_usuario(user_id):
    usredtng = usuario.query.get(user_id)
    if current_user.access >= 3:
        if current_user.id != usredtng.id:      # if current_user.username != usredtng.username:
            database.session.delete(usredtng)
            database.session.commit()
            flash('Usuario excluido com sucesso!', 'alert-danger')
            log_action('usuarios', 'excluir', 'User:' + usredtng.username + ' excluido.')
            return redirect(url_for('users'))
        else:
            abort(403)
    else:
        abort(403)

@app.route(f'{prefix}/clientes/<cli_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_cliente(cli_id):
    cliedtng = ClientesDB.query.get(cli_id)
    if current_user.access >= 3:
        cliedtng.active = 0
        #database.session.delete(cliedtng)
        database.session.commit()
        flash('Cliente excluido com sucesso!', 'alert-danger')
        log_action('clientes', 'excluir', 'Cliente:' + cliedtng.nomecliente + ' excluido.')
        return redirect(url_for('clientes'))
    else:
        abort(403)

@app.route(f'{prefix}/cliente/<cont_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_contato(cont_id):
    contedtng = ContatoDB.query.get(cont_id)
    cli_id = contedtng.idcliente
    if current_user.access >= 3:
        contedtng.active = 0
        # database.session.delete(contedtng)
        database.session.commit()
        flash('Contato excluido com sucesso!', 'alert-danger')
        log_action('contatos', 'excluir', 'Contato:' + contedtng.nomecontato + ' excluido.')
        return redirect(url_for('cliente', cli_id=cli_id))
    else:
        abort(403)

@app.route(f'{prefix}/pipeline/<pipe_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_pipeline(pipe_id):
    pipedtng = PipelineDB.query.get(pipe_id)
    cli_id = pipedtng.idcliente
    if current_user.access >= 3:
        pipedtng.active = 0
        # database.session.delete(pipedtng)
        database.session.commit()
        flash('Oportunidade excluida com sucesso!', 'alert-danger')
        log_action('pipeline', 'excluir', 'Oportunidade:' + pipe_id + ' excluida.')
        return redirect(url_for('pipeline', status='Ativo', vendr='00', mrkt='t' , prodt='-', orderby='C'))
    else:
        abort(403)


@app.route(f'{prefix}/cadastro/<cli_id>')
def cadastro(cli_id):
    link_to_page = 'http://crm.doxsg.com.br/dox/cadastro/Contato.asp?Cliente=' + cli_id
    return render_template(link_to_page)


@app.route(f'{prefix}/contractedit/<contract_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_contrato(contract_id):
    contrato = ContratosDB.query.get(contract_id)
    if current_user.access >= 3:
        database.session.delete(contrato)
        database.session.commit()
        flash(f'Contrato {contrato.nomecliente} - {contrato.unidade} excluido com sucesso!', 'alert-danger')
        log_action('contratos', 'excluir', 'Contrato:' + contrato.nomecliente + ' - ' + contrato.unidade + ' excluido.')
        return redirect(url_for('contratos', status='ativo', orderby='v'))
    else:
        abort(403)

@app.route(f'{prefix}/pipeline/<status>,<vendr>,<mrkt>,<prodt>,<orderby>', methods=['GET', 'POST'])
@login_required
def pipeline(status,vendr,mrkt,prodt,orderby):
    page = request.args.get('page', 1, type=int)
    Search = request.args.get('Search')
    varextlnk = ConfigDB.query.filter_by(var='extLink').first().valor
    # INNER JOIN entre PipelineDB, ClientesDB e usuario
    if status == 'Todos':
        pipeline = database.session.query(PipelineDB, ClientesDB, usuario).select_from(PipelineDB).join(ClientesDB).join(usuario, usuario.id == PipelineDB.vendedor).filter(PipelineDB.active == 1)
    else:
        pipeline = database.session.query(PipelineDB, ClientesDB, usuario).select_from(PipelineDB).join(ClientesDB).join(usuario, usuario.id == PipelineDB.vendedor).filter(and_(PipelineDB.active == 1, PipelineDB.status == status))

    vend_atual = vendr
    if Search:
        pipeline = database.session.query(PipelineDB, ClientesDB, usuario).select_from(PipelineDB).join(ClientesDB).join(usuario, usuario.id == PipelineDB.vendedor).filter(PipelineDB.active == 1)
        pipeline = pipeline.filter(or_(ClientesDB.nomecliente.contains(Search), ClientesDB.unidade.contains(Search),
                     PipelineDB.produto.contains(Search), PipelineDB.acao.contains(Search), PipelineDB.historico.contains(Search),
                     PipelineDB.concorrentes.contains(Search), PipelineDB.oportunidade.contains(Search), PipelineDB.mercado.contains(Search)))
    else:
        if vendr == '0':
            vend_atual = '0'
        elif vendr == '00':
            vend_atual = str(current_user.id)
            pipeline = pipeline.filter(PipelineDB.vendedor == vend_atual)
        else:
            pipeline = pipeline.filter(PipelineDB.vendedor == vend_atual)
            #  pipeline = pipeline.filter(PipelineDB.vendedor == int(vendr))

        if mrkt != 't':
            pipeline = pipeline.filter(PipelineDB.mercado.contains(mrkt))
        if prodt != '-':
            pipeline = pipeline.filter(PipelineDB.produto.contains(prodt))

    # for registro in pipeline:
    #     historico = registro.PipelineDB.historico
    #     historico_lines = historico.split('\n')
    #     formatted_lines = []
    #     for line in historico_lines:
    #         # Usar regex para encontrar e destacar datas seguidas por 8 caracteres
    #         formatted_line = re.sub(r'(\d{2}/\d{2}/\d{4} [A-Za-z0-9]{8})', r'<span style="font-weight: bold; text-decoration: underline;">\1</span>', line)
    #         formatted_lines.append(formatted_line)
    #     registro.PipelineDB.historico = formatted_lines



    # pipeline = pipeprior.union(pipereglr)
    # result = session.execute(pipeline).scalars().all()

    if orderby == 'C':
        pipeline = pipeline.order_by(PipelineDB.prioridade.desc(), ClientesDB.nomecliente.asc())
    elif orderby == 'D':
        pipeline = pipeline.order_by(PipelineDB.prioridade.desc(), PipelineDB.dtacao.desc())

    pipeline = pipeline.paginate(page=page, per_page=maxLines)

    form_scope = FormPipelineScope()
    # PEGAR SOMENTE USUARIOS ATIVOS
    #usrlst = usuario.query.filter(usuario.access > 0).order_by(usuario.username.asc())
    #form_scope.select_vendr.choices = [("0","Todos")] + [(s.id, s.username) for s in usrlst]
    form_scope.select_vendr.choices = [("0", "Todos")] + [(s.id, s.username) for s in
                         usuario.query.filter(or_(usuario.role.contains('VD'), usuario.role.contains('IS'),
                         usuario.role.contains('CM')), usuario.access > 0).order_by(usuario.username.asc())]
    form_scope.select_vendr.data = vend_atual
    form_scope.select_prd.choices = [('-','Todos')] + [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Produto')]
    form_scope.select_prd.data = prodt
    form_scope.select_stat.choices =  [('Todos','Todos')] + [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusPipe')]
    form_scope.select_stat.data = status
    form_scope.select_mkt.choices =  [('t', 'Todos')] + [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Mercado')]
    form_scope.select_mkt.data = mrkt
    if form_scope.validate_on_submit() or 'botao_submit_pipescope' in request.form:
        vendr = form_scope.select_vendr.raw_data[0]
        prodt = form_scope.select_prd.raw_data[0]
        status = form_scope.select_stat.raw_data[0]
        mrkt = form_scope.select_mkt.raw_data[0]
        return redirect(url_for('pipeline', status=status, vendr=vendr, mrkt=mrkt , prodt=prodt, orderby=orderby))

    return render_template('pipeline.html', pipeline=pipeline, status=status, vendr=vendr, mrkt=mrkt , prodt=prodt, orderby=orderby, form_scope=form_scope, hoje=hoje, varextlnk=varextlnk)

@app.route(f'{prefix}/pipeedit/<pipeline_id>', methods=['GET', 'POST'])
@login_required
def pipeedit(pipeline_id):
    if current_user.access >= 3 and pipeline_id != 'dashboard.css':
        form_editarpipeline = FormEditarPipeline()
        pipeline = PipelineDB.query.get(pipeline_id)
        if pipeline:
            cliente = ClientesDB.query.get(pipeline.idcliente)
            vendedor = usuario.query.get(pipeline.vendedor)
            if vendedor:
                v_id = str(vendedor.id)
            else:
                v_id = current_user.id
        else:
            flash(f'Erro: PipelineID {pipeline_id} não encontrado!', 'alert-danger')
            abort(403)
        # PEGAR SOMENTE USUARIOS ATIVOS
        # usrlst = usuario.query.filter(usuario.access > 0).order_by(usuario.username.asc())
        # form_editarpipeline.vendedor.choices = [(s.id, s.username) for s in usrlst ]
        form_editarpipeline.vendedor.choices = [(s.id, s.username) for s in usuario.query.filter(or_(usuario.role.contains('VD'),
                    usuario.role.contains('IS'), usuario.role.contains('CM')), usuario.access > 0).order_by(usuario.username.asc())]
        clientes = ClientesDB.query.filter_by(active=1).order_by(ClientesDB.nomecliente.asc())
        form_editarpipeline.select_cliente.choices = [(s.idcliente, s.nomecliente + ' - ' + s.unidade) for s in clientes ]
        form_editarpipeline.select_cliente.data = cliente.nomecliente + ' - ' + cliente.unidade
        form_editarpipeline.vendedor.data = v_id
        form_editarpipeline.produto.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Produto')]
        form_editarpipeline.produto.data = pipeline.produto
        form_editarpipeline.status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusPipe')]
        form_editarpipeline.status.data = pipeline.status
        form_editarpipeline.mercado.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Mercado')]
        form_editarpipeline.mercado.data = pipeline.mercado
        form_editarpipeline.prazo.data = pipeline.prazo
        form_editarpipeline.oportunidade.data = pipeline.oportunidade
        form_editarpipeline.facilit.data = pipeline.facilit
        form_editarpipeline.decisor.data = pipeline.decisor
        form_editarpipeline.concorrentes.data = pipeline.concorrentes
        form_editarpipeline.linkext.data = pipeline.linkext
        form_editarpipeline.acao.data = pipeline.acao
        form_editarpipeline.dtacao.data = pipeline.dtacao
        form_editarpipeline.dtapres.data = pipeline.dtapres
        form_editarpipeline.historico.data = session["HOJE"] + ' ' + session["WYEAR"] + str(current_user.sigla) + ':\n' + pipeline.historico
        form_editarpipeline.prioridade.data = pipeline.prioridade

        if form_editarpipeline.validate_on_submit() and 'botao_submit_editarpipeline' in request.form:
            pipeline.idusuario = current_user.id
            pipeline.dtalter = date.today()
            pipeline.produto = form_editarpipeline.produto.raw_data
            pipeline.vendedor = form_editarpipeline.vendedor.raw_data
            pipeline.status = form_editarpipeline.status.raw_data
            pipeline.mercado = form_editarpipeline.mercado.raw_data
            if request.form.get('prioridade'):
                pipeline.prioridade = 1
            else:
                pipeline.prioridade = 0
            pipeline.prazo = request.form.get('prazo')
            pipeline.oportunidade = request.form.get('oportunidade')
            pipeline.facilit = request.form.get('facilit')
            pipeline.decisor = request.form.get('decisor')
            pipeline.concorrentes = request.form.get('concorrentes')
            pipeline.linkext = request.form.get('linkext')
            pipeline.acao = request.form.get('acao')
            pipeline.dtacao = request.form.get('dtacao')
            pipeline.dtapres = request.form.get('dtapres') or None
            pipeline.historico = request.form.get('historico')

            database.session.commit()
            flash(f'Dados da oportunidade {cliente.nomecliente} - {cliente.unidade} editados com sucesso!', 'alert-success')
            log_action('pipeline', 'pipeline_edit', 'Oportunidade p/:' + cliente.nomecliente + ' - ' + cliente.unidade + ' alterado.')
            #return redirect(url_for('pipeline', status='Todos'))
            return redirect(url_for('cliente', cli_id=cliente.idcliente))
    else:
        abort(403)
    return render_template('pipeedit.html', form_editarpipeline=form_editarpipeline, pipeline=pipeline, cliente=cliente)

@app.route(f'{prefix}/pipelineadd/<cli_id>', methods=['GET', 'POST'])
@login_required
def pipelineadd(cli_id):
    pipeline = "NEW"
    form_editarpipeline = FormEditarPipeline()
    if cli_id == "0":
        clientes = ClientesDB.query.filter_by(active=1)
    else:
        clientes = ClientesDB.query.filter(and_(ClientesDB.active==1, ClientesDB.idcliente==int(cli_id)))

    form_editarpipeline.select_cliente.choices = [(s.idcliente, s.nomecliente + ' - ' + s.unidade)
                                                  for s in clientes.order_by(ClientesDB.nomecliente.asc())]
    # PEGAR SOMENTE USUARIOS ATIVOS
    # usrlst = usuario.query.filter(usuario.access > 0).order_by(usuario.username.asc())
    # form_editarpipeline.vendedor.choices = [(s.id, s.username) for s in usrlst ]
    form_editarpipeline.vendedor.choices = [(s.id, s.username) for s in usuario.query.filter(or_(usuario.role.contains('VD'),
                        usuario.role.contains('IS'),usuario.role.contains('CM')),usuario.access > 0).order_by(usuario.username.asc())]
    form_editarpipeline.vendedor.data = str(current_user.id)
    form_editarpipeline.produto.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Produto')]
    form_editarpipeline.status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusPipe')]
    form_editarpipeline.mercado.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Mercado')]
    form_editarpipeline.prazo.data = date.today() + timedelta(days=365)
    form_editarpipeline.dtacao.data = date.today() + timedelta(days=7)
    form_editarpipeline.acao.data = 'Prospectar'
    form_editarpipeline.oportunidade.data = 'GED'
    form_editarpipeline.facilit.data = ''
    form_editarpipeline.decisor.data = ''
    form_editarpipeline.concorrentes.data = ''
    form_editarpipeline.linkext.data = ''
    form_editarpipeline.historico.data = session["HOJE"] + ' ' + session["WYEAR"] + str(current_user.sigla) + ':'
    form_editarpipeline.prioridade.data = 0

    if form_editarpipeline.validate_on_submit() and 'botao_submit_editarpipeline' in request.form:
        clnt = ClientesDB.query.get(form_editarpipeline.select_cliente.raw_data)
        pipeline = PipelineDB(idusuario = current_user.id, active = 1,
                            dtcriac = date.today(),
                            dtalter = date.today(),
                            idcliente = clnt.idcliente,
                            produto = form_editarpipeline.produto.raw_data,
                            vendedor=form_editarpipeline.vendedor.raw_data,
                            status = form_editarpipeline.status.raw_data,
                            mercado=form_editarpipeline.mercado.raw_data,
                            prazo = request.form.get('prazo'),
                            oportunidade = request.form.get('oportunidade'),
                            facilit=request.form.get('facilit'),
                            decisor=request.form.get('decisor'),
                            concorrentes=request.form.get('concorrentes'),
                            linkext=request.form.get('linkext'),
                            acao = request.form.get('acao'),
                            dtacao = request.form.get('dtacao'),
                            historico = request.form.get('historico'),
                            prioridade = 0)

        database.session.add(pipeline)
        database.session.commit()
        flash(f'Oportunidade {clnt.nomecliente} - {clnt.unidade} criada com sucesso!', 'alert-success')
        log_action('pipeline', 'pipeline_add', 'Oportunidade p/:' + clnt.nomecliente + ' - ' + clnt.unidade + ' criado.')
        #return redirect(url_for('pipeline', status='Todos'))
        return redirect(url_for('cliente', cli_id=clnt.idcliente))
    return render_template('pipeedit.html', form_editarpipeline=form_editarpipeline, pipeline=pipeline, cliente='')


@app.route(f'{prefix}/contratos/<status>,<orderby>')
@login_required
def contratos(status, orderby):
    page = request.args.get('page', 1, type=int)
    hoje30 = date.today() + timedelta(days=30)
    Search = request.args.get('Search')
    # contratos = ContratosDB.query.filter_by(status=status)

    # INNER JOIN entre ContratosDB e usuario
    contratos = database.session.query(ContratosDB, usuario).join(usuario).filter(ContratosDB.status == status)

    if Search:
        contratos = contratos.filter(or_(ContratosDB.nomecliente.contains(Search),
                                         ContratosDB.unidade.contains(Search),
                                         ContratosDB.vendedor.contains(Search),
                                         ContratosDB.suporte.contains(Search),
                                         ContratosDB.produto.contains(Search)))
    if orderby == 'c':
        contratos = contratos.order_by(ContratosDB.nomecliente.asc()).paginate(page=page, per_page=maxLines)
    elif orderby == 'v':
        contratos = contratos.order_by(ContratosDB.validadecontrato.asc()).paginate(page=page, per_page=maxLines)
    else:
        orderby = 'c'
        contratos = contratos.order_by(ContratosDB.nomecliente.asc()).paginate(page=page, per_page=maxLines)

    if status != 'dashboard.css':
        log_action('contratos', 'contratos', 'Listagem status:' + status + ' - ' + orderby)
    return render_template('contratos.html', contratos=contratos, status=status, orderby=orderby, hoje30=hoje30)


@app.route(f'{prefix}/contractedit/<contract_id>', methods=['GET', 'POST'])
@login_required
def contractedit(contract_id):
    if current_user.access >= 3:
        form_editarcontrato = FormEditarContrato()
        contrato = ContratosDB.query.get(contract_id)
        vendr = ListaOpcoesDB.query.filter_by(msg=contrato.vendedor)
        propostas = PropostasDB.query.filter_by(status="Fechada")
        form_editarcontrato.select_prop.choices = [(s.idproposta, str(s.idproposta) + ' - ' + s.nomecliente)
                                                   for s in propostas.order_by(PropostasDB.idproposta.desc())]
        form_editarcontrato.select_prop.data = contrato.idproposta
        form_editarcontrato.select_produto.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Produto')]
        form_editarcontrato.select_produto.data = contrato.produto
        form_editarcontrato.select_vendor.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Vendedor')]
        form_editarcontrato.select_vendor.data = vendr[0].opt
        # AttributeError: 'NoneType' object has no attribute 'produto'
        form_editarcontrato.select_status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusC')]
        form_editarcontrato.select_status.data = contrato.status
        form_editarcontrato.proposta.data = contrato.proposta
        # form_editarcontrato.dtproposta.data = strptime('{}-{}-{}'.format(contrato.dtproposta.day, contrato.dtproposta.month, contrato.dtproposta.year))
        form_editarcontrato.dtproposta.data = contrato.dtproposta
        form_editarcontrato.pedido.data = contrato.pedido
        form_editarcontrato.dtpedido.data = contrato.dtpedido
        form_editarcontrato.codcontrato.data = contrato.codcontrato
        form_editarcontrato.validadecontrato.data = contrato.validadecontrato
        form_editarcontrato.duracaocontrato.data = contrato.duracaocontrato
        form_editarcontrato.select_fatur.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='QuemFornece')]
        form_editarcontrato.select_fatur.data = contrato.faturamento
        form_editarcontrato.select_frequenc.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='FatFreq')]
        form_editarcontrato.select_frequenc.data = contrato.fatfrequencia
        form_editarcontrato.select_infra.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='InfraType')]
        form_editarcontrato.select_infra.data = contrato.infratype
        form_editarcontrato.select_apptype.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='AppType')]
        form_editarcontrato.select_apptype.data = contrato.aplicacaotype
        form_editarcontrato.select_instance.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='InstancType')]
        form_editarcontrato.select_instance.data = contrato.instanciatype
        form_editarcontrato.usersavancados.data = contrato.usersavancados
        form_editarcontrato.usersregulares.data = contrato.usersregulares
        form_editarcontrato.milregistros.data = contrato.milregistros
        form_editarcontrato.gbstorage.data = contrato.gbstorage
        form_editarcontrato.select_pbi.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNao')]
        form_editarcontrato.select_pbi.data = contrato.powerbi
        form_editarcontrato.select_api.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNao')]
        form_editarcontrato.select_api.data = contrato.apisistema
        form_editarcontrato.select_supp.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='QuemFornece')]
        form_editarcontrato.select_supp.data = contrato.suporte
        form_editarcontrato.horascontratadas.data = contrato.horascontratadas
        form_editarcontrato.horasentregues.data = contrato.horasentregues
        form_editarcontrato.select_hrs.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusHs')]
        form_editarcontrato.select_hrs.data = contrato.horasstatus
        form_editarcontrato.bminstruc.data = contrato.bminstruc
        form_editarcontrato.nfinstruc.data = contrato.nfinstruc
        form_editarcontrato.observacao.data = contrato.observacao

        clientes = ClientesDB.query.filter_by(active=1)
        form_editarcontrato.select_cliente.choices = [(s.idcliente, s.nomecliente + ' - ' + s.unidade)
                                                      for s in clientes.order_by(ClientesDB.nomecliente.asc())]
        form_editarcontrato.select_cliente.data = contrato.idcliente
        if request.method == 'POST':
            if form_editarcontrato.validate_on_submit() and 'botao_submit_editarcontrato' in request.form:
                vendr = ListaOpcoesDB.query.filter_by(opt=form_editarcontrato.select_vendor.raw_data[0])
                contrato.idusuario = current_user.id
                contrato.dtalter = date.today()
                contrato.produto = form_editarcontrato.select_produto.raw_data[0]
                contrato.vendedor = vendr[0].msg
                contrato.idproposta = form_editarcontrato.select_prop.raw_data[0]
                contrato.status = request.form.get('select_status')
                contrato.proposta = request.form.get('proposta')
                contrato.dtproposta = request.form.get('dtproposta')
                contrato.pedido = request.form.get('pedido')
                contrato.dtpedido = request.form.get('dtpedido')
                contrato.codcontrato = request.form.get('codcontrato')
                contrato.validadecontrato = request.form.get('validadecontrato')
                contrato.duracaocontrato = request.form.get('duracaocontrato')
                contrato.faturamento = request.form.get('select_fatur')
                contrato.fatfrequencia = request.form.get('select_frequenc')
                contrato.infratype = request.form.get('select_infra')
                contrato.aplicacaotype = request.form.get('select_apptype')
                contrato.instanciatype = request.form.get('select_instance')
                contrato.usersavancados = request.form.get('usersavancados')
                contrato.usersregulares = request.form.get('usersregulares')
                contrato.milregistros = request.form.get('milregistros')
                contrato.gbstorage = request.form.get('gbstorage')
                contrato.powerbi = request.form.get('select_pbi')
                contrato.apisistema = request.form.get('select_api')
                contrato.suporte = request.form.get('select_supp')
                contrato.horascontratadas = request.form.get('horascontratadas')
                contrato.horasentregues = request.form.get('horasentregues')
                contrato.horasstatus = request.form.get('select_hrs')
                contrato.bminstruc = request.form.get('bminstruc')
                contrato.nfinstruc = request.form.get('nfinstruc')
                contrato.observacao = request.form.get('observacao')

                database.session.commit()
                flash(f'Dados do contrato {contrato.nomecliente} editados com sucesso!', 'alert-success')
                log_action('contratos', 'contract_edit', 'Contrato p/:' + contrato.nomecliente + ' alterado.')
                return redirect(url_for('contratos', status='ativo', orderby='c'))
    else:
        abort(403)
    return render_template('contractedit.html', form_editarcontrato=form_editarcontrato, contrato=contrato)


@app.route(f'{prefix}/contractadd', methods=['GET', 'POST'])
@login_required
def contractadd():
    contrato = "NEW"
    form_editarcontrato = FormEditarContrato()
    clientes = ClientesDB.query.filter_by(active=1)
    propostas = PropostasDB.query.filter_by(status="Fechada")
    form_editarcontrato.select_cliente.choices = [(s.idcliente, s.nomecliente + ' - ' + s.unidade)
                                                  for s in clientes.order_by(ClientesDB.nomecliente.asc())]
    form_editarcontrato.select_prop.choices = [(s.idproposta, str(s.idproposta) + ' - ' + s.nomecliente)
                                                  for s in propostas.order_by(PropostasDB.idproposta.desc())]
    form_editarcontrato.select_produto.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Produto')]
    form_editarcontrato.select_vendor.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Vendedor')]
    form_editarcontrato.select_status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusC')]
    form_editarcontrato.select_fatur.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='QuemFornece')]
    form_editarcontrato.select_frequenc.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='FatFreq')]
    form_editarcontrato.select_infra.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='InfraType')]
    form_editarcontrato.select_apptype.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='AppType')]
    form_editarcontrato.select_instance.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='InstancType')]
    form_editarcontrato.select_pbi.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNao')]
    form_editarcontrato.select_api.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNao')]
    form_editarcontrato.select_supp.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='QuemFornece')]
    form_editarcontrato.select_hrs.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusHs')]
    form_editarcontrato.dtproposta.data = date.today()
    form_editarcontrato.dtpedido.data = date.today()
    form_editarcontrato.validadecontrato.data = date.today()
    form_editarcontrato.duracaocontrato.data = 12
    form_editarcontrato.usersavancados.data = 0
    form_editarcontrato.usersregulares.data = 1
    form_editarcontrato.milregistros.data = 0
    form_editarcontrato.gbstorage.data = 0
    form_editarcontrato.horascontratadas.data = 0
    form_editarcontrato.horasentregues.data = 0
    form_editarcontrato.select_pbi.data = 'Não'
    form_editarcontrato.select_api.data = 'Não'
    form_editarcontrato.select_supp.data = 'DOX'
    form_editarcontrato.select_hrs.data = 'Não se Aplica'

    if request.method == 'POST':
        if form_editarcontrato.validate_on_submit() and 'botao_submit_editarcontrato' in request.form:
            clnt = ClientesDB.query.get(form_editarcontrato.select_cliente.raw_data)
            # prop = PropostasDB.query.get(form_editarcontrato.select_prop.raw_data)
            vendr = ListaOpcoesDB.query.filter_by(opt=form_editarcontrato.select_vendor.raw_data[0])
            contrato = ContratosDB(idusuario = current_user.id,
                                dtcriac = date.today(),
                                dtalter = date.today(),
                                idcliente = clnt.idcliente,
                                nomecliente = clnt.nomecliente,
                                unidade = clnt.unidade,
                                produto = form_editarcontrato.select_produto.raw_data,
                                vendedor=vendr[0].msg,
                                status = form_editarcontrato.select_status.raw_data,
                                idproposta=form_editarcontrato.select_prop.data,
                                proposta = form_editarcontrato.proposta.data,
                                dtproposta = request.form.get('dtproposta'),
                                pedido = form_editarcontrato.pedido.data,
                                dtpedido = request.form.get('dtpedido'),
                                codcontrato = form_editarcontrato.codcontrato.data,
                                validadecontrato = request.form.get('validadecontrato'),
                                duracaocontrato = request.form.get('duracaocontrato'),
                                faturamento = form_editarcontrato.select_fatur.raw_data,
                                fatfrequencia = form_editarcontrato.select_frequenc.raw_data,
                                infratype = form_editarcontrato.select_infra.raw_data,
                                aplicacaotype = form_editarcontrato.select_apptype.raw_data,
                                instanciatype = form_editarcontrato.select_instance.raw_data,
                                usersavancados = request.form.get('usersavancados'),
                                usersregulares = request.form.get('usersregulares'),
                                milregistros = request.form.get('milregistros'),
                                gbstorage = request.form.get('gbstorage'),
                                powerbi = form_editarcontrato.select_pbi.raw_data,
                                apisistema = form_editarcontrato.select_api.raw_data,
                                suporte = form_editarcontrato.select_supp.raw_data,
                                horascontratadas = request.form.get('horascontratadas'),
                                horasentregues = request.form.get('horasentregues'),
                                horasstatus = form_editarcontrato.select_hrs.raw_data,
                                bminstruc = form_editarcontrato.bminstruc.data,
                                nfinstruc = form_editarcontrato.nfinstruc.data,
                                observacao = form_editarcontrato.observacao.data)
            database.session.add(contrato)
            database.session.commit()
            flash(f'Contrato {clnt.nomecliente} - {clnt.unidade} criado com sucesso!', 'alert-success')
            log_action('contratos', 'contract_add', 'Contrato p/:' + clnt.nomecliente + ' - ' + clnt.unidade + ' criado.')
            return redirect(url_for('contratos', status='ativo', orderby='c'))
    return render_template('contractedit.html', form_editarcontrato=form_editarcontrato, contrato=contrato)

@app.route(f'{prefix}/projadd', methods=['GET', 'POST'])
@login_required
def projectadd():
    projeto = "NEW"
    cliente = {"cliente": [{"nomecliente": "Cliente"},{"unidade": "Unidade"}]}
    form_editarprojeto = FormEditarProjeto()
    # NEW: Para aparecer na lista de clietes para criar projeto, o cliente tem que ter contrato ativo
    contratos = ContratosDB.query.filter(ContratosDB.status == 'Ativo')
    form_editarprojeto.select_cliente.choices = [(s.idcliente, s.nomecliente + ' - ' + s.unidade)
                                                  for s in contratos.order_by(ContratosDB.nomecliente.asc())]
    # OLD: A lista de clientes continha todos os clitens ativos do cadastro
    # clientes = ClientesDB.query.filter_by(active=1)
    # form_editarprojeto.select_cliente.choices = [(s.idcliente, s.nomecliente + ' - ' + s.unidade)
    #                                               for s in clientes.order_by(ClientesDB.nomecliente.asc())]
    form_editarprojeto.select_status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusP')]
    form_editarprojeto.projetonome.data = 'CR ou Projeto'
    form_editarprojeto.kickoff.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNao')]
    form_editarprojeto.testes.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNao')]
    form_editarprojeto.homologacao.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNao')]
    form_editarprojeto.dbookpwrbi.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNaoNA')]
    form_editarprojeto.treinamento.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNaoNA')]
    form_editarprojeto.aceiteproj.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNaoNA')]
    form_editarprojeto.faturado.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNaoNA')]
    form_editarprojeto.atestado.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNaoNA')]
    form_editarprojeto.select_status.data = 'ativo'
    form_editarprojeto.prjinicplan.data = date.today()
    form_editarprojeto.prjfimplan.data = date.today() + timedelta(days=30)
    form_editarprojeto.propdata.data = date.today() - timedelta(days=30)
    form_editarprojeto.pedidodata.data = date.today() - timedelta(days=1)
    form_editarprojeto.osdata.data = date.today()
    form_editarprojeto.horasprev.data = 0
    form_editarprojeto.horasusds.data = 0

    if form_editarprojeto.validate_on_submit() and 'botao_submit_editarprojeto' in request.form:
        clnt = ClientesDB.query.get(form_editarprojeto.select_cliente.raw_data)
        hp = request.form.get('horasprev')
        if hp == None:
            hp = 0
        hu = request.form.get('horasusds')
        if hu == None:
            hu = 0
        projeto = ProjetosDB(idclint=clnt.idcliente,
                            idusuario=current_user.id,
                            dtcriac=date.today(),
                            dtalter=date.today(),
                            statusproj = form_editarprojeto.select_status.raw_data,
                            projetonome = request.form.get('projetonome'),
                            prjinicplan = request.form.get('prjinicplan'),
                            prjfimplan = request.form.get('prjfimplan'),
                            # prjinicreal = request.form.get('prjinicreal'),
                            # prjfimreal = request.form.get('prjfimreal'),
                            propcodigo = form_editarprojeto.propcodigo.data,
                            propdata = request.form.get('propdata'),
                            pedidocodig = form_editarprojeto.pedidocodig.data,
                            pedidodata = request.form.get('pedidodata'),
                            oscodigo = form_editarprojeto.oscodigo.data,
                            osdata = request.form.get('osdata'),
                            horasprev=hp,
                            horasusds=hu,
                            responsnome = form_editarprojeto.responsnome.data,
                            tecniconome = form_editarprojeto.tecniconome.data,
                            kickoff = 'Não',
                            # kickoffdata = request.form.get('kickoffdata'),
                            testes = 'Não',
                            # testesdata = request.form.get('testesdata'),
                            homologacao = 'Não',
                            # homologdata = request.form.get('homologdata'),
                            dbookpwrbi = 'Não',
                            # dbkpwrbidt = request.form.get('dbkpwrbidt'),
                            treinamento = 'Não',
                            # treinamdata = request.form.get('treinamdata'),
                            aceiteproj = 'Não',
                            # aceitedata = request.form.get('aceitedata'),
                            faturado = 'Não',
                            # nfnumero = form_editarprojeto.nfnumero.data,
                            # nfdata = request.form.get('nfdata'),
                            atestado = 'Não',
                            # atestadodat = request.form.get('atestadodat'),
                            percentual = 0,
                            stakeholders = form_editarprojeto.stakeholders.data,
                            observacao = form_editarprojeto.observacao.data)
        database.session.add(projeto)
        database.session.commit()
        flash(f'Projeto criado com sucesso para {clnt.nomecliente}!', 'alert-success')
        log_action('projetos', 'proj_add', 'Proj:' + projeto.projetonome + ' p/ ' + clnt.nomecliente + ' criado.')
        return redirect(url_for('projetos', status='ativo', orderby='p'))
    return render_template('projectedit.html', form_editarprojeto=form_editarprojeto, projeto=projeto, cliente=cliente)

@app.route(f'{prefix}/projectedit/<project_id>', methods=['GET', 'POST'])
@login_required
def projectedit(project_id):
    if current_user.access >= 2:
        form_editarprojeto = FormEditarProjeto()
        projeto = ProjetosDB.query.get(project_id)
        cliente = ClientesDB.query.get(projeto.idclint)

        clientes = ClientesDB.query.filter_by(active=1)
        form_editarprojeto.select_cliente.choices = [(s.idcliente, s.nomecliente + ' - ' + s.unidade)
                                                     for s in clientes.order_by(ClientesDB.nomecliente.asc())]
        form_editarprojeto.select_status.choices = [(s.opt, s.msg) for s in
                                                    ListaOpcoesDB.query.filter_by(lst='StatusP')]
        form_editarprojeto.select_status.data = projeto.statusproj
        form_editarprojeto.projetonome.data = projeto.projetonome
        form_editarprojeto.kickoff.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNao')]
        form_editarprojeto.testes.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNao')]
        form_editarprojeto.homologacao.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNao')]
        form_editarprojeto.dbookpwrbi.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNaoNA')]
        form_editarprojeto.treinamento.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNaoNA')]
        form_editarprojeto.aceiteproj.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNaoNA')]
        form_editarprojeto.faturado.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNaoNA')]
        form_editarprojeto.atestado.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SimNaoNA')]
        form_editarprojeto.kickoff.data = projeto.kickoff
        form_editarprojeto.testes.data = projeto.testes
        form_editarprojeto.homologacao.data = projeto.homologacao
        form_editarprojeto.dbookpwrbi.data = projeto.dbookpwrbi
        form_editarprojeto.treinamento.data = projeto.treinamento
        form_editarprojeto.aceiteproj.data = projeto.aceiteproj
        form_editarprojeto.faturado.data = projeto.faturado
        form_editarprojeto.atestado.data = projeto.atestado
        form_editarprojeto.prjinicplan.data = projeto.prjinicplan
        form_editarprojeto.prjfimplan.data = projeto.prjfimplan
        form_editarprojeto.prjinicreal.data = projeto.prjinicreal
        form_editarprojeto.prjfimreal.data = projeto.prjfimreal
        form_editarprojeto.propdata.data = projeto.propdata
        form_editarprojeto.pedidodata.data = projeto.pedidodata
        form_editarprojeto.osdata.data = projeto.osdata
        form_editarprojeto.horasprev.data = projeto.horasprev
        form_editarprojeto.horasusds.data = projeto.horasusds
        form_editarprojeto.kickoffdata.data = projeto.kickoffdata
        form_editarprojeto.testesdata.data = projeto.testesdata
        form_editarprojeto.homologdata.data = projeto.homologdata
        form_editarprojeto.dbkpwrbidt.data = projeto.dbkpwrbidt
        form_editarprojeto.treinamdata.data = projeto.treinamdata
        form_editarprojeto.aceitedata.data = projeto.aceitedata
        form_editarprojeto.nfdata.data = projeto.nfdata
        form_editarprojeto.atestadodat.data = projeto.atestadodat
        form_editarprojeto.propcodigo.data = projeto.propcodigo
        form_editarprojeto.pedidocodig.data = projeto.pedidocodig
        form_editarprojeto.oscodigo.data = projeto.oscodigo
        form_editarprojeto.responsnome.data = projeto.responsnome
        form_editarprojeto.tecniconome.data = projeto.tecniconome
        form_editarprojeto.nfnumero.data = projeto.nfnumero
        form_editarprojeto.stakeholders.data = projeto.stakeholders
        form_editarprojeto.observacao.data = projeto.observacao

        if form_editarprojeto.validate_on_submit() and 'botao_submit_editarprojeto' in request.form:
            # clnt = ClientesDB.query.get(form_editarprojeto.select_cliente.raw_data)
            percentual_calculado = 0
            if request.form.get('kickoff') == 'Sim':
                percentual_calculado += 0.2
            if request.form.get('testes') == 'Sim':
                percentual_calculado += 0.2
            if request.form.get('homologacao') == 'Sim':
                percentual_calculado += 0.2
            if request.form.get('dbookpwrbi') == 'Sim' or request.form.get('dbookpwrbi') == 'NA':
                percentual_calculado += 0.05
            if request.form.get('treinamento') == 'Sim' or request.form.get('treinamento') == 'NA':
                percentual_calculado += 0.15
            if request.form.get('aceiteproj') == 'Sim' or request.form.get('aceiteproj') == 'NA':
                percentual_calculado += 0.15
            if request.form.get('faturado') == 'Sim' or request.form.get('faturado') == 'NA':
                percentual_calculado += 0.04
            if request.form.get('atestado') == 'Sim' or request.form.get('atestado') == 'NA':
                percentual_calculado += 0.01

            projeto.statusproj=form_editarprojeto.select_status.raw_data
            projeto.idclint=cliente.idcliente
            projeto.idusuario=current_user.id
            projeto.dtalter=date.today()
            projeto.projetonome=request.form.get('projetonome')
            projeto.prjinicplan=request.form.get('prjinicplan')
            projeto.prjfimplan=request.form.get('prjfimplan')
            dttemp = request.form.get('prjinicreal')
            if dttemp:
                projeto.prjinicreal=dttemp
                dttemp = ''
            dttemp = request.form.get('prjfimreal')
            if dttemp:
                projeto.prjfimreal=dttemp
                dttemp = ''
            projeto.propcodigo=request.form.get('propcodigo')
            projeto.propdata=request.form.get('propdata')
            projeto.pedidocodig=request.form.get('pedidocodig')
            projeto.pedidodata=request.form.get('pedidodata')
            projeto.oscodigo=request.form.get('oscodigo')
            projeto.osdata=request.form.get('osdata')
            projeto.horasprev=request.form.get('horasprev')
            projeto.horasusds=request.form.get('horasusds')
            projeto.responsnome=request.form.get('responsnome')
            projeto.tecniconome=request.form.get('tecniconome')
            projeto.kickoff=form_editarprojeto.kickoff.raw_data
            dttemp = request.form.get('kickoffdata')
            if dttemp:
                projeto.kickoffdata=dttemp
                dttemp = ''
            projeto.testes=form_editarprojeto.testes.raw_data
            dttemp = request.form.get('testesdata')
            if dttemp:
                projeto.testesdata=dttemp
                dttemp = ''
            projeto.homologacao=form_editarprojeto.homologacao.raw_data
            dttemp = request.form.get('homologdata')
            if dttemp:
                projeto.homologdata=dttemp
                dttemp = ''
            projeto.dbookpwrbi=form_editarprojeto.dbookpwrbi.raw_data
            dttemp = request.form.get('dbkpwrbidt')
            if dttemp:
                projeto.dbkpwrbidt=dttemp
                dttemp = ''
            projeto.treinamento=form_editarprojeto.treinamento.raw_data
            dttemp = request.form.get('treinamdata')
            if dttemp:
                projeto.treinamdata=dttemp
                dttemp = ''
            projeto.aceiteproj=form_editarprojeto.aceiteproj.raw_data
            dttemp = request.form.get('aceitedata')
            if dttemp:
                projeto.aceitedata=dttemp
                dttemp = ''
            projeto.faturado=form_editarprojeto.faturado.raw_data
            projeto.nfnumero=request.form.get('nfnumero')
            dttemp = request.form.get('nfdata')
            if dttemp:
                projeto.nfdata=dttemp
                dttemp = ''
            projeto.atestado=form_editarprojeto.atestado.raw_data
            dttemp = request.form.get('atestadodat')
            if dttemp:
                projeto.atestadodat=dttemp
                dttemp = ''
            projeto.percentual=percentual_calculado
            projeto.stakeholders=request.form.get('stakeholders')
            projeto.observacao=request.form.get('observacao')
            database.session.add(projeto)
            database.session.commit()
            flash(f'Projeto {form_editarprojeto.projetonome.data} editado com sucesso!', 'alert-success')
            log_action('projetos', 'proj_edit', 'Proj:' + form_editarprojeto.projetonome.data + 'ID:' + project_id + ' alterado.')
            return redirect(url_for('projetos', status='ativo', orderby='p'))
    else:
        abort(403)
    return render_template('projectedit.html', form_editarprojeto=form_editarprojeto, projeto=projeto, cliente=cliente)

@app.route(f'{prefix}/projetos/<status>,<orderby>')
@login_required
def projetos(status, orderby):
    page = request.args.get('page', 1, type=int)
    Search = request.args.get('Search')
    # Se o status==final buscar por projetos finalizados e também por aceitos
    if status == 'final':
        projetos = database.session.query(ProjetosDB, usuario, ClientesDB) \
            .join(usuario, ProjetosDB.idusuario == usuario.id) \
            .join(ClientesDB, ProjetosDB.idclint == ClientesDB.idcliente) \
            .filter(ProjetosDB.statusproj == status)
    else:
        projetos = database.session.query(ProjetosDB, usuario, ClientesDB) \
            .join(usuario, ProjetosDB.idusuario == usuario.id) \
            .join(ClientesDB, ProjetosDB.idclint == ClientesDB.idcliente) \
            .filter(or_(ProjetosDB.statusproj == 'ativo', ProjetosDB.statusproj == 'aceito'))

    if Search:
        projetos = projetos.filter(or_(ProjetosDB.projetonome.contains(Search),
                                        ClientesDB.nomecliente.contains(Search)))

    backlog = 0
    hrsdone = 0
    if projetos:
        for prj in projetos:
            hp = prj.ProjetosDB.horasprev
            hu = prj.ProjetosDB.horasusds
            if hp != None:
                backlog += hp
            if hu != None:
                hrsdone += hu

    # bklog = projetos.query(functions.sum(projetos.ProjetosDB.horasprev).label("BackLog")).scalar()
    if status == 'final':
        if orderby == 'p':
            projetos = projetos.order_by(ProjetosDB.projetonome.asc()).paginate(page=page, per_page=maxLines)
        else:
            projetos = projetos.order_by(ProjetosDB.aceitedata.desc()).paginate(page=page, per_page=maxLines)
    else:
        if orderby == 'f':
            projetos = projetos.order_by(ProjetosDB.prjfimplan.asc()).paginate(page=page, per_page=maxLines)
        else:
            projetos = projetos.order_by(ProjetosDB.projetonome.asc()).paginate(page=page, per_page=maxLines)

    if status != 'dashboard.css':
        log_action('projetos', 'projetos', 'Listagem de Projetos:' + status)
    return render_template('projetos.html', projetos=projetos, status=status, orderby=orderby, hoje=hoje, backlog=backlog, hrsdone=hrsdone)


@app.route(f'{prefix}/projectedit/<project_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_projeto(project_id):
    projeto = ProjetosDB.query.get(project_id)
    if current_user.access >= 3:
        database.session.delete(projeto)
        database.session.commit()
        flash(f'Projeto {projeto.projetonome} excluido com sucesso!', 'alert-danger')
        log_action('projetos', 'excluir_proj', 'Proj:' + projeto.projetonome + ' excluido.')
        return redirect(url_for('projetos', status='ativo', orderby='p'))
    else:
        abort(403)

@app.route(f'{prefix}/equipamentos/<status>')
@login_required
def equipamentos(status):
    page = request.args.get('page', 1, type=int)
    Search = request.args.get('Search')
    # Se o status==final buscar por projetos finalizados e também por aceitos
    if status == 'ativo':
        equiptos = database.session.query(EquiptosDB, usuario) \
            .join(usuario, EquiptosDB.idusuario == usuario.id) \
            .filter(and_ (EquiptosDB.status == 1),(EquiptosDB.active == 1))
    else:
        equiptos = database.session.query(EquiptosDB, usuario) \
            .join(usuario, EquiptosDB.idusuario == usuario.id) \
            .filter(and_ (EquiptosDB.status == 0),(EquiptosDB.active == 1))

    if Search:
        equiptos = equiptos.filter(or_(EquiptosDB.usuario.contains(Search),
                                        EquiptosDB.equipto_tipo.contains(Search),
                                        EquiptosDB.nfcompra.contains(Search),
                                        EquiptosDB.equipto_id.contains(Search),
                                        EquiptosDB.equipto_nome.contains(Search),
                                        EquiptosDB.equipto_marca.contains(Search),
                                        EquiptosDB.equipto_modelo.contains(Search),
                                        EquiptosDB.descricao.contains(Search),
                                        EquiptosDB.motivodesativ.contains(Search),
                                        EquiptosDB.observacao.contains(Search)))

    # Ordenar concatenando TIPO+USUARIO
    equiptos = equiptos.order_by(EquiptosDB.equipto_tipo.asc(),EquiptosDB.usuario.asc()).paginate(page=page, per_page=maxLines)

    if status != 'dashboard.css':
        log_action('equipamentos', 'equipamentos', 'Listagem de Equipamentos:' + status)
    return render_template('equiptos.html', equiptos=equiptos, status=status, hoje=hoje)

@app.route(f'{prefix}/equiptosadd', methods=['GET', 'POST'])
@login_required
def equiptosadd():
    equipamento = "NEW"
    form_editarequiptos = FormEditarEquiptos()
    form_editarequiptos.equipto_tipo.choices = [(s.opt) for s in ListaOpcoesDB.query.filter_by(lst='EquipTipo')]
    form_editarequiptos.select_status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusCrd')]

    if form_editarequiptos.validate_on_submit() and 'botao_submit_editar_equiptos' in request.form:
        if form_editarequiptos.select_status.data == 'ativo':
            flag = 1
        else:
            flag = 0
        equipamento = EquiptosDB(
                            active = 1,
                            idusuario = current_user.id,
                            dtcriac = date.today(),
                            dtalter = date.today(),
                            status = flag,
                            usuario = form_editarequiptos.usuario.data,
                            equipto_id = form_editarequiptos.equipto_id.data,
                            equipto_tipo = form_editarequiptos.equipto_tipo.data,
                            equipto_nome = form_editarequiptos.equipto_nome.data,
                            equipto_marca = form_editarequiptos.equipto_marca.data,
                            equipto_modelo=form_editarequiptos.equipto_modelo.data,
                            dtcompra = request.form.get('dtcompra'),
                            dtdesativ = request.form.get('dtdesativ'),
                            motivodesativ = form_editarequiptos.motivodesativ.data,
                            nfcompra = form_editarequiptos.nfcompra.data,
                            useradmin = form_editarequiptos.useradmin.data,
                            password = form_editarequiptos.password.data,
                            pin = form_editarequiptos.pin.data,
                            descricao = form_editarequiptos.descricao.data,
                            observacao = form_editarequiptos.observacao.data)
        database.session.add(equipamento)
        database.session.commit()
        flash(f'Equipamento criado com sucesso !', 'alert-success')
        return redirect(url_for('equipamentos', status='ativo'))
        #log_action('credenciais', 'credencadd', 'Credencial:' + clnt.nomecliente + ' adicionada.')
    return render_template('equiptosedit.html', form_editarequiptos=form_editarequiptos, equipamento=equipamento)

@app.route(f'{prefix}/equiptosedit/<equipto_id>', methods=['GET', 'POST'])
@login_required
def equiptosedit(equipto_id):
    if current_user.access >= 2:
        form_editarequiptos = FormEditarEquiptos()
        equipamento = EquiptosDB.query.get(equipto_id)
        form_editarequiptos.equipto_tipo.choices = [(s.opt) for s in ListaOpcoesDB.query.filter_by(lst='EquipTipo')]
        form_editarequiptos.select_status.choices = [(s.opt, s.msg) for s in
                                                     ListaOpcoesDB.query.filter_by(lst='StatusCrd')]
        form_editarequiptos.dtcompra.data = equipamento.dtcompra
        form_editarequiptos.select_status.data = equipamento.status
        form_editarequiptos.usuario.data = equipamento.usuario
        form_editarequiptos.equipto_id.data = equipamento.equipto_id
        form_editarequiptos.equipto_tipo.data = equipamento.equipto_tipo
        form_editarequiptos.equipto_nome.data = equipamento.equipto_nome
        form_editarequiptos.equipto_marca.data = equipamento.equipto_marca
        form_editarequiptos.equipto_modelo.data = equipamento.equipto_modelo
        form_editarequiptos.motivodesativ.data = equipamento.motivodesativ
        form_editarequiptos.nfcompra.data = equipamento.nfcompra

        form_editarequiptos.useradmin.data = equipamento.useradmin
        form_editarequiptos.password.data = equipamento.password
        form_editarequiptos.pin.data = equipamento.pin
        form_editarequiptos.descricao.data = equipamento.descricao
        form_editarequiptos.observacao.data = equipamento.observacao

        if form_editarequiptos.validate_on_submit() and 'botao_submit_editar_equiptos' in request.form:
            if form_editarequiptos.select_status.raw_data[0] == 'ativo':
                flag = 1
            else:
                flag = 0

            # equipamento.equipto_tipo = form_editarequiptos.equipto_tipo.raw_data
            equipamento.idusuario = current_user.id
            equipamento.dtalter = date.today()
            equipamento.usuario = request.form.get('usuario')
            equipamento.status = flag
            equipamento.equipto_id = request.form.get('equipto_id')
            equipamento.equipto_tipo = request.form.get('equipto_tipo')
            equipamento.equipto_nome = request.form.get('equipto_nome')
            equipamento.equipto_marca = request.form.get('equipto_marca')
            equipamento.equipto_modelo = request.form.get('equipto_modelo')
            equipamento.dtcompra = request.form.get('dtcompra')
            equipamento.dtdesativ = request.form.get('dtdesativ')
            equipamento.motivodesativ = request.form.get('motivodesativ')
            equipamento.nfcompra = request.form.get('nfcompra')
            equipamento.useradmin = request.form.get('useradmin')
            equipamento.password = request.form.get('password')
            equipamento.pin = request.form.get('pin')
            equipamento.descricao = request.form.get('descricao')
            equipamento.observacao = request.form.get('observacao')
            database.session.add(equipamento)
            database.session.commit()
            flash(f'Equipamento {equipamento.equipto_tipo} editado com sucesso!', 'alert-success')
            return redirect(url_for('equipamentos', status='ativo'))
            #log_action('credenciais', 'credencedit', 'Credencial:' + credencial.nomecliente + ' alterada.')
    else:
        abort(403)
    return render_template('equiptosedit.html', form_editarequiptos=form_editarequiptos, equipamento=equipamento)

@app.route(f'{prefix}/equiptosedit/<equipto_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_equipto(equipto_id):
    equipamento = EquiptosDB.query.get(equipto_id)
    if current_user.access >= 3:
        equipamento.status = 0
        # database.session.delete(credencial)
        database.session.commit()
        flash(f'Equipamento {equipamento.equipto_tipo} excluido com sucesso!', 'alert-danger')
        log_action('equipamento', 'excluir', 'Equipamento:' + equipamento.equipto_tipo + ' excluído.')
        return redirect(url_for('equipamentos', status='ativo'))
    else:
        abort(403)

@app.route(f'{prefix}/funcs/<status>')
@login_required
def funcs(status):
    page = request.args.get('page', 1, type=int)
    hoje30 = date.today() + timedelta(days=30)
    Search = request.args.get('Search')
    # status do funcionario = pode ser Ativo / Inativo / Estágio
    if status == 'Inativo':
        pessoal = database.session.query(PessoalDB, usuario) \
            .join(usuario, PessoalDB.idusuario == usuario.id) \
            .filter(and_ (PessoalDB.statusrh == 'Inativo', PessoalDB.active == 1))
    else:
        pessoal = database.session.query(PessoalDB, usuario) \
            .join(usuario, PessoalDB.idusuario == usuario.id) \
            .filter(and_ (or_(PessoalDB.statusrh == 'Ativo', PessoalDB.statusrh == 'Estagio'), PessoalDB.active == 1))

    if Search:
        pessoal = pessoal.filter(PessoalDB.nomefunc.contains(Search))
    if status != 'dashboard.css':
        log_action('funcionarios', 'funcs', 'Listagem de funcs:' + status)
    pessoal = pessoal.order_by(PessoalDB.nomefunc.asc()).paginate(page=page, per_page=maxLines)
    return render_template('funcs.html', pessoal=pessoal, status=status, hoje=hoje, hoje30=hoje30)

@app.route(f'{prefix}/funcedit/<func_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_func(func_id):
    pessoa = PessoalDB.query.get(func_id)
    if current_user.access >= 3:
        pessoa.active = 0
        # database.session.delete(pessoa)
        database.session.commit()
        flash(f'Funcionário {pessoa.nomefunc} excluido com sucesso!', 'alert-danger')
        log_action('funcionarios', 'excluir_func', 'Func:' + pessoa.nomefunc + ' excluido.')
        return redirect(url_for('funcs', status='ativo'))
    else:
        abort(403)


@app.route(f'{prefix}/funcadd', methods=['GET', 'POST'])
@login_required
def funcadd():
    pessoal = "NEW"
    form_editarpessoal = FormEditarPessoal()
    form_editarpessoal.select_statusrh.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusRH')]
    form_editarpessoal.select_estadciv.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='EstCivil')]
    form_editarpessoal.select_statusrh.data = 'ativo'
    form_editarpessoal.select_estadciv.data = 'Solteiro(a)'
    form_editarpessoal.dtadmiss.data = date.today()
    form_editarpessoal.dtlimfer.data = date.today() + timedelta(days=730)

    if form_editarpessoal.validate_on_submit() and 'botao_submit_editarpessoal' in request.form:
        pessoal = PessoalDB(idusuario=current_user.id, active=1, dtcriac=date.today(), dtalter=date.today(),
                            statusrh=form_editarpessoal.select_statusrh.raw_data, estadciv=form_editarpessoal.select_estadciv.raw_data,
                            nomefunc = form_editarpessoal.nomefunc.data, dtadmiss = request.form.get('dtadmiss'),
                            rgfunc=form_editarpessoal.rgfunc.data, cpffunc = form_editarpessoal.cpffunc.data,
                            cargfunc = form_editarpessoal.cargfunc.data, dtlimfer=request.form.get('dtlimfer'),
                            salrinic=request.form.get('salrinic'), salrtual=request.form.get('salrinic'),
                            fonefixo = form_editarpessoal.fonefixo.data, fonecelr = form_editarpessoal.fonecelr.data,
                            escolari = form_editarpessoal.escolari.data, nomeconj = form_editarpessoal.nomeconj.data,
                            endereco = form_editarpessoal.endereco.data, emailpes = form_editarpessoal.emailpes.data,
                            bairro = form_editarpessoal.bairro.data, cidade = form_editarpessoal.cidade.data,
                            estado = form_editarpessoal.estado.data, cep = form_editarpessoal.cep.data,
                            benefc = form_editarpessoal.benefc.data, ferias = form_editarpessoal.ferias.data,
                            observacao = form_editarpessoal.observacao.data, dtnascim=request.form.get('dtnascim'))
        # dtdeslig
        dtnasc = request.form.get('dtnasccg')
        if dtnasc:
            pessoal.dtnasccg = dtnasc
        database.session.add(pessoal)
        database.session.commit()
        flash(f'Funcionário {pessoal.nomefunc} criado com sucesso!', 'alert-success')
        log_action('funcionarios', 'funcadd', 'Func:' + pessoal.nomefunc + ' adicionado.')
        return redirect(url_for('funcs', status='ativo'))
    return render_template('funcedit.html', form_editarpessoal=form_editarpessoal, pessoal=pessoal)

@app.route(f'{prefix}/funcedit/<func_id>', methods=['GET', 'POST'])
@login_required
def funcedit(func_id):
    if current_user.access >= 4:
        form_editarpessoal = FormEditarPessoal()
        pessoal = PessoalDB.query.get(func_id)

        form_editarpessoal.select_statusrh.choices = [(s.opt, s.msg) for s in
                                                      ListaOpcoesDB.query.filter_by(lst='StatusRH')]
        form_editarpessoal.select_estadciv.choices = [(s.opt, s.msg) for s in
                                                      ListaOpcoesDB.query.filter_by(lst='EstCivil')]
        form_editarpessoal.select_statusrh.data = pessoal.statusrh
        form_editarpessoal.select_estadciv.data = pessoal.estadciv
        form_editarpessoal.dtadmiss.data = pessoal.dtadmiss
        form_editarpessoal.salrinic.data = pessoal.salrinic
        form_editarpessoal.salrtual.data = pessoal.salrtual
        form_editarpessoal.cargfunc.data = pessoal.cargfunc
        form_editarpessoal.dtdeslig.data = pessoal.dtdeslig
        form_editarpessoal.dtlimfer.data = pessoal.dtlimfer
        form_editarpessoal.nomefunc.data = pessoal.nomefunc
        form_editarpessoal.rgfunc.data = pessoal.rgfunc
        form_editarpessoal.cpffunc.data = pessoal.cpffunc
        form_editarpessoal.fonefixo.data = pessoal.fonefixo
        form_editarpessoal.fonecelr.data = pessoal.fonecelr
        form_editarpessoal.emailpes.data = pessoal.emailpes
        form_editarpessoal.dtnascim.data = pessoal.dtnascim
        form_editarpessoal.escolari.data = pessoal.escolari
        form_editarpessoal.nomeconj.data = pessoal.nomeconj
        form_editarpessoal.dtnasccg.data = pessoal.dtnasccg
        form_editarpessoal.endereco.data = pessoal.endereco
        form_editarpessoal.bairro.data = pessoal.bairro
        form_editarpessoal.cidade.data = pessoal.cidade
        form_editarpessoal.estado.data = pessoal.estado
        form_editarpessoal.cep.data = pessoal.cep
        form_editarpessoal.benefc.data = pessoal.benefc
        form_editarpessoal.ferias.data = pessoal.ferias
        form_editarpessoal.observacao.data = pessoal.observacao

        if form_editarpessoal.validate_on_submit() and 'botao_submit_editarpessoal' in request.form:
           # EDITAR ABAIXO
            pessoal.statusrh=form_editarpessoal.select_statusrh.raw_data
            pessoal.estadciv = form_editarpessoal.select_estadciv.raw_data
            pessoal.idusuario=current_user.id
            pessoal.dtalter=date.today()
            pessoal.dtadmiss = request.form.get('dtadmiss')
            pessoal.salrinic = request.form.get('salrinic')
            pessoal.salrtual = request.form.get('salrtual')
            pessoal.cargfunc = request.form.get('cargfunc')
            pessoal.dtlimfer = request.form.get('dtlimfer')
            pessoal.nomefunc = request.form.get('nomefunc')
            pessoal.rgfunc = request.form.get('rgfunc')
            pessoal.cpffunc = request.form.get('cpffunc')
            pessoal.fonefixo = request.form.get('fonefixo')
            pessoal.fonecelr = request.form.get('fonecelr')
            pessoal.emailpes = request.form.get('emailpes')
            pessoal.dtnascim = request.form.get('dtnascim')
            pessoal.escolari = request.form.get('escolari')
            pessoal.nomeconj = request.form.get('nomeconj')
            dttemp = request.form.get('dtnasccg')
            if dttemp:
                pessoal.dtnasccg = dttemp
                dttemp = ''
            pessoal.endereco = request.form.get('endereco')
            pessoal.bairro = request.form.get('bairro')
            pessoal.cidade = request.form.get('cidade')
            pessoal.estado = request.form.get('estado')
            pessoal.cep = request.form.get('cep')
            pessoal.benefc = request.form.get('benefc')
            pessoal.ferias = request.form.get('ferias')
            pessoal.observacao = request.form.get('observacao')
            dttemp = request.form.get('dtdeslig')
            if dttemp:
                pessoal.dtdeslig = dttemp
                dttemp = ''
            database.session.add(pessoal)
            database.session.commit()
            flash(f'Funcionário {form_editarpessoal.nomefunc.data} editado com sucesso!', 'alert-success')
            log_action('funcionarios', 'funcedit', 'Func:' + form_editarpessoal.nomefunc.data + ' alterado.')
            return redirect(url_for('funcs', status='ativo'))
    else:
        abort(403)
    return render_template('funcedit.html', form_editarpessoal=form_editarpessoal, pessoal=pessoal)

@app.route(f'{prefix}/credencadd', methods=['GET', 'POST'])
@login_required
def credencadd():
    credencial = "NEW"
    cliente = {"cliente": [{"nomecliente": "Cliente"},{"unidade": "Unidade"}]}
    form_editarcredenc = FormEditarCredencial()
    clientes = ClientesDB.query.filter_by(active=1)
    form_editarcredenc.select_cliente.choices = [(s.idcliente, s.nomecliente + ' - ' + s.unidade)
                                                  for s in clientes.order_by(ClientesDB.nomecliente.asc())]
    form_editarcredenc.select_status.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusCrd')]
    form_editarcredenc.select_cloudloc.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='CloudLoc')]
    form_editarcredenc.select_status.data = 'ativo'
    form_editarcredenc.dtimplantac.data = date.today()
    form_editarcredenc.accesslevel.data = 2

    if form_editarcredenc.validate_on_submit() and 'botao_submit_editarcredenc' in request.form:
        clnt = ClientesDB.query.get(form_editarcredenc.select_cliente.raw_data)
        acslev = int(request.form.get('accesslevel'))
        credencial = CredencialDB(nomecliente=clnt.nomecliente+" - "+clnt.unidade,
                            active=1,
                            idusuario=current_user.id,
                            dtcriac=date.today(),
                            dtalter=date.today(),
                            accesslevel = acslev,
                            statenv = form_editarcredenc.select_status.raw_data,
                            cloudloc = form_editarcredenc.select_cloudloc.raw_data,
                            ambiente = form_editarcredenc.ambiente.data,
                            version = form_editarcredenc.version.data,
                            dtimplantac = request.form.get('dtimplantac'),
                            responsav = form_editarcredenc.responsav.data,
                            urlweb = form_editarcredenc.urlweb.data,
                            logindocc = form_editarcredenc.logindocc.data,
                            passwddocc = form_editarcredenc.passwddocc.data,
                            loginserv = form_editarcredenc.loginserv.data,
                            passwdserv = form_editarcredenc.passwdserv.data,
                            loginapi = form_editarcredenc.loginapi.data,
                            passwdapi = form_editarcredenc.passwdapi.data,
                            keyfile = form_editarcredenc.keyfile.data,
                            notas = form_editarcredenc.notas.data)
        database.session.add(credencial)
        database.session.commit()
        flash(f'Credencial criada com sucesso para {clnt.nomecliente}!', 'alert-success')
        log_action('credenciais', 'credencadd', 'Credencial:' + clnt.nomecliente + ' adicionada.')
        if acslev > current_user.access:
            flash(f'Seu nível de acesso {current_user.access} não poderá ver essa credencial!', 'alert-danger')
        return redirect(url_for('credenciais', status='ativo'))
    return render_template('credencedit.html', form_editarcredenc=form_editarcredenc, credencial=credencial, cliente=cliente)

@app.route(f'{prefix}/credencedit/<credenc_id>', methods=['GET', 'POST'])
@login_required
def credencedit(credenc_id):
    if current_user.access >= 2:
        form_editarcredenc = FormEditarCredencial()
        credencial = CredencialDB.query.get(credenc_id)
        # clientes = ClientesDB.query.filter_by(active=1)
        # form_editarcredenc.select_cliente.choices = [(s.idcliente, s.nomecliente + ' - ' + s.unidade)
        #                                              for s in clientes.order_by(ClientesDB.nomecliente.asc())]
        form_editarcredenc.select_cliente.choices = [("","")]
        form_editarcredenc.select_status.choices = [(s.opt, s.msg) for s in
                                                    ListaOpcoesDB.query.filter_by(lst='StatusCrd')]
        form_editarcredenc.select_cloudloc.choices = [(s.opt, s.msg) for s in
                                                      ListaOpcoesDB.query.filter_by(lst='CloudLoc')]
        # form_editarcredenc.select_cliente.data = credencial.nomecliente
        form_editarcredenc.select_status.data = credencial.statenv
        form_editarcredenc.select_cloudloc.data = credencial.cloudloc
        form_editarcredenc.dtimplantac.data = credencial.dtimplantac
        form_editarcredenc.accesslevel.data = credencial.accesslevel
        form_editarcredenc.ambiente.data = credencial.ambiente
        form_editarcredenc.version.data = credencial.version
        form_editarcredenc.responsav.data = credencial.responsav
        form_editarcredenc.urlweb.data = credencial.urlweb
        form_editarcredenc.logindocc.data = credencial.logindocc
        form_editarcredenc.passwddocc.data = credencial.passwddocc
        form_editarcredenc.loginserv.data = credencial.loginserv
        form_editarcredenc.passwdserv.data = credencial.passwdserv
        form_editarcredenc.loginapi.data = credencial.loginapi
        form_editarcredenc.passwdapi.data = credencial.passwdapi
        form_editarcredenc.keyfile.data = credencial.keyfile
        form_editarcredenc.notas.data = credencial.notas

        if form_editarcredenc.validate_on_submit() and 'botao_submit_editarcredenc' in request.form:
            acslev = int(request.form.get('accesslevel'))
            credencial.statenv = form_editarcredenc.select_status.raw_data
            credencial.cloudloc = form_editarcredenc.select_cloudloc.raw_data
            credencial.idusuario = current_user.id
            credencial.dtalter = date.today()
            credencial.accesslevel = acslev
            credencial.dtimplantac = request.form.get('dtimplantac')
            credencial.ambiente = request.form.get('ambiente')
            credencial.version = request.form.get('version')
            credencial.responsav = request.form.get('responsav')
            credencial.urlweb = request.form.get('urlweb')
            credencial.logindocc = request.form.get('logindocc')
            credencial.passwddocc = request.form.get('passwddocc')
            credencial.loginserv = request.form.get('loginserv')
            credencial.passwdserv = request.form.get('passwdserv')
            credencial.loginapi = request.form.get('loginapi')
            credencial.passwdapi = request.form.get('passwdapi')
            credencial.keyfile = request.form.get('keyfile')
            credencial.notas = request.form.get('notas')
            database.session.add(credencial)
            database.session.commit()
            flash(f'Credencial {credencial.nomecliente} editada com sucesso!', 'alert-success')
            log_action('credenciais', 'credencedit', 'Credencial:' + credencial.nomecliente + ' alterada.')
            if acslev > current_user.access:
                flash(f'Seu nível de acesso {current_user.access} não poderá ver essa credencial!', 'alert-danger')
            return redirect(url_for('credenciais', status='ativo'))
    else:
        abort(403)
    return render_template('credencedit.html', form_editarcredenc=form_editarcredenc, credencial=credencial)

@app.route(f'{prefix}/credenciais/<status>')
@login_required
def credenciais(status):
    page = request.args.get('page', 1, type=int)
    Search = request.args.get('Search')
    # status do cliente = pode ser Ativo / Inativo
    if status == 'inativo':
        credencial = database.session.query(CredencialDB, usuario) \
            .join(usuario, CredencialDB.idusuario == usuario.id) \
            .filter(and_(CredencialDB.statenv == 'inativo', CredencialDB.active == 1, CredencialDB.accesslevel <= current_user.access))
    else:
        credencial = database.session.query(CredencialDB, usuario) \
            .join(usuario, CredencialDB.idusuario == usuario.id) \
            .filter(and_(CredencialDB.statenv == 'ativo', CredencialDB.active == 1, CredencialDB.accesslevel <= current_user.access))

    if Search:
        credencial = credencial.filter(
            or_(CredencialDB.nomecliente.contains(Search), CredencialDB.ambiente.contains(Search),
                CredencialDB.version.contains(Search), CredencialDB.logindocc.contains(Search),
                CredencialDB.loginserv.contains(Search), CredencialDB.urlweb.contains(Search),
                CredencialDB.notas.contains(Search), CredencialDB.responsav.contains(Search)))


    if status != 'dashboard.css':
        log_action('credenciais', 'credenciais', 'Listagem de credenciais ' + status)
    credencial = credencial.order_by(CredencialDB.nomecliente.asc()).paginate(page=page, per_page=maxLines)
    return render_template('credenciais.html', credencial=credencial, status=status, versBug=versBug)

@app.route(f'{prefix}/credencedit/<credenc_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_credenc(credenc_id):
    credencial = CredencialDB.query.get(credenc_id)
    if current_user.access >= 3:
        credencial.active = 0
        # database.session.delete(credencial)
        database.session.commit()
        flash(f'Credencial {credencial.nomecliente} excluida com sucesso!', 'alert-danger')
        log_action('credenciais', 'excluir', 'Credencial:' + credencial.nomecliente + ' excluída.')
        return redirect(url_for('credenciais', status='ativo'))
    else:
        abort(403)

@app.route(f'{prefix}/versionadd', methods=['GET', 'POST'])
@login_required
def versionadd():
    version = "NEW"
    form_editarversao = FormVersionEdit()
    form_editarversao.whoid.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='VersWhoId')]
    form_editarversao.produto.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Produto')]
    if request.method == 'POST':
        if form_editarversao.validate_on_submit() and 'botao_submit_editarversao' in request.form:
            version = VersionDB(idusuario=current_user.id,
                                active=1,
                                dtalter=date.today(),
                                produto=form_editarversao.produto.raw_data[0],
                                version = form_editarversao.version.data,
                                nomecliente = form_editarversao.nomecliente.data,
                                bug = evalint(request.form.get('bug')),
                                dtbug = request.form.get('dtbug') or None,
                                descricao = form_editarversao.descricao.data,
                                whoid = form_editarversao.whoid.raw_data[0],
                                chamado = form_editarversao.chamado.data,
                                prazofix = request.form.get('prazofix') or None,
                                bugfix = evalint(request.form.get('bugfix')),
                                dtfix = request.form.get('dtfix') or None,
                                versionfix = form_editarversao.versionfix.data)
            database.session.add(version)
            database.session.commit()
            flash(f'Versão criada com sucesso {version.version}!', 'alert-success')
            log_action('versions', 'versionadd', 'Versão:' + version.version + ' adicionada.')
            return redirect(url_for('versions'))
        else:
            flash(f'Formulário inválido: {form_editarversao.errors}', 'alert-danger')

    return render_template('versionedt.html', form_editarversao=form_editarversao, version=version)

@app.route(f'{prefix}/versionedt/<version_id>', methods=['GET', 'POST'])
@login_required
def versionedt(version_id):
    if current_user.access >= 2:
        form_editarversao = FormVersionEdit()
        version = VersionDB.query.get(version_id)
        form_editarversao.whoid.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='VersWhoId')]
        form_editarversao.whoid.data = version.whoid
        form_editarversao.produto.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='Produto')]
        form_editarversao.produto.data = version.produto
        form_editarversao.version.data = version.version
        form_editarversao.nomecliente.data = version.nomecliente
        form_editarversao.bug.data = version.bug
        form_editarversao.dtbug.data = version.dtbug
        form_editarversao.descricao.data = version.descricao
        form_editarversao.chamado.data = version.chamado
        form_editarversao.prazofix.data = version.prazofix
        form_editarversao.bugfix.data = version.bugfix
        form_editarversao.dtfix.data = version.dtfix
        form_editarversao.versionfix.data = version.versionfix
        if request.method == 'POST':
            if form_editarversao.validate_on_submit() and 'botao_submit_editarversao' in request.form:
                version.produto = form_editarversao.produto.raw_data[0]
                version.whoid = form_editarversao.whoid.raw_data[0]
                version.nomecliente = request.form.get('nomecliente')
                version.bug = evalint(request.form.get('bug'))
                version.dtbug = request.form.get('dtbug') or None
                version.descricao = request.form.get('descricao')
                version.chamado = request.form.get('chamado')
                version.prazofix = request.form.get('prazofix') or None
                version.bugfix = evalint(request.form.get('bugfix'))
                version.dtfix = request.form.get('dtfix') or None
                version.versionfix = request.form.get('versionfix')
                database.session.commit()
                flash(f'Versão {version.version} editada com sucesso!', 'alert-success')
                log_action('versions', 'versionedit', 'Versão:' + version.version + ' alterada.')
                return redirect(url_for('versions'))
            else:
                flash(f'Formulário inválido: {form_editarversao.errors}', 'alert-danger')
    else:
        abort(403)
    return render_template('versionedt.html', form_editarversao=form_editarversao, version=version)

def evalint(var):
    if var:
        if var == 'y' or var == 1 or var == '1':
            return 1
        else:
            return 0
    else:
       return 0

@app.route(f'{prefix}/versions')
@login_required
def versions():
    page = request.args.get('page', 1, type=int)
    Search = request.args.get('Search')
    versions = database.session.query(VersionDB, usuario).join(usuario, VersionDB.idusuario == usuario.id).filter(VersionDB.active == 1)
    if Search:
        versions = versions.filter(
            or_(VersionDB.produto.contains(Search),VersionDB.version.contains(Search),VersionDB.nomecliente.contains(Search),
                    VersionDB.descricao.contains(Search),VersionDB.chamado.contains(Search),VersionDB.versionfix.contains(Search)))
    log_action('versions', 'versions', 'Listagem de versões')
    versions = versions.order_by(VersionDB.produto.asc(),VersionDB.version.desc()).paginate(page=page, per_page=maxLines)
    return render_template('versions.html', versions=versions, cliCredenc=cliCredenc)

def cliCredenc(vers):
    nomes = (CredencialDB.query.with_entities(CredencialDB.nomecliente).filter(CredencialDB.version == vers).all())
    if not nomes:
        return "CLIENTES: Nenhum encontrado"
    nomes_lista = [n[0] for n in nomes]  # n é uma tupla (nomecliente,)
    return 'CLIENTES:\n' + '\n'.join(nomes_lista)

def versBug(vers):
    versao = (VersionDB.query.with_entities(VersionDB.version).filter(VersionDB.version == vers, VersionDB.active == 1, VersionDB.bug == 1).all())
    if not versao:
        return False
    else:
        return True

@app.route(f'{prefix}/versionedt/<version_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_version(version_id):
    version = VersionDB.query.get(version_id)
    if current_user.access >= 3:
        version.active = 0
        # database.session.delete(version)
        database.session.commit()
        flash(f'Versão {version.version} excluida com sucesso!', 'alert-danger')
        log_action('versions', 'excluir', 'Versão:' + version.version + ' excluída.')
        return redirect(url_for('versions'))
    else:
        abort(403)

@app.route(f'{prefix}/financ/<status>,<tipo>,<mesatl>', methods=['GET', 'POST'])
@login_required
def financ(status, tipo, mesatl):
    page = request.args.get('page', 1, type=int)
    Search = request.args.get('Search')
    currency = ConfigDB.query.filter_by(var='Currency').first().valor
    if not mesatl:
        mesatl = session['MESATL']

    dtinic = datetime.strptime('01-'+mesatl, '%d-%m-%Y').date()
    # Soma 1 mês ao primeiro dia, e subtrai um dia para pegar o último dia do mês, funciona para Fev de ano bissexto
    # if mesatl[0:2] == '12':
    if dtinic.month == 12:
        dtfim = datetime(dtinic.year+1, 1, 1) + timedelta(days=-1)
    else:
        dtfim = datetime(dtinic.year,dtinic.month+1,1) + timedelta(days=-1)

    total_itens = 0
    total_valor = 0
    # status financeiro = pode ser t=todos / a=aberto / p=pago
    # tipo financeiro = pode ser t=todos / r=receita / d=despesa
    if status == 'a':
        regstat = 0
    elif status == 'p':
        regstat = 1

    if status == 't':
        if tipo == 'r':
            financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                .filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.valor > 0))
        elif tipo == 'd':
            financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                .filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.valor <= 0))
        else:
            financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                .filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim))
    else:
        if tipo == 'r':
            financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.valor > 0))
        elif tipo == 'd':
            financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.valor <= 0))
        else:
            financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim))

    if Search:
        buscar = Search
        if Search[0] == '*':
            financeiro = database.session.query(FinancDB, usuario) \
                .join(usuario, FinancDB.idusuario == usuario.id).filter(FinancDB.active == 1)
            buscar = Search[1:]
                # .filter(and_(FinancDB.active == 1, (or_(FinancDB.descricao.contains(Search), FinancDB.observacao.contains(Search)))))
        financeiro = financeiro.filter(or_(FinancDB.benefic.contains(buscar), FinancDB.descricao.contains(buscar), FinancDB.observacao.contains(buscar)))
    else:
        buscar=''

    for item in financeiro:
        total_itens += 1
        total_valor += item.FinancDB.valor

    financeiro = financeiro.order_by(FinancDB.dt_data.asc()).paginate(page=page, per_page=(maxLines*15))

    meses = []
    for y in range(2017, (hoje.year+3)):
        for n in range(12):
            ns = '{:02}'.format(n + 1)
            ys = '{:04}'.format(y)
            meses = meses + [ns + '-' + ys]

    form_scope = FormFinancScope()
    form_scope.select_clifrn.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='ClientForn')]
    form_scope.select_clifrn.data = ' W3K Tecnologia'
    form_scope.select_mes.choices = meses
    form_scope.select_mes.data = mesatl
    form_scope.select_mesfim.choices = meses
    form_scope.select_mesfim.data = mesatl
    form_scope.select_stat.choices = [('t', 'Todos'), ('a', 'ABERTO'), ('p', 'PAGO')]
    form_scope.select_stat.data = status
    form_scope.select_tipo.choices = [('t', 'Todos'), ('r', 'RECEITA'), ('d', 'DESPESA')]
    form_scope.select_tipo.data = tipo
    if form_scope.validate_on_submit() or 'botao_submit_financscope' in request.form:
        mesatl = form_scope.select_mes.raw_data[0]
        status = form_scope.select_stat.raw_data[0]
        tipo = form_scope.select_tipo.raw_data[0]
        session['MESATL'] = mesatl
        return redirect(url_for('financ', status=status, tipo=tipo, mesatl=mesatl))

    form_financclose = FormFinancClose()
    form_financclose.dtpagto.data = date.today()
    # if form_financclose.validate_on_submit() or 'botao_submit_financlose' in request.form:
    #     dtpagto = request.form.get('dtpagto')
    #     return redirect(url_for('financ', status=status, tipo=tipo, mesatl=mesatl))
    if Search:
        log_action('financeiro', 'financ', 'Status:'+status+' Tipo:'+tipo+' MesAtl:'+mesatl+' Search:'+Search)
    else:
        log_action('financeiro', 'financ', 'Status:' + status + ' Tipo:' + tipo + ' MesAtl:' + mesatl)
    return render_template('financ.html', app=app, financeiro=financeiro, form_scope=form_scope, form_financclose=form_financclose, currency=currency,
                            status=status, tipo=tipo, mesatl=mesatl, hoje=hoje, Search=Search, total_itens=total_itens, total_valor=total_valor)

@app.route(f'{prefix}/financedit/<financ_id>,<financ_pg>,<status>,<tipo>,<mesatl>,<dtpg>/change', methods=['GET', 'POST'])
@login_required
def financ_change(financ_id, financ_pg, status, tipo, mesatl, dtpg):
    financ = FinancDB.query.get(financ_id)
    if 'botao_submit_financlose' in request.form:
        dtpg = request.form.get('dtpagto')
    if financ and current_user.access >= 4:
        if financ_pg == "0":
            financ.pago = 0
            financ.dtpagto = None
            database.session.commit()
        elif financ_pg == "1":
            financ.pago = 1
            if dtpg:
                financ.dtpagto = dtpg
            else:
                financ.dtpagto = date.today()
            database.session.commit()
        if financ_pg == "0":
            flash(f'Registro {financ.idfinanc} {financ.benefic} {financ.valor} aberto com sucesso!', 'alert-success')
        elif financ_pg == "1":
            flash(f'Registro {financ.idfinanc} {financ.benefic} {financ.valor} baixado com sucesso!', 'alert-success')
        else:
            flash(f'Parâmetro ({financ_id}-{financ_pg}) incorreto!', 'alert-danger')
        log_action('financeiro', 'financ_change','Id:'+financ_id+' PG:'+financ_pg+' Status:'+status+' Tipo:'+tipo+' Mes:'+mesatl+' DtPg:'+dtpg)
        return redirect(url_for('financ', status=status, tipo=tipo, mesatl=mesatl))
    else:
        flash(f'Ocorrência desconhecida ou nível de acesso insuficiente!', 'alert-danger')
    return redirect(url_for('financ', status=status, tipo=tipo, mesatl=mesatl))


@app.route(f'{prefix}/financ/<financ_id>,<status>,<tipo>,<mesatl>/excluir')
@login_required
def excluir_financ(financ_id,status,tipo,mesatl):
    financ = FinancDB.query.get(financ_id)
    if financ and current_user.access >= 4:
        financ.active = 0
        # database.session.delete(credencial)
        database.session.commit()
        flash(f'Registro {financ.idfinanc} {financ.benefic} excluido com sucesso!', 'alert-danger')
        log_action('financeiro', 'excluir_financ','Id:'+financ_id+' Status:'+status+' Tipo:'+tipo+' Mes:'+mesatl)
        return redirect(url_for('financ', status=status, tipo=tipo, mesatl=mesatl))
    else:
        flash(f'Ocorrência desconhecida ou nível de acesso insuficiente!', 'alert-danger')
    return redirect(url_for('financ', status=status, tipo=tipo, mesatl=mesatl))

@app.route(f'{prefix}/financedit/<int:financ_id>', methods=['GET', 'POST'])
@login_required
def financedit(financ_id):
    if current_user.access >= 4:
        form_financedit = FormFinancEdit()
        financeiro = FinancDB.query.get(financ_id)
        # form_financedit.valor.data = financeiro.valor
        form_financedit.categoria.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='FinCategor').order_by(ListaOpcoesDB.opt)]
        form_financedit.categoria.data = financeiro.categoria
        form_financedit.subcategor.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SubCategor').order_by(ListaOpcoesDB.opt)]
        form_financedit.subcategor.data = financeiro.subcategor
        form_financedit.benefic.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='ClientForn').order_by(ListaOpcoesDB.opt)]
        form_financedit.benefic.data = financeiro.benefic
        form_financedit.frequencia.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='FatFreq').order_by(ListaOpcoesDB.opt)]
        form_financedit.frequencia.data = 'Unico'
        form_financedit.parcelas.data = 1
        form_financedit.dt_data.data = financeiro.dt_data
        dtpgt = financeiro.dtpagto
        form_financedit.dtpagto.data = dtpgt
        dtfat = financeiro.dtfatur
        form_financedit.dtfatur.data = dtfat
        form_financedit.descricao.data = financeiro.descricao
        form_financedit.observacao.data = financeiro.observacao
        valor = financeiro.valor
        if valor > 0:
            form_financedit.tipo = 'R'
            form_financedit.valor.data = valor
        else:
            form_financedit.tipo = 'D'
            form_financedit.valor.data = -valor

        if form_financedit.validate_on_submit() and 'botao_submit_financedit' in request.form:
            financeiro.idusuario = current_user.id
            financeiro.dtalter = date.today()
            financeiro.categoria = request.form.get('categoria')
                            # form_financedit.categoria.raw_data
            financeiro.subcategor = request.form.get('subcategor')
            financeiro.benefic = request.form.get('benefic')
            financeiro.dt_data = request.form.get('dt_data')
            dpg = request.form.get('dtpagto')
            if dpg:
                if dpg != dtpgt:
                    financeiro.pago = 1
                financeiro.dtpagto = dpg
            else:
                financeiro.pago = 0
            dpg = request.form.get('dtfatur')
            if dpg:
                if dpg != dtfat:
                    financeiro.faturado = 1
                financeiro.dtfatur = dpg
            else:
                financeiro.faturado = 0

            financeiro.descricao = request.form.get('descricao')
            financeiro.observacao = request.form.get('observacao')
            if form_financedit.tipo == 'R':
                financeiro.valor = float(request.form.get('valor'))
            elif form_financedit.tipo == 'D':
                financeiro.valor = -abs(float(request.form.get('valor')))
            else:
                financeiro.valor = 0
            database.session.add(financeiro)
            database.session.commit()
            if form_financedit.tipo == 'R':
                flash(f'Receita {financeiro.idfinanc} {financeiro.benefic} editada com sucesso!', 'alert-success')
            else:
                flash(f'Despesa {financeiro.idfinanc} {financeiro.benefic} editada com sucesso!', 'alert-success')
            log_action('financeiro', 'financ_edit', 'Id:' + str(financ_id)+' Tipo:'+form_financedit.tipo+' Valor:'+str(valor)+' Novo:'+str(financeiro.valor)+' Benef:'+financeiro.benefic)
            return redirect(url_for('financ', status='t', tipo='t', mesatl=session['MESATL']))
    else:
        abort(403)
    return render_template('financedit.html', form_financedit=form_financedit, financeiro=financeiro)


@app.route(f'{prefix}/financadd/<type>', methods=['GET', 'POST'])
@login_required
def financadd(type):
    financeiro = "NEW"
    form_financedit = FormFinancEdit()
    form_financedit.categoria.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='FinCategor').order_by(ListaOpcoesDB.opt)]
    form_financedit.subcategor.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='SubCategor').order_by(ListaOpcoesDB.opt)]
    form_financedit.benefic.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='ClientForn').order_by(ListaOpcoesDB.opt)]
    form_financedit.frequencia.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='FatFreq').order_by(ListaOpcoesDB.opt)]
    form_financedit.frequencia.data = 'Unico'
    form_financedit.parcelas.data = 1
    form_financedit.dt_data.data = date.today()
    form_financedit.valor.data = 0

    if form_financedit.validate_on_submit() and 'botao_submit_financedit' in request.form:
        if type == 'R':
            value = float(request.form.get('valor'))
        elif type == 'D':
            value = -abs(float(request.form.get('valor')))
        else:
            value = 0
        freq = form_financedit.frequencia.raw_data[0]
        parc = int(request.form.get('parcelas'))
        data = datetime.strptime(request.form.get('dt_data'), '%Y-%m-%d').date()
        observ = request.form.get('observacao')
        if parc > 1 and freq != 'Unico':
            if freq == 'Mensal':
                for n in range(parc):
                    financeiro = FinancDB(idusuario=current_user.id, active=1, dtpagto=None, dtfatur=None, dtcriac=date.today(), dtalter=date.today(),
                                  pago=0, faturado=0, valor=value, dt_data=data,categoria=form_financedit.categoria.raw_data,
                                  subcategor=form_financedit.subcategor.raw_data,benefic=form_financedit.benefic.raw_data,
                                  descricao=request.form.get('descricao'),observacao=observ + ' - Mensal Parc(' + str(n+1) + '/' + str(parc) + ')')
                    database.session.add(financeiro)
                    database.session.commit()
                    data = data + relativedelta(months=+1)
            elif freq == 'Anual':
                for n in range(parc):
                    financeiro = FinancDB(idusuario=current_user.id, active=1, dtpagto=None, dtfatur=None, dtcriac=date.today(),dtalter=date.today(),
                                  pago=0, faturado=0, valor=value, dt_data=data, categoria=form_financedit.categoria.raw_data,
                                  subcategor=form_financedit.subcategor.raw_data,benefic=form_financedit.benefic.raw_data,
                                  descricao=request.form.get('descricao'),observacao=observ + ' - Anual Parc(' + str(n + 1) + '/' + str(parc) + ')')
                    database.session.add(financeiro)
                    database.session.commit()
                    data = data + relativedelta(years=+1)
            elif freq == 'Semanal':
                for n in range(parc):
                    financeiro = FinancDB(idusuario=current_user.id, active=1, dtpagto=None, dtfatur=None, dtcriac=date.today(),dtalter=date.today(),
                                  pago=0, faturado=0, valor=value, dt_data=data, categoria=form_financedit.categoria.raw_data,
                                  subcategor=form_financedit.subcategor.raw_data,benefic=form_financedit.benefic.raw_data,
                                  descricao=request.form.get('descricao'),observacao=observ + ' - Semanal Parc(' + str(n + 1) + '/' + str(parc) + ')')
                    database.session.add(financeiro)
                    database.session.commit()
                    data = data + relativedelta(days=+7)
            elif freq == 'Quinzenal':
                for n in range(parc):
                    financeiro = FinancDB(idusuario=current_user.id, active=1, dtpagto=None, dtfatur=None, dtcriac=date.today(),dtalter=date.today(),
                                  pago=0, faturado=0, valor=value, dt_data=data, categoria=form_financedit.categoria.raw_data,
                                  subcategor=form_financedit.subcategor.raw_data,benefic=form_financedit.benefic.raw_data,
                                  descricao=request.form.get('descricao'),observacao=observ + ' - Quinzenal Parc(' + str(n + 1) + '/' + str(parc) + ')')
                    database.session.add(financeiro)
                    database.session.commit()
                    data = data + relativedelta(days=+15)
            elif freq == 'Semestral':
                for n in range(parc):
                    financeiro = FinancDB(idusuario=current_user.id, active=1, dtpagto=None, dtfatur=None, dtcriac=date.today(),dtalter=date.today(),
                                  pago=0, faturado=0, valor=value, dt_data=data, categoria=form_financedit.categoria.raw_data,
                                  subcategor=form_financedit.subcategor.raw_data,benefic=form_financedit.benefic.raw_data,
                                  descricao=request.form.get('descricao'),observacao=observ + ' - Semestral Parc(' + str(n + 1) + '/' + str(parc) + ')')
                    database.session.add(financeiro)
                    database.session.commit()
                    data = data + relativedelta(months=+6)
            elif freq == 'Trimestral':
                for n in range(parc):
                    financeiro = FinancDB(idusuario=current_user.id, active=1, dtpagto=None, dtfatur=None, dtcriac=date.today(),dtalter=date.today(),
                                  pago=0, faturado=0, valor=value, dt_data=data, categoria=form_financedit.categoria.raw_data,
                                  subcategor=form_financedit.subcategor.raw_data,benefic=form_financedit.benefic.raw_data,
                                  descricao=request.form.get('descricao'),observacao=observ + ' - Trimestral Parc(' + str(n + 1) + '/' + str(parc) + ')')
                    database.session.add(financeiro)
                    database.session.commit()
                    data = data + relativedelta(months=+3)
            elif freq == 'Bimestral':
                for n in range(parc):
                    financeiro = FinancDB(idusuario=current_user.id, active=1, dtpagto=None, dtfatur=None, dtcriac=date.today(),dtalter=date.today(),
                                  pago=0, faturado=0, valor=value, dt_data=data, categoria=form_financedit.categoria.raw_data,
                                  subcategor=form_financedit.subcategor.raw_data,benefic=form_financedit.benefic.raw_data,
                                  descricao=request.form.get('descricao'),observacao=observ + ' - Bimestral Parc(' + str(n + 1) + '/' + str(parc) + ')')
                    database.session.add(financeiro)
                    database.session.commit()
                    data = data + relativedelta(months=+2)
            elif freq == 'Bianual':
                for n in range(parc):
                    financeiro = FinancDB(idusuario=current_user.id, active=1, dtpagto=None, dtfatur=None, dtcriac=date.today(),dtalter=date.today(),
                                  pago=0, faturado=0, valor=value, dt_data=data, categoria=form_financedit.categoria.raw_data,
                                  subcategor=form_financedit.subcategor.raw_data,benefic=form_financedit.benefic.raw_data,
                                  descricao=request.form.get('descricao'),observacao=observ + ' - Bianual Parc(' + str(n + 1) + '/' + str(parc) + ')')
                    database.session.add(financeiro)
                    database.session.commit()
                    data = data + relativedelta(years=+2)
            elif freq == 'Trianual':
                for n in range(parc):
                    financeiro = FinancDB(idusuario=current_user.id, active=1, dtpagto=None, dtfatur=None, dtcriac=date.today(),dtalter=date.today(),
                                  pago=0, faturado=0, valor=value, dt_data=data, categoria=form_financedit.categoria.raw_data,
                                  subcategor=form_financedit.subcategor.raw_data,benefic=form_financedit.benefic.raw_data,
                                  descricao=request.form.get('descricao'),observacao=observ + ' - Trianual Parc(' + str(n + 1) + '/' + str(parc) + ')')
                    database.session.add(financeiro)
                    database.session.commit()
                    data = data + relativedelta(years=+3)
        else:
            financeiro = FinancDB(idusuario=current_user.id, active=1, dtpagto=None, dtfatur=None,
                                  dtcriac=date.today(), dtalter=date.today(), pago=0, faturado=0,
                                  valor=value, dt_data=request.form.get('dt_data'),
                                  categoria=form_financedit.categoria.raw_data,
                                  subcategor=form_financedit.subcategor.raw_data,
                                  benefic=form_financedit.benefic.raw_data,
                                  descricao=request.form.get('descricao'),
                                  observacao=request.form.get('observacao')
                                  )
            database.session.add(financeiro)
            database.session.commit()
        log_action('financeiro', 'financ_add', 'Tipo:' + type+' Vlr:'+str(value)+' '+str(parc)+'x '+freq+' Benef:'+financeiro.benefic)
        if type == 'R':
            flash(f'{parc}x Receita de {financeiro.benefic} criada com sucesso!', 'alert-success')
        else:
            flash(f'{parc}x Despesa de {financeiro.benefic} criada com sucesso!', 'alert-success')
        return redirect(url_for('financ', status='t', tipo='t', mesatl=session['MESATL']))
    return render_template('financedit.html', form_financedit=form_financedit, financeiro=financeiro)


@app.route(f'{prefix}/relatorios/<mesatl>')
def relatorios(mesatl):
    if not mesatl:
        mesatl = session['MESATL']
    return render_template('relatorios.html', hoje=hoje, mesatl=session['MESATL'], mesfim=session['MESFIM'])


@app.route(f'{prefix}/relatforn/<mesatl>,<mesfim>,<benef>', methods=['GET', 'POST'])
@login_required
def relatforn(mesatl,mesfim,benef):
    currency = ConfigDB.query.filter_by(var='Currency').first().valor
    if not mesatl:
        mesatl = session['MESATL']
    if not mesfim:
        mesfim = session['MESFIM']

    meses = []
    for y in range(2017, (hoje.year+3)):
        for n in range(12):
            ns = '{:02}'.format(n + 1)
            ys = '{:04}'.format(y)
            meses = meses + [ns + '-' + ys]
    form_scope = FormFinancScope()
    form_scope.select_clifrn.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='ClientForn')]
    if benef == 'W3K Tecnologia':
        form_scope.select_clifrn.data = benef
    form_scope.select_mes.choices = meses
    form_scope.select_mes.data = mesatl
    form_scope.select_mesfim.choices = meses
    form_scope.select_mesfim.data = mesfim
    form_scope.select_stat.choices = [('t', 'Todos'), ('a', 'ABERTO'), ('p', 'PAGO')]
    form_scope.select_stat.data = 't'
    form_scope.select_tipo.choices = [('t', 'Todos'), ('r', 'RECEITA'), ('d', 'DESPESA')]
    form_scope.select_tipo.data = 't'
    if form_scope.validate_on_submit() or 'botao_submit_financscope' in request.form:
        if benef == 'W3K Tecnologia':
            clifrn = benef
            mesatl = form_scope.select_mes.raw_data[0]
            mesfim = form_scope.select_mesfim.raw_data[0]
            status = 'p'
            tipo = 't'
        else:
            clifrn = form_scope.select_clifrn.raw_data[0]
            mesatl = form_scope.select_mes.raw_data[0]
            mesfim = form_scope.select_mesfim.raw_data[0]
            status = form_scope.select_stat.raw_data[0]
            tipo = form_scope.select_tipo.raw_data[0]
        log_action('relatorio', 'relatforn', 'Benef:' + benef + ' Mes:' + mesatl + ' ate:' + mesfim)
        session['MESATL'] = mesatl
        session['MESFIM'] = mesfim
        return redirect(url_for('relfrn_new', clifrn=clifrn, status=status, tipo=tipo, mesatl=mesatl, mesfim=mesfim, benef=benef, currency=currency))
    return render_template('relatforn.html', form_scope=form_scope, mesatl=session['MESATL'], mesfim=session['MESFIM'], hoje=hoje, benef=benef, currency=currency)

@app.route(f'{prefix}/relatcfcs/<mesatl>,<mesfim>,<scope>,<status>,<tipo>', methods=['GET', 'POST'])
@login_required
def relatcfcs(mesatl,mesfim,scope, status, tipo):
    currency = ConfigDB.query.filter(ConfigDB.var=='Currency').first().valor

    if not mesfim:
        if session['MESFIM']:
            mesfim = session['MESFIM']
        else:
            mesfim = mesatl

    meses = []
    for y in range(2017, (hoje.year+3)):
        for n in range(12):
            ns = '{:02}'.format(n + 1)
            ys = '{:04}'.format(y)
            meses = meses + [ns + '-' + ys]

    form_scope = FormFinancCfcs()
    form_scope.select_cfcs.choices = (
    ('CliFor', 'CliFor'), ('Categoria', 'Categoria'), ('Subcategoria', 'Subcategoria'))
    form_scope.select_cfcs.data = scope
    form_scope.select_mes.choices = meses
    form_scope.select_mes.data = mesatl
    form_scope.select_mesfim.choices = meses
    form_scope.select_mesfim.data = mesfim
    form_scope.select_stat.choices = [('t', 'Todos'), ('a', 'ABERTO'), ('p', 'PAGO')]
    form_scope.select_stat.data = status
    form_scope.select_tipo.choices = [('t', 'Todos'), ('r', 'RECEITA'), ('d', 'DESPESA')]
    form_scope.select_tipo.data = tipo
    if form_scope.validate_on_submit() or 'botao_submit_financcfcs' in request.form:
        scope = form_scope.select_cfcs.raw_data[0]
        mesatl = form_scope.select_mes.raw_data[0]
        mesfim = form_scope.select_mesfim.raw_data[0]
        status = form_scope.select_stat.raw_data[0]
        tipo = form_scope.select_tipo.raw_data[0]
        session['MESATL'] = mesatl
        session['MESFIM'] = mesfim
        form_scope.select_cfcs.data = scope
        form_scope.select_stat.data = status
        form_scope.select_tipo.data = tipo
        form_scope.select_mes.data = mesatl
        form_scope.select_mesfim.data = mesfim
        log_action('relatorio', 'relatcfcs', 'Scope:' + scope + ' Mes:' + mesatl + ' ate:' + mesfim)
        # return redirect(url_for('relatcfcs', scope=scope, status=status, tipo=tipo, mesatl=mesatl, mesfim=mesfim,
        #                financeiro=financeiro, total_itens=total_itens, total_valor=total_valor, labelvalues=labelvalues, valorvalues=valorvalues, hoje=hoje, currency=currency))

    dtinic = datetime.strptime('01-' + mesatl, '%d-%m-%Y').date()
    dtfim = datetime.strptime('01-' + mesfim, '%d-%m-%Y').date()
    if dtfim.month == 12:
        dtfim = datetime(dtfim.year + 1, 1, 1) + timedelta(days=-1)
    else:
        dtfim = datetime(dtfim.year, dtfim.month + 1, 1) + timedelta(days=-1)

    # status financeiro t=todos / p=pago / a=aberto
    # tipo financeiro = pode ser t=todos / r=receita / d=despesa
    if status == 'a':
        regstat = 0
    elif status == 'p':
        regstat = 1
    else:
        regstat = 9

    if status == 't':
        if tipo == 'r':
            financeiro = FinancDB.query.filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.valor > 0))
        elif tipo == 'd':
            financeiro = FinancDB.query.filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.valor <= 0))
        else:
            financeiro = FinancDB.query.filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim))
    else:
        if tipo == 'r':
            financeiro = FinancDB.query.filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.valor > 0))
        elif tipo == 'd':
            financeiro = FinancDB.query.filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.valor <= 0))
        else:
            financeiro = FinancDB.query.filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim))

    total_itens = 0
    total_valor = Decimal(0)
    for item in financeiro:
        total_itens += 1
        total_valor += item.valor

    # Criando um dicionário para agrupar os valores por 'benefic'
    agrupado = defaultdict(float)

    if scope == 'Subcategoria':
        financeiro = financeiro.order_by(FinancDB.subcategor.asc()).all()
        # Consulta agrupando por 'subcategor' e somando os valores
        for item in financeiro:
            if item.subcategor:  # Evitar problemas com valores None
                agrupado[item.subcategor] += float(item.valor) if item.valor else 0.0
    elif scope == 'Categoria':
        financeiro = financeiro.order_by(FinancDB.categoria.asc()).all()
        # Consulta agrupando por 'categoria' e somando os valores
        for item in financeiro:
            if item.categoria:  # Evitar problemas com valores None
                agrupado[item.categoria] += float(item.valor) if item.valor else 0.0
    else:
        financeiro = financeiro.order_by(FinancDB.benefic.asc()).all()
        # Consulta agrupando por 'benefic' e somando os valores
        for item in financeiro:
            if item.benefic:  # Evitar problemas com valores None
                agrupado[item.benefic] += float(item.valor) if item.valor else 0.0

    # Criando as listas para o gráfico
    labelvalues = list(agrupado.keys())  # Beneficiários (rótulos do gráfico)
    valorvalues = list(agrupado.values())  # Valores somados

    return render_template('relatcfcs.html', form_scope=form_scope, scope=scope, status=status, tipo=tipo, mesatl=mesatl, mesfim=mesfim,
                       financeiro=financeiro, total_itens=total_itens, total_valor=total_valor, labelvalues=labelvalues, valorvalues=valorvalues, hoje=hoje, currency=currency)

@app.route(f'{prefix}/relattecn/<mesatl>', methods=['GET', 'POST'])
@login_required
def relattecn(mesatl):
    currency = ConfigDB.query.filter_by(var='Currency').first().valor
    btAceit = ConfigDB.query.filter_by(var='TechAceitBonus').first().valor
    btAtest = ConfigDB.query.filter_by(var='TechAtestBonus').first().valor
    meses = []
    for y in range(2017, (hoje.year+3)):
        for n in range(12):
            ns = '{:02}'.format(n + 1)
            ys = '{:04}'.format(y)
            meses = meses + [ns + '-' + ys]

    form_scope = FormScopeTecn()
    form_scope.select_mes.choices = meses
    form_scope.select_mes.data = mesatl
    if form_scope.validate_on_submit() or 'botao_submit_scopetecn' in request.form:
        mesatl = form_scope.select_mes.raw_data[0]
        # mesfim = form_scope.select_mesfim.raw_data[0]
        # session['MESATL'] = mesatl
        form_scope.select_mes.data = mesatl
        log_action('relatorio', 'relattecn', ' Mes:' + mesatl)

    if re.match(r'^\d{2}-\d{4}$', mesatl):
        session['MESATL'] = mesatl
    else:
        # Redirecionar ou lançar erro apropriado
        # abort(400, description="Parâmetro de data inválido.")
        mesatl = session['MESATL']

    dtinic = datetime.strptime('01-' + mesatl, '%d-%m-%Y').date()
    dtfim = datetime.strptime('01-' + mesatl, '%d-%m-%Y').date()

    if dtfim.month == 12:
        dtfim = datetime(dtfim.year + 1, 1, 1) + timedelta(days=-1)
    else:
        dtfim = datetime(dtfim.year, dtfim.month + 1, 1) + timedelta(days=-1)

    projetos = database.session.query(ProjetosDB, usuario, ClientesDB) \
            .join(usuario, ProjetosDB.idusuario == usuario.id) \
            .join(ClientesDB, ProjetosDB.idclint == ClientesDB.idcliente) \
            .filter(or_(ProjetosDB.statusproj == 'ativo', ProjetosDB.statusproj == 'aceito'))
    projaceitos = database.session.query(ProjetosDB, ClientesDB).join(ClientesDB, ProjetosDB.idclint == ClientesDB.idcliente) \
            .filter(and_(ProjetosDB.aceitedata >= dtinic, ProjetosDB.aceitedata <= dtfim, ProjetosDB.aceiteproj == 'Sim')).all()
    btAceitos = float(btAceit) * len(projaceitos) if projaceitos else 0
    projatestados = database.session.query(ProjetosDB, ClientesDB).join(ClientesDB, ProjetosDB.idclint == ClientesDB.idcliente) \
            .filter(and_(ProjetosDB.atestadodat >= dtinic, ProjetosDB.atestadodat <= dtfim, ProjetosDB.atestado == 'Sim')).all()
    btAtestados = float(btAtest) * len(projatestados) if projatestados else 0

    total_itens = 0
    total_horas = Decimal(0)
    for item in projetos:
        total_itens += 1
        total_horas += item.ProjetosDB.horasprev

    # Criando um dicionário para agrupar os valores por 'benefic'
    hsprev = defaultdict(float)
    hsused = defaultdict(float)

    projetos = projetos.order_by(ProjetosDB.projetonome.asc()).all()
        # Consulta agrupando por 'benefic' e somando os valores
    for item in projetos:
        if item.ProjetosDB.projetonome:  # Evitar problemas com valores None
            hsprev[item.ProjetosDB.projetonome] += float(item.ProjetosDB.horasprev) if item.ProjetosDB.horasprev else 0.0
            hsused[item.ProjetosDB.projetonome] += float(item.ProjetosDB.horasusds) if item.ProjetosDB.horasusds else 0.0

    # Criando as listas para o gráfico
    labelvalues = list(hsprev.keys())  # Projetos (rótulos do gráfico)
    valorvaluesprev = list(hsprev.values())  # Horas somados
    valorvaluesused = list(hsused.values())  # Horas somados

    return render_template('relattecn.html', form_scope=form_scope, mesatl=mesatl, hoje=hoje, btAceitos=btAceitos, btAtestados=btAtestados,
                           projetos=projetos, total_itens=total_itens, total_horas=total_horas, labelvalues=labelvalues, currency=currency,
                           valorvaluesprev=valorvaluesprev,  valorvaluesused=valorvaluesused, projaceitos=projaceitos, projatestados=projatestados)

@app.route(f'{prefix}/relatpipe/<mesatl>', methods=['GET', 'POST'])
@login_required
def relatpipe(mesatl):
    currency = ConfigDB.query.filter_by(var='Currency').first().valor
    bcApres = ConfigDB.query.filter_by(var='ComlApresBonus').first().valor
    bcOrder = ConfigDB.query.filter_by(var='ComlOrderBonus').first().valor

    meses = []
    for y in range(2017, hoje.year + 3):
        for n in range(12):
            ns = f'{n + 1:02}'
            ys = f'{y:04}'
            meses.append(f'{ns}-{ys}')

    form_scope = FormScopeTecn()
    form_scope.select_mes.choices = meses
    form_scope.select_mes.data = mesatl

    if form_scope.validate_on_submit() or 'botao_submit_scopetecn' in request.form:
        mesatl = form_scope.select_mes.raw_data[0]
        form_scope.select_mes.data = mesatl
        log_action('relatorio', 'relattecn', ' Mes:' + mesatl)

    if re.match(r'^\d{2}-\d{4}$', mesatl):
        session['MESATL'] = mesatl
    else:
        mesatl = session['MESATL']

    dtinic = datetime.strptime('01-' + mesatl, '%d-%m-%Y').date()
    dtfim = (dtinic.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    ano = int(mesatl.split('-')[1])
    anoini = datetime(ano, 1, 1).date()
    anofim = datetime(ano, 12, 31).date()

    apresentacoes = database.session.query(PipelineDB, usuario, ClientesDB)\
        .join(usuario, PipelineDB.vendedor == usuario.id)\
        .join(ClientesDB, PipelineDB.idcliente == ClientesDB.idcliente)\
        .filter(or_(PipelineDB.status == 'Ativo', PipelineDB.status == 'Lead'),
                PipelineDB.dtapres.between(dtinic, dtfim))\
        .all()

    bcApresent = float(bcApres) * len(apresentacoes) if apresentacoes else 0

    apresent_ano = database.session.query(PipelineDB, usuario, ClientesDB)\
        .join(usuario, PipelineDB.idusuario == usuario.id)\
        .join(ClientesDB, PipelineDB.idcliente == ClientesDB.idcliente)\
        .filter(PipelineDB.dtapres.between(anoini, anofim))\
        .all()

    graf_apresent_por_mes = defaultdict(int)
    for p, u, c in apresent_ano:
        mes_ano = p.dtapres.strftime('%m-%Y')
        graf_apresent_por_mes[mes_ano] += 1

    pedidos = database.session.query(ContratosDB, usuario, ClientesDB)\
        .join(usuario, ContratosDB.idusuario == usuario.id)\
        .join(ClientesDB, ContratosDB.idcliente == ClientesDB.idcliente)\
        .filter(ContratosDB.status == 'Ativo',
                ContratosDB.dtpedido.between(dtinic, dtfim))\
        .all()

    bcPedidos = float(bcOrder) * len(pedidos) if pedidos else 0

    pedidos_ano = database.session.query(ContratosDB, usuario, ClientesDB)\
        .join(usuario, ContratosDB.idusuario == usuario.id)\
        .join(ClientesDB, ContratosDB.idcliente == ClientesDB.idcliente)\
        .filter(ContratosDB.dtpedido.between(anoini, anofim))\
        .all()

    graf_pedidos_por_mes = defaultdict(int)
    for p, u, c in pedidos_ano:
        mes_ano = p.dtpedido.strftime('%m-%Y')
        graf_pedidos_por_mes[mes_ano] += 1

    # Unificar os meses de ambas as séries
    meses_unificados = sorted(set(graf_apresent_por_mes.keys()) | set(graf_pedidos_por_mes.keys()),
                              key=lambda x: datetime.strptime(x, '%m-%Y'))

    # Garantir alinhamento dos dados no gráfico
    valores_apresent = [graf_apresent_por_mes.get(mes, 0) for mes in meses_unificados]
    valores_pedidos = [graf_pedidos_por_mes.get(mes, 0) for mes in meses_unificados]

    return render_template('relatpipe.html', form_scope=form_scope, mesatl=mesatl, hoje=hoje, ano=ano, currency=currency, totPedidos=len(pedidos),
                           bcApresent=bcApresent, bcPedidos=bcPedidos, totApresent=len(apresentacoes), pedidos=pedidos, apresentacoes=apresentacoes,
                           labels_apresent=meses_unificados, valores_apresent=valores_apresent, labels_pedidos=meses_unificados, valores_pedidos=valores_pedidos)

@app.route(f'{prefix}/relatusers/<mesatl>', methods=['GET', 'POST'])
@login_required
def relatusers(mesatl):
    if not mesatl:
        mesatl = session['MESATL']
    meses = []
    for y in range(2017, (hoje.year+3)):
        for n in range(12):
            ns = '{:02}'.format(n + 1)
            ys = '{:04}'.format(y)
            meses = meses + [ns + '-' + ys]
    form_scope = FormUsersScope()
    form_scope.select_user.choices = [(s.username) for s in usuario.query.all()] + ["TODOS"]
    form_scope.select_user.data = "TODOS"
    form_scope.select_mes.choices = meses
    form_scope.select_mes.data = mesatl
    form_scope.select_mesfim.choices = meses
    form_scope.select_mesfim.data = session['MESFIM']
    if form_scope.validate_on_submit() or 'botao_submit_usersscope' in request.form:
        users = form_scope.select_user.raw_data[0]
        mesatl = form_scope.select_mes.raw_data[0]
        mesfim = form_scope.select_mesfim.raw_data[0]
        session['MESATL'] = mesatl
        session['MESFIM'] = mesfim
        # log_action('relatorio', 'relatusers', 'User:' + users + ' De:' + mesatl + ' a '+ mesfim)
        return redirect(url_for('relatusrs', usrname=users, mesatl=mesatl, mesfim=mesfim))
    return render_template('relatusers.html', form_scope=form_scope, mesatl=mesatl)

@app.route(f'{prefix}/relatusrs/<usrname>,<mesatl>,<mesfim>')
@login_required
def relatusrs(usrname,mesatl,mesfim):
    if current_user.access >= 4:
        dtinicial = datetime.strptime('01-' + mesatl, '%d-%m-%Y').date()
        dtfinal = datetime.strptime('01-' + mesfim, '%d-%m-%Y').date()
        # Soma 1 mês ao primeiro dia, e subtrai um dia para pegar o último dia do mês, funciona para Fev de ano bissexto
        if mesfim[0:2] == '12':
            dtfim = datetime(dtfinal.year + 1, 1, 1) + timedelta(days=-1)
        else:
            dtfim = datetime(dtfinal.year, dtfinal.month + 1, 1) + timedelta(days=-1)

        if usrname == "TODOS":
            operacoes = database.session.query(LogDB, usuario).join(usuario, LogDB.idusuario == usuario.id) \
                .filter(and_(LogDB.datahora >= dtinicial, LogDB.datahora <= dtfim))
        else:
            operacoes = database.session.query(LogDB, usuario).join(usuario, LogDB.idusuario == usuario.id) \
                .filter(and_(usuario.username == usrname, LogDB.datahora >= dtinicial, LogDB.datahora <= dtfim))

        total_itens = 0
        for row in operacoes:
            total_itens += 1
            utc_datetime = original_timezone.localize(row[0].datahora)
            # Convert the datahora to your local timezone
            datahora_local = utc_datetime.astimezone(local_tz)
            # Update the datahora value in the query result
            row[0].datahora = datahora_local

    # log_action('relatorio', 'relatusrs', 'User:' + usrname + ' De:' + mesatl + ' a ' + mesfim)
    return render_template('relatusrs.html', usrname=usrname, total_itens=total_itens, operacoes=operacoes, mesatl=mesatl, mesfim=mesfim, hoje=hoje)

@app.route(f'{prefix}/relfatur/<status>, <tipo>, <mesatl>', methods=['GET', 'POST'])
@login_required
def relfatur(status,tipo,mesatl):
    currency = ConfigDB.query.filter_by(var='Currency').first().valor
    if not mesatl:
        mesatl = session['MESATL']

    meses = []
    for y in range(2017, (hoje.year+3)):
        for n in range(12):
            ns = '{:02}'.format(n + 1)
            ys = '{:04}'.format(y)
            meses = meses + [ns + '-' + ys]
    form_scope = FormFinancScope()
    form_scope.select_clifrn.choices = [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='ClientForn')]
    form_scope.select_mes.choices = meses
    form_scope.select_mes.data = mesatl
    form_scope.select_mesfim.choices = meses
    form_scope.select_mesfim.data = mesatl
    form_scope.select_stat.choices = [('t', 'Todos'), ('a', 'ABERTO'), ('p', 'PAGO')]
    form_scope.select_stat.data = 't'
    form_scope.select_tipo.choices = [('t', 'Todos'), ('r', 'RECEITA'), ('d', 'DESPESA')]
    form_scope.select_tipo.data = 't'
    if form_scope.validate_on_submit() or 'botao_submit_financscope' in request.form:
        mesatl = form_scope.select_mes.raw_data[0]
        status = 't'
        tipo = 'r'
        session['MESATL'] = mesatl
        # status = form_scope.select_stat.raw_data[0]
        # tipo = form_scope.select_tipo.raw_data[0]
        return redirect(url_for('relatfatur', status=status, tipo=tipo, mesatl=mesatl, currency=currency))
    log_action('relatorio', 'relfatur','Status:' + status + ' Tipo:' + tipo +' Mes:' + mesatl)
    return render_template('relfatur.html', form_scope=form_scope, mesatl=mesatl, hoje=hoje, currency=currency)

@app.route(f'{prefix}/relfrn_new/<clifrn>,<status>,<tipo>,<mesatl>,<mesfim>,<benef>')
@login_required
def relfrn_new(clifrn,status,tipo,mesatl,mesfim,benef):

    if current_user.access >= 4:
        currency = ConfigDB.query.filter_by(var='Currency').first().valor
        cliforn = "%"+clifrn+"%"

        total_itens = 0
        total_valor = 0

        dtinic = datetime.strptime('01-' + mesatl, '%d-%m-%Y').date()
        dtfim = datetime.strptime('01-' + mesfim, '%d-%m-%Y').date()
        # Soma 1 mês ao primeiro dia, e subtrai um dia para pegar o último dia do mês, funciona para Fev de ano bissexto
        if mesfim[0:2] == '12':
            dtfim = datetime(dtfim.year+1, 1, 1) + timedelta(days=-1)
        else:
            dtfim = datetime(dtfim.year, dtfim.month + 1, 1) + timedelta(days=-1)

        # status financeiro = pode ser t=todos / a=aberto / p=pago
        # tipo financeiro = pode ser t=todos / r=receita / d=despesa
        if status == 'a':
            regstat = 0
        elif status == 'p':
            regstat = 1
        if benef == 'Todos':
            busca = ''
            if status == 't':
                if tipo == 'r':
                    financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                        .filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.valor > 0, FinancDB.benefic.like(cliforn)))
                elif tipo == 'd':
                    financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                        .filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.valor <= 0, FinancDB.benefic.like(cliforn)))
                else:
                    financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                        .filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.benefic.like(cliforn)))
            else:
                if tipo == 'r':
                    financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                        .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.benefic.like(cliforn), FinancDB.valor > 0))
                elif tipo == 'd':
                    financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                        .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.benefic.like(cliforn), FinancDB.valor <= 0))
                else:
                    financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                        .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.benefic.like(cliforn)))

        else:
            busca = 'W3K - SubCateg=Comissão W3K/Softwares(revenda)/Produtos(revenda)/Serviços(uso próprio)/Faturado W3K'
            busca = 'W3K - SubCateg=Comissão W3K/Softwares(revenda)/Produtos(revenda)/Serviços(revenda)/Faturado W3K'
            financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                .filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim,# \ FinancDB.benefic.like(cliforn), \
                         or_(FinancDB.subcategor.like('Comissão W3K%'), FinancDB.subcategor.like('Serviços(revenda)%'), \
                             FinancDB.subcategor.like('Softwares(revenda)%'),FinancDB.subcategor.like('Produtos(revenda)%'), \
                             FinancDB.subcategor.like('Faturado W3K%'))))

        financeiro = financeiro.order_by(FinancDB.dt_data.asc())

        for item in financeiro:
            total_itens += 1
            total_valor += item.FinancDB.valor
    else:
        abort(403)
    log_action('relatorio', 'relfrn_new', 'Status:' + status + ' Tipo:' + tipo + ' Mes:' + mesatl+ ' ate:' + mesfim+' CliFrn:'+clifrn+' Benef:'+benef)
    return render_template('relfrn_new.html', financeiro=financeiro, cliforn=cliforn, status=status, tipo=tipo, mesatl=mesatl, mesfim=mesfim, hoje=hoje,
                           total_itens=total_itens, total_valor=total_valor, busca=busca, currency=currency)

@app.route(f'{prefix}/relatfatur/<status>,<tipo>,<mesatl>')
@login_required
def relatfatur(status,tipo,mesatl):

    if current_user.access >= 4:
        currency = ConfigDB.query.filter_by(var='Currency').first().valor
        total_itens = 0
        total_valor = 0

        dtinic = datetime.strptime('01-' + mesatl, '%d-%m-%Y').date()
        # Soma 1 mês ao primeiro dia, e subtrai um dia para pegar o último dia do mês, funciona para Fev de ano bissexto
        if mesatl[0:2] == '12':
            dtfim = datetime(dtinic.year+1, 1, 1) + timedelta(days=-1)
        else:
            dtfim = datetime(dtinic.year, dtinic.month + 1, 1) + timedelta(days=-1)

        # status financeiro = pode ser t=todos / a=aberto / p=pago
        # tipo financeiro = pode ser t=todos / r=receita / d=despesa
        if status == 'a':
            regstat = 0
        else:
            regstat = 1

        if status == 't':
            if tipo == 'r':
                financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                    .filter(and_(FinancDB.active == 1, FinancDB.dtfatur >= dtinic, FinancDB.dtfatur <= dtfim, FinancDB.valor > 0))
            elif tipo == 'd':
                financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                    .filter(and_(FinancDB.active == 1, FinancDB.dtfatur >= dtinic, FinancDB.dtfatur <= dtfim, FinancDB.valor <= 0))
            else:
                financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                    .filter(and_(FinancDB.active == 1, FinancDB.dtfatur >= dtinic, FinancDB.dtfatur <= dtfim))
        else:
            if tipo == 'r':
                financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                    .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dtfatur >= dtinic, FinancDB.dtfatur <= dtfim, FinancDB.valor > 0))
            elif tipo == 'd':
                financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                    .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dtfatur >= dtinic, FinancDB.dtfatur <= dtfim, FinancDB.valor <= 0))
            else:
                financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                    .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dtfatur >= dtinic, FinancDB.dtfatur <= dtfim))

        financeiro = financeiro.order_by(FinancDB.dtfatur.asc())
        for item in financeiro:
            total_itens += 1
            total_valor += item.FinancDB.valor
    else:
        abort(403)
    log_action('relatorio', 'relatfatur', 'Status:' + status + ' Tipo:' + tipo + ' Mes:' + mesatl)
    return render_template('relatfatur.html', financeiro=financeiro, status=status, tipo=tipo, mesatl=mesatl, hoje=hoje,
                           total_itens=total_itens, total_valor=total_valor, currency=currency)

def somavalor(dados):
    valortotal = 0
    for item in dados:
        valortotal += item.valor
    return valortotal

@app.route(f'{prefix}/relatresult/<mesatl>,<mesfim>', methods=['GET', 'POST'])
@login_required
def relatresult(mesatl,mesfim):

    if current_user.access >= 4:
        currency = ConfigDB.query.filter_by(var='Currency').first().valor
        form_result = FormFinancResult()
        meses = []
        for y in range(2017, (hoje.year + 3)):
            for n in range(12):
                ns = '{:02}'.format(n + 1)
                ys = '{:04}'.format(y)
                meses = meses + [ns + '-' + ys]

        form_result.select_mes.choices = meses
        form_result.select_mes.data = mesatl
        form_result.select_mesfim.choices = meses
        form_result.select_mesfim.data = mesfim

        dtinic = datetime.strptime('01-' + mesatl, '%d-%m-%Y').date()
        dtfim = datetime.strptime('01-' + mesfim, '%d-%m-%Y').date()
        if dtfim.month == 12:
            dtfim = datetime(dtfim.year + 1, 1, 1) + timedelta(days=-1)
        else:
            dtfim = datetime(dtfim.year, dtfim.month + 1, 1) + timedelta(days=-1)

        financresreal = 0
        financreceitr = 0
        financdespsr = 0
        financlucrosr = 0
        financimposr = 0
        ebitdar = 0
        despaielr = 0
        financresprev = 0
        financreceitp = 0
        financdespsp = 0
        financlucrosp = 0
        financimposp = 0
        ebitdap = 0
        despaielp = 0

        if form_result.validate_on_submit() or 'botao_submit_financresult' in request.form:
            mesatl = form_result.select_mes.raw_data[0]
            mesfim = form_result.select_mesfim.raw_data[0]
            dtinic = datetime.strptime('01-' + mesatl, '%d-%m-%Y').date()
            dtfim = datetime.strptime('01-' + mesfim, '%d-%m-%Y').date()
            if dtfim.month == 12:
                dtfim = datetime(dtfim.year + 1, 1, 1) + timedelta(days=-1)
            else:
                dtfim = datetime(dtfim.year, dtfim.month + 1, 1) + timedelta(days=-1)
            session['MESATL'] = mesatl
            session['MESFIM'] = mesfim
            # Resultado Real - Soma todos as receitas e despesas que já foram quitadas
            financresreal = somavalor(database.session.query(FinancDB).filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic,FinancDB.dt_data <= dtfim, FinancDB.pago == 1)))
            # Resultado Previsto - Soma todos as receitas e despesas, fechadas e abertas
            financresprev = somavalor(database.session.query(FinancDB).filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim)))
            # Receitas Reais - Tudo positivo e pago
            financreceitr = somavalor(database.session.query(FinancDB).filter(and_(FinancDB.active == 1, FinancDB.valor > 0, FinancDB.pago == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim)))
            # Receitas Previstas - Tudo positivo
            financreceitp = somavalor(database.session.query(FinancDB).filter(and_(FinancDB.active == 1, FinancDB.valor > 0, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim)))
            # Despesas Reais - Tudo negativo e pago
            financdespsr = somavalor(database.session.query(FinancDB).filter(and_(FinancDB.active == 1, FinancDB.valor < 0, FinancDB.pago == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim)))
            # Despesas Previstas - Tudo negativo
            financdespsp = somavalor(database.session.query(FinancDB).filter(and_(FinancDB.active == 1, FinancDB.valor < 0, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim)))
            # Lucros distribuídos (Despesa Real)
            financlucrosr = somavalor(database.session.query(FinancDB) \
                .filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.pago == 1, FinancDB.subcategor.like('Distribuição de Lucros%'))))
            # Lucros distribuídos (Despesa Prevista)
            financlucrosp = somavalor(database.session.query(FinancDB) \
                .filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.subcategor.like('Distribuição de Lucros%'))))
            # Impostos (Despesa Real)
            financimposr = somavalor(database.session.query(FinancDB) \
                .filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.pago == 1, FinancDB.categoria.like('Imposto%'))))
            # Impostos (Despesa Prevista)
            financimposp = somavalor(database.session.query(FinancDB) \
                .filter(and_(FinancDB.active == 1, FinancDB.dt_data >= dtinic, FinancDB.dt_data <= dtfim, FinancDB.categoria.like('Imposto%'))))
            # Despesas (antes de Impostos e Lucros)
            despaielr = financdespsr - financlucrosr - financimposr
            despaielp = financdespsp - financlucrosp - financimposp
            # EBITDA
            ebitdar = financreceitr+(financdespsr-financlucrosr-financimposr)
            ebitdap = financreceitp+(financdespsp-financlucrosp-financimposp)
            log_action('relatorio', 'relatresult', 'MesInicio:' + mesatl + ' MesFinal:' + mesfim)
            # logging.info(f'Relat result EBIT(r){str(ebitdar)} com EBIT(p){str(ebitdap)} em {mesfim}!')
    else:
        abort(403)

    return render_template('relatresult.html', form_result=form_result, mesatl=mesatl, mesfim=mesfim, hoje=hoje, financresreal=financresreal, ebitdar=ebitdar, despaielr=despaielr,
                           financreceitr=financreceitr, financdespsr=financdespsr, financlucrosr=financlucrosr, financimposr=financimposr, ebitdap=ebitdap, despaielp=despaielp,
                           financresprev=financresprev, financreceitp=financreceitp, financdespsp=financdespsp, financlucrosp=financlucrosp, financimposp=financimposp, currency=currency)

@app.route(f'{prefix}/relatprop', methods=['GET', 'POST'])
@login_required
def relatprop():
    currency = ConfigDB.query.filter_by(var='Currency').first().valor
    hoje60 = date.today() + timedelta(days=60)
    vendrnam = ''
    forcst = 60
    stat = "Ativas"
    propostas = []
    prop_soft = 0
    prop_serv = 0
    prop_bklg = 0
    form_relatprop = FormRelatProp()
    if current_user.access >= 2:
        form_relatprop.select_status.choices = [("Ativas", "Ativas"),("Todas", "Todas"),("Inativas", "Inativas")] + [(s.opt, s.msg) for s in ListaOpcoesDB.query.filter_by(lst='StatusPrp')]
        form_relatprop.select_status.data = stat
        # TODO PEGAR SOMENTE USUARIOS ATIVOS
        #form_relatprop.select_vendor.choices = [("0", "Todos")] + [(s.id, s.username) for s in
        #                                                      usuario.query.order_by(usuario.username.asc())]
        form_relatprop.select_vendor.choices = [("0", "Todos")] + [(s.id, s.username) for s in
            usuario.query.filter(or_(usuario.role.contains('VD'),usuario.role.contains('IS'),usuario.role.contains('CM')),usuario.access > 0)
            .order_by(usuario.username.asc())]
        form_relatprop.select_vendor.data = "0"
        form_relatprop.forecast.data = forcst
        form_relatprop.dataini.data = date.today()
        form_relatprop.datafim.data = hoje60

        if form_relatprop.validate_on_submit() or 'botao_submit_relatprop' in request.form:
            stat = form_relatprop.select_status.raw_data[0]
            vendr = int(form_relatprop.select_vendor.raw_data[0])
            forcst = int(request.form.get('forecast'))
            btext = (request.form.get('busca_texto'))
            if stat == 'Ativas':
                propostas = database.session.query(PropostasDB).filter(and_(or_(PropostasDB.status.contains('Aberta'),
                                     PropostasDB.status.contains('Negociando'), PropostasDB.status.contains('Aguardando'))),
                                     PropostasDB.forecast >= forcst, PropostasDB.dtprovavel >= request.form.get('dataini'),
                                     PropostasDB.dtprovavel <= request.form.get('datafim'))
            elif stat == 'Inativas':
                propostas = database.session.query(PropostasDB).filter(and_(or_(PropostasDB.status.contains('Vencida'),
                                     PropostasDB.status.contains('Recusada'), PropostasDB.status.contains('Indefinida'),
                                                                                PropostasDB.status.contains('Perdida'))),
                                     PropostasDB.forecast >= forcst, PropostasDB.dtprovavel >= request.form.get('dataini'),
                                     PropostasDB.dtprovavel <= request.form.get('datafim'))
            elif stat == 'Todas':
                propostas = database.session.query(PropostasDB).filter(and_(PropostasDB.forecast >= forcst,
                                     PropostasDB.dtprovavel >= request.form.get('dataini'),
                                     PropostasDB.dtprovavel <= request.form.get('datafim')))
            else:
                propostas = database.session.query(PropostasDB).filter(and_(PropostasDB.status.contains(stat),
                                     PropostasDB.forecast >= forcst, PropostasDB.dtprovavel >= request.form.get('dataini'),
                                     PropostasDB.dtprovavel <= request.form.get('datafim')))

            if request.form.get('renovac') == 'y':
                renov = 1
                propostas = propostas.filter(PropostasDB.renovac == renov)
            else:
                renov = 0

            if vendr > 0:
                propostas = propostas.filter(PropostasDB.idvendor == vendr)
                vendrnam=usuario.query.get(vendr).username
            else:
                vendrnam = 'Todos'

            if btext != '':
                propostas = propostas.filter(or_(PropostasDB.nomecliente.contains(btext),
                                                 PropostasDB.descricao.contains(btext),
                                                 PropostasDB.notas.contains(btext)))

            for prop in propostas:
                prop_soft += prop.vlrsoft
                prop_serv += prop.vlrserv
                prop_bklg += prop.horasprev

                log_action('relatorio', 'relatprop', 'St:' + stat + ' Vd:' + str(vendr) + ' Fcst:' + str(forcst))
            # return render_template('relatprop.html', form_relatprop=form_relatprop, propostas=propostas, vendrnam=vendrnam)
    else:
        abort(403)

    return render_template('relatprop.html', form_relatprop=form_relatprop, propostas=propostas, vendrnam=vendrnam, stat=stat, forcst=forcst, currency=currency, hoje=hoje, prop_soft=prop_soft, prop_serv=prop_serv, prop_bklg=prop_bklg)

@app.route(f'{prefix}/relattag/<tipo>,<tag>,<mark>', methods=['GET', 'POST'])
@login_required
def relattag(tipo, tag, mark):
    if current_user.access >= 2:
        resultado = []
        searchtag = ''
        total_itens = 0
        if current_user.access >= 2:
            form_relattag = FormRelatScope()
            form_relattag.select_tipo.choices = [('p', 'PIPELINE'), ('m', 'MAILING')]
            form_relattag.select_tipo.data = tipo
            if mark == '1':
                form_relattag.select_bool.data = 1
            else:
                form_relattag.select_bool.data = 0
            form_relattag.select_tag.data = tag
            if form_relattag.validate_on_submit() or 'botao_submit_relattag' in request.form:
                tipo = form_relattag.select_tipo.raw_data[0]
                if request.form.get('select_bool'):
                    mark = 1
                else:
                    mark = 0
                if request.form.get('select_tag'):
                    tag = request.form.get('select_tag')
                if tag == '#':
                    searchtag = ''
                else:
                    searchtag = tag

                if tipo == 'p':
                    resultado = database.session.query(PipelineDB, ClientesDB, usuario).select_from(PipelineDB).join(
                        ClientesDB).join(usuario, usuario.id == PipelineDB.vendedor).filter(PipelineDB.active == 1)
                    if mark == 1:
                        resultado = resultado.filter(and_(PipelineDB.prioridade == mark, (or_(PipelineDB.oportunidade.contains(searchtag), PipelineDB.historico.contains(searchtag))))).order_by(ClientesDB.nomecliente.asc())
                    else:
                        resultado = resultado.filter(or_(PipelineDB.oportunidade.contains(searchtag), PipelineDB.historico.contains(searchtag))).order_by(ClientesDB.nomecliente.asc())
                    log_action('relatorio', 'relattag', 'Mark:' + str(mark) + ' Tipo:PIPELINE Tag:' + tag)
                elif tipo == 'm':
                    resultado = database.session.query(ContatoDB, ClientesDB, usuario).select_from(ContatoDB).join(
                        ClientesDB, ContatoDB.idcliente == ClientesDB.idcliente).join(usuario, usuario.id == ContatoDB.idusuario).filter(ContatoDB.active == 1)
                    if mark == 1:
                        resultado = resultado.filter(and_(ContatoDB.observacao.contains(searchtag),ContatoDB.mailing == 1)).order_by(ContatoDB.nomecontato.asc())
                    else:
                        resultado = resultado.filter(or_(ContatoDB.observacao.contains(searchtag), ContatoDB.nomecontato.contains(searchtag),
                                ContatoDB.email.contains(searchtag), ClientesDB.nomecliente.contains(searchtag))).order_by(ContatoDB.nomecontato.asc())
                        # resultado = resultado.filter(and_(ContatoDB.observacao.contains(searchtag))).order_by(ContatoDB.nomecontato.asc())
                    log_action('relatorio', 'relattag', 'Mark:' + str(mark) + ' Tipo:MAILING Tag:' + tag)
                return render_template('relattag.html', form_relattag=form_relattag, resultado=resultado, tipo=tipo,
                                       tag=tag, mark=mark, hoje=hoje, mesatl=session['MESATL'])
    else:
        abort(403)

    return render_template('relattag.html', form_relattag=form_relattag, resultado=resultado, tipo=tipo, tag=tag, mark=mark, hoje=hoje, mesatl=session['MESATL'])


@app.route(f'{prefix}/relatrealiz/<status>,<tipo>,<mesatl>', methods=['GET', 'POST'])
@login_required
def relatrealiz(status,tipo,mesatl):

    if current_user.access >= 4:
        currency = ConfigDB.query.filter_by(var='Currency').first().valor
        daysahead = int(ConfigDB.query.filter_by(var='DiasFluxoCaixa').first().valor)
        form_realiz = FormFinancRealiz()
        meses = []
        for y in range(2017, (hoje.year + 3)):
            for n in range(12):
                ns = '{:02}'.format(n + 1)
                ys = '{:04}'.format(y)
                meses = meses + [ns + '-' + ys]

        form_realiz.select_mes.choices = meses
        form_realiz.select_mes.data = mesatl
        form_realiz.select_tipo.choices = [('t', 'Todos'), ('r', 'RECEITA'), ('d', 'DESPESA')]
        form_realiz.select_tipo.data = 't'
        buscar = ''

        if form_realiz.validate_on_submit() or 'botao_submit_financrealiz' in request.form:
            mesatl = form_realiz.select_mes.raw_data[0]
            tipo = form_realiz.select_tipo.raw_data[0]
            if request.form.get('busca'):
                    buscar = request.form.get('busca')
            session['MESATL'] = mesatl

        dtinic = datetime.strptime('01-' + mesatl, '%d-%m-%Y').date()
        dtfim = datetime.strptime('01-' + mesatl, '%d-%m-%Y').date()
        if dtfim.month == 12:
            dtfim = datetime(dtfim.year + 1, 1, 1) + timedelta(days=-1)
        else:
            dtfim = datetime(dtfim.year, dtfim.month + 1, 1) + timedelta(days=-1)

        # status financeiro p=pago ou a=aberto
        # tipo financeiro = pode ser t=todos / r=receita / d=despesa
        if status == 'a':
            regstat = 0
        else:
            regstat = 1

        saldo = 0
        if status == 'p':
            if tipo == 'r':
                financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                    .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dtpagto >= dtinic, FinancDB.dtpagto <= dtfim, FinancDB.valor > 0, FinancDB.observacao.contains(buscar)))
            elif tipo == 'd':
                financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                    .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dtpagto >= dtinic, FinancDB.dtpagto <= dtfim, FinancDB.valor <= 0, FinancDB.observacao.contains(buscar)))
            else:
                financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                    .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dtpagto >= dtinic, FinancDB.dtpagto <= dtfim, FinancDB.observacao.contains(buscar)))
            financeiro = financeiro.order_by(FinancDB.dtpagto.asc())
        else:
            saldo = SaldoDB.query.order_by(SaldoDB.idsaldo.desc()).first().saldo
            financeiro = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                    .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.observacao.contains(buscar)))
            financeiro = financeiro.order_by(FinancDB.dt_data.asc())
            financgraph = database.session.query(FinancDB, usuario).join(usuario, FinancDB.idusuario == usuario.id) \
                    .filter(and_(FinancDB.pago == regstat, FinancDB.active == 1, FinancDB.dt_data <= date.today() + timedelta(days=daysahead), FinancDB.observacao.contains(buscar)))
            financgraph = financgraph.order_by(FinancDB.dt_data.asc())

        # if status == 'p':
        #     for item in financeiro:
        #         total_itens += 1
        #         total_valor += item.FinancDB.valor
        # else:
        #     for item in financeiro:
        #         total_itens += 1
        #         total_valor += item.FinancDB.valor
        #         if lst_saldo == 0:
        #             lst_saldo = ([(item.FinancDB.idfinanc, item.FinancDB.valor, total_valor)])
        #         else:
        #             lst_saldo.append([item.FinancDB.idfinanc, item.FinancDB.valor, total_valor])

        total_itens = 0
        lst_saldo = 0
        total_valor = saldo
        total_graph = saldo
        labelvalues = []
        saldovalues = []
        valorvalues = []
        if status == 'p':
            for item in financeiro:
                total_itens += 1
                total_valor += item.FinancDB.valor
        else:
            for item in financeiro:
                total_itens += 1
                total_valor += item.FinancDB.valor
                if lst_saldo == 0:
                    lst_saldo = ([(item.FinancDB.idfinanc, item.FinancDB.valor, total_valor)])
                else:
                    lst_saldo.append([item.FinancDB.idfinanc, item.FinancDB.valor, total_valor])

            for item in financgraph:
                total_graph += item.FinancDB.valor
                labelvalues.append('{:02d}/{:02d}/{:02d}'.format(item.FinancDB.dt_data.day, item.FinancDB.dt_data.month, item.FinancDB.dt_data.year))
                saldovalues.append(float(total_graph))
                valorvalues.append(float(item.FinancDB.valor))
    else:
        abort(403)
    log_action('relatorio','relatrealiz','Status:'+status+' Tipo:'+tipo+' Mes:'+mesatl)
    return render_template('relatrealiz.html', form_realiz=form_realiz, financeiro=financeiro, status=status, tipo=tipo, mesatl=mesatl, hoje=hoje,
                           total_itens=total_itens, total_valor=total_valor, lst_saldo=lst_saldo, saldo=saldo, currency=currency, labelvalues=labelvalues, saldovalues=saldovalues, valorvalues=valorvalues)

@app.route(f'{prefix}/relatrecur')
@login_required
def relatrecur():
    if current_user.access < 4:
        return "Acesso Negado", 403

    currency_setting = ConfigDB.query.filter_by(var='Currency').first()
    currency = currency_setting.valor if currency_setting else ''

    query_results = database.session.query(ContratosDB, PropostasDB) \
        .join(PropostasDB, ContratosDB.idproposta == PropostasDB.idproposta) \
        .filter(ContratosDB.status == 'Ativo') \
        .order_by(ContratosDB.nomecliente, ContratosDB.unidade) \
        .all()

    relatorio_data = []
    mrr_total = Decimal(0)
    arr_total = Decimal(0)
    min_date = None
    max_date = None

    # Variáveis para os totais da tabela
    total_vlrsoft = Decimal(0)
    total_vlrserv = Decimal(0)
    total_geral = Decimal(0)

    for contrato, proposta in query_results:
        vlrsoft = proposta.vlrsoft or Decimal(0)
        vlrserv = proposta.vlrserv or Decimal(0)

        # Cálculos para MRR/ARR
        if contrato.fatfrequencia == 'Mensal':
            mrr_total += vlrsoft
        # elif contrato.fatfrequencia in ['Anual', 'Unico']:
        else:
            arr_total += vlrsoft

        # Cálculos para os totais da tabela
        total_vlrsoft += vlrsoft
        total_vlrserv += vlrserv
        total_geral += vlrsoft + vlrserv

        relatorio_data.append({
            'cliente': contrato.nomecliente, 'unidade': contrato.unidade,
            'produto': contrato.produto, 'faturamento': contrato.faturamento,
            'frequencia': contrato.fatfrequencia, 'infratype': contrato.infratype,
            'users_regulares': contrato.usersregulares, 'gb_storage': contrato.gbstorage,
            'powerbi': contrato.powerbi, 'vlrsoft': vlrsoft, 'vlrserv': vlrserv,
            'total': vlrsoft + vlrserv, 'validade': contrato.validadecontrato
        })

        if contrato.dtpedido and (min_date is None or contrato.dtpedido < min_date):
            min_date = contrato.dtpedido
        if contrato.validadecontrato and (max_date is None or contrato.validadecontrato > max_date):
            max_date = contrato.validadecontrato

    # --- Lógica de Cálculo para o Gráfico ---
    chart_labels = []
    chart_values = []
    chart_customers = []

    if min_date and max_date:
        monthly_data = {}
        current_month = min_date.replace(day=1)
        while current_month <= max_date:
            month_key = current_month.strftime('%Y-%m-01')
            monthly_data[month_key] = {'total': Decimal(0), 'customers': set()}
            chart_labels.append(current_month.strftime('%b/%y'))
            current_month += relativedelta(months=1)

        for contrato, proposta in query_results:
            if not contrato.dtpedido or not contrato.validadecontrato:
                continue

            vlrsoft = proposta.vlrsoft or Decimal(0)
            vlrserv = proposta.vlrserv or Decimal(0)
            customer_firstname = contrato.nomecliente.split(' ')[0]

            start_month_date = contrato.dtpedido.replace(day=1)


            if contrato.fatfrequencia == 'Mensal':
                periodo_contrato = min(contrato.duracaocontrato or 12, 12)
                periodo = 1
                current_billing_month = start_month_date
                is_first_month = True
                while current_billing_month <= contrato.validadecontrato:
                    month_key = current_billing_month.strftime('%Y-%m-01')
                    if month_key in monthly_data:
                        if is_first_month:
                            monthly_data[month_key]['total'] += (vlrsoft/periodo_contrato) # + vlrserv
                            is_first_month = False
                        else:
                            monthly_data[month_key]['total'] += (vlrsoft/periodo_contrato)
                        monthly_data[month_key]['customers'].add(customer_firstname)
                    current_billing_month += relativedelta(months=periodo)
            else:
                if contrato.fatfrequencia == 'Semestral':
                    periodo_contrato = 6
                elif contrato.fatfrequencia == 'Trimestral':
                    periodo_contrato = 3
                elif contrato.fatfrequencia == 'Bimestral':
                    periodo_contrato = 2
                else:
                #elif contrato.fatfrequencia in ['Anual', 'Unico']:
                    periodo_contrato = 1
                month_key = start_month_date.strftime('%Y-%m-01')
                if month_key in monthly_data:
                    monthly_data[month_key]['total'] += (vlrsoft/periodo_contrato) # + vlrserv
                    monthly_data[month_key]['customers'].add(customer_firstname)


        for key in sorted(monthly_data.keys()):
            chart_values.append(float(monthly_data[key]['total']))
            chart_customers.append(list(monthly_data[key]['customers']))

    log_action('relatorio', 'relatrecur', 'MRR & ARR')

    return render_template('relatrecur.html',
        hoje=hoje, currency=currency, relatorio_data=relatorio_data, total_itens=len(relatorio_data), mrr_total=mrr_total, arr_total=arr_total,
        chart_labels=json.dumps(chart_labels), chart_values=json.dumps(chart_values), chart_customers=json.dumps(chart_customers),
        total_vlrsoft=total_vlrsoft, total_vlrserv=total_vlrserv, total_geral=total_geral)


def process_txt_file(file):
    lines = []
    for line in file:
        lines.append(line.decode('utf-8').strip())  # Decodifica a linha e remove espaços em branco
    return lines

def process_xlsx_file(file):
    lines = []
    # df = pd.read_excel(file, engine="openpyxl")
    df = pd.read_excel(file)
    for parametro in df['parametros']:
        lines.append(parametro.strip())
    # lines = df.values.tolist()
    return lines

@app.route(f'{prefix}/apicall/<credenc_id>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def apicall(credenc_id):
    if current_user.access >= 2:
        credencial = CredencialDB.query.get(credenc_id)

        form_apicall = FormApiCall()
        form_apicall.method.choices = [("GET"), ("PUT"), ("POST"), ("DELETE")]
        form_apicall.scope.choices = [("items"), ("users"), ("workflows")]
        searchparam = ''
        response_data = ''
        response_code = 0

        if form_apicall.validate_on_submit() and 'botao_submit_apicall' in request.form:
            website = credencial.urlweb
            if website[-1] != '/':
                website = website + '/'
            usr = credencial.logindocc
            pwd = credencial.passwddocc
            usrsrv = credencial.loginserv
            pwdsrv = credencial.passwdserv

            metodo = form_apicall.method.raw_data[0]
            escopo = form_apicall.scope.raw_data[0]
            usrmail = form_apicall.useremail.data

            # Processar o arquivo enviado
            file = request.files['file']
            filename, fileext = os.path.splitext(file.filename)
            if fileext == '.txt':
                lines = process_txt_file(file)
            elif fileext == '.xlsx':
                lines = process_xlsx_file(file)
            else:
                flash(f'Formato de arquivo não suportado.', 'alert-danger')
                return redirect(url_for('credenciais', status='ativo'))

            response_code = 0
            request_sentence = website+"api/v2/"+escopo+"?"  # Essa sentença serve pra Items e Workflows
            if escopo == "users" and len(usrmail) > 3:
                response_code = 200
                request_sentence = website+"api/v2/users/"+usrmail+"/positions/"
                if metodo == "POST":
                    eval_start = 'requests.post("'+request_sentence+'", json='
                    eval_end = ', auth=(usrsrv, pwdsrv))'
                elif metodo == "DELETE":
                    eval_start = 'requests.delete("'+request_sentence+'", json='
                    eval_end = ', auth=(usrsrv, pwdsrv))'
                else:
                    response_code = 0
            elif escopo == "workflows":
                response_code = 200
                if metodo == "POST":
                    eval_start = 'requests.post("'+request_sentence+'", params="'
                    eval_end = '", auth=(usr, pwd))'
                else:
                    response_code = 0
            elif escopo == "items":
                response_code = 200
                if metodo == "GET":
                    eval_start = 'requests.get("'+request_sentence+'", params="'
                    eval_end = '", auth=(usr, pwd))'
                elif metodo == "PUT":
                    eval_start = 'requests.put("'+request_sentence+'", params="'
                    eval_end = '", auth=(usr, pwd))'
                else:
                    response_code = 0
            else:
                flash(f'Dados insuficientes! Preencha todos os valores.', 'alert-danger')

            count = 0
            if response_code == 0:
                line = ''
                flash(f'Combinação de valores inválida.', 'alert-danger')
            else:
                for line in lines:
                    if len(line) > 1 and (response_code == 200 or response_code == 204):
                        count += 1
                        if escopo == "users":
                            line = line.replace("'", chr(34))  # para trocar as aspas simples por aspas duplas
                        line = eval_start + line + eval_end
                        response = eval(line)
                        response_code = response.status_code

            if response_code == 0:
                searchparam = str(count) + " linha(s). Status Code:<> " + website + " " + metodo + " " + escopo + " " + line
            else:
                searchparam = str(count) + " linha(s). Status Code:<" + str(response.status_code) + "> " + website + " " + metodo + " " + escopo + " " + line
                if response.status_code == 200 or response.status_code == 204:
                    # Aqui definimos a resposta para ser passada ao HTML
                    response_data = response.text
                else:
                    flash(f'Erro na requisição. Código de status: <{response.status_code}>', 'alert-danger')

            log_action('apicall', 'api', 'Call:' + credencial.nomecliente + ' succesful. ' + str(count) + ' linhas.')
    else:
        abort(403)
    return render_template('apicall.html', form_apicall=form_apicall, response=response_data, response_code=response_code, searchparam=searchparam)

def normalize_phone(phone):
    numeros = re.sub(r'\D', '', phone).lstrip('0')  # Remove tudo que não for número e zeros à esquerda
    if not numeros.startswith('55'):
        numeros = '55' + numeros
    return numeros

@app.route(f'{prefix}/webhook/received', methods=['POST'])
def webhook_received():
    # Comentar quando terminar o debug
    # logging.info("🔔 Webhook Received (Supte) foi chamado")

    if not request.is_json:
        logging.warning("❗ Requisição não é JSON válida.")
        return {"error": "Requisição precisa ser JSON"}, 415

    try:
        dados_json = request.get_json()
        logging.info(f"📦 Dados recebidos do Z-API: {json.dumps(dados_json, indent=2)}")
        processar_received(dados_json,'Suporte11978109256')

    except Exception as e:
        logging.error("❌ Erro no webhook:")
        logging.error(traceback.format_exc())
        return {"error": "Erro interno"}, 500

@app.route(f'{prefix}/webhook/received2', methods=['POST'])
def webhook_received2():
    # Comentar quando terminar o debug
    # logging.info("🔔 Webhook Received2 (Sales) foi chamado")

    if not request.is_json:
        logging.warning("❗ Requisição não é JSON válida.")
        return {"error": "Requisição precisa ser JSON"}, 415

    try:
        dados_json = request.get_json()
        logging.info(f"📦 Dados recebidos do Z-API: {json.dumps(dados_json, indent=2)}")
        processar_received(dados_json,'Sales11970847098')

    except Exception as e:
        logging.error("❌ Erro no webhook:")
        logging.error(traceback.format_exc())
        return {"error": "Erro interno"}, 500


def processar_received(data, instzapi):
    telefone = data.get('phone')
    phone = normalize_phone(telefone)
    msg_type = data.get('type')
    msg_id = data.get('messageId')
    conteudo = ""

    # Comentar quando terminar o debug
    # logging.info(f"📩 Tipo de mensagem recebida: {msg_type}")
    # logging.debug(f"📦 Payload completo: {json.dumps(data, indent=2)}")

    if msg_type == 'ReceivedCallback':
        # Verifica se é reação
        if 'reaction' in data:
            emoji = data['reaction'].get('value', '')
            conteudo = f"[Reação: {emoji}]"
        # Verifica se é mensagem de texto
        elif 'text' in data and data.get('text', {}).get('message'):
            conteudo = data['text']['message']
        # Verifica se é imagem
        elif 'image' in data:
            media_url = data['image'].get('imageUrl')
            filename = data['image'].get('fileName','imagem' + '' + datetime.today().strftime("%Y-%m-%d%H:%M") + '.jpg')
            filename = secure_filename(filename)
            conteudo = processar_midia('image', media_url, filename)
        # Verifica se é vídeo
        elif 'video' in data:
            media_url = data['video'].get('videoUrl')
            filename = data['video'].get('fileName', 'video' + '' + datetime.today().strftime("%Y-%m-%d%H:%M") + '.mp4')
            filename = secure_filename(filename)
            conteudo = processar_midia('video', media_url, filename)
        # Verifica se é áudio
        elif 'audio' in data:
            media_url = data['audio'].get('audioUrl')
            filename = data['audio'].get('fileName', 'audio' + '' + datetime.today().strftime("%Y-%m-%d%H:%M") + '.mp3')
            filename = secure_filename(filename)
            conteudo = processar_midia('audio', media_url, filename)
        # Verifica se é documento
        elif 'document' in data:
            logging.info(f"📄 Dados do documento recebido: {data['document']}")
            media_url = data['document'].get('documentUrl')
            filename = data['document'].get('fileName', 'documento' + '' + datetime.today().strftime("%Y-%m-%d%H:%M"))
            filename = secure_filename(filename)
            conteudo = processar_midia('document', media_url, filename)
        # Verifica se é uma call
        elif 'call' in data:
            call_info = data.get('call', {})
            if call_info.get('status') == 'finished':
                duracao = call_info.get('duration', 0)
                conteudo = f"[Chamada de voz/vídeo atendida - Duração: {duracao} segundos]"
            else:
                conteudo = "[Chamada de voz/vídeo]"
        # Verifica se é localização
        elif 'location' in data:
            location = data.get('location', {})
            latitude = location.get('latitude', '')
            longitude = location.get('longitude', '')
            conteudo = f"[Localização compartilhada: {latitude},{longitude}]"
        # Verifica se é contato
        elif 'contact' in data:
            contact = data.get('contact', {})
            display_name = contact.get('displayName', '')
            conteudo = f"[Contato compartilhado: {display_name}]"
        # Verifica se é sticker
        elif 'sticker' in data:
            conteudo = "[Sticker]"
        # Verifica se é resposta de botão
        elif 'buttonsResponseMessage' in data:
            button_response = data.get('buttonsResponseMessage', {})
            selected_button = button_response.get('selectedButtonId', '')
            conteudo = f"[Resposta de botão: {selected_button}]"
        # Verifica se é resposta de lista
        elif 'listResponseMessage' in data:
            list_response = data.get('listResponseMessage', {})
            selected_item = list_response.get('title', '')
            conteudo = f"[Resposta de lista: {selected_item}]"
            # Verifica se é notificação
        elif 'notification' in data:
            notification_type = data.get('notification', '')
            conteudo = f"[Notificação: {notification_type}]"
        else:
            logging.warning(f"⚠ Tipo de mensagem não identificado. Payload: {json.dumps(data, indent=2)}")
            conteudo = f"[Tipo de mensagem não identificado] {msg_type}"

    if phone and conteudo:
        #telefone_formatado = phone.split('-')[0] #retira o que tem depois do hífen, tipo numa msg de grupo
        if len(phone) <= 13:
            msg = MsgDB.query.filter_by(telefone=phone).first()
            if not msg:
                resposta = whatsapp_resp_automatica(phone, instzapi)
                if resposta != 200:
                    logging.warning(f"⚠ Mensagem automática com erro no envio: {resposta}")

            nova_msg = MsgDB(
                instancia=instzapi,
                telefone=phone,
                mensagem_id=msg_id,
                mensagem=conteudo,
                tipo='recebida',
                dtcriac=date.today()
            )
            database.session.add(nova_msg)
            database.session.commit()
        else:
            logging.warning(f"⚠ Não parece ser um telefone válido: {phone} - {conteudo}")

    return {"status": "ok"}, 200


def processar_midia(tipo, media_url, filename):
    if not media_url:
        return f"[{tipo.upper()} sem URL]"

    local_path = os.path.join(WA_FOLDER, DN_FOLDER, filename)

    # Garante que a base URL tenha a barra final
    base_url = DXSURL if DXSURL.endswith('/') else DXSURL + '/'
    # Monta a URL completa
    doxsys_path = urljoin(base_url, f"{WA_FOLDER}/{DN_FOLDER}/{filename}")

    try:
        media_response = requests.get(media_url)
        if media_response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(media_response.content)
            return f"[{tipo.upper()} recebido] <a href='{doxsys_path}' target='_blank'>{filename}</a>"
        else:
            return f"[Erro ao baixar {tipo}: código {media_response.status_code}]"
    except Exception as e:
        return f"[Erro ao baixar {tipo}: {e}]"


@app.route(f'{prefix}/webhook/status', methods=['POST'])
def webhook_status():
    # EXEMPLO DE PAYLOAD
    # 2025-06-02 14:01:09,617 - INFO - 📦 Dados recebidos: {
    #     "instanceId": "3E16EBDA683A1067961A16374B74BED7",
    #     "status": "READ",
    #     "ids": [
    #         "3EB03EFB102060536FE698"
    #     ],
    #     "momment": 1748883674000,
    #     "phoneDevice": 33,
    #     "phone": "5511999631100",
    #     "type": "MessageStatusCallback",
    #     "isGroup": false
    # }
    if not request.is_json:
        logging.warning("❗ Requisição não é JSON válida.")
        return {"error": "Requisição precisa ser JSON"}, 415

    try:
        dados = request.get_json()

        # Comentar quando terminar o debug
        # logging.info(f"📦 Dados recebidos: {json.dumps(dados, indent=2)}")
        # if dados.get('type') == 'MessageStatusCallback':
        #     logging.info(f"Status recebido: {dados.get('status')}")
        #     logging.debug(f"Payload completo do status: {json.dumps(dados, indent=2)}")
        # Comentar o debug até aqui

        # Z-API pode enviar o ID em diferentes campos
        # message_id = dados.get("messageId") or dados.get("zaapId") or dados.get("id")
        # message_id = dados.get("ids", [])[0] if dados.get("ids") else None
        ids_list = dados.get("ids", [])
        status_msg = dados.get("status")

        # Validação dos campos obrigatórios
        if not ids_list:
            logging.error("❗ ID da mensagem não encontrado no payload")
            return {"error": "ID da mensagem não encontrado"}, 400

        if not status_msg:
            logging.error("❗ Status não encontrado no payload")
            return {"error": "Status não encontrado"}, 400

        # Validação do status recebido
        # valid_statuses = ['SENT', 'RECEIVED', 'READ', 'WAITING', 'ERROR']
        valid_statuses = [
            'PENDING',  # Mensagem na fila para ser enviada
            'SENT',  # Mensagem enviada pelo WhatsApp
            'RECEIVED',  # Mensagem recebida pelo destinatário
            'READ',  # Mensagem lida pelo destinatário
            'PLAYED',  # Áudio/vídeo foi reproduzido (específico para mídia)
            'ERROR',  # Erro no envio
            'DELETED'  # Mensagem deletada
        ]

        if status_msg not in valid_statuses:
            logging.warning(f"⚠ Status desconhecido recebido: {status_msg}")

        # Localiza e atualiza o status da mensagem
        for message_id in ids_list:
            msg = MsgDB.query.filter_by(mensagem_id=message_id).first()
            if msg:
                msg.status = status_msg
                msg.data = datetime.now(pytz.timezone("America/Sao_Paulo"))
                database.session.commit()
                logging.info(f"✅ Status atualizado para {status_msg} na mensagem {message_id}")
                return {"message": f"Status atualizado para {status_msg}"}, 200
            else:
                logging.warning(f"⚠ Mensagem não encontrada: {message_id}")
                return {"message": "Mensagem não encontrada"}, 404

    # except SQLAlchemyError as e:
    #     logging.error(f"❌ Erro de banco de dados: {str(e)}")
    #     database.session.rollback()
    #     return {"error": "Erro no banco de dados"}, 500
    except Exception as e:
        logging.error("❌ Erro no webhook de status:")
        logging.error(traceback.format_exc())
        return {"error": "Erro interno"}, 500

@app.route(f'{prefix}/webhook/disconnected', methods=['POST'])
def webhook_disconnected():
    logging.info("🔌 Webhook Disconnected foi chamado")

    if not request.is_json:
        logging.warning("❗ Requisição não é JSON válida")
        return {"error": "Requisição precisa ser JSON"}, 415

    try:
        dados = request.get_json()
        logging.info(f"📦 Dados recebidos: {json.dumps(dados, indent=2)}")

        # Validação dos dados recebidos
        instance_id = dados.get("instanceId")  # Z-API usa instanceId
        if not instance_id:
            logging.error("❗ ID da instância não encontrado no payload")
            return {"error": "ID da instância não encontrado"}, 400

        # Coleta informações adicionais úteis
        timestamp = dados.get("momment") or dados.get("timestamp")  # Z-API usa 'momment'
        device_info = dados.get("device") or "não informado"
        reason = dados.get("reason") or "não informado"

        # Formata a mensagem para o email
        disconnect_info = {
            "instance_id": instance_id,
            "timestamp": datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S') if timestamp else "não informado",
            "device": device_info,
            "reason": reason
        }

        logging.warning(f"⚠ Instância desconectada: {instance_id}")
        logging.info(f"📝 Detalhes da desconexão: {json.dumps(disconnect_info, indent=2)}")

        # Tenta enviar o email
        try:
            send_email_zapi_disconnected(disconnect_info)
            logging.info("✅ Email de notificação enviado com sucesso")
            return {"message": "Notificação enviada"}, 200
        except Exception as email_error:
            logging.error(f"❌ Erro ao enviar email: {str(email_error)}")
            # Ainda retorna 200 pois o webhook foi processado
            return {"message": "Webhook processado, mas falha ao enviar email"}, 200

    except Exception as e:
        logging.error("❌ Erro no webhook de desconexão:")
        logging.error(traceback.format_exc())
        return {"error": "Erro interno"}, 500


@app.route(f'{prefix}/whatsapp')
def whatsapp():
    instzapi, ZAPI_INSTANCE, ZAPI_TOKEN = instancia_zapi(current_user.role)
    is_admin = 'AD' in current_user.role
    # Página atual vinda da URL (default: 1)
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * maxLines

    # Subquery agora agrupa por telefone E instancia
    # subquery = (
    #     database.session.query(
    #         MsgDB.telefone,
    #         MsgDB.instancia,
    #         func.max(MsgDB.data).label('ultima_data')
    #     )
    #     .group_by(MsgDB.telefone, MsgDB.instancia)
    #     .subquery()
    # )
    # Subquery com max(id) para garantir unicidade
    subquery = (
        database.session.query(
            MsgDB.telefone,
            MsgDB.instancia,
            func.max(MsgDB.id).label('msg_id')
        )
        .group_by(MsgDB.telefone, MsgDB.instancia)
        .subquery()
    )

    # Consulta principal com join na subquery
    # ultimas_mensagens_query = (
    #     database.session.query(MsgDB)
    #     .join(
    #         subquery,
    #         (MsgDB.telefone == subquery.c.telefone) &
    #         (MsgDB.instancia == subquery.c.instancia) &
    #         (MsgDB.data == subquery.c.ultima_data)
    #     )
    #     .order_by(desc(MsgDB.data))
    # )
    # Consulta principal com join apenas pelo ID da mensagem
    ultimas_mensagens_query = (
        database.session.query(MsgDB)
        .join(subquery, MsgDB.id == subquery.c.msg_id)
        .order_by(desc(MsgDB.data))
    )

    # Se não for admin, filtra pela instância permitida
    if not is_admin:
        ultimas_mensagens_query = ultimas_mensagens_query.filter(MsgDB.instancia == instzapi)

    #ultimas_mensagens = ultimas_mensagens_query.all()
    # Paginação
    #total = ultimas_mensagens_query.count()
    #ultimas_mensagens = ultimas_mensagens_query.limit(maxLines).offset(offset).all()
    ultimas_mensagens_paginated = ultimas_mensagens_query.paginate(page=page, per_page=maxLines)
    ultimas_mensagens = ultimas_mensagens_paginated.items

    # Parte de contatos (sem mudanças):
    Cliente = ClientesDB
    Contrato = ContratosDB

    contatos = (
        database.session.query(ContatoDB, Cliente)
        .join(Cliente, ContatoDB.idcliente == Cliente.idcliente)
        .all()
    )

    contratos_ativos = {
        idcliente
        for (idcliente,) in (
            database.session.query(Contrato.idcliente)
            .filter(Contrato.status.ilike("ativo"))
            .distinct()
            .all()
        )
    }

    mapa_contatos = {
        normalize_phone(c.mobile or ""): (
            c.nomecontato,
            cliente.nomecliente,
            cliente.unidade,
            c.idcliente in contratos_ativos
        )
        for c, cliente in contatos
    }

    lista_contatos = []
    for msg in ultimas_mensagens:
        dados = mapa_contatos.get(normalize_phone(msg.telefone))
        if dados:
            nome_contato, nome_cliente, unidade, contrato_ativo = dados
        else:
            nome_contato = nome_cliente = unidade = None
            contrato_ativo = False
        lista_contatos.append((msg, nome_contato, nome_cliente, unidade, contrato_ativo))

    return render_template("whatsapp_list.html", contatos=lista_contatos, instancia=instzapi, admin=is_admin, mensagens_paginadas=ultimas_mensagens_paginated)

@app.route(f'{prefix}/whatsapp/conversa/<telefone>', methods=['GET', 'POST'])
def whatsapp_conversa(telefone):
    phone = normalize_phone(telefone)
    instzapi, ZAPI_INSTANCE, ZAPI_TOKEN = instancia_zapi(current_user.role)
    is_admin = 'AD' in current_user.role

    if request.method == 'POST':
        message = request.form.get('message', '')
        file = request.files.get('media')
        headers = {
            "Content-Type": "application/json",
            "Client-Token": ZAPI_CLIENT
        }

        if file and file.filename != '':
            # Salva o arquivo em pasta estática
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1].lower()  # pega a extensão (.jpg, .png, etc)
            filepath = os.path.join(WA_FOLDER, UP_FOLDER, filename)
            file.save(filepath)
            # Determina o tipo de mídia pela extensão
            media_type = EXTENSION_TO_MEDIA_TYPE.get(ext)
            if not media_type:
                return f"Erro: Formato de arquivo não suportado. Extensão: {ext}"

            config = MEDIA_CONFIGS[media_type]

            # Garante que a base URL tenha a barra final
            base_url = DXSURL if DXSURL.endswith('/') else DXSURL + '/'
            # Monta a URL completa
            doxsys_url = urljoin(base_url, f"{WA_FOLDER}/{UP_FOLDER}/{filename}")

            # Verifica se o tipo de mídia é suportado
            if media_type not in MEDIA_CONFIGS:
                return f"Erro: Tipo de mídia '{media_type}' não suportado"

            # Importante: Garantir que o ponteiro do arquivo está no início
            file.seek(0)
            # Lê o conteúdo do arquivo
            file_content = file.read()
            # Checa tamanho
            if len(file_content) > MAX_FILE_SIZE:
                return "Erro: Arquivo muito grande. Tamanho máximo: 16MB"

            # Define mime type
            mime_type = config['mime_types'].get(ext)
            # base64_data = base64.b64encode(file_content).decode('utf-8')
            base64_data = base64.b64encode(file_content).decode('utf-8').replace('\n', '')
            # Monta o data URI corretamente
            base64_uri = f"data:{mime_type};base64,{base64_data}"

            # Monta payload
            payload = {
                'phone': phone,
                config['payload_key']: base64_uri
            }
            # Payload especial para documentos
            if media_type == 'document':
                payload = {
                    'phone': phone,
                    'document': f"data:{mime_type};base64,{base64_data}",
                    'fileName': filename  # Nome do arquivo é obrigatório para documentos
                }
            else:
                payload = {
                    'phone': phone,
                    config['payload_key']: base64_uri
                }
                # Se for imagem ou vídeo, permite caption
                if media_type in ['image', 'video']:
                    payload['caption'] = ('*'+current_user.username+'*: '+message) or filename

            # Monta a URL para a Z-API
            url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}{config['endpoint']}"
            logging.info(f'file_url:{doxsys_url}')
            msg_salva = f"[{config['payload_key']} enviado] {filename} - {message} "
        else:
            # Apenas texto
            url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
            payload = {
                "phone": phone,
                "message": '*'+current_user.username+'*: '+message
            }
            msg_salva = message

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            tipo = 'enviada'
            message_data = response.json()
            message_id = message_data.get('messageId')  # id no whatsapp
            zaap_id = message_data.get('zaapId')  # id na fila da z-api
            nova_msg = MsgDB(
                instancia=instzapi,
                telefone=phone,
                mensagem_id = message_id,
                mensagem=msg_salva,
                tipo=tipo,
                idusuario=current_user.id,
                dtcriac=date.today()
            )
            database.session.add(nova_msg)
            database.session.commit()
            flash("Mensagem enviada com sucesso!", "alert-success")
        else:
            flash(f"Erro ao enviar: {response.text}", "alert-danger")

        return redirect(url_for('whatsapp_conversa', telefone=phone))

    # Marcar mensagens como lidas
    filtro_leitura = MsgDB.query.filter_by(telefone=phone, tipo='recebida', lida=False)
    if not is_admin:
        filtro_leitura = filtro_leitura.filter(MsgDB.instancia == instzapi)
    filtro_leitura.update({'lida': True})
    database.session.commit()

    # Buscar mensagens com este número
    mensagens_query = (
        database.session.query(MsgDB, usuario.username)
        .outerjoin(usuario, MsgDB.idusuario == usuario.id)
        .filter(MsgDB.telefone == phone)
        .order_by(MsgDB.data.desc())
    )
    if not is_admin:
        mensagens_query = mensagens_query.filter(MsgDB.instancia == instzapi)

    mensagens_raw = mensagens_query.all()

    contatos = ContatoDB.query.all()
    mapa_contatos = {normalize_phone(c.mobile or ""): c.nomecontato for c in contatos}
    nome = mapa_contatos.get(phone)

    return render_template("whatsapp_conversa.html", mensagens=mensagens_raw, nomecontato=nome, telefone=phone)


def whatsapp_resp_automatica(telefone, instzapi):
    if instzapi == 'Suporte11978109256':
        ZAPI_INSTANCE = ZAPI_INSTANCE_SUPP
        ZAPI_TOKEN = ZAPI_TOKEN_SUPP
        usr_resp = 30 # Emanuel
    elif instzapi == 'Sales11970847098':
        ZAPI_INSTANCE = ZAPI_INSTANCE_SALES
        ZAPI_TOKEN = ZAPI_TOKEN_SALES
        usr_resp = 36 # Luciana

    phone = normalize_phone(telefone)

    if request.method == 'POST':
        message = request.form.get('message', '')
        file = request.files.get('media')
        headers = {
            "Content-Type": "application/json",
            "Client-Token": ZAPI_CLIENT
        }
        url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
        message = 'Olá, o nosso horário de funcionamento é das 8h00 às 18h00 de segunda a sexta-feira. Agradecemos seu contato e informamos que retornaremos assim que possível.'
        payload = {
            "phone": phone,
            "message": '*DOX SG Ltda*: '+message
        }
        msg_salva = message
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            tipo = 'enviada'
            message_data = response.json()
            message_id = message_data.get('messageId')  # id no whatsapp
            nova_msg = MsgDB(
                instancia=instzapi,
                telefone=phone,
                mensagem_id = message_id,
                mensagem=msg_salva,
                tipo=tipo,
                idusuario=usr_resp, # 9=Legado
                dtcriac=date.today()
            )
            database.session.add(nova_msg)
            database.session.commit()

    return response.status_code

def instancia_zapi(role):
    if 'TC' in role or 'ST' in role:
        return 'Suporte11978109256', ZAPI_INSTANCE_SUPP, ZAPI_TOKEN_SUPP
    else:
        return 'Sales11970847098', ZAPI_INSTANCE_SALES, ZAPI_TOKEN_SALES

# Uso do Libre Translate para traduzir as mensagens (estava off-line)
# Trocamos para o MyMemory Translated
@app.route('/traduzir_mensagem', methods=['POST'])
def traduzir_mensagem():
    try:
        dados = request.get_json(force=True)
        texto = dados.get('texto', '').strip()
        origem = dados.get('origem', '').strip()
        destino = dados.get('destino', '').strip()
        if not texto or not origem or not destino:
            return jsonify({'erro': 'Parâmetros inválidos'}), 400
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': texto,
            'langpair': f'{origem}|{destino}'
        }
        response = requests.get(url, params=params)
        # response = requests.post(
        #     'https://libretranslate.de/translate',
        #     data={
        #         'q': texto,
        #         'source': origem,
        #         'target': destino,
        #         'format': 'text'
        #     },
        #     headers={'Content-Type': 'application/x-www-form-urlencoded'}
        # )
        if response.status_code != 200:
            logging.error(f"Erro na tradução: {response.status_code} - {response.text}")
            return jsonify({'erro': 'Erro ao traduzir o texto'}), 500
        # traduzido = response.json().get('translatedText') # Libre Translate
        traduzido = response.json().get('responseData', {}).get('translatedText')  # MyMemory Translated
        return jsonify({'traduzido': traduzido})
    except Exception as e:
        logging.exception("Erro interno na tradução")
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

# Uso do LanguageTool para corrigir as mensagens no WhatsApp
@app.route('/corrigir_mensagem', methods=['POST'])
def corrigir_mensagem():
    try:
        dados = request.get_json(force=True)
        texto = dados.get('mensagem', '')
        idioma = dados.get('idioma', 'pt-BR')
        if not texto.strip():
            return jsonify({'erro': 'Mensagem vazia.'}), 400
        response = requests.post(
            'https://api.languagetool.org/v2/check',
            data={'text': texto, 'language': idioma}
        )
        if response.status_code != 200:
            return jsonify({'erro': 'Erro na API do LanguageTool'}), 500
        result = response.json()
        corrigido = texto
        for match in reversed(result.get('matches', [])):
            if match.get('replacements'):
                start = match['offset']
                end = start + match['length']
                replacement = match['replacements'][0]['value']
                corrigido = corrigido[:start] + replacement + corrigido[end:]
        return jsonify({'correta': corrigido})
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

# Uso do CHATGPT para corrigir as mensagens no WhatsApp
# @app.route('/corrigir_mensagem_com_openai', methods=['POST'])
# def corrigir_mensagem_com_openai():
#     dados = request.get_json()
#     mensagem = dados.get('mensagem', '')
#
#     if not mensagem.strip():
#         return jsonify({'erro': 'Mensagem vazia.'}), 400
#
#     prompt = f"Corrija erros de português nesta frase:\n\n\"{mensagem}\""
#
#     try:
#         resposta = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "Você é um revisor de português."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.3,
#             max_tokens=300
#         )
#         texto_corrigido = resposta.choices[0].message.content.strip()
#         return jsonify({'correta': texto_corrigido})
#     except Exception as e:
#         print("❌ ERRO NA CORREÇÃO:", str(e))
#         return jsonify({'erro': str(e)}), 500

#TESTE PARA O RECEIVED VIA CURL NO CMD:
#curl -v -X POST https://www.doxsg.com/doxsys/webhook/received -H "Content-Type: application/json" -d "{\"from\": \"5511999631100\", \"message\": \"teste via curl\", \"type\": \"text\"}"

# DIGEST REPORTS
def weekly_digest():
    userslst = usuario.query.filter(and_(usuario.access >= 3, usuario.role.contains('TT'))).order_by(usuario.username.asc()).all()
    if userslst:
        accounts_digest(userslst)
    return "Ok", 200
def accounts_digest(usrlst):
    hoje7 = date.today() + timedelta(days=7)
    for usr in usrlst:
        contas_vencidos = FinancDB.query.filter(and_(
            FinancDB.valor <= 0, FinancDB.active == 1,
            FinancDB.dt_data < date.today(), FinancDB.pago == 0)).order_by(
            FinancDB.dt_data.asc()).all()
        receb_vencidos = FinancDB.query.filter(and_(
            FinancDB.valor > 0, FinancDB.active == 1,
            FinancDB.dt_data < date.today(), FinancDB.pago == 0)).order_by(
            FinancDB.dt_data.asc()).all()
        contas_a_vencer = FinancDB.query.filter(and_(
            FinancDB.valor <= 0, FinancDB.active == 1,
            FinancDB.dt_data >= date.today(), FinancDB.dt_data <= hoje7,
            FinancDB.pago == 0)).order_by(
            FinancDB.dt_data.asc()).all()
        receb_a_vencer = FinancDB.query.filter(and_(
            FinancDB.valor > 0, FinancDB.active == 1,
            FinancDB.dt_data >= date.today(), FinancDB.dt_data <= hoje7,
            FinancDB.pago == 0)).order_by(
            FinancDB.dt_data.asc()).all()
        if (contas_vencidos or receb_vencidos or contas_a_vencer or receb_a_vencer):
            send_email_accounts(usr.email,usr.username,usr.sigla,contas_vencidos,receb_vencidos,contas_a_vencer,receb_a_vencer)

def send_email_accounts(to_email, username, sigla, list_contvencid, list_recebvencid, list_contvencer, list_recebvencer):
    # msg_from = ConfigDB.query.filter(and_(ConfigDB.company == ciaidsystem, ConfigDB.var == 'MessageFrom')).first().valor
    msg_from = "DOXSYS"
    # msg_logo = ConfigDB.query.filter(and_(ConfigDB.company == ciaidsystem, ConfigDB.var == 'MessageLogo')).first().valor
    msg_logo = 'logo300x58.gif'
    # Criar mensagem de e-mail
    message = MIMEMultipart("related")
    message["From"] = msg_from + "<"+sender_email+">"
    message["To"] = username+"<"+to_email+">"
    message["Subject"] = f"DOXSYS [{sigla}] - Contas vencidas e a vencer"

    # Gerar o HTML da tabela CONTAS VENCIDAS
    contas_list_vencidas = "<table border='1' cellpadding='5' cellspacing='0'>"
    contas_list_vencidas += "<thead><tr><th>Data</th><th>Fornecedor</th><th>Valor</th><th>Fatur</th><th>Descrição</th><th>Observação</th></tr></thead><tbody>"
    for item in list_contvencid:
        data_formatada = item.dt_data.strftime('%d/%m/%Y') if item.dt_data else 'N/A'
        faturado_texto = "Sim" if item.faturado else "Não"
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
            valor_formatado = locale.currency(item.valor, grouping=True)
        except (ImportError, locale.Error):
            valor_formatado = f"R$ {item.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        contas_list_vencidas += (f"<tr style='color: #AA0000'><td>{data_formatada}</td><td>{item.benefic}</td><td>{valor_formatado}</td><td>{faturado_texto}</td><td>{item.descricao}</td><td>{item.observacao}</td></tr>")
    contas_list_vencidas += "</tbody></table>"

    # Gerar o HTML da tabela RECEBIMENTOS VENCIDOS
    receb_list_vencidos = "<table border='1' cellpadding='5' cellspacing='0'>"
    receb_list_vencidos += "<thead><tr><th>Data</th><th>Cliente</th><th>Valor</th><th>Fatur</th><th>Descrição</th><th>Observação</th></tr></thead><tbody>"
    for item in list_recebvencid:
        data_formatada = item.dt_data.strftime('%d/%m/%Y') if item.dt_data else 'N/A'
        faturado_texto = "Sim" if item.faturado else "Não"
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
            valor_formatado = locale.currency(item.valor, grouping=True)
        except (ImportError, locale.Error):
            valor_formatado = f"R$ {item.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        receb_list_vencidos += (f"<tr><td>{data_formatada}</td><td>{item.benefic}</td><td>{valor_formatado}</td><td>{faturado_texto}</td><td>{item.descricao}</td><td>{item.observacao}</td></tr>")
    receb_list_vencidos += "</tbody></table>"

    # Gerar o HTML da tabela CONTAS A VENCER
    contas_list_vencer = "<table border='1' cellpadding='5' cellspacing='0'>"
    contas_list_vencer += "<thead><tr><th>Data</th><th>Fornecedor</th><th>Valor</th><th>Fatur</th><th>Descrição</th><th>Observação</th></tr></thead><tbody>"
    for item in list_contvencer:
        data_formatada = item.dt_data.strftime('%d/%m/%Y') if item.dt_data else 'N/A'
        faturado_texto = "Sim" if item.faturado else "Não"
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
            valor_formatado = locale.currency(item.valor, grouping=True)
        except (ImportError, locale.Error):
            valor_formatado = f"R$ {item.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        contas_list_vencer += (f"<tr style='color: #AA0000'><td>{data_formatada}</td><td>{item.benefic}</td><td>{valor_formatado}</td><td>{faturado_texto}</td><td>{item.descricao}</td><td>{item.observacao}</td></tr>")
    contas_list_vencer += "</tbody></table>"

    # Gerar o HTML da tabela RECEBIMENTOS A VENCER
    receb_list_vencer = "<table border='1' cellpadding='5' cellspacing='0'>"
    receb_list_vencer += "<thead><tr><th>Data</th><th>Cliente</th><th>Valor</th><th>Fatur</th><th>Descrição</th><th>Observação</th></tr></thead><tbody>"
    for item in list_recebvencer:
        data_formatada = item.dt_data.strftime('%d/%m/%Y') if item.dt_data else 'N/A'
        faturado_texto = "Sim" if item.faturado else "Não"
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
            valor_formatado = locale.currency(item.valor, grouping=True)
        except (ImportError, locale.Error):
            valor_formatado = f"R$ {item.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        receb_list_vencer += (f"<tr style='color: #000099'><td>{data_formatada}</td><td>{item.benefic}</td><td>{valor_formatado}</td><td>{faturado_texto}</td><td>{item.descricao}</td><td>{item.observacao}</td></tr>")
    receb_list_vencer += "</tbody></table>"

    # Renderizar o template HTML e passar o valor de 'username'
    body = render_template('email_contas-digest.html', username=username, contas_list_vencidas=contas_list_vencidas, receb_list_vencidos=receb_list_vencidos, contas_list_vencer=contas_list_vencer, receb_list_vencer=receb_list_vencer)

    # Anexar corpo HTML ao e-mail
    message.attach(MIMEText(body, "html"))

    # Anexar a imagem (logomarca)
    logomarca = current_app.config['APP_STATIC'] + '/' + msg_logo

    with open(logomarca, 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header("Content-ID", "<logo_dox>")
        message.attach(img)

    # Enviar e-mail via Gmail SMTP
    try:
        server = smtplib.SMTP(send_smtp_srv, 587)
        server.starttls()  # Usar TLS
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())
        server.close()
        log_action('financeiro', 'digest', 'Usr:' + to_email + ' Itens: CVD' +
        str(len(contas_list_vencidas)) + '/RVD' + str(len(receb_list_vencidos)) + '/CAV' + str(len(contas_list_vencer)) + '/RAV' + str(len(receb_list_vencer)))
    except Exception as e:
        return jsonify({'erro': f"Erro ao enviar e-mail para {to_email}: {str(e)}"}), 500

    return jsonify({"status": "ok", "msg": "Email digest contas enviado!"}), 200
