from sqlalchemy.engine import Connection


def create_state(
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


def create_city(
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


def create_address(
    conn: Connection
):
    query = """
        CREATE TABLE IF NOT EXISTS endereco (
            cd_endereco         INTEGER NOT NULL AUTO_INCREMENT
            , cd_cidade         INTEGER NOT NULL
            , no_logradouro     VARCHAR(100) NOT NULL
            , no_bairro         VARCHAR(100) NOT NULL
            , ds_complemento    VARCHAR(100)
            , ds_numero         VARCHAR(10)
            , nu_cep            CHAR(8)

            , CONSTRAINT pk_endereco
                PRIMARY KEY (cd_endereco)

            , CONSTRAINT fk_endereco_cidade
                FOREIGN KEY (cd_cidade)
                    REFERENCES cidade(cd_cidade)
        )
    """

    conn.execute(query)


def create_user(
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


def create_discount(
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


def create_order(
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


def create_apply_discount(
    conn: Connection
):
    query = """
        CREATE TABLE IF NOT EXISTS aplicacao_desconto (
            cd_desconto     INTEGER NOT NULL
            , cd_pedido     INTEGER NOT NULL
            , vl_percentual DOUBLE NOT NULL

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


def create_tax(
    conn: Connection
):
    query = """
        CREATE TABLE IF NOT EXISTS imposto (
            cd_imposto              INTEGER NOT NULL AUTO_INCREMENT
            , no_imposto            VARCHAR(10) NOT NULL
            , vl_percentual         DOUBLE NOT NULL
            , dt_ultima_alteracao   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , dt_criacao            TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            , CONSTRAINT pk_imposto
                PRIMARY KEY (cd_imposto)
        )
    """

    conn.execute(query)


def create_apply_tax(
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



def create_product_category(
    conn: Connection
):
    query = """
        CREATE TABLE IF NOT EXISTS categoria_produto (
            cd_categoria            INTEGER NOT NULL AUTO_INCREMENT
            , ds_categoria          VARCHAR(100) NOT NULL
            , dt_ultima_alteracao   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , dt_criacao            TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            , CONSTRAINT pk_categoria
                PRIMARY KEY (cd_categoria)
        )
    """

    conn.execute(query)


def create_product(
    conn: Connection
):
    query = """
        CREATE TABLE IF NOT EXISTS produto (
            cd_produto              INTEGER NOT NULL AUTO_INCREMENT
            , cd_categoria          INTEGER NOT NULL
            , no_produto            VARCHAR(100) NOT NULL
            , vl_unitario           DOUBLE NOT NULL
            , qt_estoque            INTEGER NOT NULL
            , dt_ultima_alteracao   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , dt_criacao            TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            , UNIQUE(no_produto)

            , CONSTRAINT pk_produto
                PRIMARY KEY (cd_produto)
            
            , CONSTRAINT fk_produto_categoria
                FOREIGN KEY (cd_categoria)
                    REFERENCES categoria_produto(cd_categoria)
        )
    """

    conn.execute(query)


def create_item_order(
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
    create_state(conn)
    create_city(conn)
    create_address(conn)
    create_user(conn)
    create_discount(conn)
    create_order(conn)
    create_apply_discount(conn)
    create_tax(conn)
    create_apply_tax(conn)
    create_product_category(conn)
    create_product(conn)
    create_item_order(conn)


def drop_state(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS estado"

    conn.execute(query)


def drop_city(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS cidade"

    conn.execute(query)


def drop_address(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS endereco"

    conn.execute(query)


def drop_user(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS usuario"

    conn.execute(query)


def drop_discount(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS desconto"

    conn.execute(query)


def drop_order(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS pedido"

    conn.execute(query)


def drop_apply_discount(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS aplicacao_desconto"

    conn.execute(query)


def drop_tax(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS imposto"

    conn.execute(query)


def drop_apply_tax(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS aplicacao_imposto"

    conn.execute(query)


def drop_product_category(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS categoria_produto"

    conn.execute(query)


def drop_product(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS produto"

    conn.execute(query)


def drop_item_order(
    conn: Connection
):
    query = "DROP TABLE IF EXISTS item_pedido"

    conn.execute(query)


def drop_all(
    conn: Connection
):
    drop_apply_discount(conn)
    drop_apply_tax(conn)
    drop_item_order(conn)
    drop_product(conn)
    drop_product_category(conn)
    drop_tax(conn)
    drop_order(conn)
    drop_discount(conn)
    drop_user(conn)
    drop_address(conn)
    drop_city(conn)
    drop_state(conn)


def recreate_all(
    conn: Connection
):
    drop_all(conn)
    create_all(conn)
