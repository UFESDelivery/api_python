from flask import Flask
from flask import request

from flask_cors import CORS

import os

import dotenv

import datetime as dt

import src.api_tools as apit
import src.ddl as ddl
import src.dml as dml
import src.controllers.user as user
import src.controllers.state as state
import src.controllers.address as address
import src.controllers.city as city
import src.controllers.order as order
import src.controllers.product as produtc
import src.controllers.product_order as product_order


dotenv.load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_SERV = os.getenv("DB_SERV")
DB_PORT = os.getenv("DB_PORT")

APP_PORT = os.getenv("APP_PORT")
APP_HOST = os.getenv("APP_HOST")
APP_DEBUG = os.getenv("APP_DEBUG")

SSL_CONTEXT = (
    "./server.cert",
    "./server.key"
)

DB_CONN = apit.conn_mysql(
    username=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    server=DB_SERV,
    port=DB_PORT
)

APP = Flask(__name__)
CORS(APP)


@APP.route("/", methods=["GET"])
def index():
    return apit.get_response(
        response={
            "message": "Bem vindo ao UFES Delivery"
        },
        status=200
    )


@APP.route("/db/reset", methods=["POST"])
def reset_db():
    json: dict = request.get_json()

    if not apit.authenticate(
        conn=DB_CONN,
        type_=4,
        email=json.get("email"),
        password=json.get("senha")
    ):
        return apit.get_response(
            response={
                "message": "Email ou Senha inválidos"
            },
            status=400
        )

    ddl.recreate_all(DB_CONN)
    dml.insert_all(DB_CONN)

    return apit.get_response(
        response={
            "message": "O banco de dados foi redefinido para o padrão inicial"
        },
        status=200
    )


@APP.route("/state/get/<uf>", methods=["GET"])
def get_all_states(
    uf: str
):
    realy_uf = apit.treat_str(uf)

    response = {}
    
    if realy_uf == "ALL":
        all_states = state.get(
            conn=DB_CONN,
            like=False
        )

        qtt_states = len(all_states)

        if qtt_states > 0:
            response["message"] = f"'{qtt_states}' estados encontrados"
            response["result"] = all_states
            status = 200
        
        else:
            response["message"] = "Nenhum estado encontrado"
            status = 400

    elif realy_uf is not None:
        one_state = state.get(
            conn=DB_CONN,
            id_uf=realy_uf,
            like=False
        )

        if len(one_state) > 0:
            response["message"] = f"Estado encontrado"
            response["result"] = one_state[0]
            status = 200
        
        else:
            response["message"] = f"O cd_uf '{realy_uf}' não foi encontrado"
            status = 400

    else:
        response["message"] = f"Parâmetros incorretos ou faltando"
        status = 400

    return apit.get_response(
        response=response,
        status=status
    )


@APP.route("/city/new", methods=["POST"])
def new_city():
    json: dict = request.get_json()

    kwargs = {
        "name": json.get("nome"),
        "uf": json.get("uf")
    }

    if not apit.validate_parameters(kwargs):
        return apit.get_response(
            response={
                "message": "Parâmetros incorretos ou faltando"
            },
            status=400
        )

    return city.new(
        conn=DB_CONN,
        **kwargs
    )


@APP.route("/address/new", methods=["POST"])
def new_address():
    json: dict = request.get_json()

    kwargs = {
        "id_city": apit.treat_int(json.get("cd_cidade")),
        "street_name": json.get("no_logradouro"),
        "district_name": json.get("no_bairro"),
        "number": json.get("ds_numero"),
        "postal_code": apit.treat_postal_code(json.get("nu_cep")),
        "complement": json.get("ds_complemento")
    }

    ignore_kwargs = [
        "complement"
    ]

    if not apit.validate_parameters(kwargs, ignore_kwargs):
        return apit.get_response(
            response={
                "message": "Parâmetros incorretos ou faltando"
            },
            status=400
        )

    return address.new(
        conn=DB_CONN,
        **kwargs
    )


@APP.route("/user/get/address", methods=["POST"])
def get_user_address():
    json: dict = request.get_json()

    response = {}
    status = 200

    kwargs = {
        "id_user": apit.treat_int(json.get("cd_usuario")),
        "user_email": apit.treat_str(json.get("ds_email")),
        "user_password": json.get("cd_senha"),
        "user_token": json.get("cd_token"),
    }

    ignore_args = [
        "user_email",
        "user_password",
        "user_token"
    ]

    if not apit.validate_parameters(kwargs, ignore_args):
        response["message"] = "Parâmetros incorretos ou faltando"
        status = 400

    else:
        logged = False

        for ut in apit.get_all_valid_users_types():
            logged = apit.authenticate(
                conn=DB_CONN,
                type_=ut,
                id_user=kwargs["id_user"],
                token=kwargs["user_token"],
                email=kwargs["user_email"],
                password=kwargs["user_password"]
            )
            
            if logged:
                user_ = user.get(
                    conn=DB_CONN,
                    id_user=kwargs["id_user"]
                )[0]

                user_address = address.get(
                    conn=DB_CONN,
                    id_address=user_["cd_endereco"]
                )

                response["message"] = (
                    f"Endereço do usuário '{user_['no_usuario']}'"
                )

                response["result"] = user_address[0]

                status = 200

                break

        if not logged:
            response["message"] = "Credenciais inválidas"
            status = 401

    return apit.get_response(
        response=response,
        status=status
    )


@APP.route("/user/get/client/<id_>", methods=["GET"])
def get_user(
    id_: int | str
):
    treat_id = apit.treat_int(id_)

    response = {}
    
    if str(id_) == "all":
        all_clients = user.get(
            conn=DB_CONN,
            user_type=1,
            like=False
        )

        qtt_clients = len(all_clients)

        if qtt_clients > 0:
            response["message"] = f"'{qtt_clients}' clientes encontrados"
            response["result"] = all_clients
            status = 200
        
        else:
            response["message"] = "Nenhum cliente encontrado"
            status = 400

    elif treat_id is not None:
        one_client = user.get(
            conn=DB_CONN,
            id_user=treat_id,
            user_type=1,
            like=False
        )

        if len(one_client) > 0:
            response["message"] = f"Cliente encontrado"
            response["result"] = one_client[0]
            status = 200
        
        else:
            response["message"] = f"O cd_cliente '{treat_id}' não foi encontrado"
            status = 400

    else:
        response["message"] = f"Parâmetros incorretos ou faltando"
        status = 400

    return apit.get_response(
        response=response,
        status=status
    )


@APP.route("/user/new", methods=["POST"])
def new_user():
    json: dict = request.get_json()

    kwargs = {
        "id_address": apit.treat_int(json.get("cd_endereco")),
        "user_email": json.get("email_usuario"),
        "user_password": json.get("senha_usuario"),
        "user_name": json.get("nome_usuario"),
        "user_type": apit.treat_int(json.get("tipo_usuario")),
        "user_adm_email": json.get("email_adm"),
        "user_adm_password": json.get("senha_adm")
    }

    ignore_kwargs = [
        "user_adm_email",
        "user_adm_password"
    ]

    if not apit.validate_parameters(kwargs, ignore_kwargs):
        return apit.get_response(
            response={
                "message": "Parâmetros incorretos ou faltando"
            },
            status=400
        )

    return user.new(
        conn=DB_CONN,
        **kwargs
    )


@APP.route("/order/get", methods=["POST"])
def get_customized_orders():
    json: dict = request.get_json()

    last_date_modify: dict = json.get("dt_ultima_alteracao")
    last_min_date_modify: dict = json.get("dt_min_ultima_alteracao")
    last_max_date_modify: dict = json.get("dt_max_ultima_alteracao")

    date = None
    min_date = None
    max_date = None

    default_date = dt.datetime(1, 1, 1, 0, 0, 0, 0)

    if last_date_modify is not None:
        date = dt.datetime(
            day=apit.treat_int(last_date_modify.get("dia")) or 1,
            month=apit.treat_int(last_date_modify.get("mes")) or 1,
            year=apit.treat_int(last_date_modify.get("ano")) or 1,
            hour=apit.treat_int(last_date_modify.get("hora")) or 0,
            minute=apit.treat_int(last_date_modify.get("minuto")) or 0,
            second=apit.treat_int(last_date_modify.get("segundo")) or 0,
            microsecond=apit.treat_int(last_date_modify.get("microsegundo")) or 0
        )

        if date == default_date:
            date = None

    if last_min_date_modify is not None:
        min_date = dt.datetime(
            day=apit.treat_int(last_min_date_modify.get("dia")) or 1,
            month=apit.treat_int(last_min_date_modify.get("mes")) or 1,
            year=apit.treat_int(last_min_date_modify.get("ano")) or 1,
            hour=apit.treat_int(last_min_date_modify.get("hora")) or 0,
            minute=apit.treat_int(last_min_date_modify.get("minuto")) or 0,
            second=apit.treat_int(last_min_date_modify.get("segundo")) or 0,
            microsecond=apit.treat_int(last_min_date_modify.get("microsegundo")) or 0
        )

        if min_date == default_date:
            min_date = None

    if last_max_date_modify is not None:
        max_date = dt.datetime(
            day=apit.treat_int(last_max_date_modify.get("dia")) or 1,
            month=apit.treat_int(last_max_date_modify.get("mes")) or 1,
            year=apit.treat_int(last_max_date_modify.get("ano")) or 1,
            hour=apit.treat_int(last_max_date_modify.get("hora")) or 0,
            minute=apit.treat_int(last_max_date_modify.get("minuto")) or 0,
            second=apit.treat_int(last_max_date_modify.get("segundo")) or 0,
            microsecond=apit.treat_int(last_max_date_modify.get("microsegundo")) or 0
        )

        if max_date == default_date:
            max_date = None

    orders = order.get(
        conn=DB_CONN,
        id_order=json.get("cd_pedido"),
        id_user=json.get("cd_usuario"),
        id_status=json.get("cd_status"),
        min_id_status=json.get("cd_min_status"),
        max_id_status=json.get("cd_max_status"),
        value_order=json.get("vl_total_compra"),
        min_value_order=json.get("vl_min_total_compra"),
        max_value_order=json.get("vl_max_total_compra"),
        date=date,
        min_date=min_date,
        max_date=max_date,
        closed_order=json.get("fl_pedidos_fechados")
    )

    qtt_orders = len(orders)

    if qtt_orders > 0:
        response = {
            "message": f"'{qtt_orders}' pedidos encontrados",
            "result": orders
        }

        status = 200
    
    else:
        response = {
            "message": "Nenhum pedido encontrado"
        }

        status = 400

    return apit.get_response(
        response=response,
        status=status
    )


@APP.route("/order/get/<id_>", methods=["GET"])
def get_all_order(
    id_: int | str
):
    treat_id = apit.treat_int(id_)

    response = {}
    
    if str(id_) == "all":
        all_orders = order.get(DB_CONN)

        if bool(all_orders):
            response["message"] = f"Todos os pedidos"
            response["result"] = all_orders
            status = 200
        
        else:
            response["message"] = f"Não existem pedidos cadastrados"
            status = 400

    elif treat_id is not None:
        one_order = order.get(DB_CONN, id_order=treat_id)

        one_order = (
            one_order[0]
            if bool(one_order)
            else None
        )

        if one_order is None:
            response["message"] = f"O cd_pedido '{treat_id}' não foi encontrado"
            status = 400
        
        else:
            response["message"] = f"cd_pedido '{treat_id}' encontrado"
            response["result"] = one_order
            status = 200
    
    else:
        response["message"] = f"Parâmetros incorretos ou faltando"
        status = 400

    return apit.get_response(
        response=response,
        status=status
    )


@APP.route("/order/new", methods=["POST"])
def new_order():
    json: dict = request.get_json()

    kwargs = {
        "id_user": apit.treat_int(json.get("cd_usuario"))
    }

    if not apit.validate_parameters(kwargs):
        return apit.get_response(
            response={
                "message": "Parâmetros incorretos ou faltando"
            },
            status=400
        )

    return order.new(
        conn=DB_CONN,
        **kwargs
    )


@APP.route("/product/get/<id_>", methods=["GET"])
def get_all_product(
    id_: int | str
):
    treat_id = apit.treat_int(id_)

    response = {}
    
    if str(id_) == "all":
        all_product = produtc.get(
            conn=DB_CONN,
            like=False
        )

        qtt_products = len(all_product)

        if qtt_products > 0:
            response["message"] = f"'{qtt_products}' produtos encontrados"
            response["result"] = all_product
            status = 200
        
        else:
            response["message"] = "Nenhum produto encontrado"
            status = 400

    elif treat_id is not None:
        one_product = produtc.get(
            conn=DB_CONN,
            id_product=treat_id
        )

        if len(one_product) > 0:
            response["message"] = f"Produto encontrado"
            response["result"] = one_product[0]
            status = 200
        
        else:
            response["message"] = f"O cd_produto '{treat_id}' não foi encontrado"
            status = 400

    else:
        response["message"] = f"Parâmetros incorretos ou faltando"
        status = 400

    return apit.get_response(
        response=response,
        status=status
    )


@APP.route("/order/add/product", methods=["POST"])
def new_product_order():
    json: dict = request.get_json()

    kwargs = {
        "id_order": apit.treat_int(json.get("cd_pedido")),
        "id_product": apit.treat_int(json.get("cd_produto")),
        "qtt_items": apit.treat_int(json.get("qt_itens"))
    }

    if not apit.validate_parameters(kwargs):
        return apit.get_response(
            response={
                "message": "Parâmetros incorretos ou faltando"
            },
            status=400
        )

    return product_order.new(
        conn=DB_CONN,
        **kwargs
    )


if __name__ == "__main__":
    msg = (
        "\nPara rodar essa aplicação no linux\n"
        "1º export FLASK_APP=app.py\n"
        "2º flask run\n"
    )

    print(msg)

    APP.run(
        debug=APP_DEBUG,
        host=APP_HOST,
        port=APP_PORT,
        ssl_context=SSL_CONTEXT
    )
