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

