from sqlalchemy.engine import Connection

import datetime as dt

import src.api_tools as apit


def get(
    conn: Connection,
    id_product: int = None,
    product_name: str = None,
    value_unit: float = None,
    min_value_unit: float = None,
    max_value_unit: float = None,
    qtt_storege: int = None,
    min_qtt_storege: int = None,
    max_qtt_storege: int = None,
    like: bool = False
):
    table_name = "produto"

    realy_product_name = apit.treat_str(product_name)

    equal_operator = "="

    if like:
        realy_product_name = f"%{realy_product_name}%"

        equal_operator = "LIKE"

    where = []

    if bool(id_product):
        where.append(f"AND cd_pedido = {id_product}")

    else:
        if bool(realy_product_name):
            where.append(f"AND no_produto {equal_operator} '{realy_product_name}'")

        if bool(value_unit):
            where.append(f"AND vl_unitario = {value_unit}")

        if bool(min_value_unit):
            where.append(f"AND vl_unitario >= {min_value_unit}")

        if bool(max_value_unit):
            where.append(f"AND vl_unitario <= {max_value_unit}")

        if bool(qtt_storege):
            where.append(f"AND qt_estoque = {qtt_storege}")

        if bool(min_qtt_storege):
            where.append(f"AND qt_estoque >= {min_qtt_storege}")

        if bool(max_qtt_storege):
            where.append(f"AND qt_estoque <= {max_qtt_storege}")
    
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE 1 = 1
            {"".join(where)}
    """

    ref_product = conn.execute(query)

    return apit.rows_in_list_dict(ref_product)


def new(
    conn: Connection,
    product_name: str,
    value_unit: float,
    qtt_storege: int
):
    table_name = "produto"

    realy_product_name = apit.treat_str(product_name)

    error = None

    if value_unit < 0:
        error = f"O valor '{value_unit}' é inválido"
    
    elif not bool(realy_product_name) or len(realy_product_name) < 5:
        error = f"O nome '{realy_product_name}' é inválido"

    elif qtt_storege < 0:
        error = f"A quantidade '{qtt_storege}' é inválida"
    
    if bool(error):
        return apit.get_response(
            response={
                "message": error
            },
            status=400
        )

    current_datetime = dt.datetime.now()

    columns = {
        "no_produto": realy_product_name,
        "vl_unitario": value_unit,
        "qt_estoque": qtt_storege,
        "dt_ultima_alteracao": current_datetime,
        "dt_criacao": current_datetime
    }

    product_info = get(
        conn=conn,
        product_name=realy_product_name
    )

    if bool(product_info):
        id_product = product_info[0]["cd_produto"]

        return apit.get_response(
            response={
                "message": f"O cd_produto '{id_product}' já existe",
                "id_product": id_product
            },
            status=409
        )

    query_insert = f"""
        INSERT INTO {table_name} (
            {apit.format_columns(columns.keys())}
        )
        VALUES
            ({apit.format_values(columns.values())})
    """

    conn.execute(query_insert)

    id_product = get(
        conn=conn,
        product_name=realy_product_name
    )

    return apit.get_response(
        response={
            "message": f"O cd_produto '{id_product}' foi criado com sucesso",
            "id_product": id_product
        },
        status=201
    )


def update(
    conn: Connection,
    id_product: int,
    product_name: str = None,
    value_unit: float = None,
    qtt_storege: int = None,
):
    table_name = "produto"

    realy_product_name = apit.treat_str(product_name)

    error = None

    values = {}

    try:
        get(
            conn=conn,
            id_product=id_product
        )[0]["cd_produto"]
    except:
        error = f"O cd_produto '{id_product}' não foi encontrado"
    else:
        if bool(realy_product_name):
            if len(realy_product_name) < 5:
                error = f"O no_produto '{realy_product_name}' é inválido"
            else:
                values["no_produto"] = realy_product_name

        if bool(value_unit):
            if value_unit < 0:
                error = f"O vl_unitario '{value_unit}' é inválido"
            else:
                values["vl_unitario"] = value_unit
        
        if bool(qtt_storege):
            if qtt_storege < 0:
                error = f"A qt_estoque '{qtt_storege}' é inválida"
            else:
                values["qt_estoque"] = qtt_storege

        if len(values) == 0:
            error = f"Nenhuma coluna foi informada para alteração"

    if bool(error):
        return apit.get_response(
            response={
                "message": error
            },
            status=400
        )
    
    values["dt_ultima_alteracao"] = dt.datetime.now()

    query_update = f"""
        UPDATE {table_name}
        SET {apit.format_set(values)}
        WHERE cd_produto = {id_product}
    """

    conn.execute(query_update)

    return apit.get_response(
        response={
            "message": f"O cd_produto '{id_product}' foi alterado com sucesso",
            "id_product": id_product
        },
        status=200
    )
