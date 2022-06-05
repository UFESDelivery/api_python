from sqlalchemy.engine import Connection

import src.api_tools as apit

import src.controllers.address as address


def get(
    conn: Connection,
    id_user: int = None,
    id_address: int = None,
    user_email: str = None,
    user_name: str = None,
    user_type: int = None,
    like: bool = True
):
    table_name = "usuario"

    equal_operator = "="

    realy_user_email = apit.treat_str(user_email)
    realy_user_name = apit.treat_str(user_name)

    if like:
        realy_user_email = f"%{realy_user_email}%"
        realy_user_name = f"%{realy_user_name}%"

        equal_operator = "LIKE"
    
    where = ["1 = 1"]

    values = {}

    if id_user is not None:
        values["id_user"] = id_user
        where.append("cd_usuario = %(id_user)s")
    
    else:
        if id_address is not None:
            values["id_address"] = id_address
            where.append("cd_endereco = %(id_address)s")
        
        if realy_user_email is not None:
            values["realy_user_email"] = realy_user_email
            where.append(f"ds_email {equal_operator} %(realy_user_email)s")
        
        if realy_user_name is not None:
            values["realy_user_name"] = realy_user_name
            where.append(f"no_usuario {equal_operator} %(realy_user_name)s")
        
        if user_type is not None:
            values["user_type"] = user_type
            where.append("cd_tipo_usuario = %(user_type)s")

    columns = [
        "cd_usuario",
        "cd_endereco",
        "no_usuario",
        "cd_tipo_usuario"
    ]

    query = f"""
        SELECT {", ".join(columns)}
        FROM {table_name}
        WHERE {" AND ".join(where)}
    """

    ref_user = conn.exec_driver_sql(query, values)

    return apit.rows_in_list_dict(ref_user)


def new(
    conn: Connection,
    id_address: int,
    user_email: str,
    user_password: str,
    user_name: str,
    user_type: int,
    user_adm_email: str = None,
    user_adm_password: str = None
):
    table_name = "usuario"

    realy_user_email = apit.treat_str(user_email)
    realy_user_name = apit.treat_str(user_name)
    realy_user_adm_email = apit.treat_str(user_adm_email)

    erro = None
    
    addresses = address.get(
        conn=conn,
        id_address=id_address
    )

    if len(addresses) == 0:
        erro = f"O cd_endereco '{id_address}' não foi encontrado"

    else:
        if not apit.is_valid_email(realy_user_email):
            erro = f"O email '{realy_user_email}' é inválido"
        
        elif realy_user_name is None or len(realy_user_name) < 4:
            erro = f"O nome do usuário deve possuir no mínimo 4 caracteres"
        
        elif len(user_password) < 8:
            erro = f"A senha do usuário deve possuir no mínimo 8 caracteres"
        
        elif user_type not in apit.get_all_valid_users_types():
            erro = f"Tipo '{user_type}' de usuário inválido"
        
        elif (
            user_type > 1
            and (
                realy_user_adm_email is None
                or user_adm_password is None
            )
        ):
            erro = (
                f"Para criar esse tipo de usuário é necessário informar as "
                f"credenciais de um administrador"
            )

        elif user_type > 1 and not apit.authenticate(
            conn=conn,
            type_=4,
            email=realy_user_adm_email,
            password=user_adm_password
        ):
            erro = f"Credenciais do administrador inválida"

    if erro is not None:
        return apit.get_response(
            response={
                "message": erro
            },
            status=400
        )
    
    emails = get(
        conn=conn,
        user_email=realy_user_email,
        like=False
    )

    if len(emails) > 0:
        return apit.get_response(
            response={
                "message": f"O ds_email '{realy_user_email}' já está cadastrado"
            },
            status=409
        )
    
    token = apit.generate_token(conn)

    cv = {
        "cd_endereco": id_address,
        "ds_email": realy_user_email,
        "cd_senha": user_password,
        "no_usuario": realy_user_name,
        "cd_tipo_usuario": user_type,
        "cd_token": token
    }

    query_insert = apit.insert_into_formater(
        table_name=table_name,
        columns=cv.keys()
    )

    conn.exec_driver_sql(query_insert, cv)

    apit.commit_db(conn)

    id_user = get(
        conn=conn,
        user_email=realy_user_email,
        like=False
    )[0]["cd_usuario"]

    return apit.get_response(
        response={
            "message": f"O usuário '{realy_user_name}' foi criado com sucesso",
            "id_user": id_user,
            "token": token
        },
        status=201
    )
