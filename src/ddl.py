from sqlalchemy.engine import Connection


def create_estado(
    conn: Connection
):
    query = """
        CREATE TABLE IF NOT EXISTS estado (
            cd_estado   INTEGER NOT NULL AUTO_INCREMENT
            , cd_uf     CHAR(2) NOT NULL
            , ds_estado VARCHAR(100) NOT NULL

            , UNIQUE(cd_uf)

            , CONSTRAINT pk_estado
                PRIMARY KEY (cd_estado)
        )
    """

    conn.execute(query)


def create_cidade(
    conn: Connection
):
    query = """
        CREATE TABLE IF NOT EXISTS cidade (
            cd_cidade   INTEGER NOT NULL AUTO_INCREMENT
            , cd_estado INTEGER NOT NULL
            , no_cidade VARCHAR(100) NOT NULL

            , CONSTRAINT pk_cidade
                PRIMARY KEY (cd_cidade)

            , CONSTRAINT fk_cidade_estado
                FOREIGN KEY (cd_estado)
                    REFERENCES estado(cd_estado)
        )
    """

    conn.execute(query)


def create_endereco(
    conn: Connection
):
    query = """
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
        )
    """

    conn.execute(query)


def create_usuario(
    conn: Connection
):
    query = """
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
        )
    """

    conn.execute(query)


def create_desconto(
    conn: Connection
):
    query = """
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
        )
    """

    conn.execute(query)


def create_pedido(
    conn: Connection
):
    query = """
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
        )
    """

    conn.execute(query)


def create_aplicacao_desconto(
    conn: Connection
):
    query = """
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
        )
    """

    conn.execute(query)


def create_imposto(
    conn: Connection
):
    query = """
        CREATE TABLE IF NOT EXISTS imposto (
            cd_imposto      INTEGER NOT NULL AUTO_INCREMENT
            , no_imposto    VARCHAR(10) NOT NULL
            , vl_percentual DOUBLE NOT NULL

            , CONSTRAINT pk_imposto
                PRIMARY KEY (cd_imposto)
        )
    """

    conn.execute(query)


def create_aplicacao_imposto(
    conn: Connection
):
    query = """
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
        )
    """

    conn.execute(query)


def create_produto(
    conn: Connection
):
    query = """
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
        )
    """

    conn.execute(query)


def create_item_pedido(
    conn: Connection
):
    query = """
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
        )
    """

    conn.execute(query)


def create_all(
    conn: Connection
):
    create_estado(conn)
    create_cidade(conn)
    create_endereco(conn)
    create_usuario(conn)
    create_desconto(conn)
    create_pedido(conn)
    create_aplicacao_desconto(conn)
    create_imposto(conn)
    create_aplicacao_imposto(conn)
    create_produto(conn)
    create_item_pedido(conn)


def drop_estado(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS estado"

    conn.execute(query)


def drop_cidade(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS cidade"

    conn.execute(query)


def drop_endereco(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS endereco"

    conn.execute(query)


def drop_usuario(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS usuario"

    conn.execute(query)


def drop_desconto(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS desconto"

    conn.execute(query)


def drop_pedido(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS pedido"

    conn.execute(query)


def drop_aplicacao_desconto(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS aplicacao_desconto"

    conn.execute(query)


def drop_imposto(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS imposto"

    conn.execute(query)


def drop_aplicacao_imposto(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS aplicacao_imposto"

    conn.execute(query)


def drop_produto(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS produto"

    conn.execute(query)


def drop_item_pedido(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS item_pedido"

    conn.execute(query)


def drop_all(
    conn: Connection
):
    drop_aplicacao_desconto(conn)
    drop_aplicacao_imposto(conn)
    drop_item_pedido(conn)
    drop_produto(conn)
    drop_imposto(conn)
    drop_pedido(conn)
    drop_desconto(conn)
    drop_usuario(conn)
    drop_endereco(conn)
    drop_cidade(conn)
    drop_estado(conn)


def recreate_all(
    conn: Connection
):
    drop_all(conn)
    create_all(conn)
