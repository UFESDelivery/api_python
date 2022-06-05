from sqlalchemy.engine import Connection

import src.api_tools as apit
import src.controllers.order as order
import src.controllers.product as product


def get(
    conn: Connection,
    id_order: int = None,
    id_product: int = None
):
    table_name = "item_pedido"

    where = ["1 = 1"]

    values = {}

    if id_order is not None:
        values["id_order"] = id_order
        where.append("cd_pedido = %(id_order)s")
    
    if id_product is not None:
        values["id_product"] = id_product
        where.append("cd_produto = %(id_product)s")

    query_select = f"""
        SELECT *
        FROM {table_name}
        WHERE {" AND ".join(where)}
    """

    ref_product_order = conn.exec_driver_sql(query_select, values)

    return apit.rows_in_list_dict(ref_product_order)


def new(
    conn: Connection,
    id_order: int,
    id_product: int,
    qtt_items: int
):
    table_name = "item_pedido"

    error = None

    products = product.get(
        conn=conn,
        id_product=id_product
    )

    orders = order.get(
        conn=conn,
        id_order=id_order
    )

    if len(products) == 0:
        error = f"O cd_produto '{id_product}' não foi encontrado"
    
    elif len(orders) == 0:
        error = f"O cd_produto '{id_order}' não foi encontrado"
    
    elif qtt_items < 1:
        error = f"A quantidade de itens '{qtt_items}' é inválida"
    
    elif products[0]["qt_estoque"] < qtt_items:
        error = (
            f"Só existem '{products[0]['qt_estoque']}' "
            f"itens do produto '{products[0]['no_produto']}' em estoque"
        )

    if error is not None:
        return apit.get_response(
            response={
                "message": error
            },
            status=400
        )
    
    product.update(
        conn=conn,
        id_product=id_product,
        qtt_storege=products[0]["qt_estoque"] - qtt_items
    )

    order.update(
        conn=conn,
        id_order=id_order,
        id_status=1,
        amount_value=(
            orders[0]["vl_total_compra"]
            + qtt_items
            * products[0]["vl_unitario"]
        ),
        payment_value=(
            orders[0]["vl_total_a_pagar"]
            + qtt_items
            * products[0]["vl_unitario"]
        )
    )

    product_order = get(
        conn=conn,
        id_order=id_order,
        id_product=id_product
    )

    if len(product_order) > 0:
        update(
            conn=conn,
            id_order=id_order,
            id_product=id_product,
            qtt_items=product_order[0]["qt_itens"] + qtt_items,
            amount_value=(
                product_order[0]["vl_total"]
                + qtt_items
                * product_order[0]["vl_unitario"]
            )
        )
    
    else:
        cv = {
            "cd_pedido": id_order,
            "cd_produto": id_product,
            "qt_itens": qtt_items,
            "vl_unitario": products[0]["vl_unitario"],
            "vl_total": products[0]["vl_unitario"] * qtt_items
        }

        query = apit.insert_into_formater(
            table_name=table_name,
            columns=cv.keys()
        )

        conn.exec_driver_sql(query, cv)
    
        apit.commit_db(conn)
    
    return apit.get_response(
        response={
            "message": (
                f"Foram adicionados '{qtt_items}' itens do produto "
                f"'{products[0]['no_produto']}' no pedido '{id_order}'"
            )
        },
        status=200
    )


def update(
    conn: Connection,
    id_order: int,
    id_product: int,
    qtt_items: int = None,
    value_unit: float = None,
    amount_value: float = None
):
    table_name = "item_pedido"

    error = None

    cv = {}

    product_order = get(
        conn=conn,
        id_order=id_order,
        id_product=id_product
    )

    if len(product_order) == 0:
        error = (
            f"O cd_produto '{id_product}' ou o cd_pedido '{id_order}'"
            " não foi encontrado"
        )
    else:
        if qtt_items is not None:
            if qtt_items < 0:
                error = f"A qt_itens '{qtt_items}' é inválida"
            else:
                cv["qt_itens"] = qtt_items
        
        if value_unit is not None and error is None:
            if value_unit < 0:
                error = f"O vl_unitario '{value_unit}' é inválido"
            else:
                cv["vl_unitario"] = value_unit
        
        if amount_value is not None and error is None:
            if amount_value < 0:
                error = f"O vl_total '{amount_value}' é inválido"
            else:
                cv["vl_total"] = amount_value

        if len(cv) == 0 and error is None:
            error = f"Nenhuma coluna foi informada para alteração"

    if error is not None:
        return apit.get_response(
            response={
                "message": error
            },
            status=400
        )

    query_update = apit.update_from_formater(
        table_name=table_name,
        columns=cv.keys(),
        pk_v=[
            ("cd_pedido", id_order),
            ("cd_produto", id_product)
        ]
    )

    conn.exec_driver_sql(query_update, cv)

    apit.commit_db(conn)

    return apit.get_response(
        response={
            "message": f"Os valores foram alterados com sucesso"
        },
        status=200
    )
