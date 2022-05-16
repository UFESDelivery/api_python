from sqlalchemy.engine import Connection

import src.api_tools as apit

import src.controllers.state as state


def get(
    conn: Connection,
    id_city: int = None,
    name: str = None,
    id_state: int = None,
    like: bool = True
):
    table_name = "cidade"

    realy_name = apit.treat_str(name)

    equal_operator = "="

    if like:
        realy_name = f"%{realy_name}%"
        equal_operator = "LIKE"
    
    where = []

    if bool(id_city):
        where.append(f" AND cd_cidade = {id_city}")

    else:
        if bool(realy_name):
            where.append(f" AND no_cidade {equal_operator} '{realy_name}'")
        
        if bool(id_state):
            where.append(f" AND cd_estado = {id_state}")

    query_exists = f"""
        SELECT *
        FROM {table_name}
        WHERE 1 = 1
            {"".join(where)}
    """

    ref_cities = conn.execute(query_exists)

    return apit.rows_in_list_dict(ref_cities)


def new(
    conn: Connection,
    name: str = None,
    uf: str = None,
):
    table_name = "cidade"

    realy_name = apit.treat_str(name)
    realy_uf = apit.treat_str(uf)

    error = None

    if not bool(realy_name) or len(realy_name) < 2:
        error = f"O nome da cidade '{realy_name}' é inválido"
    
    elif not bool(realy_uf) or len(realy_uf) != 2:
        error = f"A UF '{realy_uf}' do estado é inválida"
    
    if bool(error):
        return apit.get_response(
            response={
                "message": error
            },
            status=500
        )

    try:
        id_state = state.get(
            conn=conn,
            id_uf=realy_uf,
            like=False
        )[0]["cd_estado"]
    except:
        id_state = None

    if not bool(id_state):
        return apit.get_response(
            response={
                "message": f"O estado '{realy_uf}' não existe no banco"
            },
            status=500
        )

    query_city_exists = f"""
        SELECT cd_cidade
        FROM {table_name}
        WHERE no_cidade = '{realy_name}'
            AND cd_estado = '{id_state}'
    """

    try:
        id_city = conn.execute(query_city_exists).fetchone()[0]
    except:
        id_city = None

    if bool(id_city):
        return apit.get_response(
            response={
                "message": f"A cidade '{realy_name}' já está cadastrada",
                "id_city": id_city
            },
            status=409
        )

    cv = {
        "no_cidade": realy_name,
        "cd_estado": id_state
    }

    query_insert = apit.insert_into_formater(
        table_name=table_name,
        columns=cv.keys()
    )

    conn.exec_driver_sql(query_insert, cv)

    id_city = get(
        conn=conn,
        name=realy_name,
        id_state=id_state,
        like=False
    )[0]["cd_cidade"]

    return apit.get_response(
        response={
            "message": f"A cidade '{realy_name}' foi criada com sucesso",
            "id_city": id_city
        },
        status=201
    )
