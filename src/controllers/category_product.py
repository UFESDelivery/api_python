from sqlalchemy.engine import Connection

import src.api_tools as apit


def get(
    conn: Connection,
    id_category: int,
    category_name: str,
    like: bool = False
):
    table_name = "categoria_produto"

    realy_category_name = apit.treat_str(category_name)

    equal_operator = "="

    if like:
        realy_category_name = f"%{realy_category_name}%"

        equal_operator = "LIKE"

    where = []

    if id_category is not None:
        where.append(f"AND cd_categoria = {id_category}")
    
    else:
        if realy_category_name is not None:
            where.append(f"AND ds_categoria {equal_operator} {realy_category_name}")
    
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE 1 = 1
            {" ".join(where)}
    """

    ref_category_product = conn.execute(query)

    return apit.rows_in_list_dict(ref_category_product)
