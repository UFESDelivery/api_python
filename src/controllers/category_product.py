from sqlalchemy.engine import Connection

import src.api_tools as apit


def get(
    conn: Connection,
    id_category: int = None,
    category_name: str = None,
    like: bool = True
):
    table_name = "categoria_produto"

    realy_category_name = apit.treat_str(category_name)

    equal_operator = "="

    if like:
        realy_category_name = f"%{realy_category_name}%"

        equal_operator = "LIKE"

    where = ["1 = 1"]

    values = {}

    if id_category is not None:
        values["id_category"] = id_category
        where.append("cd_categoria = %(id_category)s")
    
    else:
        if realy_category_name is not None:
            values["realy_category_name"] = realy_category_name
            where.append(f"ds_categoria {equal_operator} %(realy_category_name)s")
    
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE {" AND ".join(where)}
    """

    ref_category_product = conn.exec_driver_sql(query, values)

    return apit.rows_in_list_dict(ref_category_product)
