--------------------------------------------------------------------------------

-- CREATE TABLES

CREATE DATABASE ufesdelivery;


USE ufesdelivery;


CREATE TABLE IF NOT EXISTS estado (
    cd_estado   INTEGER NOT NULL AUTO_INCREMENT
    , cd_uf     CHAR(2) NOT NULL
    , ds_estado VARCHAR(100) NOT NULL

    , UNIQUE(cd_uf)

    , CONSTRAINT pk_estado
        PRIMARY KEY (cd_estado)
);


CREATE TABLE IF NOT EXISTS cidade (
    cd_cidade   INTEGER NOT NULL AUTO_INCREMENT
    , cd_estado INTEGER NOT NULL
    , no_cidade VARCHAR(100) NOT NULL

    , CONSTRAINT pk_cidade
        PRIMARY KEY (cd_cidade)

    , CONSTRAINT fk_cidade_estado
        FOREIGN KEY (cd_estado)
            REFERENCES estado(cd_estado)
);


CREATE TABLE IF NOT EXISTS endereco (
    cd_endereco     INTEGER NOT NULL AUTO_INCREMENT
    , cd_cidade     INTEGER
    , no_logradouro VARCHAR(100) NOT NULL
    , no_bairro     VARCHAR(100) NOT NULL
    , ds_numero     VARCHAR(10)
    , nu_cep        CHAR(8)

    , CONSTRAINT pk_endereco
        PRIMARY KEY (cd_endereco)

    , CONSTRAINT fk_endereco_cidade
        FOREIGN KEY (cd_cidade)
            REFERENCES cidade(cd_cidade)
);


CREATE TABLE IF NOT EXISTS usuario (
    cd_usuario              INTEGER NOT NULL AUTO_INCREMENT
    , cd_endereco           INTEGER
    , cd_token              CHAR(64) DEFAULT NULL
    , cd_tipo_usuario       INTEGER NOT NULL
    , no_usuario            VARCHAR(100) NOT NULL
    , ds_email              VARCHAR(100) NOT NULL
    , cd_senha              VARCHAR(100) NOT NULL
    , dt_ultima_alteracao   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    , dt_criacao            TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    , UNIQUE(ds_email)
    , UNIQUE(cd_token)

    , CONSTRAINT pk_usuario
        PRIMARY KEY (cd_usuario)

    , CONSTRAINT fk_usuario_endereco
        FOREIGN KEY (cd_endereco)
            REFERENCES endereco(cd_endereco)
);


CREATE TABLE IF NOT EXISTS desconto (
    cd_desconto     INTEGER NOT NULL AUTO_INCREMENT
    , cd_usuario    INTEGER
    , ds_desconto   VARCHAR(100) NOT NULL
    , qt_usos       INTEGER NOT NULL DEFAULT 0
    , qt_max_usos   INTEGER NOT NULL DEFAULT 1
    , dt_inicio     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    , dt_fim        TIMESTAMP DEFAULT NULL

    , CONSTRAINT pk_desconto
        PRIMARY KEY (cd_desconto)

    , CONSTRAINT fk_desconto_usuario
        FOREIGN KEY (cd_usuario)
            REFERENCES usuario(cd_usuario)
);


CREATE TABLE IF NOT EXISTS pedido (
    cd_pedido               INTEGER NOT NULL AUTO_INCREMENT
    , cd_usuario            INTEGER NOT NULL
    , cd_status             INTEGER NOT NULL DEFAULT 1
    , vl_total_impostos     DOUBLE DEFAULT 0
    , vl_total_compra       DOUBLE DEFAULT 0
    , vl_total_descontos    DOUBLE DEFAULT 0
    , vl_total_a_pagar      DOUBLE DEFAULT 0
    , dt_ultima_alteracao   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    , dt_inicio             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    , dt_fim                TIMESTAMP DEFAULT NULL

    , CONSTRAINT pk_pedido
        PRIMARY KEY (cd_pedido)

    , CONSTRAINT fk_pedido_usuario
        FOREIGN KEY (cd_usuario)
            REFERENCES usuario(cd_usuario)
);


CREATE TABLE IF NOT EXISTS aplicacao_desconto (
    cd_desconto INTEGER NOT NULL
    , cd_pedido INTEGER NOT NULL

    , CONSTRAINT pk_aplicacao_desconto_pedido
        PRIMARY KEY (cd_desconto, cd_pedido)

    , CONSTRAINT fk_aplicacao_desconto_desconto
        FOREIGN KEY (cd_desconto)
            REFERENCES desconto(cd_desconto)

    , CONSTRAINT fk_aplicacao_desconto_pedido
        FOREIGN KEY (cd_pedido)
            REFERENCES pedido(cd_pedido)
);


CREATE TABLE IF NOT EXISTS imposto (
    cd_imposto      INTEGER NOT NULL AUTO_INCREMENT
    , no_imposto    VARCHAR(10) NOT NULL
    , vl_percentual DOUBLE NOT NULL

    , CONSTRAINT pk_imposto
        PRIMARY KEY (cd_imposto)
);


CREATE TABLE IF NOT EXISTS aplicacao_imposto (
    cd_imposto      INTEGER NOT NULL
    , cd_pedido     INTEGER NOT NULL
    , vl_percentual DOUBLE NOT NULL

    , CONSTRAINT pk_aplicacao_imposto_pedido
        PRIMARY KEY (cd_imposto, cd_pedido)
    
    , CONSTRAINT fk_aplicacao_imposto_imposto
        FOREIGN KEY (cd_imposto)
            REFERENCES imposto(cd_imposto)

    , CONSTRAINT fk_aplicacao_imposto_pedido
        FOREIGN KEY (cd_pedido)
            REFERENCES pedido(cd_pedido)
);


CREATE TABLE IF NOT EXISTS produto (
    cd_produto              INTEGER NOT NULL AUTO_INCREMENT
    , no_produto            VARCHAR(100) NOT NULL
    , vl_unitario           DOUBLE NOT NULL
    , qt_estoque            INTEGER NOT NULL
    , dt_ultima_alteracao   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    , dt_criacao            TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    , UNIQUE(no_produto)

    , CONSTRAINT pk_produto
        PRIMARY KEY (cd_produto)
);


CREATE TABLE IF NOT EXISTS item_pedido (
    cd_pedido       INTEGER NOT NULL
    , cd_produto    INTEGER NOT NULL
    , qt_itens      INTEGER NOT NULL
    , vl_unitario   DOUBLE NOT NULL
    , vl_total      DOUBLE NOT NULL

    , CONSTRAINT pk_item_pedido_produto
        PRIMARY KEY (cd_pedido, cd_produto)

    , CONSTRAINT fk_item_pedido_pedido
        FOREIGN KEY (cd_pedido)
            REFERENCES pedido(cd_pedido)

    , CONSTRAINT fk_item_pedido_produto
        FOREIGN KEY (cd_produto)
            REFERENCES produto(cd_produto)
);

--------------------------------------------------------------------------------

-- DROP TABLES

DROP TABLE IF EXISTS aplicacao_desconto;
DROP TABLE IF EXISTS aplicacao_imposto;
DROP TABLE IF EXISTS item_pedido;
DROP TABLE IF EXISTS produto;
DROP TABLE IF EXISTS imposto;
DROP TABLE IF EXISTS pedido;
DROP TABLE IF EXISTS desconto;
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS endereco;
DROP TABLE IF EXISTS cidade;
DROP TABLE IF EXISTS estado;

--------------------------------------------------------------------------------
