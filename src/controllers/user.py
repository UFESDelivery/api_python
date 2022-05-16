import re

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
    
    where = []

    if bool(id_user):
        where.append(f" AND cd_usuario = {id_user}")
    
    else:
        if bool(id_address):
            where.append(f" AND cd_endereco = {id_address}")
        
        if bool(realy_user_email):
            where.append(f" AND ds_email {equal_operator} '{realy_user_email}'")
        
        if bool(realy_user_name):
            where.append(f" AND no_usuario {equal_operator} '{realy_user_name}'")
        
        if bool(user_type):
            where.append(f" AND cd_tipo_usuario = {user_type}")

    columns = [
        "cd_usuario",
        "cd_endereco",
        "no_usuario",
        "cd_tipo_usuario"
    ]

    query_exists = f"""
        SELECT {", ".join(columns)}
        FROM {table_name}
        WHERE 1 = 1
            {"".join(where)}
    """

    ref_user = conn.execute(query_exists)

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

    regex_email = r"([A-Za-z0-9]+)(\.[A-za-z0-9]*)@([A-Za-z0-9]+)(\.[A-za-z0-9]*)"

    erro = None

    try:
        address.get(
            conn=conn,
            id_address=id_address
        )[0]["cd_endereco"]
    except:
        erro = f"O cd_endereco '{id_address}' não foi encontrado"
    else:
        if not re.search(regex_email, realy_user_email):
            erro = f"O email '{realy_user_email}' é inválido"
        
        elif not realy_user_name or len(realy_user_name) < 4:
            erro = f"O nome do usuário deve possuir no mínimo 4 caracteres"
        
        elif len(user_password) < 8:
            erro = f"A senha do usuário deve possuir no mínimo 8 caracteres"
        
        elif user_type not in apit.get_all_valid_users_types():
            erro = f"Tipo '{user_type}' de usuário inválido"
        
        elif user_type > 1 and (not realy_user_adm_email or not user_adm_password):
            erro = (
                f"Para criar esse tipo de usuário é necessário informar as "
                f"credenciais de um administrador"
            )

        elif user_type > 1 and not apit.authenticate(
            conn=conn,
            type=4,
            email=realy_user_adm_email,
            password=user_adm_password
        ):
            erro = f"Credenciais do administrador inválida"

    if bool(erro):
        return apit.get_response(
            response={
                "message": erro
            },
            status=500
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

    try:
        conn.exec_driver_sql(query_insert, cv)
    except:
        return apit.get_response(
            response={
                "message": f"O ds_email '{realy_user_email}' já está cadastrado"
            },
            status=409
        )

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
