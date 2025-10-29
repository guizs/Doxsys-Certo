from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, HiddenField, \
                    BooleanField, TextAreaField, DateTimeField, IntegerField, SelectField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from resellercontrol.models import usuario
# from flask_login import current_user

mesdefault = '01-2025'
anodefault = '2025'

class FormEditarPessoal(FlaskForm):
    nomefunc = StringField('Nome do Funcionário', validators=[DataRequired(), Length(0, 64)])
    select_statusrh = SelectField(u'Status', validate_choice=False)
    select_estadciv = SelectField(u'Estado Civil', validate_choice=False)
    dtadmiss = DateField('Data de Admissão', format='%Y-%m-%d', validators=[Optional()])
    salrinic = DecimalField('Salário Inicial', places=2)
    salrtual = DecimalField('Salário Atual', places=2)
    cargfunc = StringField('Cargo / Função', validators=[Length(0, 64)])
    rgfunc = StringField('RG do Funcionário', validators=[Length(0, 16)])
    cpffunc = StringField('CPF do Funcionário', validators=[Length(0, 14)])
    dtdeslig = DateField('Data do Desligamento', format='%Y-%m-%d', validators=[Optional()])
    dtlimfer = DateField('Data Limite para Férias', format='%Y-%m-%d', validators=[Optional()])
    fonefixo = StringField('Telefone Fixo', validators=[Length(0, 32)])
    fonecelr = StringField('Telefone Celular', validators=[Length(0, 32)])
    emailpes = StringField('Email Pessoal', validators=[Length(0, 128), Email()])
    dtnascim = DateField('Data de Nascimento', format='%Y-%m-%d', validators=[DataRequired()])
    escolari = StringField('Escolaridade', validators=[Length(0, 32)])
    nomeconj = StringField('Nome do(a) cônjuge', validators=[Length(0, 64)])
    dtnasccg = DateField('Data de Nascimento do(a) cônjuge', format='%Y-%m-%d', validators=[Optional()])
    endereco = StringField('Endereço', validators=[Length(0, 128)])
    bairro = StringField('Bairro', validators=[Length(0, 32)])
    cidade = StringField('Município', validators=[Length(0, 32)])
    estado = StringField('Estado', validators=[Length(0, 2)])
    cep = StringField('CEP', validators=[Length(0, 9)])
    benefc = TextAreaField('Benefícios', validators=[Length(0, 255)])
    ferias = TextAreaField('Anotaçoes de férias', validators=[Length(0, 255)])
    observacao = TextAreaField('Observações (incluir notas sobre filhos)', validators=[Length(0, 255)])
    botao_submit_editarpessoal = SubmitField('Salvar dados do funcionário')

class FormEditarCredencial(FlaskForm):
    # nomecliente = StringField('Nome do Cliente', validators=[DataRequired(), Length(0, 64)])
    select_cliente = SelectField(u'Cliente - Unidade', validate_choice=False)
    select_status = SelectField(u'Status', validate_choice=False)
    select_cloudloc = SelectField(u'Local do servidor', validate_choice=False)
    dtimplantac = DateField('Data de Implantação', format='%Y-%m-%d', validators=[Optional()])
    accesslevel = IntegerField('Nível de acesso')
    ambiente = StringField('Nome do Ambiente', validators=[Length(0, 64)])
    version = StringField('Versão Software', validators=[Length(0, 16)])
    responsav = StringField('Técnico Responsável', validators=[Length(0, 64)])
    urlweb = StringField('URL WEB', validators=[Length(0, 255)])
    logindocc = StringField('Login DocControl', validators=[Length(0, 32)])
    passwddocc = StringField('Senha DocControl', validators=[Length(0, 32)])
    loginserv = StringField('Login de Serviço', validators=[Length(0, 32)])
    passwdserv = StringField('Senha de Serviço', validators=[Length(0, 32)])
    loginapi = StringField('Login para API', validators=[Length(0, 32)])
    passwdapi = StringField('Senha para API', validators=[Length(0, 32)])
    keyfile = StringField('Keyfile Path', validators=[Length(0, 64)])
    notas = TextAreaField('Notas gerais', validators=[Length(0, 1024)])
    botao_submit_editarcredenc = SubmitField('Salvar dados da credencial')

class FormEditarContrato(FlaskForm):
    select_produto = SelectField(u'Produto', validate_choice=False)
    select_vendor = SelectField(u'Vendedor', validate_choice=False)
    select_status = SelectField(u'Status', validate_choice=False)
    select_prop = SelectField('Proposta Número', coerce=int)
    proposta = StringField('Proposta Arquivo', validators=[Length(0, 64)])
    dtproposta = DateField('Data Proposta', format='%Y-%m-%d', validators=[DataRequired()])
    pedido = StringField('Pedido', validators=[Length(0, 64)])
    dtpedido = DateField('Data Pedido', format='%Y-%m-%d', validators=[DataRequired()])
    codcontrato = StringField('Cod.Contrato', validators=[Length(0, 45)])
    validadecontrato = DateField('Validade', format='%Y-%m-%d', validators=[DataRequired()])
    duracaocontrato = IntegerField('Duração')
    select_fatur = SelectField(u'Faturamento', validate_choice=False)
    select_frequenc = SelectField(u'Frequência do Faturamento', validate_choice=False)
    select_infra = SelectField(u'Tipo Infraestrutura', validate_choice=False)
    select_apptype = SelectField(u'Tipo Aplicação', validate_choice=False)
    select_instance = SelectField(u'Tipo Instância', validate_choice=False)
    usersavancados = IntegerField('Usuários Avançados')
    usersregulares = IntegerField('Usuários Regulares')
    milregistros = IntegerField('Milhares de Registros')
    gbstorage = IntegerField('Gb de Storage')
    select_pbi = SelectField(u'Power BI', validate_choice=False)
    select_api = SelectField(u'API do Sistema', validate_choice=False)
    select_supp = SelectField(u'Suporte Técnico', validate_choice=False)
    horascontratadas = IntegerField('Horas Contratadas')
    horasentregues = IntegerField('Horas Entregues')
    select_hrs = SelectField(u'Status das Horas', validate_choice=False)
    bminstruc = TextAreaField('Instruções para BM', validators=[Length(0, 254)])
    nfinstruc = TextAreaField('Instruções para NF', validators=[Length(0, 254)])
    observacao = TextAreaField('Observações sobre o contrato', validators=[Length(0, 254)])
    select_cliente = SelectField(u'Cliente - Unidade', validate_choice=False)
    botao_submit_editarcontrato = SubmitField('Salvar dados do contrato')

class FormEditarProjeto(FlaskForm):
    # idprojeto
    # idclint
    select_cliente = SelectField(u'Cliente - Unidade', validate_choice=False)
    select_status = SelectField(u'Status', validate_choice=False)
    projetonome = StringField('Nome do Projeto', validators=[Length(0, 64)])
    prjinicplan = DateField('Data do Início do Projeto', format='%Y-%m-%d', validators=[DataRequired()])
    prjfimplan = DateField('Data Prevista para o Final do Projeto', format='%Y-%m-%d', validators=[DataRequired()])
    prjinicreal = DateField('Data Real de Início do Projeto', format='%Y-%m-%d', validators=[Optional()])
    prjfimreal = DateField('Data Real Final do Projeto', format='%Y-%m-%d', validators=[Optional()])
    propcodigo = StringField('Proposta', validators=[Length(0, 64)])
    propdata = DateField('Data da Proposta', format='%Y-%m-%d', validators=[DataRequired()])
    pedidocodig = StringField('Pedido do Cliente', validators=[Length(0, 64)])
    pedidodata = DateField('Data do Pedido', format='%Y-%m-%d', validators=[DataRequired()])
    oscodigo = StringField('Ordem de Serviço', validators=[Length(0, 32)])
    osdata = DateField('Data da OS', format='%Y-%m-%d', validators=[Optional()])
    horasprev = DecimalField('Horas Previstas', places=1)
    horasusds = DecimalField('Horas Utilizadas', places=1)
    responsnome = StringField('Nome do Analista Responsável', validators=[Length(0, 64)])
    tecniconome = StringField('Nome do Técnico Responsável', validators=[Length(0, 64)])
    kickoff = SelectField(u'Kickoff', validate_choice=False)
    kickoffdata = DateField('Data do Kickoff', format='%Y-%m-%d', validators=[Optional()])
    testes = SelectField(u'Testes', validate_choice=False)
    testesdata = DateField('Data final do Teste', format='%Y-%m-%d', validators=[Optional()])
    homologacao = SelectField(u'Homologação', validate_choice=False)
    homologdata = DateField('Data da Homologação', format='%Y-%m-%d', validators=[Optional()])
    dbookpwrbi = SelectField(u'Databook/PowerBI', validate_choice=False)
    dbkpwrbidt = DateField('Entrega do Databook/PowerBI', format='%Y-%m-%d', validators=[Optional()])
    treinamento = SelectField(u'Treinamento', validate_choice=False)
    treinamdata = DateField('Data do Treinamento', format='%Y-%m-%d', validators=[Optional()])
    aceiteproj = SelectField(u'Aceite do projeto', validate_choice=False)
    aceitedata = DateField('Data do Aceite', format='%Y-%m-%d', validators=[Optional()])
    faturado = SelectField(u'Faturado', validate_choice=False)
    nfnumero = StringField('NFe número', validators=[Length(0, 10)])
    nfdata = DateField('Data da NF', format='%Y-%m-%d', validators=[Optional()])
    atestado = SelectField(u'Atestado', validate_choice=False)
    atestadodat = DateField('Data do Atestado', format='%Y-%m-%d', validators=[Optional()])
    stakeholders = TextAreaField('Principais Stakeholders', validators=[Length(0, 254)])
    observacao = TextAreaField('Observações sobre o projeto', validators=[Length(0, 254)])
    botao_submit_editarprojeto = SubmitField('Salvar dados do projeto')
    # percentual - náo entrar - calcular

class FormEditarCliente(FlaskForm):
    nomecliente = StringField('Nome do cliente', validators=[DataRequired(), Length(0, 64)])
    unidade = StringField('Unidade', validators=[DataRequired(), Length(0, 45)])
    status = SelectField(u'Status', validate_choice=False)
    razaosocial = StringField('Razão Social', validators=[Length(0, 64)])
    cnpj = StringField('CNPJ', validators=[Length(0, 45)])
    inscrmunicipal = StringField('Inscrição Municipal', validators=[Length(0, 45)])
    inscrestadual = StringField('Inscrição Estadual', validators=[Length(0, 45)])
    municipio = StringField('Cidade', validators=[Length(0, 45)])
    estado = StringField('UF', validators=[Length(0, 20)])
    pais = StringField('País', validators=[Length(0, 20)])
    endereco = StringField('Endereço', validators=[Length(0, 128)])
    complemento = StringField('Complemento', validators=[Length(0, 64)])
    cep = StringField('CEP', validators=[Length(0, 10)])
    telefone = StringField('Telefone Principal', validators=[Length(0, 45)])
    emailnfe = StringField('E-Mail p/ NFe', validators=[Length(0, 64)])
    linkcadastro = StringField('ID no Cadastro', default=0)
    linkpipeline = StringField('ID no Pipeline', default=0)
    website = StringField('Website', validators=[Length(0, 128)])
    observacao = TextAreaField('Observações sobre o cliente', validators=[Length(0, 254)])
    botao_submit_editarcliente = SubmitField('Salvar dados do cliente')
    # def validate_cnpj(self, cnpj):
    #     cliente = ClientesDB.query.filter_by(cnpj=cnpj.data).first()
    #     if cliente:
    #         raise ValidationError('CNPJ já cadastrado! Cadastre outro CNPJ.')

class FormEditarContato(FlaskForm):
    nomecontato = StringField('Nome de contato', validators=[DataRequired(), Length(0, 64)])
    mobile = StringField('Telefone Celular', validators=[Length(0, 45)])
    phone = StringField('Telefone Fixo', validators=[Length(0, 45)])
    email = StringField('E-Mail', validators=[Length(0, 64)])
    departamento = StringField('Departamento', validators=[Length(0, 45)])
    cargo = StringField('Cargo', validators=[Length(0, 45)])
    bizrole = StringField('Business Role', validators=[Length(0, 45)])
    observacao = TextAreaField('Observações sobre o contato', validators=[Length(0, 255)])
    emphasis = BooleanField('Destaque?')
    mailing = BooleanField('Mailing?')
    aniversario = StringField('Aniversario', validators=[Length(0, 16)])
    botao_submit_editarcontato = SubmitField('Salvar dados do contato')

class FormSearchCli(FlaskForm):
    nomecliente = StringField('Nome do cliente', validators=[Length(0, 64)])
    unidade = StringField('Unidade', validators=[Length(0, 45)])
    razaosocial = StringField('Razão Social', validators=[Length(0, 64)])
    cnpj = StringField('CNPJ', validators=[Length(0, 45)])
    inscrmunicipal = StringField('Inscrição Municipal', validators=[Length(0, 45)])
    inscrestadual = StringField('Inscrição Estadual', validators=[Length(0, 45)])
    municipio = StringField('Cidade', validators=[Length(0, 45)])
    estado = StringField('UF', validators=[Length(0, 20)])
    pais = StringField('País', validators=[Length(0, 20)])
    endereco = StringField('Endereço', validators=[Length(0, 128)])
    complemento = StringField('Complemento', validators=[Length(0, 64)])
    cep = StringField('CEP', validators=[Length(0, 10)])
    telefone = StringField('Telefone Principal', validators=[Length(0, 45)])
    emailnfe = StringField('E-Mail p/ NFe', validators=[Length(0, 64)])
    website = StringField('Website', validators=[Length(0, 128)])
    observacao = TextAreaField('Observações sobre o cliente', validators=[Length(0, 255)])
    botao_submit_search_cli = SubmitField('Buscar cliente')

class FormSearchCont(FlaskForm):
    nomecontato = StringField('Nome de contato', validators=[Length(0, 64)])
    mobile = StringField('Telefone Celular', validators=[Length(0, 45)])
    phone = StringField('Telefone Fixo', validators=[Length(0, 45)])
    email = StringField('E-Mail', validators=[Length(0, 64)])
    departamento = StringField('Departamento', validators=[Length(0, 45)])
    cargo = StringField('Cargo', validators=[Length(0, 45)])
    bizrole = StringField('Business Role', validators=[Length(0, 45)])
    observacao = TextAreaField('Observações sobre o contato', validators=[Length(0, 255)])
    botao_submit_search_cont = SubmitField('Buscar contato')

class FormEditarPipeline(FlaskForm):
    prazo = DateField('Prazo', format='%Y-%m-%d', validators=[DataRequired()])
    acao = TextAreaField('Ação', validators=[Length(0, 255)])
    dtacao = DateField('Data da Açao', format='%Y-%m-%d', validators=[DataRequired()])
    dtapres = DateField('Apresentaçao', format='%Y-%m-%d', validators=[Optional()])
    produto = SelectField(u'Produto', validate_choice=False)
    vendedor = SelectField(u'Vendedor', validate_choice=False)
    status = SelectField(u'Status', validate_choice=False)
    oportunidade = StringField('Oportunidade', validators=[Length(0, 128)])
    historico = TextAreaField('Histórico', validators=[Length(0, 65536)])
    facilit = StringField('Facilitador', validators=[Length(0, 16)])
    decisor = StringField('Decisor', validators=[Length(0, 16)])
    concorrentes = StringField('Concorrentes', validators=[Length(0, 64)])
    linkext = StringField('Link', validators=[Length(0, 255)])
    prioridade = BooleanField('Prioridade?')
    mercado = SelectField(u'Mercado', validate_choice=False)
    select_cliente = SelectField(u'Cliente - Unidade', validate_choice=False)
    botao_submit_editarpipeline = SubmitField('Salvar dados da oportunidade')

class FormCriarConta(FlaskForm):
    username = StringField('Nome de usuário', validators=[DataRequired(), Length(0, 64)])
    sigla = StringField('Sigla', validators=[Length(0, 3)])
    role = StringField('Funções', validators=[Length(0, 64)])
    email = StringField('E-Mail', validators=[DataRequired(), Length(0, 64), Email()])
    mobile = StringField('Telefone Celular', validators=[DataRequired(), Length(0, 45)])
    phone = StringField('Telefone Fixo', validators=[Length(0, 45)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirmação da senha', validators=[DataRequired(), EqualTo('senha')])
    access = 0
    botao_submit_criarconta = SubmitField('Criar conta')

    def validate_email(self, email):
        utilizador = usuario.query.filter_by(email=email.data).first()
        if utilizador:
            raise ValidationError('E-mail já cadastrado! Cadastre-se com outro email ou faça login para continuar.')

    def validate_username(self, username):
        utilizador = usuario.query.filter_by(username=username.data).first()
        if utilizador:
            raise ValidationError('Nome já cadastrado! Cadastre-se com outro nome ou faça login para continuar.')

class FormEditarConta(FlaskForm):
    username = StringField('Nome de usuário', validators=[DataRequired(), Length(3, 64)])
    sigla = StringField('Sigla', validators=[DataRequired(), Length(0, 3)])
    role = StringField('Funções', validators=[Length(0, 64)])
    email = StringField('E-Mail', validators=[DataRequired(), Length(3, 64), Email()])
    mobile = StringField('Telefone Celular', validators=[Length(0, 45)])
    phone = StringField('Telefone Fixo', validators=[Length(0, 45)])
    senha = PasswordField('Senha', validators=[Length(0, 20)])
    confirmacao_senha = PasswordField('Confirmação da senha', validators=[EqualTo('senha')])
    access = StringField('Access Level')
    botao_submit_editarconta = SubmitField('Salvar dados do usuário')

class FormLogin(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar dados de acesso')
    botao_submit_login = SubmitField('Fazer login')

class FormAddProp(FlaskForm):
    status = SelectField(u'Status', validate_choice=False)
    vendedor = StringField('Vendedor', validators=[Length(0, 32)])
    nomecliente = StringField('Cliente', validators=[Length(0, 45)])
    descricao = StringField('Descrição', validators=[Length(0, 128)], default='PROP ou CR ?')
    notas = TextAreaField('Notas', validators=[Length(0, 250)])
    idvendor = SelectField(u'Vendedor', validate_choice=False)
    dtprovavel = DateField('Fechamento:', format='%Y-%m-%d', validators=[DataRequired()])
    forecast = IntegerField('Forecast(%):')
    vlrsoft = DecimalField('Vlr Software:', places=2, validators=None)
    vlrserv = DecimalField('Vlr Serviços:', places=2, validators=None)
    horasprev = IntegerField('Hs Previstas:', validators=None)
    periodo = IntegerField('Período:', validators=None)
    arquivo = StringField('Arquivo', validators=[Length(0, 255)], default='C:\\DOX-COML\\CLIENTES\\')
    renovac = BooleanField('Renovaçao?')
    botao_submit_addprop = SubmitField('GRAVAR')
    # select_orderby = SelectField(u'Ordem')
    # select_orderby = SelectField('Ordem', choices=[('n', 'Ordem por ID'), ('c', 'Ordem por Cliente')])

class FormRelatScope(FlaskForm):
    select_tipo = SelectField(u'Relatorio', default=mesdefault, validate_choice=False)
    select_tag = StringField('Busca:', validators=[Length(0, 32)])
    select_bool = BooleanField('Prioridade/Mailing?')
    botao_submit_relattag = SubmitField('OK')

class FormFinancCfcs(FlaskForm):
    select_cfcs = SelectField(u'Escopo', validate_choice=False)
    select_mes = SelectField(u'Mês', default='01-'+anodefault, validate_choice=False)
    select_mesfim = SelectField(u'Até', default='12-'+anodefault, validate_choice=False)
    select_stat = SelectField(u'Status', default='t', validate_choice=False)
    select_tipo = SelectField(u'Tipo', default='t', validate_choice=False)
    botao_submit_financcfcs = SubmitField('OK')

class FormScopeTecn(FlaskForm):
    select_mes = SelectField(u'Mês', default='01-'+anodefault, validate_choice=False)
    botao_submit_scopetecn = SubmitField('OK')

class FormRelatProp(FlaskForm):
    select_vendor = SelectField(u'Vendedor:', validate_choice=False)
    select_status = SelectField(u'Status:', validate_choice=False)
    busca_texto = StringField('Busca:', validators=[Length(0, 32)])
    forecast = IntegerField('Forecast(%):', validators=None)
    renovac = BooleanField('Renovação?')
    dataini = DateField('Início:', format='%Y-%m-%d', validators=[DataRequired()])
    datafim = DateField('Fim:', format='%Y-%m-%d', validators=[DataRequired()])
    botao_submit_relatprop = SubmitField('OK')

class FormUsersScope(FlaskForm):
    select_user = SelectField(u'Usuário', default='TODOS', validate_choice=False)
    select_mes = SelectField(u'Mês', default=mesdefault, validate_choice=False)
    select_mesfim = SelectField(u'Até', default=mesdefault, validate_choice=False)
    botao_submit_usersscope = SubmitField('OK')

class FormFinancScope(FlaskForm):
    select_clifrn = SelectField(u'Client/Forn', default='W3K Tecnologia', validate_choice=False)
    select_mes = SelectField(u'Mês', default='01-'+anodefault, validate_choice=False)
    select_mesfim = SelectField(u'Até', default='12-'+anodefault, validate_choice=False)
    select_stat = SelectField(u'Status', default='t', validate_choice=False)
    select_tipo = SelectField(u'Tipo', default='t', validate_choice=False)
    botao_submit_financscope = SubmitField('OK')

class FormPipelineScope(FlaskForm):
    select_vendr = SelectField(u'Vendedor', validate_choice=False)
    select_stat = SelectField(u'Status', default='t', validate_choice=False)
    select_mkt = SelectField(u'Mercado', default='t', validate_choice=False)
    select_prd = SelectField(u'Produto', default='t', validate_choice=False)
    botao_submit_pipescope = SubmitField('OK')

class FormFinancRealiz(FlaskForm):
    select_mes = SelectField(u'Mês', default='11-2022', validate_choice=False)
    select_tipo = SelectField(u'Tipo', default='t', validate_choice=False)
    busca = StringField('Busca:', validators=[Length(0, 32)])
    botao_submit_financrealiz = SubmitField('OK')

class FormFinancResult(FlaskForm):
    select_mes = SelectField(u'Mês', default='01-2022', validate_choice=False)
    select_mesfim = SelectField(u'Até', default='12-2022', validate_choice=False)
    botao_submit_financresult = SubmitField('OK')

class FormFinancEdit(FlaskForm):
    tipo = StringField('Receita/Despesa:', validators=[Length(0, 1)])
    dt_data = DateField('Data:', format='%Y-%m-%d', validators=[DataRequired()], render_kw={"title": "Data prevista para o pagamento"})
    dtpagto = DateField('Pagto:', format='%Y-%m-%d', validators=[Optional()], render_kw={"title": "Data efetiva do pagamento"})
    dtfatur = DateField('Faturado:', format='%Y-%m-%d', validators=[Optional()], render_kw={"title": "Data em que foi faturado (lançamento)"})
    categoria = SelectField(u'Categoria:', validate_choice=False)
    subcategor = SelectField(u'Sub-Categoria:', validate_choice=False)
    benefic = SelectField('Cli_For:', validate_choice=False, render_kw={"title": "Cliente ou Fornecedor"})
    valor = DecimalField('Valor:', places=2)
    descricao = StringField('Descrição:', validators=[Length(0, 255)])
    observacao = StringField('Observação:', validators=[Length(0, 255)])
    frequencia = SelectField(u'Repetir:', validate_choice=False)
    parcelas = IntegerField('Parcelas:', default=1)
    botao_submit_financedit = SubmitField(' OK ')

class FormFinancClose(FlaskForm):
    dtpagto = DateField('Pagamento:', format='%Y-%m-%d', validators=[Optional()])
    botao_submit_financlose = SubmitField(' OK ')

class FormAddSaldo(FlaskForm):
    saldo = DecimalField('Saldo:', places=2)
    aplic = DecimalField('Aplicação:', places=2)
    variac = DecimalField('Aplicado:', places=2)
    conta = StringField('Conta:', validators=[Length(0, 32)])
    observacao = StringField('Descrição:', validators=[Length(0, 255)])
    botao_submit_addsaldo = SubmitField(' OK ')

class FormEditCfg(FlaskForm):
    variable = StringField('Variável:', validators=[Length(0, 16)])
    varvalue = StringField('Valor:', validators=[Length(0, 64)])
    botao_submit_editcfg = SubmitField(' OK ')

class FormAddLstOpc(FlaskForm):
    lst = SelectField('Lista:', validate_choice=False)
    opt = StringField('Valor:', validators=[Length(0, 32)])
    msg = StringField('Mensagem:', validators=[Length(0, 32)])
    botao_submit_addlstopc = SubmitField(' OK ')

class FormEditarEquiptos(FlaskForm):
    equipto_tipo = SelectField(u'Tipo', validate_choice=False)
    usuario = StringField(u'Usuário', validators=[DataRequired(), Length(3, 64)])
    select_status = SelectField(u'Status', validate_choice=False)
    equipto_nome = StringField(u'Nome', validators=[DataRequired(), Length(3, 32)])
    equipto_marca = StringField(u'Marca', validators=[Length(0, 32)])
    equipto_modelo = StringField(u'Modelo', validators=[Length(0, 64)])
    equipto_id = StringField(u'ID/ServiceTag/Serial Number', validators=[DataRequired(), Length(1, 32)])
    dtcompra = DateField('Data Compra', format='%Y-%m-%d')
    nfcompra = StringField('Nota Fiscal', validators=[Length(0, 32)])
    descricao = TextAreaField('Descrição', validators=[Length(0, 255)])
    useradmin = StringField('User Admin', validators=[Length(0, 32)])
    password = StringField('Password', validators=[Length(0, 32)])
    pin = StringField('PIN', validators=[Length(0, 16)])
    observacao = TextAreaField('Observação', validators=[Length(0, 255)])
    dtdesativ = DateField('Desativação', format='%Y-%m-%d')
    motivodesativ = TextAreaField('Motivo', validators=[Length(0, 255)])
    botao_submit_editar_equiptos = SubmitField('Salvar Equipamento')


class FormEditarKBFaq(FlaskForm):
    # idkbfaq = HiddenField()
    accesslevel = IntegerField('Nível de acesso')
    categoria = SelectField(u'Categoria', validate_choice=False)
    titulo = TextAreaField('Titulo / Pergunta', validators=[Length(0, 255)])
    descricao = TextAreaField('Descrição / Resposta', validators=[Length(0, 65536)])
    botao_submit_editar_kbfaq = SubmitField('Salvar registro')

class FormApiCall(FlaskForm):
    method = SelectField('Metodo:', validate_choice=False)
    scope = SelectField('Escopo:', validate_choice=False)
    useremail = StringField('Usuário', validators=[Length(0, 128), Email(), Optional()])
    values = StringField('Valores:', validators=[Length(0, 32)])
    botao_submit_apicall = SubmitField(' OK ')

class FormVersionEdit(FlaskForm):
    produto = SelectField(u'Produto', validate_choice=False, render_kw={"title": "Nome do produto"})
    version = StringField('Versão', validators=[DataRequired(), Length(0, 16)], render_kw={"title": "Código da versão"})
    nomecliente = StringField('Cliente', validators=[Optional(), Length(0, 64)], render_kw={"title": "Nome do cliente"})
    bug = BooleanField('Bug?', render_kw={"title": "Foi detectado um bug?"})
    dtbug = DateField('Data Bug', format='%Y-%m-%d', validators=[Optional()], render_kw={"title": "Data do Bug"})
    descricao = TextAreaField('Descrição', validators=[Optional(), Length(0, 65536)], render_kw={"title": "Descrição do caso"})
    whoid = SelectField('Quem identificou', validate_choice=False)
    chamado = StringField('Chamado', validators=[Optional(), Length(0, 16)], render_kw={"title": "Número do chamado aberto"})
    prazofix = DateField('Prazo', format='%Y-%m-%d', validators=[Optional()], render_kw={"title": "Prazo para conserto"})
    bugfix = BooleanField('Bug fixed?', render_kw={"title": "O Bug foi arrumado?"})
    dtfix = DateField('Data conserto', format='%Y-%m-%d', validators=[Optional()], render_kw={"title": "Data em que o Bug foi arrumado"})
    versionfix = StringField('Nova Versão', validators=[Optional(), Length(0, 16)], render_kw={"title": "Versão em que o Bug foi arrumado"})
    botao_submit_editarversao = SubmitField('Salvar dados')

