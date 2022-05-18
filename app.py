from flask import Flask
from flask import request

import os

import dotenv

import src.api_tools as apit
import src.ddl as ddl
import src.dml as dml
import src.controllers.user as user
import src.controllers.address as address
import src.controllers.city as city
import src.controllers.order as order
import src.controllers.product_order as product_order


dotenv.load_dotenv()

DB_USER = os.getenv("DB_USER")
# DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
# DB_SERV = os.getenv("DB_SERV")
# DB_PORT = 3306

DB_PASS = 1234
DB_SERV = "localhost"
DB_PORT = 5070

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


@APP.route("/city/new", methods=["POST"])
def new_city():
    json: dict = request.get_json()

    kwargs = {
        "name": json.get("nome"),
        "uf": json.get("uf")
    }

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

    return user.new(
        conn=DB_CONN,
        **kwargs
    )


@APP.route("/order/get/all", methods=["GET"])
@APP.route("/order/get/<id_>", methods=["GET"])
def get_all_order(
    id_: int | str = None
):
    treat_id = apit.treat_int(id_)

    response = {}
    
    if id_ is None:
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
        response["message"] = f"Parâmetros incorretos"
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

    return order.new(
        conn=DB_CONN,
        **kwargs
    )


@APP.route("/order/add/product", methods=["POST"])
def new_product_order():
    json: dict = request.get_json()

    kwargs = {
        "id_order": apit.treat_int(json.get("cd_pedido")),
        "id_product": apit.treat_int(json.get("cd_produto")),
        "qtt_items": apit.treat_int(json.get("qt_itens"))
    }

    if (
        kwargs["id_order"] is None
        or kwargs["id_product"] is None
        or kwargs["qtt_items"] is None
    ):
        return apit.get_response(
            response={
                "message": "parâmetros incorretos"
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
