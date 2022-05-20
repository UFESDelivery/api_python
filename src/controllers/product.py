from sqlalchemy.engine import Connection

import datetime as dt

import src.api_tools as apit

import src.controllers.category_product as category_product


def get(
    conn: Connection,
    id_product: int = None,
    id_category: int = None,
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

    if id_product is not None:
        where.append(f"AND cd_produto = {id_product}")

    else:
        if id_category is not None:
            where.append(f"AND cd_categoria = {id_category}")

        if realy_product_name is not None:
            where.append(f"AND no_produto {equal_operator} '{realy_product_name}'")

        if value_unit is not None:
            where.append(f"AND vl_unitario = {value_unit}")

        if min_value_unit is not None:
            where.append(f"AND vl_unitario >= {min_value_unit}")

        if max_value_unit is not None:
            where.append(f"AND vl_unitario <= {max_value_unit}")

        if qtt_storege is not None:
            where.append(f"AND qt_estoque = {qtt_storege}")

        if min_qtt_storege is not None:
            where.append(f"AND qt_estoque >= {min_qtt_storege}")

        if max_qtt_storege is not None:
            where.append(f"AND qt_estoque <= {max_qtt_storege}")
    
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE 1 = 1
            {" ".join(where)}
    """

    ref_product = conn.execute(query)

    return apit.rows_in_list_dict(ref_product)


def new(
    conn: Connection,
    id_category: int,
    product_name: str,
    value_unit: float,
    qtt_storege: int
):
    table_name = "produto"

    realy_product_name = apit.treat_str(product_name)

    error = None

    if id_category < 0:
        error = f"O cd_categoria '{id_category}' é inválido"

    elif value_unit < 0:
        error = f"O valor '{value_unit}' é inválido"
    
    elif realy_product_name is None or len(realy_product_name) < 5:
        error = f"O nome '{realy_product_name}' é inválido"

    elif qtt_storege < 0:
        error = f"A quantidade '{qtt_storege}' é inválida"
    
    if error is not None:
        return apit.get_response(
            response={
                "message": error
            },
            status=400
        )
    
    id_category_exists = category_product.get(
        conn=conn,
        id_category=id_category
    )

    if len(id_category_exists) == 0:
        return apit.get_response(
            response={
                "message": f"O cd_categoria '{id_category}' não existe"
            },
            status=400
        )

    current_datetime = dt.datetime.now()

    product_info = get(
        conn=conn,
        product_name=realy_product_name
    )

    if len(product_info) > 0:
        id_product = product_info[0]["cd_produto"]

        return apit.get_response(
            response={
                "message": f"O cd_produto '{id_product}' já existe",
                "id_product": id_product
            },
            status=409
        )
    
    cv = {
        "cd_categoria": id_category,
        "no_produto": realy_product_name,
        "vl_unitario": value_unit,
        "qt_estoque": qtt_storege,
        "dt_ultima_alteracao": current_datetime,
        "dt_criacao": current_datetime
    }

    query_insert = apit.insert_into_formater(
        table_name=table_name,
        columns=cv.keys()
    )

    conn.exec_driver_sql(query_insert, cv)

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
    id_category: int = None,
    product_name: str = None,
    value_unit: float = None,
    qtt_storege: int = None,
):
    table_name = "produto"

    realy_product_name = apit.treat_str(product_name)

    error = None

    cv = {}

    exists_id_product = get(
        conn=conn,
        id_product=id_product
    )
    
    if len(exists_id_product) == 0:
        error = f"O cd_produto '{id_product}' não foi encontrado"
    else:
        cv["cd_produto"] = id_product

        if id_category is not None:
            exists_category_product = category_product.get(
                conn=conn,
                id_category=id_category
            )

            if len(exists_category_product) == 0:
                error = f"O cd_categoria '{id_category}' não foi encontrado"
            else:
                cv["cd_categoria"] = id_category

        if realy_product_name is not None:
            if len(realy_product_name) < 5:
                error = f"O no_produto '{realy_product_name}' é inválido"
            else:
                cv["no_produto"] = realy_product_name

        if value_unit is not None:
            if value_unit < 0:
                error = f"O vl_unitario '{value_unit}' é inválido"
            else:
                cv["vl_unitario"] = value_unit
        
        if qtt_storege is not None:
            if qtt_storege < 0:
                error = f"A qt_estoque '{qtt_storege}' é inválida"
            else:
                cv["qt_estoque"] = qtt_storege

        if len(cv) == 0:
            error = f"Nenhuma coluna foi informada para alteração"

    if error is not None:
        return apit.get_response(
            response={
                "message": error
            },
            status=400
        )
    
    cv["dt_ultima_alteracao"] = dt.datetime.now()

    query_update = apit.update_from_formater(
        table_name=table_name,
        columns=cv.keys(),
        pk_v=[
            ("cd_produto", id_product)
        ]
    )

    conn.exec_driver_sql(query_update, cv)

    return apit.get_response(
        response={
            "message": f"O cd_produto '{id_product}' foi alterado com sucesso",
            "id_product": id_product
        },
        status=200
    )
