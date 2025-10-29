from resellercontrol import login_manager
from resellercontrol import database
from flask_login import UserMixin
from datetime import date, datetime
import pytz
# from sqlalchemy import Integer, ForeignKey, String, Column
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship

@login_manager.user_loader
def load_usuario(id_usuario):
    return usuario.query.get(int(id_usuario))

def now_brazil():
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz)

class usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    sigla = database.Column(database.String, nullable=False)
    role = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    mobile = database.Column(database.String)
    phone = database.Column(database.String)
    senha = database.Column(database.String, nullable=False)
    access = database.Column(database.Integer, nullable=False, default=0)
    cli_hist = database.Column(database.String)

class ClientesDB(database.Model):
    __tablename__ = 'clientes'
    idcliente = database.Column('idcliente', database.Integer, primary_key=True)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    dtalter = database.Column(database.Date)
    active = database.Column('active')
    status = database.Column(database.String)
    nomecliente = database.Column(database.String, nullable=False)
    unidade = database.Column(database.String, nullable=False, default='Matriz')
    razaosocial = database.Column(database.String)
    cnpj = database.Column(database.String)
    inscrmunicipal = database.Column(database.String)
    inscrestadual = database.Column(database.String)
    municipio = database.Column(database.String)
    estado = database.Column(database.String)
    pais = database.Column(database.String)
    endereco = database.Column(database.String)
    complemento = database.Column(database.String)
    cep = database.Column(database.String)
    telefone = database.Column(database.String)
    emailnfe = database.Column(database.String)
    linkcadastro = database.Column(database.String)
    linkpipeline = database.Column(database.String)
    website = database.Column(database.String)
    observacao = database.Column(database.Text)

class ContatoDB(database.Model):
    __tablename__ = 'contatos'
    idcontato = database.Column(database.Integer, primary_key=True)
    idcliente = database.Column(database.Integer)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    dtalter = database.Column(database.Date)
    active = database.Column('active')
    emphasis = database.Column(database.Integer)
    mailing = database.Column(database.Integer)
    nomecontato = database.Column(database.String)
    mobile = database.Column(database.String)
    phone = database.Column(database.String)
    email = database.Column(database.String)
    departamento = database.Column(database.String)
    cargo = database.Column(database.String)
    bizrole = database.Column(database.String)
    observacao = database.Column(database.String)
    aniversario = database.Column(database.String)

class PropostasDB(database.Model):
    __tablename__ = 'propostas'
    idproposta = database.Column(database.Integer, primary_key=True)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    dtalter = database.Column(database.Date)
    status = database.Column(database.String)
    vendedor = database.Column(database.String)
    idcliente = database.Column(database.Integer)
    nomecliente = database.Column(database.String)
    descricao = database.Column(database.String)
    dataprop = database.Column(database.String)
    notas = database.Column(database.String)
    idvendor = database.Column(database.Integer)
    idpipeline = database.Column(database.Integer)
    horasprev = database.Column(database.Numeric)
    dtprovavel = database.Column(database.Date)
    forecast = database.Column(database.Integer)
    vlrsoft = database.Column(database.Numeric)
    vlrserv = database.Column(database.Numeric)
    periodo = database.Column(database.Integer)
    arquivo = database.Column(database.String)
    renovac  = database.Column(database.Integer)  # (1/0)


class ContratosDB(database.Model):
    __tablename__ = 'contratos'
    idcontrato = database.Column(database.Integer, primary_key=True)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    idproposta = database.Column(database.Integer, database.ForeignKey('propostas.idproposta'))
    dtcriac = database.Column(database.Date)
    dtalter = database.Column(database.Date)
    idcliente = database.Column(database.Integer)
    nomecliente = database.Column(database.String)
    vendedor = database.Column(database.String)
    unidade = database.Column(database.String)
    produto = database.Column(database.String)
    status = database.Column(database.String)
    proposta = database.Column(database.String)
    dtproposta = database.Column(database.Date)
    pedido = database.Column(database.String)
    dtpedido = database.Column(database.Date)
    codcontrato = database.Column(database.String)
    validadecontrato = database.Column(database.Date)
    duracaocontrato = database.Column(database.Integer)
    faturamento = database.Column(database.String)
    fatfrequencia = database.Column(database.String)
    infratype = database.Column(database.String)
    aplicacaotype = database.Column(database.String)
    instanciatype = database.Column(database.String)
    usersavancados = database.Column(database.Integer)
    usersregulares = database.Column(database.Integer)
    milregistros = database.Column(database.Integer)
    gbstorage = database.Column(database.Integer)
    powerbi = database.Column(database.String)
    apisistema = database.Column(database.String)
    suporte = database.Column(database.String)
    horascontratadas = database.Column(database.Integer)
    horasentregues = database.Column(database.Integer)
    horasstatus = database.Column(database.String)
    bminstruc = database.Column(database.String)
    nfinstruc = database.Column(database.String)
    observacao = database.Column(database.String)

class ListaOpcoesDB(database.Model):
    __tablename__ = 'lista_opcoes'
    id = database.Column(database.Integer, primary_key=True)
    lst = database.Column(database.String)
    opt = database.Column(database.String)
    msg = database.Column(database.String)

class OrderbyOptDB(database.Model):
    __tablename__ = 'orderbyopt'
    id = database.Column(database.Integer, primary_key=True)
    option = database.Column(database.String)
    label = database.Column(database.String)

class ProjetosDB(database.Model):
    __tablename__ = 'projetos'
    idprojeto = database.Column(database.Integer, primary_key=True)
    idclint = database.Column(database.Integer, database.ForeignKey('clientes.idcliente'))
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    dtcriac = database.Column(database.Date)
    dtalter = database.Column(database.Date)
    statusproj = database.Column(database.String)
    projetonome = database.Column(database.String)
    prjinicplan = database.Column(database.Date)
    prjfimplan = database.Column(database.Date)
    prjinicreal = database.Column(database.Date)
    prjfimreal = database.Column(database.Date)
    propcodigo = database.Column(database.String)
    propdata = database.Column(database.Date)
    pedidocodig = database.Column(database.String)
    pedidodata = database.Column(database.Date)
    oscodigo = database.Column(database.String)
    osdata = database.Column(database.Date)
    horasprev = database.Column(database.Numeric)
    horasusds = database.Column(database.Numeric)
    responsnome = database.Column(database.String)
    tecniconome = database.Column(database.String)
    kickoff = database.Column(database.String)
    kickoffdata = database.Column(database.Date)
    testes = database.Column(database.String)
    testesdata = database.Column(database.Date)
    homologacao = database.Column(database.String)
    homologdata = database.Column(database.Date)
    dbookpwrbi = database.Column(database.String)
    dbkpwrbidt = database.Column(database.Date)
    treinamento = database.Column(database.String)
    treinamdata = database.Column(database.Date)
    aceiteproj = database.Column(database.String)
    aceitedata = database.Column(database.Date)
    faturado = database.Column(database.String)
    nfnumero = database.Column(database.String)
    nfdata = database.Column(database.Date)
    atestado = database.Column(database.String)
    atestadodat = database.Column(database.Date)
    percentual = database.Column(database.Numeric)
    stakeholders = database.Column(database.String)
    observacao = database.Column(database.String)
    #parent = relationship("clientes", back_populates="projetos")

# percentual DECIMAL(4,3) - 4 casas, sendo 3 decimais
# class sqlalchemy.types.DECIMAL(precision=None, scale=None, decimal_return_scale=None, asdecimal=True)

class PessoalDB(database.Model):
    __tablename__ = 'pessoal'
    idfunc = database.Column(database.Integer, primary_key=True)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    active = database.Column(database.Integer)
    dtcriac = database.Column(database.Date)
    dtalter = database.Column(database.Date)
    statusrh = database.Column(database.String)
    dtadmiss = database.Column(database.Date)
    salrinic = database.Column(database.Numeric)
    salrtual = database.Column(database.Numeric)
    cargfunc = database.Column(database.String)
    dtdeslig = database.Column(database.Date)
    dtlimfer = database.Column(database.Date)
    nomefunc = database.Column(database.String)
    rgfunc = database.Column(database.String)
    cpffunc = database.Column(database.String)
    fonefixo = database.Column(database.String)
    fonecelr = database.Column(database.String)
    emailpes = database.Column(database.String)
    dtnascim = database.Column(database.Date)
    escolari = database.Column(database.String)
    estadciv = database.Column(database.String)
    nomeconj = database.Column(database.String)
    dtnasccg = database.Column(database.Date)
    endereco = database.Column(database.String)
    bairro = database.Column(database.String)
    cidade = database.Column(database.String)
    estado = database.Column(database.String)
    cep = database.Column(database.String)
    benefc = database.Column(database.String)
    ferias = database.Column(database.String)
    observacao = database.Column(database.String)

class CredencialDB(database.Model):
    __tablename__ = 'credencial'
    idcredenc = database.Column(database.Integer, primary_key=True)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    active = database.Column(database.Integer)
    dtcriac = database.Column(database.Date)
    dtalter = database.Column(database.Date)
    accesslevel = database.Column(database.Integer)
    nomecliente = database.Column(database.String)
    statenv = database.Column(database.String)
    cloudloc = database.Column(database.String)
    ambiente = database.Column(database.String)
    version = database.Column(database.String)
    dtimplantac = database.Column(database.Date)
    responsav = database.Column(database.String)
    urlweb = database.Column(database.String)
    logindocc = database.Column(database.String)
    passwddocc = database.Column(database.String)
    loginserv = database.Column(database.String)
    passwdserv = database.Column(database.String)
    loginapi = database.Column(database.String)
    passwdapi = database.Column(database.String)
    keyfile = database.Column(database.String)
    notas = database.Column(database.String)

class FinancDB(database.Model):
    __tablename__ = 'financeiro'
    idfinanc = database.Column(database.Integer, primary_key=True)
    active = database.Column(database.Integer)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    dtcriac = database.Column(database.Date)
    dtalter = database.Column(database.Date)
    dt_data = database.Column(database.Date)
    pago = database.Column(database.Integer)
    dtpagto = database.Column(database.Date)
    faturado = database.Column(database.Integer)
    dtfatur = database.Column(database.Date)
    valor = database.Column(database.Numeric)
    categoria = database.Column(database.String)
    subcategor = database.Column(database.String)
    benefic = database.Column(database.String)
    descricao = database.Column(database.String)
    observacao = database.Column(database.String)

class SaldoDB(database.Model):
    __tablename__ = 'saldo'
    idsaldo = database.Column(database.Integer, primary_key=True)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    data = database.Column(database.Date)
    saldo = database.Column(database.Numeric)
    aplic = database.Column(database.Numeric)
    variac = database.Column(database.Numeric)
    conta = database.Column(database.String)
    observacao = database.Column(database.String)

class ConfigDB(database.Model):
    __tablename__ = 'variables'
    idvar = database.Column(database.Integer, primary_key=True)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    dtalter = database.Column(database.Date)
    var = database.Column(database.String)
    valor = database.Column(database.String)

class LogDB(database.Model):
    __tablename__ = 'log_actions'
    idlog = database.Column(database.Integer, primary_key=True)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    datahora = database.Column(database.Date)
    modulo = database.Column(database.String)
    funcao = database.Column(database.String)
    acao = database.Column(database.String)

class PipelineDB(database.Model):
    __tablename__ = 'pipeline'
    idpipeline = database.Column(database.Integer, primary_key=True)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    active = database.Column(database.Integer)
    dtcriac = database.Column(database.Date)
    dtalter = database.Column(database.Date)
    idcliente = database.Column(database.Integer, database.ForeignKey('clientes.idcliente'))
    prazo = database.Column(database.Date)
    acao = database.Column(database.String) # TINYTEXT (255)
    dtacao = database.Column(database.Date)
    dtapres = database.Column(database.Date)
    produto = database.Column(database.String) # CHAR(16)
    vendedor = database.Column(database.Integer)
    status = database.Column(database.String) # CHAR(12)
    oportunidade = database.Column(database.String) # CHAR(128)
    historico = database.Column(database.String) # TEXT (64k)
    facilit = database.Column(database.String) # CHAR(16)
    decisor = database.Column(database.String) # CHAR(16)
    concorrentes = database.Column(database.String) # CHAR(64)
    prioridade = database.Column(database.Integer)
    mercado = database.Column(database.String) #CHAR(32)
    linkext = database.Column(database.String) # TINYTEXT (255)

class EquiptosDB(database.Model):
    __tablename__ = 'equiptos'
    idequipto = database.Column(database.Integer, primary_key=True)
    active = database.Column(database.Integer)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    dtcriac = database.Column(database.Date)
    dtalter = database.Column(database.Date)
    status = database.Column(database.Integer) # CHAR(12)
    usuario = database.Column(database.String) # VARCHAR (64)
    equipto_id = database.Column(database.String) # VARCHAR (32)
    equipto_tipo = database.Column(database.String) # VARCHAR (32)
    equipto_nome = database.Column(database.String) # VARCHAR (32)
    equipto_marca = database.Column(database.String) # VARCHAR (32)
    equipto_modelo = database.Column(database.String) # VARCHAR (64)
    dtcompra = database.Column(database.Date)
    dtdesativ = database.Column(database.Date)
    motivodesativ = database.Column(database.String) # TINYTEXT
    nfcompra = database.Column(database.String) # VARCHAR (32)
    valor = database.Column(database.Numeric) # DECIMAL(12,2)
    useradmin = database.Column(database.String) # VARCHAR (32)
    password = database.Column(database.String) # VARCHAR (32)
    pin = database.Column(database.String) # VARCHAR (16)
    descricao = database.Column(database.String) # TINYTEXT
    observacao = database.Column(database.String) # TINYTEXT

class KBFaqDB(database.Model):
    __tablename__ = 'kbfaq'
    idkbfaq = database.Column(database.Integer, primary_key=True)
    active = database.Column(database.Integer)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    dtcriac = database.Column(database.Date)
    dtalter = database.Column(database.Date)
    accesslevel = database.Column(database.Integer)
    categoria = database.Column(database.String) # VARCHAR (32)
    titulo = database.Column(database.String) # TINYTEXT 255
    descricao = database.Column(database.String) # TEXT 65536

class MsgDB(database.Model):
    __tablename__ = 'mensagens'
    id = database.Column(database.Integer, primary_key=True)
    instancia = database.Column(database.String(32), nullable=False)
    telefone = database.Column(database.String(32), nullable=False)
    mensagem_id = database.Column(database.String(64), nullable=False)
    mensagem = database.Column(database.Text, nullable=False)
    tipo = database.Column(database.String(20), nullable=False)  # 'enviada' ou 'recebida'
    data = database.Column(database.DateTime, default=now_brazil)
    # data = database.Column(database.DateTime, default=datetime.utcnow)
    dtcriac = database.Column(database.Date, default=date.today)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=True)
    lida = database.Column(database.Boolean, default=False)  # NOVO CAMPO
    status = database.Column(database.String(20), default='pendente') # NOVO CAMPO
    usuario = database.relationship('usuario', backref='mensagens', lazy=True)

class VersionDB(database.Model):
    __tablename__ = 'versions'
    id = database.Column(database.Integer, primary_key=True)
    active = database.Column(database.Integer)
    idusuario = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    dtalter = database.Column(database.Date)
    produto = database.Column(database.String)
    version = database.Column(database.String)
    nomecliente = database.Column(database.String)
    bug = database.Column(database.Integer)
    dtbug = database.Column(database.Date)
    descricao = database.Column(database.String) # TEXT 65536
    whoid = database.Column(database.String)
    chamado = database.Column(database.String)
    prazofix = database.Column(database.Date)
    bugfix = database.Column(database.Integer)
    dtfix = database.Column(database.Date)
    versionfix = database.Column(database.String)

class WebAccessDB(database.Model):
    __tablename__ = 'webaccess'
    id = database.Column(database.Integer, primary_key=True)
    datahora = database.Column(database.DateTime, nullable=False)
    usr_email = database.Column(database.String(32)) # 32
    user_agent = database.Column(database.String(96)) # 96
    ipaddr = database.Column(database.String(64)) # 64
    referrer = database.Column(database.String(256)) # 256
    language = database.Column(database.String(64)) # 64
    host = database.Column(database.String(32)) # 32
    full_path = database.Column(database.String(256)) # 256
    httpmethod = database.Column(database.String(16)) # 16
    querystr = database.Column(database.String(256)) # 256
    notify = database.Column(database.String(16)) # 16


"""
CRUD Básico
USE `resellercontrol`
select idcliente,nomecliente,unidade from resellercontrol.contratos;
SELECT idcliente,nomecliente,unidade FROM resellercontrol.clientes where nomecliente like 'n%';
SELECT idcontrato,idcliente,nomecliente,unidade FROM resellercontrol.contratos where nomecliente like 'n%';
UPDATE `resellercontrol`.`contratos` SET `nomecliente` = 'Bracell SP', `unidade` = 'Lwarcel' WHERE (`idcliente` = '47');

---- PARA CRIAR AS TABELAS E O BANCO DE DADOS PARA A APLICAÇÃO
CREATE DATABASE `resellercontrol` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
CREATE USER 'doxsys'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON resellercontrol.* TO 'doxsys'@'localhost';
show grants for 'doxsys'@'localhost';
ALTER TABLE `resellercontrol`.`mensagens` ADD COLUMN `status` VARCHAR(20) NOT NULL DEFAULT 'pendente';
ALTER TABLE `resellercontrol`.`pipeline` ADD COLUMN `dtapres` date DEFAULT NULL AFTER `dtacao`;
ALTER TABLE `resellercontrol`.`contratos` ADD COLUMN idproposta INT, ADD CONSTRAINT fk_contratos_propostas FOREIGN KEY (idproposta) REFERENCES propostas(idproposta);

CREATE TABLE mensagens (
    `id` INT NOT NULL AUTO_INCREMENT,
    `instancia` VARCHAR(32) NOT NULL,
    `telefone` VARCHAR(32) NOT NULL,
    `mensagem_id` VARCHAR(64) NOT NULL,
    `mensagem` TEXT NOT NULL COLLATE utf8mb4_unicode_ci,
    `tipo` VARCHAR(20) NOT NULL,  -- 'enviada' ou 'recebida'
    `data` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `dtcriac` DATE DEFAULT NULL,
    `idusuario` INT,
    `lida` BOOLEAN DEFAULT FALSE,
    `status` VARCHAR(20) NOT NULL DEFAULT 'pendente',
    PRIMARY KEY (`id`),
    FOREIGN KEY (idusuario) REFERENCES usuario(id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `kbfaq` (
  `idkbfaq` int NOT NULL AUTO_INCREMENT,
  `active` tinyint NOT NULL DEFAULT 1,
  `idusuario` int NOT NULL,
  `dtcriac` date DEFAULT NULL,
  `dtalter` date DEFAULT NULL,
  `accesslevel` int NOT NULL DEFAULT 2,
  `categoria` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `titulo` tinytext COLLATE utf8mb4_unicode_ci,
  `descricao` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`idkbfaq`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `equiptos` (
  `idequipto` int NOT NULL AUTO_INCREMENT,
  `active` tinyint NOT NULL DEFAULT 1,
  `idusuario` int NOT NULL,
  `dtcriac` date DEFAULT NULL,
  `dtalter` date DEFAULT NULL,
  `status` int NOT NULL DEFAULT 1,
  `usuario` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipto_id` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipto_tipo` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipto_nome` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipto_marca` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipto_modelo` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dtcompra` date DEFAULT NULL,
  `dtdesativ` date DEFAULT NULL,
  `motivodesativ` tinytext COLLATE utf8mb4_unicode_ci,
  `nfcompra` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `valor` decimal(12,2) DEFAULT 0,
  `useradmin` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pin` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descricao` tinytext COLLATE utf8mb4_unicode_ci,
  `observacao` tinytext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`idequipto`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `usuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `active` tinyint NOT NULL DEFAULT 1,
  `username` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sigla` varchar(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mobile` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `senha` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cli_hist` tinytext COLLATE utf8mb4_unicode_ci,
  `access` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
---- Criar um usuário Anonymous ID=0
INSERT INTO `resellercontrol`.`usuario` (`id`, `username`, `email`, `senha`, `access`) VALUES ('0', 'Anonymous', 'Anonymous', 'no_passwrod', '0');

CREATE TABLE `clientes` (
  `idcliente` int NOT NULL AUTO_INCREMENT,
  `active` tinyint NOT NULL DEFAULT 1,
  `idusuario` int NOT NULL,
  `dtalter` date DEFAULT NULL,
  `status` varchar(16) NULL DEFAULT `Dox-Prospect`,
  `nomecliente` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `unidade` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Matriz',
  `razaosocial` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cnpj` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inscrmunicipal` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inscrestadual` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `municipio` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pais` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `endereco` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `complemento` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cep` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telefone` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `emailnfe` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observacao` tinytext COLLATE utf8mb4_unicode_ci,
  `linkcadastro` int DEFAULT NULL,
  `linkpipeline` int DEFAULT NULL,
  `website` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`idcliente`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `contatos` (
  `idcontato` int NOT NULL AUTO_INCREMENT,
  `idcliente` int NOT NULL,
  `active` tinyint NOT NULL DEFAULT 1;
  `idusuario` int NOT NULL,
  `dtalter` date DEFAULT NULL,
  `emphasis` tinyint NOT NULL DEFAULT 1;
  `mailing` tinyint NOT NULL DEFAULT 0;
  `nomecontato` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mobile` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `departamento` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cargo` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bizrole` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `aniversario` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observacao` tinytext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`idcontato`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `propostas` (
  `idproposta` int NOT NULL AUTO_INCREMENT,
  `status` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `idusuario` int NOT NULL,
  `dtalter` date DEFAULT NULL,
  `vendedor` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nomecliente` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `descricao` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dataprop` datetime DEFAULT NULL,
  `idcliente` int DEFAULT NULL,
  `notas` tinytext COLLATE utf8mb4_unicode_ci,
  `idvendor` int NOT NULL,
  `idpipeline` int NOT NULL,
  `dtprovavel` datetime DEFAULT NULL,
  `forecast` int DEFAULT 0,
  `vlrsoft` decimal(12,2) DEFAULT 0,
  `vlrserv` decimal(12,2) DEFAULT 0,
  `horasprev` int DEFAULT 0,
  `periodo` int DEFAULT NULL,
  `arquivo` tinytext COLLATE utf8mb4_unicode_ci,
  `renovac` int DEFAULT 0,  # (1/0)
  PRIMARY KEY (`idproposta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `contratos` (
  `idcontrato` int NOT NULL AUTO_INCREMENT,
  `idusuario` int NOT NULL,
  `idproposta` int NOT NULL,
  `dtcriac` date DEFAULT NULL,
  `dtalter` date DEFAULT NULL,
  `idcliente` int NOT NULL,
  `nomecliente` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unidade` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `vendedor` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `produto` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `proposta` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dtproposta` date DEFAULT NULL,
  `pedido` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dtpedido` date DEFAULT NULL,
  `codcontrato` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `validadecontrato` date DEFAULT NULL,
  `duracaocontrato` int NOT NULL,
  `faturamento` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fatfrequencia` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `infratype` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `aplicacaotype` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `instanciatype` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `usersavancados` int NOT NULL,
  `usersregulares` int NOT NULL,
  `milregistros` int NOT NULL,
  `gbstorage` int NOT NULL,
  `powerbi` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `apisistema` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `suporte` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `horascontratadas` int NOT NULL,
  `horasentregues` int NOT NULL,
  `horasstatus` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bminstruc` tinytext COLLATE utf8mb4_unicode_ci,
  `nfinstruc` tinytext COLLATE utf8mb4_unicode_ci,
  `observacao` tinytext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`idcontrato`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `lista_opcoes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `lst` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `opt` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `msg` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `projetos` (
  `idprojeto` int NOT NULL AUTO_INCREMENT,
  `active` tinyint NOT NULL DEFAULT 1,
  `idclint` int NOT NULL,
  `idusuario` int NOT NULL,
  `dtcriac` date DEFAULT NULL,
  `dtalter` date DEFAULT NULL,
  `statusproj` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `projetonome` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prjinicplan` date DEFAULT NULL,
  `prjfimplan` date DEFAULT NULL,
  `prjinicreal` date DEFAULT NULL,
  `prjfimreal` date DEFAULT NULL,
  `propcodigo` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `propdata` date DEFAULT NULL,
  `pedidocodig` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pedidodata` date DEFAULT NULL,
  `oscodigo` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `osdata` date DEFAULT NULL,
  `horasprev` decimal(4,1) DEFAULT 0,
  `horasusds` decimal(4,1) DEFAULT 0,
  `responsnome` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tecniconome` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `kickoff` varchar(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `kickoffdata` date DEFAULT NULL,
  `testes` varchar(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `testesdata` date DEFAULT NULL,
  `homologacao` varchar(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `homologdata` date DEFAULT NULL,
  `dbookpwrbi` varchar(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dbkpwrbidt` date DEFAULT NULL,
  `treinamento` varchar(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `treinamdata` date DEFAULT NULL,
  `aceiteproj` varchar(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `aceitedata` date DEFAULT NULL,
  `faturado` varchar(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nfnumero` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nfdata` date DEFAULT NULL,
  `atestado` varchar(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `atestadodat` date DEFAULT NULL,
  `percentual` decimal(4,3) DEFAULT 0,
  `stakeholders` tinytext COLLATE utf8mb4_unicode_ci,
  `observacao` tinytext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`idprojeto`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `pessoal` (
  `idfunc` int NOT NULL AUTO_INCREMENT,
  `active` tinyint NOT NULL DEFAULT 1,
  `idusuario` int NOT NULL,
  `dtcriac` date DEFAULT NULL,
  `dtalter` date DEFAULT NULL,
  `statusrh` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dtadmiss` date DEFAULT NULL,
  `salrinic` decimal(8,2) DEFAULT 0,
  `salrtual` decimal(8,2) DEFAULT 0,
  `cargfunc` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dtdeslig` date DEFAULT NULL,
  `dtlimfer` date DEFAULT NULL,
  `nomefunc` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rgfunc` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cpffunc` varchar(14) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fonefixo` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fonecelr` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `emailpes` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dtnascim` date DEFAULT NULL,
  `escolari` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estadciv` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nomeconj` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dtnasccg` date DEFAULT NULL,
  `endereco` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bairro` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cidade` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` varchar(2) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cep` varchar(9) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `benefc` tinytext COLLATE utf8mb4_unicode_ci,
  `ferias` tinytext COLLATE utf8mb4_unicode_ci,
  `observacao` tinytext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`idfunc`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `credencial` (
  `idcredenc` int NOT NULL AUTO_INCREMENT,
  `active` tinyint NOT NULL DEFAULT 1,
  `idusuario` int NOT NULL,
  `dtcriac` date DEFAULT NULL,
  `dtalter` date DEFAULT NULL,
  `statenv` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dtimplantac` date DEFAULT NULL,
  `accesslevel` int NOT NULL DEFAULT 2,
  `cloudloc` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nomecliente` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ambiente` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `version` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `responsav` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `urlweb` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `logindocc` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `passwddocc` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `loginserv` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `passwdserv` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `loginapi` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `passwdapi` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `keyfile` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notas` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`idcredenc`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `financeiro` (
  `idfinanc` int NOT NULL AUTO_INCREMENT,
  `active` tinyint NOT NULL DEFAULT 1,
  `idusuario` int NOT NULL,
  `dtcriac` date DEFAULT NULL,
  `dtalter` date DEFAULT NULL,
  `dt_data` date DEFAULT NULL,
  `pago` tinyint NOT NULL DEFAULT 0,
  `dtpagto` date DEFAULT NULL,
  `faturado` tinyint NOT NULL DEFAULT 0,
  `dtfatur` date DEFAULT NULL,
  `valor` decimal(12,2) DEFAULT 0,
  `categoria` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `subcategor` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `benefic` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descricao` tinytext COLLATE utf8mb4_unicode_ci,
  `observacao` tinytext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`idfinanc`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `resellercontrol`.`pipeline` (
    `idpipeline` int NOT NULL AUTO_INCREMENT,
    `idusuario` int NOT NULL,
    `active` tinyint NOT NULL DEFAULT 1,
    `dtcriac` date DEFAULT NULL,
    `dtalter` date DEFAULT NULL,
    `idcliente` int NOT NULL,
    `prazo` date DEFAULT NULL,
    `acao` tinytext COLLATE utf8mb4_unicode_ci,
    `dtacao` date DEFAULT NULL,
    `dtapres` date DEFAULT NULL,
    `produto` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `vendedor` int NOT NULL,
    `status` varchar(12) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `oportunidade` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `historico` text COLLATE utf8mb4_unicode_ci,
    `facilit` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `decisor` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `concorrentes` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `prioridade` tinyint NOT NULL DEFAULT 0,
    `mercado` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `linkext` TINYTEXT COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`idpipeline`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `saldo` (
   `idsaldo` int NOT NULL AUTO_INCREMENT,
   `idusuario` int NOT NULL,
   `data` date DEFAULT NULL,
   `saldo` decimal(12,2) DEFAULT 0,
   `aplic` decimal(12,2) DEFAULT 0,
   `variac` decimal(12,2) DEFAULT 0,
   `conta` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
   `observacao` tinytext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`idsaldo`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `variables` (
   `idvar` int NOT NULL AUTO_INCREMENT,
   `idusuario` int NOT NULL,
   `dtalter` date DEFAULT NULL,
   `var` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
   `valor` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`idvar`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `log_actions` (
   `idlog` int NOT NULL AUTO_INCREMENT,
   `idusuario` int NOT NULL,
   `datahora` datetime DEFAULT NULL,
   `modulo` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
   `funcao` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
   `acao` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`idlog`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `versions` (
   `id` int NOT NULL AUTO_INCREMENT,
   `active` tinyint NOT NULL DEFAULT 1,
   `idusuario` int NOT NULL,
   `dtalter` date NOT NULL,
   `produto` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
   `version` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
   `nomecliente` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `bug` tinyint NOT NULL DEFAULT 0,
   `dtbug` date DEFAULT NULL,
   `descricao` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `whoid` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `chamado` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `prazofix` date DEFAULT NULL,
   `bugfix` tinyint NOT NULL DEFAULT 0,
   `dtfix` date DEFAULT NULL,
   `versionfix` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `webaccess` (
   `id` int NOT NULL AUTO_INCREMENT,
   `datahora` datetime NOT NULL,
   `usr_email` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `user_agent` varchar(96) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `ipaddr` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `referrer` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `language` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `host` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `full_path` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `httpmethod` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `querystr` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `notify` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


class Post(database.Model):
    data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
    foto_perfil = database.Column(database.String, nullable=False, default='default.jpg')
"""
