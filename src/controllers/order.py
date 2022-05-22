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

    if id_order is not None:
        where.append(f"cd_pedido = {id_order}")
    
    else:
        if id_user is not None:
            where.append(f"cd_usuario = {id_user}")
        
        if id_status is not None:
            where.append(f"cd_status = {id_status}")
        
        if min_id_status is not None:
            where.append(f"cd_status >= {min_id_status}")
        
        if max_id_status is not None:
            where.append(f"cd_status <= {max_id_status}")
        
        if value_order is not None:
            where.append(f"vl_total_compra = {value_order}")
        
        if min_value_order is not None:
            where.append(f"vl_total_compra >= {min_value_order}")

        if max_value_order is not None:
            where.append(f"vl_total_compra <= {max_value_order}")
        
        if date is not None:
            format_date = apit.format_date(date)

            where.append(f"dt_ultima_alteracao = {format_date}")
        
        if min_date is not None:
            format_date = apit.format_date(min_date)

            where.append(f"dt_ultima_alteracao >= {format_date}")
        
        if max_date is not None:
            format_date = apit.format_date(max_date)

            where.append(f"dt_ultima_alteracao <= {format_date}")
        
        if closed_order:
            where.append(f"dt_fim IS NOT NULL")
        else:
            where.append(f"dt_fim IS NULL")

    query = f"""
        SELECT *
        FROM {table_name}
        WHERE {" AND ".join(where)}
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
    
    if error is not None:
        return apit.get_response(
            response={
                "message": error
            },
            status=500
        )

    current_date = dt.datetime.now()

    cv = {
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

    query_insert = apit.insert_into_formater(
        table_name=table_name,
        columns=cv.keys()
    )
    
    conn.exec_driver_sql(query_insert, cv)

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

    cv = {}

    current_date = dt.datetime.now()

    try:
        get(
            conn=conn,
            id_order=id_order
        )[0]["cd_pedido"]
    except:
        error = f"O cd_pedido '{id_order}' não foi encontrado"
    else:
        if close:
            cv["dt_fim"] = current_date
            cv["cd_status"] = 5
        else:
            if id_status is not None:
                if id_status not in apit.get_all_valid_status():
                    error = f"O cd_status '{id_status}' é inválido"
                else:
                    cv["cd_status"] = id_status
            
            if tax_value is not None:
                if tax_value < 0:
                    error = f"O vl_total_impostos '{tax_value}' é inválido"
                else:
                    cv["vl_total_impostos"] = tax_value
            
            if amount_value is not None:
                if amount_value < 0:
                    error = f"O vl_total_compra '{amount_value}' é invalido"
                else:
                    cv["vl_total_compra"] = amount_value
            
            if discount_value is not None:
                if discount_value < 0:
                    error = f"O vl_total_descontos '{discount_value}' é inválido"
                else:
                    cv["vl_total_descontos"] = discount_value
            
            if payment_value is not None:
                if payment_value < 0:
                    error = f"O vl_total_a_pagar '{payment_value}' é inválido"
                else:
                    cv["vl_total_a_pagar"] = payment_value

            if len(cv) == 0:
                error = f"Nenhuma coluna foi informada para alteração"

    if error is not None:
        return apit.get_response(
            response={
                "message": error
            },
            status=400
        )
    
    cv["dt_ultima_alteracao"] = current_date

    query_update = apit.update_from_formater(
        table_name=table_name,
        columns=cv.keys(),
        pk_v=[
            ("cd_pedido", id_order)
        ]
    )

    conn.exec_driver_sql(query_update, cv)

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
