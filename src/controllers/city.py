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
    
    where = ["1 = 1"]

    values = {}

    if id_city is not None:
        values["id_city"] = id_city
        where.append("cd_cidade = %(id_city)s")

    else:
        if realy_name is not None:
            values["realy_name"] = realy_name
            where.append(f"no_cidade {equal_operator} %(realy_name)s")
        
        if id_state is not None:
            values["id_state"] = id_state
            where.append("cd_estado = %(id_state)s")

    query = f"""
        SELECT *
        FROM {table_name}
        WHERE {" AND ".join(where)}
    """

    ref_cities = conn.exec_driver_sql(query, values)

    return apit.rows_in_list_dict(ref_cities)


def new(
    conn: Connection,
    name: str,
    uf: str,
):
    table_name = "cidade"

    realy_name = apit.treat_str(name)
    realy_uf = apit.treat_str(uf)

    error = None

    if realy_name is None or len(realy_name) < 2:
        error = f"O nome da cidade '{realy_name}' é inválido"
    
    elif realy_uf is None or len(realy_uf) != 2:
        error = f"A UF '{realy_uf}' do estado é inválida"
    
    if error is not None:
        return apit.get_response(
            response={
                "message": error
            },
            status=500
        )

    states = state.get(
        conn=conn,
        id_uf=realy_uf,
        like=False
    )

    if len(states) == 0:
        return apit.get_response(
            response={
                "message": f"O estado '{realy_uf}' não existe no banco"
            },
            status=500
        )

    id_state = states[0]["cd_estado"]

    cities = get(
        conn=conn,
        name=realy_name,
        id_state=id_state
    )

    if len(cities) > 0:
        return apit.get_response(
            response={
                "message": f"A cidade '{realy_name}' já está cadastrada",
                "id_city": cities[0]["cd_cidade"]
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

    apit.commit_db(conn)

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
