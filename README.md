# API Python
API backend do site UFES Delivery usando python

***

# Open Endpoints

***

## Wellcome

URL: `/`

Method: `GET`

Success Response Code: `200`

Content Result:
```json
{
    "message": "Bem vindo ao UFES Delivery"
}
```

***

## States

URL: `/state/get/<uf>`

Method: `GET`

Parameter `uf`: state abbreviation or `ALL`

Success Response Code: `200`

**Content Result:**

If `uf`: `AC`
```json
{
    "message": "Estado encontrado",
    "result": {
        "cd_estado": 1,
        "cd_uf": "AC",
        "ds_estado": "ACRE"
    }
}
```
If `uf`: `ALL`
```json
{
    "message": "'27' estados encontrados",
    "result": [
        {
            "cd_estado": 1,
            "cd_uf": "AC",
            "ds_estado": "ACRE"
        },
        ...
        {
            "cd_estado": 27,
            "cd_uf": "TO",
            "ds_estado": "TOCANTINS"
        }
    ]
}
```

Error Response Code: `400`

**Possible Messages Error:**
```json
{
    "message": "Nenhum estado encontrado"
}
```
```json
{
    "message": "O cd_uf '7' não foi encontrado"
}
```
```json
{
    "message": "Parâmetros incorretos ou faltando"
}
```

***

## City

URL: `/city/new`

Method: `POST`

**Possibles Parameters JSON:**
```json
{
    "nome": "",     // Nome da cidade   - Obrigatório
    "uf": ""        // Sigla do estado  - Obrigatório
}
```

Success Response Code: `201`

**Content Result:**
```json
{
    "message": "A cidade 'LINHARES' foi criada com sucesso",
    "id_city": 1
}
```

Error Response Code: `400`

**Content Result:**
```json
{
    "message": "Parâmetros incorretos ou faltando"
}
```

Error Response Code: `409`

**Content Result:**
```json
{
    "message": "A cidade 'LINHARES' já está cadastrada",
    "id_city": 1
}
```

Error Response Code: `500`

**Content Result:**
```json
{
    "message": "O nome da cidade 'A' é inválido"
}
```
```json
{
    "message": "A UF 'AFD' do estado é inválida"
}
```
```json
{
    "message": "O estado 'AF' não existe no banco"
}
```

***

## Address

URL: `/address/new`

Method: `POST`

**Possibles Parameters JSON:**
```json
{
    "cd_cidade": 1,      // ID da cidade               - Obrigatório
    "no_logradouro": "", // Nome do logradouro         - Obrigatório
    "no_bairro": "",     // Nome do bairro             - Obrigatório
    "ds_numero": "",     // Número da Casa/Apartamento - Obrigatório
    "nu_cep": "",        // CEP válido                 - Obrigatório
    "ds_complemento": "" // Complemento                - Opcional
}
```

Success Response Code: `201`

**Content Result:**
```json
{
    "message": "O endereço 'RUA TAL' foi criado com sucesso",
    "id_address": 1
}
```

Error Response Code: `400`

**Content Result:**
```json
{
    "message": "Parâmetros incorretos ou faltando"
}
```

Error Response Code: `409`

**Content Result:**
```json
{
    "message": "O endereço 'RUA TAL' já está cadastrado",
    "id_address": 1
}
```

Error Response Code: `500`

**Content Result:**
```json
{
    "message": "O cd_cidade '0' não existe"
}
```
```json
{
    "message": "Nome do bairro 'None' inválido"
}
```
```json
{
    "message": "Logradouro 'None' inválido"
}
```
```json
{
    "message": "CEP '22222A222' inválido"
}
```
```json
{
    "message": "Número 'None' inválido"
}
```

URL: `/user/get/address`

Method: `POST`

**Possibles Parameters JSON:**
```json
{
    "cd_usuario": 2, // ID do usuário     - Obrigatório
    "ds_email": "",  // E-mail do usuário - Opcional se tiver token
    "cd_senha": "",  // Senha do usuário  - Opcional se tiver token
    "cd_token": ""   // Token do usuário  - Opcional se tiver e-mail e senha
}
```

Success Response Code: `200`

**Content Result:**
```json
{
    "message": "Endereço do usuário 'JUBILEU'",
    "result": {
        "cd_endereco": 1,
        "cd_cidade": 1,
        "no_logradouro": "RUA TAL",
        "no_bairro": "GERÚNDIO",
        "ds_complemento": null,
        "ds_numero": "A208",
        "nu_cep": "29500000"
    }
}
```

Error Response Code: `400`

**Content Result:**
```json
{
    "message": "Parâmetros incorretos ou faltando"
}
```

Error Response Code: `401`

**Content Result:**
```json
{
    "message": "Credenciais inválidas"
}
```

***
