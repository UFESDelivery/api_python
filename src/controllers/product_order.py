from sqlalchemy.engine import Connection

import src.api_tools as apit
import src.controllers.order as order
import src.controllers.product as product


def get(
    conn: Connection,
    id_order: int,
    id_product: int
):
    table_name = "item_pedido"

    where = [
        f" AND cd_pedido = {id_order}",
        f" AND cd_produto = {id_product}"
    ]

    query_select = f"""
        SELECT *
        FROM {table_name}
        WHERE 1 = 1
            {", ".join(where)}
    """

    ref_product_order = conn.execute(query_select)

    return apit.rows_in_list_dict(ref_product_order)


def new(
    conn: Connection,
    id_order: int,
    id_product: int,
    qtt_items: int
):
    table_name = "item_pedido"

    error = None

    if qtt_items < 1:
        error = f"A quantidade '{qtt_items}' de itens é inválida"
    else:
        try:
            order_info = order.get(
                conn=conn,
                id_order=id_order
            )[0]
        except:
            error = f"O cd_pedido '{id_order}' não foi encontrado"
        else:
            try:
                product_info = product.get(
                    conn=conn,
                    id_product=id_product
                )[0]

                value_unit = (
                    product_info["vl_unitario"]
                    if product_info["qt_estoque"] >= qtt_items
                    else None
                )

                qtt_storage = product_info["qt_estoque"]
            except:
                error = f"O cd_produto '{id_product}' não foi encontrado"
            else:
                try:
                    product_order_info = get(
                        conn=conn,
                        id_order=id_order,
                        id_product=id_product
                    )[0]

                    product.update(
                        conn=conn,
                        id_product=id_product,
                        qtt_storege=qtt_storage - qtt_items
                    )

                    order.update(
                        conn=conn,
                        id_order=id_order,
                        id_status=2,
                        amount_value=(
                            order_info["vl_total_compra"]
                            + qtt_items * value_unit
                        )
                    )
                    
                    update(
                        conn=conn,
                        id_order=id_order,
                        id_product=id_product,
                        qtt_items=product_order_info["qt_itens"] + qtt_items
                    )

                    return apit.get_response(
                        response={
                            "message": (
                                f"Foram adicionados '{qtt_items}' itens "
                                f"no pedido '{id_order}' do produto "
                                f"'{id_product}'"
                            ),
                            "id_order": id_order,
                            "id_product": id_product
                        },
                        status=201
                    )
                except:
                    pass

    if bool(error):
        return apit.get_response(
            response={
                "message": error
            },
            status=400
        )

    if value_unit is None:
        return apit.get_response(
            response={
                "message": (
                    f"O cd_produto '{id_product}' está sem estoque"
                    " suficiente no momento"
                ),
                "id_product": id_product,
                "qtt_storage": qtt_storage
            },
            status=503
        )
    
    product.update(
        conn=conn,
        id_product=id_product,
        qtt_storege=qtt_storage - qtt_items
    )

    order.update(
        conn=conn,
        id_order=id_order,
        id_status=2,
        amount_value=order_info["vl_total_compra"] + qtt_items * value_unit
    )

    cv = {
        "cd_pedido": id_order,
        "cd_produto": id_product,
        "qt_itens": qtt_items,
        "vl_unitario": value_unit
    }

    query_insert = apit.insert_into_formater(
        table_name=table_name,
        columns=cv.keys()
    )

    conn.exec_driver_sql(query_insert, cv)

    return apit.get_response(
        response={
            "message": (
                f"O cd_produto '{id_product}' foi adicionado no pedido "
                f"'{id_order}' com sucesso"
            ),
            "id_order": id_order,
            "id_product": id_product
        },
        status=201
    )


def update(
    conn: Connection,
    id_order: int,
    id_product: int,
    qtt_items: int = None,
    value_unit: float = None
):
    table_name = "item_pedido"

    error = None

    values = {}

    try:
        get(
            conn=conn,
            id_order=id_order,
            id_product=id_product
        )[0]
    except:
        error = (
            f"O cd_produto '{id_product}' ou o cd_pedido '{id_order}'"
            " não foi encontrado"
        )
    else:
        if bool(qtt_items):
            if qtt_items < 0:
                error = f"A qt_itens '{qtt_items}' é inválida"
            else:
                values["qt_itens"] = qtt_items
        
        elif bool(value_unit):
            if value_unit < 0:
                error = f"O vl_unitario '{value_unit}' é inválido"
            else:
                values["vl_unitario"] = value_unit

    if bool(error):
        return apit.get_response(
            response={
                "message": error
            },
            status=400
        )

    query_update = f"""
        UPDATE {table_name}
        SET {apit.format_set(values)}
        WHERE cd_pedido = {id_order}
            AND cd_produto = {id_product}
    """

    conn.execute(query_update)

    return apit.get_response(
        response={
            "message": f"Os valores foram alterados com sucesso"
        },
        status=200
    )
