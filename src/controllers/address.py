from sqlalchemy.engine import Connection

import src.api_tools as apit

import src.controllers.city as city


def get(
    conn: Connection,
    id_address: int = None,
    id_city: int = None,
    street_name: str = None,
    district_name: str = None,
    number: str = None,
    postal_code: str = None,
    like: bool = True
):
    table_name = "endereco"

    equal_operator = "="

    realy_district_name = apit.treat_str(district_name)
    realy_street_name = apit.treat_str(street_name)
    realy_postal_code = apit.treat_str(postal_code)
    realy_number = apit.treat_str(number)

    if like:
        realy_district_name = f"%{realy_district_name}%"
        realy_street_name = f"%{realy_street_name}%"
        realy_postal_code = f"%{realy_postal_code}%"
        realy_number = f"%{realy_number}%"

        equal_operator = "LIKE"
    
    where = []

    if bool(id_address):
        where.append(f" AND cd_endereco = {id_address}")
    
    else:
        if bool(id_city):
            where.append(f" AND cd_cidade = {id_city}")
        
        if bool(realy_district_name):
            where.append(f" AND no_bairro {equal_operator} '{realy_district_name}'")
        
        if bool(realy_street_name):
            where.append(f" AND no_logradouro {equal_operator} '{realy_street_name}'")
        
        if bool(realy_postal_code):
            where.append(f" AND nu_cep {equal_operator} '{realy_postal_code}'")
        
        if bool(realy_number):
            where.append(f" AND ds_numero {equal_operator} '{realy_number}'")

    query_exists = f"""
        SELECT *
        FROM {table_name}
        WHERE 1 = 1
            {"".join(where)}
    """

    ref_address = conn.execute(query_exists)

    return apit.rows_in_list_dict(ref_address)


def new(
    conn: Connection,
    id_city: int,
    street_name: str,
    district_name: str,
    number: str,
    postal_code: str,
):
    table_name = "endereco"

    realy_district_name = apit.treat_str(district_name)
    realy_street_name = apit.treat_str(street_name)
    realy_postal_code = apit.treat_str(postal_code)
    realy_number = apit.treat_str(number)

    error = None

    try:
        city.get(
            conn=conn,
            id_city=id_city
        )[0]["cd_cidade"]
    except:
        error = f"O cd_cidade '{id_city}' não existe"
    else:
        if not bool(realy_district_name) or len(realy_district_name) < 5:
            error = f"Nome do bairro '{realy_district_name}' inválido"
        
        elif not bool(realy_street_name) or len(realy_street_name) < 7:
            error = f"Logradouro '{realy_street_name}' inválido"
        
        elif not bool(realy_postal_code) or len(realy_postal_code) != 8:
            error = f"CEP '{realy_postal_code}' inválido"
        
        elif not bool(realy_number):
            error = f"Número '{realy_number}' inválido"

    if bool(error):
        return apit.get_response(
            response={
                "message": error
            },
            status=500
        )
    
    query_address_exists = f"""
        SELECT cd_endereco
        FROM {table_name}
        WHERE cd_cidade = {id_city}
            AND no_logradouro = '{realy_street_name}'
            AND no_bairro = '{realy_district_name}'
            AND ds_numero = '{realy_number}'
            AND nu_cep = '{realy_postal_code}'
    """

    try:
        id_address = conn.execute(query_address_exists).fetchone()[0]
    except:
        id_address = None

    if bool(id_address):
        return apit.get_response(
            response={
                "message": f"O endereço '{realy_district_name}' já está cadastrado",
                "id_address": id_address
            },
            status=409
        )
    
    columns = {
        "cd_cidade": id_city,
        "no_bairro": realy_district_name,
        "no_logradouro": realy_street_name,
        "nu_cep": realy_postal_code,
        "ds_numero": realy_number
    }

    query_insert = f"""
        INSERT INTO {table_name} (
            {apit.format_columns(columns.keys())}
        )
        VALUES
            ({apit.format_values(columns.values())})
    """

    conn.execute(query_insert)

    id_address = get(
        conn=conn,
        id_city=id_city,
        street_name=realy_street_name,
        district_name=realy_district_name,
        number=realy_number,
        postal_code=realy_postal_code,
        like=False
    )[0]["cd_cidade"]

    return apit.get_response(
        response={
            "message": f"O endereço '{realy_street_name}' foi criado com sucesso",
            "id_address": id_address
        },
        status=201
    )
