from typing import Any, Iterable

from flask import Response

import datetime as dt

import sqlalchemy as sa

import random as rdm

import json

import re


def commit_db(
    conn: sa.engine.Connection
):
    conn.exec_driver_sql("COMMIT")


def rollback_db(
    conn: sa.engine.Connection
):
    conn.exec_driver_sql("ROLLBACK")


def delete_from_formater(
    table_name: str,
    columns: Iterable[str]
):
    where_format = [
        f"{k} = %({k})s"
        for k in columns
    ]

    query_update = f"""
        UPDATE FROM {table_name}
        WHERE {" AND ".join(where_format)}
    """

    return query_update


def update_from_formater(
    table_name: str,
    columns: Iterable[str],
    pk_v: list[tuple[str, int]]
):
    set_format = [
        f"{k} = %({k})s"
        for k in columns
    ]

    where_format = [
        f"{pk} = {v}"
        for pk, v in pk_v
    ]

    query_update = f"""
        UPDATE {table_name}
        SET {", ".join(set_format)}
        WHERE {" AND ".join(where_format)}
    """

    return query_update


def insert_into_formater(
    table_name: str,
    columns: Iterable[str]
):
    columns_formated = [
        f"%({k})s"
        for k in columns
    ]

    query_insert = f"""
        INSERT INTO {table_name} (
            {format_columns(columns)}
        )
        VALUES
            ({", ".join(columns_formated)})
    """

    return query_insert


def get_all_valid_users_types():
    all_users = dict(
        enumerate([
            "CLIENTE",
            "ATENDENTE",
            "GERENTE",
            "ADMINISTRADOR"
        ], 1)
    )

    return all_users.keys()


def get_all_valid_status():
    all_status = dict(
        enumerate([
            "NOVO",
            "AGUARDANDO PAGAMENTO",
            "CONFIRMADO",
            "PRONTO PARA ENTREGA",
            "EM ROTA DE ENTREGA",
            "ENTREGUE",
            "CANCELADO PELO CLIENTE",
            "CANCELADO PELO ESTABELECIMENTO"
        ], 1)
    )

    return all_status.keys()


def format_columns(
    cols: Iterable[str]
):
    values = ", ".join(cols)

    return values


def datetime_to_dict(
    date: dt.datetime
):
    return {
        "dia": date.day,
        "mes": date.month,
        "ano": date.year,
        "hora": date.hour,
        "minuto": date.minute,
        "segundo": date.second
    }


def rows_in_list_dict(
    ref_table: sa.engine.CursorResult
):
    rows = ref_table.fetchall()
    columns = [c for c in ref_table.keys()]

    list_dict = [
        {
            columns[i % len(columns)]: (
                datetime_to_dict(c)
                if isinstance(c, dt.datetime)
                else c
            )
            for i, c in enumerate(r)
        }
        for r in rows
    ]

    return list_dict


def authenticate(
    conn: sa.engine.Connection,
    type_: int,
    id_user: int = None,
    email: str = None,
    password: str = None,
    token: str = None,
):
    table_name = "usuario"

    realy_email = treat_str(email)

    values = {"type_": type_}
    where = ["cd_tipo_usuario = %(type_)s"]

    if id_user is not None:
        values["id_user"] = id_user
        where.append("cd_usuario = %(id_user)s")

    if token is not None:
        values["token"] = token
        where.append("cd_token = %(token)s")

    elif realy_email is None or password is None:
        return False

    else:
        values["realy_email"] = realy_email
        values["password"] = password

        where.append("ds_email = %(realy_email)s")
        where.append("cd_senha = %(password)s")

    query = f"""
        SELECT COUNT(1)
        FROM {table_name}
        WHERE {" AND ".join(where)}
    """

    return conn.exec_driver_sql(query, values).fetchone()[0] == 1


def generate_token(
    conn: sa.engine.Connection,
    len_: int = 64
):
    query = """
        SELECT cd_token
        FROM usuario
    """

    result = conn.exec_driver_sql(query).fetchall()

    try:
        token_list = [t[0] for t in result]
    except:
        token_list = []

    possible_char = "1234567890abcdef"

    while True:
        token = "".join([rdm.choice(possible_char) for _ in range(len_)])

        if token not in token_list:
            break

    return token


def get_response(
    response: dict,
    status: int,
    mimetype: str = "application/json"
):
    return Response(
        response=json.dumps(response),
        status=status,
        mimetype=mimetype
    )


def conn_mysql(
    username: str,
    password: str,
    database: str,
    server: str,
    port: int
) -> sa.engine.Connection:
    url = f"mysql+pymysql://{username}:{password}@{server}:{port}/{database}"

    return sa.create_engine(url=url).connect()


def treat_str(
    value: str | int | float
):
    if value is not None:
        return str(value).strip().upper()
    
    return None


def treat_int(
    value: str | int | float
):
    try:
        return int(value)
    except:
        return None


def treat_float(
    value: str | int | float
):
    try:
        return float(value)
    except:
        try:
            return float(value.replace(",", "."))
        except:
            return None


def treat_postal_code(
    value: str | int
):
    template = re.compile(r"^[0-9]{5}-?[0-9]{3}$")

    if template.match(str(value)) is not None:
        return str(value).replace("-", "")
    
    return None


def table_exists(
    conn: sa.engine.Connection,
    table_name: str
):
    return conn.dialect.has_table(conn, table_name)


def is_valid_email(
    email: str
):
    template = re.compile(r"^[a-z]+([._][a-z]+)*@[a-z]+(\.[a-z]+)*$")

    return template.match(email.lower()) is not None


def validate_parameters(
    dict_args: dict[str, Any],
    ignore_args: Iterable[str] = []
):
    return None not in [v for k, v in dict_args.items() if k not in ignore_args]
