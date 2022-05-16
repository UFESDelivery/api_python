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
    
    where = []

    if bool(id_state):
        where.append(f" AND cd_estado = {id_state}")

    else:
        if bool(realy_state_name):
            where.append(f" AND ds_estado {equal_operator} '{realy_state_name}'")

        if bool(realy_uf):
            where.append(f" AND cd_uf {equal_operator} '{realy_uf}'")

    query_exists = f"""
        SELECT *
        FROM {table_name}
        WHERE 1 = 1
            {"".join(where)}
    """

    ref_states = conn.execute(query_exists)

    return apit.rows_in_list_dict(ref_states)
