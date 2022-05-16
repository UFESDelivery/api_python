from typing import Iterable

from flask import Response

import datetime as dt

import sqlalchemy as sa

import random as rdm

import json


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
            "ADICIONANDO ITENS",
            "CONFIRMADO",
            "EM PREPARACAO",
            "SAIU PARA ENTREGA",
            "ENTREGUE"
        ], 1)
    )

    return all_status.keys()


def format_date(
    date: dt.datetime
):
    format_date = (
        f"STR_TO_DATE('"
        f"{date.day:02}"
        f"{date.month:02}"
        f"{date.year:04}"
        f"{date.hour:02}"
        f"{date.minute:02}"
        f"{date.second:02}"
        f"', '%d%m%Y%H%i%s')"
    )

    return format_date


def format_values(
    row: list,
    join: bool = True
):
    values = [
        f"'{v}'"
        if isinstance(v, str)
        else format_date(v)
        if isinstance(v, dt.datetime)
        else "NULL"
        if v is None
        else str(v)
        for v in row
    ]

    if join:
        return ", ".join(values)

    return values


def format_columns(
    cols: Iterable[str]
):
    values = ", ".join(cols)

    return values


def format_set(
    values: dict[str]
):
    format_v = format_values(values.values(), False)
    cols = values.keys()

    ziped = list(zip(cols, format_v))

    return ", ".join([f"{c} = {v}" for c, v in ziped])


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
    type: int,
    email: str = None,
    password: str = None,
    token: str = None,
):
    table_name = "usuario"

    realy_email = treat_str(email)

    if token:
        query = f"""
            SELECT COUNT(1)
            FROM {table_name}
            WHERE cd_token = '{token}'
                AND cd_tipo_usuario = {type}
        """
    else:
        if not realy_email or not password:
            return False
        
        query = f"""
            SELECT COUNT(1)
            FROM {table_name}
            WHERE ds_email = '{realy_email}'
                AND cd_senha = '{password}'
                AND cd_tipo_usuario = {type}
        """

    if conn.execute(query).fetchone()[0] == 1:
        return True
    
    return False


def generate_token(
    conn: sa.engine.Connection,
    len_: int = 64
):
    query = """
        SELECT cd_token
        FROM usuario
    """

    result = conn.execute(query).fetchall()

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
    if treat_int(value) is None:
        return None

    if len(str(value)) != 8:
        return None
    
    return value


def table_exists(
    conn: sa.engine.Connection,
    table_name: str
):
    return conn.dialect.has_table(conn, table_name)
