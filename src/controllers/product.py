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
    like: bool = True
):
    table_name = "produto"

    realy_product_name = apit.treat_str(product_name)

    equal_operator = "="

    if like:
        realy_product_name = f"%{realy_product_name}%"

        equal_operator = "LIKE"

    where = ["1 = 1"]

    values = {}

    if id_product is not None:
        values["id_product"] = id_product
        where.append("cd_produto = %(id_product)s")

    else:
        if id_category is not None:
            values["id_category"] = id_category
            where.append("cd_categoria = %(id_category)s")

        if realy_product_name is not None:
            values["realy_product_name"] = realy_product_name
            where.append(f"no_produto {equal_operator} %(realy_product_name)s")

        if value_unit is not None:
            values["value_unit"] = value_unit
            where.append("vl_unitario = %(value_unit)s")

        else:
            if min_value_unit is not None:
                values["min_value_unit"] = min_value_unit
                where.append("vl_unitario >= %(min_value_unit)s")

            if max_value_unit is not None:
                values["max_value_unit"] = max_value_unit
                where.append("vl_unitario <= %(max_value_unit)s")

        if qtt_storege is not None:
            values["qtt_storege"] = qtt_storege
            where.append("qt_estoque = %(qtt_storege)s")
        
        else:
            if min_qtt_storege is not None:
                values["min_qtt_storege"] = min_qtt_storege
                where.append("qt_estoque >= %(min_qtt_storege)s")

            if max_qtt_storege is not None:
                values["max_qtt_storege"] = max_qtt_storege
                where.append("qt_estoque <= %(max_qtt_storege)s")
    
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE {" AND ".join(where)}
    """

    ref_product = conn.exec_driver_sql(query, values)

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
    
    categories = category_product.get(
        conn=conn,
        id_category=id_category
    )

    if len(categories) == 0:
        return apit.get_response(
            response={
                "message": f"O cd_categoria '{id_category}' não existe"
            },
            status=400
        )

    current_datetime = dt.datetime.now()

    products = get(
        conn=conn,
        product_name=realy_product_name
    )

    if len(products) > 0:
        id_product = products[0]["cd_produto"]

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

    apit.commit_db(conn)

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

    products = get(
        conn=conn,
        id_product=id_product
    )
    
    if len(products) == 0:
        error = f"O cd_produto '{id_product}' não foi encontrado"
    else:
        if id_category is not None:
            categories = category_product.get(
                conn=conn,
                id_category=id_category
            )

            if len(categories) == 0:
                error = f"O cd_categoria '{id_category}' não foi encontrado"
            else:
                cv["cd_categoria"] = id_category

        if realy_product_name is not None and error is None:
            if len(realy_product_name) < 5:
                error = f"O no_produto '{realy_product_name}' é inválido"
            else:
                cv["no_produto"] = realy_product_name

        if value_unit is not None and error is None:
            if value_unit < 0:
                error = f"O vl_unitario '{value_unit}' é inválido"
            else:
                cv["vl_unitario"] = value_unit
        
        if qtt_storege is not None and error is None:
            if qtt_storege < 0:
                error = f"A qt_estoque '{qtt_storege}' é inválida"
            else:
                cv["qt_estoque"] = qtt_storege

        if len(cv) == 0 and error is None:
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

    apit.commit_db(conn)

    return apit.get_response(
        response={
            "message": f"O cd_produto '{id_product}' foi alterado com sucesso",
            "id_product": id_product
        },
        status=200
    )
