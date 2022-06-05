from sqlalchemy.engine import Connection

import src.api_tools as apit


def get(
    conn: Connection,
    id_state: int = None,
    id_uf: str = None,
    state_name: str = None,
    like: bool = True
):
    table_name = "estado"

    equal_operator = "="

    realy_state_name = apit.treat_str(state_name)
    realy_uf = apit.treat_str(id_uf)
    
    if like:
        realy_state_name = f"%{realy_state_name}%"
        realy_uf = f"%{realy_uf}%"

        equal_operator = "LIKE"
    
    where = ["1 = 1"]

    values = {}

    if id_state is not None:
        values["id_state"] = id_state
        where.append("cd_estado = %(id_state)s")

    else:
        if realy_state_name is not None:
            values["realy_state_name"] = realy_state_name
            where.append(f"ds_estado {equal_operator} %(realy_state_name)s")

        if realy_uf is not None:
            values["realy_uf"] = realy_uf
            where.append(f"cd_uf {equal_operator} %(realy_uf)s")

    query = f"""
        SELECT *
        FROM {table_name}
        WHERE {" AND ".join(where)}
    """

    ref_states = conn.exec_driver_sql(query, values)

    return apit.rows_in_list_dict(ref_states)
