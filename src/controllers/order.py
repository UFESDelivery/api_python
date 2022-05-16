from sqlalchemy.engine import Connection

import datetime as dt

import src.api_tools as apit
import src.controllers.user as user


def get(
    conn: Connection,
    id_order: int = None,
    id_user: int = None,
    id_status: int = None,
    min_id_status: int = None,
    max_id_status: int = None,
    value_order: float = None,
    min_value_order: float = None,
    max_value_order: float = None,
    date: dt.datetime = None,
    min_date: dt.datetime = None,
    max_date: dt.datetime = None,
    closed_order: bool = False
):
    table_name = "pedido"

    where = []

    if bool(id_order):
        where.append(f" AND cd_pedido = {id_order}")
    
    else:
        if bool(id_user):
            where.append(f" AND cd_usuario = {id_user}")
        
        if bool(id_status):
            where.append(f" AND cd_status = {id_status}")
        
        if bool(min_id_status):
            where.append(f" AND cd_status >= {min_id_status}")
        
        if bool(max_id_status):
            where.append(f" AND cd_status <= {max_id_status}")
        
        if bool(value_order):
            where.append(f" AND vl_total_compra = {value_order}")
        
        if bool(min_value_order):
            where.append(f" AND vl_total_compra >= {min_value_order}")

        if bool(max_value_order):
            where.append(f" AND vl_total_compra <= {max_value_order}")
        
        if bool(date):
            format_date = apit.format_date(date)

            where.append(f" AND dt_ultima_alteracao = {format_date}")
        
        if bool(min_date):
            format_date = apit.format_date(min_date)

            where.append(f" AND dt_ultima_alteracao >= {format_date}")
        
        if bool(max_date):
            format_date = apit.format_date(max_date)

            where.append(f" AND dt_ultima_alteracao <= {format_date}")
        
        if closed_order:
            where.append(f" AND dt_fim IS NOT NULL")
        else:
            where.append(f" AND dt_fim IS NULL")

    query = f"""
        SELECT *
        FROM {table_name}
        WHERE 1 = 1
            {"".join(where)}
    """

    ref_order = conn.execute(query)

    return apit.rows_in_list_dict(ref_order)


def new(
    conn: Connection,
    id_user: int
):
    table_name = "pedido"

    error = None

    try:
        user_type = user.get(
            conn=conn,
            id_user=id_user
        )[0]["cd_tipo_usuario"]

        if user_type > 1:
            return apit.get_response(
                response={
                    "message": f"O cd_usuario '{id_user}' não é um cliente"
                },
                status=400
            )
    except:
        error = f"O cd_usuario '{id_user}' não foi encontrado"
    else:
        try:
            id_order = get(
                conn=conn,
                id_user=id_user,
                max_id_status=3
            )[0]["cd_pedido"]

            return apit.get_response(
                response={
                    "message": f"O cd_usuario '{id_user}' já possuí um pedido aberto",
                    "id_order": id_order
                },
                status=409
            )
        except:
            pass
    
    if bool(error):
        return apit.get_response(
            response={
                "message": error
            },
            status=500
        )

    current_date = dt.datetime.now()

    columns = {
        "cd_usuario": id_user,
        "cd_status": 1,
        "vl_total_impostos": 0.0,
        "vl_total_compra": 0.0,
        "vl_total_descontos": 0.0,
        "vl_total_a_pagar": 0.0,
        "dt_ultima_alteracao": current_date,
        "dt_inicio": current_date,
        "dt_fim": None
    }

    query_insert = f"""
        INSERT INTO {table_name} (
            {apit.format_columns(columns.keys())}
        )
        VALUES
            ({apit.format_insert(columns.keys())})
    """
    
    conn.exec_driver_sql(query_insert, columns)

    id_order = get(
        conn=conn,
        id_user=id_user,
        id_status=1
    )[0]["cd_pedido"]

    return apit.get_response(
        response={
            "message": f"O pedido '{id_order}' foi criado com sucesso",
            "id_order": id_order
        },
        status=201
    )


def update(
    conn: Connection,
    id_order: int,
    id_status: int = None,
    tax_value: float = None,
    amount_value: float = None,
    discount_value: float = None,
    payment_value: float = None,
    close: bool = False
):
    table_name = "pedido"

    error = None

    values = {}

    current_date = dt.datetime.now()

    try:
        get(
            conn=conn,
            id_product=id_order
        )[0]["cd_pedido"]
    except:
        error = f"O cd_produto '{id_order}' não foi encontrado"
    else:
        if close:
            values["dt_fim"] = current_date
            values["cd_status"] = 5
        else:
            if bool(id_status):
                if id_status not in apit.get_all_valid_status():
                    error = f"O cd_status '{id_status}' é inválido"
                else:
                    values["cd_status"] = id_status
            
            if bool(tax_value):
                if tax_value < 0:
                    error = f"O vl_total_impostos '{tax_value}' é inválido"
                else:
                    values["vl_total_impostos"] = tax_value
            
            if bool(amount_value):
                if amount_value < 0:
                    error = f"O vl_total_compra '{amount_value}' é invalido"
                else:
                    values["vl_total_compra"] = amount_value
            
            if bool(discount_value):
                if discount_value < 0:
                    error = f"O vl_total_descontos '{discount_value}' é inválido"
                else:
                    values["vl_total_descontos"] = discount_value
            
            if bool(payment_value):
                if payment_value < 0:
                    error = f"O vl_total_a_pagar '{payment_value}' é inválido"
                else:
                    values["vl_total_a_pagar"] = payment_value

            if len(values) == 0:
                error = f"Nenhuma coluna foi informada para alteração"

    if bool(error):
        return apit.get_response(
            response={
                "message": error
            },
            status=400
        )
    
    values["dt_ultima_alteracao"] = current_date

    query_update = f"""
        UPDATE {table_name}
        SET {apit.format_set(values)}
        WHERE cd_pedido = {id_order}
    """

    conn.execute(query_update)

    return apit.get_response(
        response={
            "message": f"O cd_pedido '{id_order}' foi alterado com sucesso",
            "id_order": id_order
        },
        status=200
    )


def delete(
    conn: Connection,
    id_order: int
):
    table_name = "pedido"

    query_delete = f"""
        DELETE FROM {table_name}
        WHERE cd_pedido = {id_order}
    """

    if conn.execute(query_delete).rowcount() == 0:
        return apit.get_response(
            response={
                "message": f"O cd_pedido '{id_order}' não foi encontrado"
            },
            status=400
        )

    return apit.get_response(
        response={
            "message": f"O cd_pedido '{id_order}' foi removido com sucesso"
        },
        status=200
    )
