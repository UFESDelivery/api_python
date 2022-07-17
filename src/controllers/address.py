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
    
    where = ["1 = 1"]

    values = {}

    if id_address is not None:
        values["id_address"] = id_address
        where.append("cd_endereco = %(id_address)s")
    
    else:
        if id_city is not None:
            values["id_city"] = id_city
            where.append("cd_cidade = %(id_city)s")
        
        if realy_district_name is not None:
            values["realy_district_name"] = realy_district_name
            where.append(f"no_bairro {equal_operator} %(realy_district_name)s")
        
        if realy_street_name is not None:
            values["realy_street_name"] = realy_street_name
            where.append(f"no_logradouro {equal_operator} %(realy_street_name)s")
        
        if realy_postal_code is not None:
            values["realy_postal_code"] = realy_postal_code
            where.append(f"nu_cep {equal_operator} %(realy_postal_code)s")
        
        if realy_number is not None:
            values["realy_number"] = realy_number
            where.append(f"ds_numero {equal_operator} %(realy_number)s")

    query = f"""
        SELECT *
        FROM {table_name}
        WHERE {" AND ".join(where)}
    """

    ref_address = conn.exec_driver_sql(query, values)

    return apit.rows_in_list_dict(ref_address)


def new(
    conn: Connection,
    id_city: int,
    street_name: str,
    district_name: str,
    number: str,
    postal_code: str,
    complement: str = None
):
    table_name = "endereco"

    realy_district_name = apit.treat_str(district_name)
    realy_street_name = apit.treat_str(street_name)
    realy_postal_code = apit.treat_str(postal_code)
    realy_complement = apit.treat_str(complement)
    realy_number = apit.treat_str(number)

    error = None

    get_city = city.get(
        conn=conn,
        id_city=id_city
    )

    if len(get_city) == 0:
        error = f"O cd_cidade '{id_city}' não existe"
    else:
        if realy_district_name is None or len(realy_district_name) < 5:
            error = f"Nome do bairro '{realy_district_name}' inválido"
        
        elif realy_street_name is None or len(realy_street_name) < 7:
            error = f"Logradouro '{realy_street_name}' inválido"
        
        elif realy_postal_code is None or len(realy_postal_code) != 8:
            error = f"CEP '{realy_postal_code}' inválido"
        
        elif realy_number is None:
            error = f"Número '{realy_number}' inválido"

    if error is not None:
        return apit.get_response(
            response={
                "message": error
            },
            status=500
        )
    
    address = get(
        conn=conn,
        id_city=id_city,
        street_name=realy_street_name,
        district_name=realy_district_name,
        number=realy_number,
        postal_code=realy_postal_code,
        like=False
    )

    if len(address) > 0:
        return apit.get_response(
            response={
                "message": f"O endereço '{realy_street_name}' já está cadastrado",
                "id_address": address[0]["cd_endereco"]
            },
            status=409
        )
    
    cv = {
        "cd_cidade": id_city,
        "no_bairro": realy_district_name,
        "no_logradouro": realy_street_name,
        "nu_cep": realy_postal_code,
        "ds_numero": realy_number,
        "ds_complemento": realy_complement
    }

    query_insert = apit.insert_into_formater(
        table_name=table_name,
        columns=cv.keys()
    )

    conn.exec_driver_sql(query_insert, cv)

    apit.commit_db(conn)

    id_address = get(
        conn=conn,
        id_city=id_city,
        street_name=realy_street_name,
        district_name=realy_district_name,
        number=realy_number,
        postal_code=realy_postal_code,
        like=False
    )[0]["cd_endereco"]

    return apit.get_response(
        response={
            "message": f"O endereço '{realy_street_name}' foi criado com sucesso",
            "id_address": id_address
        },
        status=201
    )
