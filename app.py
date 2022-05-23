from flask import Flask
from flask import request

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

# DB_USER = "root"
# DB_PASS = "1234"
# DB_NAME = "ufesdelivery"
# DB_SERV = "localhost"
# DB_PORT = 5070

DB_CONN = apit.conn_mysql(
    username=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    server=DB_SERV,
    port=DB_PORT
)

APP = Flask(__name__)


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
        type=4,
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
        "street_name": json.get("logradouro"),
        "district_name": json.get("bairro"),
        "number": json.get("numero"),
        "postal_code": apit.treat_postal_code(json.get("cep"))
    }

    if not apit.validate_parameters(kwargs):
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

    if last_date_modify is not None:
        date = dt.datetime(
            day=last_date_modify.get("dia"),
            month=last_date_modify.get("mes"),
            year=last_date_modify.get("ano"),
            hour=last_date_modify.get("hora"),
            minute=last_date_modify.get("minuto"),
            second=last_date_modify.get("segundo"),
            microsecond=last_date_modify.get("microsegundo")
        )

    if last_min_date_modify is not None:
        min_date = dt.datetime(
            day=last_min_date_modify.get("dia"),
            month=last_min_date_modify.get("mes"),
            year=last_min_date_modify.get("ano"),
            hour=last_min_date_modify.get("hora"),
            minute=last_min_date_modify.get("minuto"),
            second=last_min_date_modify.get("segundo"),
            microsecond=last_min_date_modify.get("microsegundo")
        )

    if last_max_date_modify is not None:
        max_date = dt.datetime(
            day=last_max_date_modify.get("dia"),
            month=last_max_date_modify.get("mes"),
            year=last_max_date_modify.get("ano"),
            hour=last_max_date_modify.get("hora"),
            minute=last_max_date_modify.get("minuto"),
            second=last_max_date_modify.get("segundo"),
            microsecond=last_max_date_modify.get("microsegundo")
        )

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

    if len(orders) > 0:
        response = {
            "message": "Todos os pedidos encontrados",
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
            conn=DB_CONN
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

    APP.run(debug=True, host="0.0.0.0")
