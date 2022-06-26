# API Python
API backend do site UFES Delivery usando python

***

# Open Endpoints

***

## Wellcome

URL: `/`

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
