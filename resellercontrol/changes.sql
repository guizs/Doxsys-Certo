
-- DEPLOY EM PRODUÇÃO EM 22/04/2025
ALTER TABLE `resellercontrol`.`kbfaq` ADD COLUMN `accesslevel` int NOT NULL DEFAULT 2;

-- DEPLOY EM PRODUÇÃO EM 19/04/2025
CRIAR TABELA KBFAQ
Incluir campo em propostas:
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `arquivo` tinytext COLLATE utf8mb4_unicode_ci;
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('KBFaqCategor', 'Comercial', 'Comercial');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('KBFaqCategor', 'Técnico', 'Técnico');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('KBFaqCategor', 'Greendocs', 'Greendocs');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('KBFaqCategor', 'Develop', 'Develop');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('KBFaqCategor', 'Infraestrutura', 'Infraestrutura');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('KBFaqCategor', 'Linux', 'Linux');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('KBFaqCategor', 'Microsoft', 'Microsoft');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('KBFaqCategor', 'Google', 'Google');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('KBFaqCategor', 'Oracle', 'Oracle');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('KBFaqCategor', 'Amazon', 'Amazon');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('KBFaqCategor', 'Azure', 'Azure');

-- DEPLOY EM PRODUÇÃO EM 25/10/2024
ALTER TABLE `resellercontrol`.`usuario` ADD COLUMN `role` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL AFTER `sigla`;
-- DEPLOY EM PRODUÇÃO EM 10/11/2023
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `horasprev` int DEFAULT 0;

-- DEPLOY EM PRODUÇÃO EM 08/08/2023
ALTER TABLE `resellercontrol`.`usuario` ADD COLUMN `sigla` varchar(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL AFTER `username`;

-- DEPLOY EM PRODUÇÃO EM 01/08/2023
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `idvendor` int NOT NULL;
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `idpipeline` int NOT NULL;
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `dtprovavel` datetime DEFAULT NULL;
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `forecast` int DEFAULT 0;
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `vlrsoft` decimal(12,2) DEFAULT 0;
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `vlrserv` decimal(12,2) DEFAULT 0;
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `periodo` int DEFAULT 0;
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `renovac` int DEFAULT 0;

-- DEPLOY EM PRODUÇÃO EM 26/07/2023
INSERT INTO `resellercontrol`.`variables` (`idusuario`, `dtalter`, `var`, `valor`) VALUES ('1', '2023-07-26', 'extLink', 'https://br01.greendocs.net');
ALTER TABLE `resellercontrol`.`pipeline` ADD COLUMN `linkext` TINYTEXT NULL COLLATE utf8mb4_unicode_ci DEFAULT NULL AFTER `mercado`;
ALTER TABLE `resellercontrol`.`contatos` ADD COLUMN `mailing` TINYINT NOT NULL DEFAULT 0 AFTER emphasis;

-- DEPLOY EM PRODUÇÃO EM 25/07/2023
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPipe','Ativo','Ativo');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPipe','Cliente','Cliente');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPipe','Hold','Hold');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPipe','Lead','Lead');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPipe','W3K','W3K');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPipe','Comprou','Comprou');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPipe','Legado','Legado');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Produto','Serviço','Serviço');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Engineering','Engineering');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Corporate','Corporate');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Pulp-Paper','Pulp-Paper');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Mining','Mining');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Chemical','Chemical');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Petrochemical','Petrochemical');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Steel','Steel');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Facilities','Facilities');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Banking','Banking');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Retail','Retail');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Food-Drug','Food-Drug');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Manufacturing','Manufacturing');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Natural-Resources','Natural-Resources');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Government','Government');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Cooperativo','Cooperativo');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Mercado','Sucroalcooleiro','Sucroalcooleiro');

CREATE TABLE `resellercontrol`.`pipeline` (
    `idpipeline` int NOT NULL AUTO_INCREMENT,
    `idusuario` int NOT NULL,
    `active` tinyint NOT NULL DEFAULT 1,
    `dtcriac` date DEFAULT NULL,
    `dtalter` date DEFAULT NULL,
    `idcliente` int NOT NULL,
    `prazo` date DEFAULT NULL,
    `acao` TINYTEXT COLLATE utf8mb4_unicode_ci,
    `dtacao` date DEFAULT NULL,
    `produto` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `vendedor` int NOT NULL,
    `status` varchar(12) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `oportunidade` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `historico` TEXT COLLATE utf8mb4_unicode_ci,
    `facilit` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `decisor` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `concorrentes` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `prioridade` tinyint NOT NULL DEFAULT 0,
    `mercado` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`idpipeline`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- DEPLOY EM PRODUÇÃO EM 22/07/2023
ALTER TABLE `resellercontrol`.`contatos` ADD COLUMN `idusuario` int NOT NULL;
ALTER TABLE `resellercontrol`.`contatos` ADD COLUMN `dtalter` date DEFAULT NULL;
ALTER TABLE `resellercontrol`.`clientes` ADD COLUMN `idusuario` int NOT NULL;
ALTER TABLE `resellercontrol`.`clientes` ADD COLUMN `dtalter` date DEFAULT NULL;
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `idusuario` int NOT NULL;
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `dtalter` date DEFAULT NULL;
ALTER TABLE `resellercontrol`.`usuario` ADD COLUMN `cli_hist` tinytext NULL DEFAULT NULL COLLATE utf8mb4_unicode_ci;

-- DEPLOY EM PRODUÇÃO EM 20/07/2023
ALTER TABLE `resellercontrol`.`contatos` ADD COLUMN `emphasis` TINYINT NOT NULL DEFAULT 1;
ALTER TABLE `resellercontrol`.`contatos` ADD COLUMN `aniversario` VARCHAR(16) NULL DEFAULT NULL;
ALTER TABLE `resellercontrol`.`clientes` ADD COLUMN `status` VARCHAR(16) NULL DEFAULT NULL AFTER `active`;
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusCli','Prospect','Prospect');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusCli','Client','Client');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusCli','Parceiro','Parceiro');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusCli','Dox-Prospect','Dox-Prospect');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusCli','Cadastro','Cadastro');

-- DEPLOY EM PRODUÇÃO EM 24/05/23
ALTER TABLE `resellercontrol`.`contratos` ADD COLUMN `vendedor` VARCHAR(32) NULL DEFAULT NULL AFTER `unidade`;
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Vendedor','Indefinido','Indefinido');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Vendedor','Compartilhado','Compartilhado');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Vendedor','Julio','Julio');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Vendedor','Alexandre','Alexandre');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Vendedor','Bairon','Bairon');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('Vendedor','Flavia','Flavia');
UPDATE `resellercontrol`.`contratos` SET `vendedor` = 'Indefinido' WHERE idcontrato>=1;

-- DEPLOY EM PRODUÇÃO EM 22/12
CREATE TABLE `log_actions` (
   `idlog` int NOT NULL AUTO_INCREMENT,
   `idusuario` int NOT NULL,
   `datahora` datetime DEFAULT NULL,
   `modulo` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
   `funcao` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
   `acao` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`idlog`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- DEPLOY EM PRODUĆÃO EM 15/12
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `vendedor` VARCHAR(32) NULL DEFAULT NULL AFTER `status`;
UPDATE `resellercontrol`.`propostas` SET `vendedor` = 'Indefinido' WHERE idproposta>=1;
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `notas` tinytext NULL DEFAULT NULL COLLATE utf8mb4_unicode_ci;

-- DEPLOY EM PRODUĆÃO EM 14/12
ALTER TABLE `resellercontrol`.`propostas` ADD COLUMN `status` VARCHAR(32) NULL DEFAULT NULL AFTER `idproposta`;
UPDATE `resellercontrol`.`propostas` SET `status` = 'Vencida' WHERE idproposta>=1;
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPrp','Aberta','Aberta');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPrp','Fechada','Fechada');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPrp','Negociando','Negociando');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPrp','Aguardando','Aguardando');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPrp','Vencida','Vencida');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPrp','Perdida','Perdida');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('StatusPrp','Indefinida','Indefinida');

-- DEPLOY EM PRODUĆÃO EM 06/12
ALTER TABLE `resellercontrol`.`financeiro`
ADD COLUMN `faturado` TINYINT NOT NULL DEFAULT '0' AFTER `dtpagto`,
ADD COLUMN `dtfatur` DATE NULL DEFAULT NULL AFTER `faturado`;
UPDATE `resellercontrol`.`financeiro` SET `faturado` = 1, `dtfatur` = `dtpagto` WHERE `pago` = 1 and idfinanc >= 1;

-- DEPLOY EM PRODUĆÃO EM 02/12
CREATE TABLE `variables` (
   `idvar` int NOT NULL AUTO_INCREMENT,
   `idusuario` int NOT NULL,
   `dtalter` date DEFAULT NULL,
   `var` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
   `valor` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`idvar`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `resellercontrol`.`variables` (`idusuario`,`dtalter`,`var`,`valor`) VALUES (1,'2022-12-02','Currency','R$');

-- DEPLOY EM PRODUĆÃO EM 29/11
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
INSERT INTO `resellercontrol`.`saldo` (`idusuario`,`data`,`saldo`,`aplic`,`variac`,`conta`,`observacao`) VALUES (1,'2022-11-29',67719.49,206718.48,0,'ITAU-1669-390146','Primeira inclusão do saldo da conta do Itaú');

-- DEPLOY EM PRODUĆÃO EM 28/11
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('FatFreq','Unico','Unico');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('FatFreq','Semanal','Semanal');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`,`opt`,`msg`) VALUES ('FatFreq','Quinzenal','Quinzenal');

-- DEPLOY EM PRODUĆÃO EM 15/11
CREATE TABLE `financeiro` (
  `idfinanc` int NOT NULL AUTO_INCREMENT,
  `active` tinyint NOT NULL DEFAULT 1,
  `idusuario` int NOT NULL,
  `dtcriac` date DEFAULT NULL,
  `dtalter` date DEFAULT NULL,
  `dt_data` date DEFAULT NULL,
  `pago` tinyint NOT NULL DEFAULT 0,
  `dtpagto` date DEFAULT NULL,
  `valor` decimal(12,2) DEFAULT 0,
  `categoria` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `subcategor` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `benefic` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descricao` tinytext COLLATE utf8mb4_unicode_ci,
  `observacao` tinytext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`idfinanc`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE `resellercontrol`.`lista_opcoes`
CHANGE COLUMN `opt` `opt` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci' NULL DEFAULT NULL ;
-- IMPORTAR ARQUIVO OPCOES.SQL
-- IMPORTAR ARQUIVO FINANCEIRO.SQL


-- DEPLOY EM PRODUĆÃO EM 07/11
ALTER TABLE `resellercontrol`.`credencial`
CHANGE COLUMN `notas` `notas` VARCHAR(1024) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci' NULL DEFAULT NULL ;

-- DEPLOY EM PRODUĆÃO EM 02/11
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('StatusCrd', 'ativo', 'Ativo');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('StatusCrd', 'inativo', 'Inativo');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('CloudLoc', 'Cloud-W3K', 'Cloud-W3K');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('CloudLoc', 'Cloud-DOX', 'Cloud-DOX');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('CloudLoc', 'On-Premises', 'On-Premises');

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
  `notas` tinytext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`idcredenc`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- DEPLOY EM PRODUĆÃO EM 01/11
ALTER TABLE `resellercontrol`.`projetos` ADD COLUMN `horasprev` DECIMAL(4,1) DEFAULT 0;
ALTER TABLE `resellercontrol`.`projetos` ADD COLUMN `horasusds` DECIMAL(4,1) DEFAULT 0;

-- DEPLOY EM PRODUĆÃO EM 25/10
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('EstCivil', 'Solteiro(a)', 'Solteiro(a)');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('EstCivil', 'Casado(a)', 'Casado(a)');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('EstCivil', 'Divorciado(a)', 'Divorciado(a)');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('EstCivil', 'Separado(a)', 'Separado(a)');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('EstCivil', 'Viuvo(a)', 'Viuvo(a)');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('StatusRH', 'ativo', 'Ativo');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('StatusRH', 'inativo', 'Inativo');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('StatusRH', 'estagio', 'Estagio');

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

--- DEPLOY EM PRODUĆÃO EM 17/10
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('StatusP', 'ativo', 'Ativo');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('StatusP', 'final', 'Finalizado');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('StatusP', 'aceito', 'Aceito');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('SimNaoNA', 'Sim', 'Sim');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('SimNaoNA', 'Não', 'Não');
INSERT INTO `resellercontrol`.`lista_opcoes` (`lst`, `opt`, `msg`) VALUES ('SimNaoNA', 'NA', 'Não se Aplica');

--- DEPLOY EM PRODUĆÃO EM 17/10
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

-- DEPLOY EM PRODUĆÃO EM 01/10
ALTER TABLE `resellercontrol`.`clientes` ADD COLUMN `active` TINYINT NOT NULL DEFAULT 1;
ALTER TABLE `resellercontrol`.`contatos` ADD COLUMN `active` TINYINT NOT NULL DEFAULT 1;
