# ProtoRH

## Sommaire
1. [Installations](#installations)
    1. [Installations classiques](#installations-classiques)
    2. [Installations développeurs](#installations-développeurs)
2. [Configuration](#configuration)
    1. [Création de l'utilisateur postgresql](#création-de-lutilisateur-postgresql)
    2. [Configuration de l'accès à la DB](#configuration-de-laccès-à-la-db)
3. [Utilisation](#utilisation)
4. [Tests](#tests)
5. [Endpoints](#endpoints)
    1. [/hello](#hello)
    2. [Users](#users)
        1. [/user/create](#usercreate)
        2. [/connect](#connect)
        3. [/user/{user_id}](#useruser_id)
        4. [/user/update](#userupdate)
        5. [/user/password](#userpassword)
        6. [/upload/picture/user/{user_id}](#uploadpictureuseruser_id)
        7. [/picture/user/{user_id}](#pictureuseruser_id)
    3. [Departments](#departments)
        1. [/departements/{department_id}/users/add](#departementsdepartment_idusersadd)
        2. [/departements/{department_id}/users/remove](#departementsdepartment_idusersremove)
        3. [/departements/{department_id}/users](#departementsdepartment_idusers)
    4. [RequestRH](#requestrh)
        1. [/rh/msg/add](#rhmsgadd)
        2. [/rh/msg/remove](#rhmsgremove)
        3. [/rh/msg/update](#rhmsgupdate)
        4. [/rh/msg](#rhmsg)
___

## Installations

Pour ce projet plusieurs configurations d'installations existent, la configuration classique permettant d'éxécuter l'API et de l'utiliser ainsi que la configuration développeurs permettant aux développeurs d'accéder à tous les outils nécessaires au développement de l'API.

### Installations classiques

Pour effectuer les installations classiques, vous devez éxécuter la commande suivante:
```bash
bash build.sh
```
Celle-ci installe les packages suivants:
- **Packages linux**:
    - curl
    - python3
    - python3-pip
    - uvicorn postgresql
    - postgresql-client
- **Packages python**:
    - sqlalchemy
    - sqlalchemy-utils
    - psycopg2-binary
    - pydantic
    - fastapi
    - pyjwt
    - python-dotenv
    - python-multipart
    - Pillow

### Installations développeurs

Pour effectuer les installations développeurs, vous devez éxécuter la commande suivante:
```bash
bash build.sh --dev
```
Celle-ci installe deux packages linux supplémentaires:
- pycodestyle
- pylint

## Configuration

### Création de l'utilisateur postgresql

#### Étape 1
```bash
sudo nano /etc/postgresql/{version}/main/pg_hba.conf
```
Remplacez cette ligne:
```bash
# "local" is for Unix domain socket connections only
local   all             postgres                                peer
```
par:
```bash
# "local" is for Unix domain socket connections only
local   all             postgres                                md5
```
#### Étape 2
```bash
sudo service postgresql start
```
#### Étape 3
```bash
sudo -u postgres psql
```
#### Étape 4
```sql
postgres=# CREATE USER admin PASSWORD 'admin';
ALTER USER admin CREATEDB;
ALTER USER admin WITH SUPERUSER;
\q
```

### Configuration de l'accès à la DB

Pour configurer l'accès à la DB voir changer certaines valeurs relatives à la DB, vous devez éditer le fichier [protorh.env](protorh.env) présent à la racine du projet.

- `salt` Sel utilisé pour le hachage des mots de passe
- `SECRET_KEY` Clé secrète utilisée pour la génération des JWT
- `DATABASE_HOST` Adresse du serveur de la DB
- `DATABASE_PORT` Port utilisé par la DB
- `DATABASE_NAME` Nom de la DB
- `DATABASE_USER` Nom de l'utilisateur ayant accès à la DB (voir [Création de l'utilisateur postgresql](#création-de-lutilisateur-postgresql))
- `DATABASE_PASSWORD` Mot de passe de l'utilisateur ayant accès à la DB

## Utilisation

Il est très simple d'utiliser l'API, il suffit simplement d'éxécuter le script [run.sh](run.sh) en éxécutant la commande suivante:
```bash
bash run.sh
```
Si vous souhaitez effectuer des requêtes à l'API, je vous conseille de consulter la documentation des différents endpoints (voir [Endpoints](#endpoints)) ou de consulter la section [Tests](#tests).

## Tests

Lors du développement de ce projet, nous avons été amenés à devoir tester les différents endpoints de notre API. Dans le but de faciliter cette tâche, nous avons utilisé et mis en place plusieurs outils.



Le premier de ces outils est la page "Docs" fournie par FastAPI, accessible à l'adresse [http://localhost:4242/docs#/](http://localhost:4242/docs#/) lorsque l'API est en cours d'éxécution. Cette page offre une interface graphique qui simplifie l'envoi de requêtes à l'API, ce qui nous a grandement facilité la tâche lors des tests.

Le ou les seconds outils que nous avons utilisé ont été différents scripts bash réalisés par nos soins et disponibles dans le répertoire `tests/` à la racine du projet. Ces scripts ont été conçus pour automatiser l'envoi de requêtes à l'API en utilisant la commande `curl`. Ils ont considérablement amélioré l'efficacité de nos tests en nous permettant de tester les versions finales de nos endpoints qui nécessitaient l'utilisation de JWT, une fonctionnalité que l'interface "Docs" de FastAPI ne nous offrait pas.

## Endpoints

#### /hello

```python
@app.get('/hello')
async def hello()
```

- **URL:** '/hello'
- **Méthode:** POST
- **Description:** Retourne 'Hello World !' dans un objet JSON.
- **Sortie:**
```json
"string"
```
- **curl:**
```bash
curl -X GET http://{server_IP}/hello
```
- **Test Script:**
```bash
bash tests/hello.sh
```

### Users

#### /user/create

```python
@app.post('/user/create')
async def create_user(request: Create)
```

- **URL:** '/user/create/'
- **Méthode:** POST
- **Description:** Ajoute un utilisateur à la Base de Données(DB).
- **Request Body:**
```json
{
  "email": "string",
  "password": "string",
  "firstname": "string",
  "lastname": "string",
  "birthday_date": "YYYY-MM-DD",
  "adress": "string",
  "postal_code": "string"
}
```
- **Sortie:**
```json
"string"
```
- **curl:**
```bash
curl -X POST -H "Content-Type: application/json" -d "{Request Body}" http://{server_IP}/user/create
```
- **Test Script:**
```bash
bash tests/create_user.sh
```

#### /connect

```python
@app.post('/connect')
async def connect(request: Connect)
```

- **URL:** '/connect'
- **Méthode:** POST
- **Description:** Retourne un token d'authentification JWT si les informations d'authentification entrées sont correctes.
- **Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```
- **Sortie:**
```json
"string"
```
- **curl:**
```bash
curl -X POST -H "Content-Type: application/json" -d "{Request Body}" http://{server_IP}/connect
```
- **Test Script:**
```bash
bash tests/connect.sh
```

#### /user/{user_id}

```python
@app.get('/user/{user_id}')
async def get_user(user_id: int, token: Annotated[str, Depends(oauth2_scheme)])
```

- **URL:** '/user/{user_id}'
- **Méthode:** GET
- **Description:** Retourne les informations d'un utilisateur ; certaines informations ne sont accessibles qu'aux utilisateurs ayant le statut d'administrateur.
- **Sortie:**
```json
{
    "email": "string",
    "firstname": "string",
    "lastname": "string",
    "birthday_date": "YYYY-MM-DD",
    "adress": "string",
    "postal_code": "string",
    "age": int,
    "meta": json,
    "registration_date": "YYYY-MM-DD",
    "token": "string",
    "role": "string"
}
```
- **curl:**
```bash
curl -X GET -H "Authorization: Bearer {jwt}" http://{server_IP}/user/{user_id}
```
- **Test Script:**
```bash
bash tests/get_user.sh
```

#### /user/update

```python
@app.post('/user/update')
async def update_user(request: Update, token: Annotated[str, Depends(oauth2_scheme)])
```

- **URL:** '/user/update'
- **Méthode:** POST
- **Description:** Mets à jour les informations relatives à un utilisateur.
- **Request Body:**
```json
{
    "id": int,
    "email": "string",
    "firstname": "string",
    "lastname": "string",
    "birthday_date": "YYYY-MM-DD",
    "adress": "string",
    "postal_code": "string",
    "role": "string"
}
```
- **Sortie:**
```json
"string"
```
- **curl:**
```bash
curl -X POST -H "Authorization: Bearer {jwt}" -H "Content-Type: application/json" -d "{Request Body}" http://{server_IP}/user/update
```
- **Test Script:**
```bash
bash tests/update.sh
```

#### /user/password

```python
@app.post('/user/password')
async def update_password(request: UpdatePassword)
```

- **URL:** '/user/password'
- **Méthode:** POST
- **Description:** Mets à jour le mot de passe d'un utilisateur.
- **Request Body:**
```json
{
    "email": "string",
    "password": "string",
    "new_password": "string",
    "repeat_new_password": "string"
}
```
- **Sortie:**
```json
"string"
```
- **curl:**
```bash
curl -X POST -H "Content-Type: application/json" -d "{Request Body}" http://{server_IP}/user/password
```
- **Test Script:**
```bash
bash tests/update_password.sh
```

#### /upload/picture/user/{user_id}

```python
@app.post('/upload/picture/user/{user_id}')
async def upload_profile_picture(user_id: int, file: UploadFile = File(...))
```

- **URL:** '/upload/picture/user/{user_id}'
- **Méthode:** POST
- **Description:** Permet d'upload une photo de profile associée à un utilisateur.
- **Sortie:**
```json
"string"
```

#### /picture/user/{user_id}

```python
@app.get('/picture/user/{user_id}')
async def get_profile_picture(user_id: int)
```

- **URL:** '/picture/user/{user_id}'
- **Méthode:** GET
- **Description:** Retourne le chemin de la photo de profile associée à un utilisateur.
- **Sortie:**
```json
"string"
```

### Departments

#### /departements/{department_id}/users/add

```python
@app.post('/departements/{department_id}/users/add')
async def add_users_to_department(department_id: int, request: AddUserToDepartment, token: Annotated[str, Depends(oauth2_scheme)])
```

- **URL:** '/departements/{department_id}/users/add'
- **Méthode:** POST
- **Description:** Associe une liste d'utilisateurs à un département dans la DB.
- **Request Body:**
```json
{
    "user_ids": int[]
}
```
- **Sortie:**
```json
[
    {
        "id": int,
        "email": "string",
        "firstname": "string",
        "lastname": "string"
    }
]
```
- **curl:**
```bash
curl -X POST -H "Authorization: Bearer {jwt}" -H "Content-Type: application/json" -d "{Request Body}" http://{server_IP}/departements/{department_id}/users/add
```
- **Test Script:**
```bash
bash tests/add_users_to_department.sh
```

#### /departements/{department_id}/users/remove

```python
@app.post('/departements/{department_id}/users/remove')
async def remove_users_from_department(department_id: int, request: RemoveUserFromDepartment, token: Annotated[str, Depends(oauth2_scheme)])
```

- **URL:** '/departements/{department_id}/users/remove'
- **Méthode:** POST
- **Description:** Supprime l'association d'une liste d'utilisateurs à un département dans la DB.
- **Request Body:**
```json
{
    "user_ids": int[]
}
```
- **Sortie:**
```json
[
    {
        "id": int,
        "email": "string",
        "firstname": "string",
        "lastname": "string"
    }
]
```
- **curl:**
```bash
curl -X POST -H "Authorization: Bearer {jwt}" -H "Content-Type: application/json" -d "{Request Body}" http://{server_IP}/departements/{department_id}/users/remove
```
- **Test Script:**
```bash
bash tests/remove_users_from_department.sh
```

#### /departements/{department_id}/users

```python
@app.get('/departements/{department_id}/users')
async def get_users_from_department(department_id: int, token: Annotated[str, Depends(oauth2_scheme)])
```

- **URL:** '/departements/{department_id}/users'
- **Méthode:** GET
- **Description:** Affiche la liste des utilisateurs associés à un département.
- **Sortie:**
```json
[
    {
        "id": int,
        "email": "string",
        "firstname": "string",
        "lastname": "string"
    }
]
```
- **curl:**
```bash
curl -X GET -H "Authorization: Bearer {jwt}" http://{server_IP}/departements/{department_id}/users
```
- **Test Script:**
```bash
bash tests/get_users_from_department.sh
```

### RequestRH

#### /rh/msg/add

```python
@app.post('/rh/msg/add')
async def add_request_rh(request: CreateRequestRH, token: Annotated[str, Depends(oauth2_scheme)])
```

- **URL:** '/rh/msg/add'
- **Méthode:** POST
- **Description:** Ajoute une requête rh à la DB.
- **Request Body:**
```json
{
    "user_id": int,
    "content": "string"
}
```
- **Sortie:**
```json
"string"
```
- **curl:**
```bash
curl -X POST -H "Authorization: Bearer {jwt}" -H "Content-Type: application/json" -d "{Request Body}" http://{server_IP}/rh/msg/add
```
- **Test Script:**
```bash
bash tests/add_request_rh.sh
```

#### /rh/msg/remove

```python
@app.post('/rh/msg/remove')
async def remove_request_rh(request: RemoveRequestRH, token: Annotated[str, Depends(oauth2_scheme)])
```

- **URL:** '/rh/msg/remove'
- **Méthode:** POST
- **Description:** Ferme une requête rh mais ne la supprime pas de la DB.
- **Request Body:**
```json
{
    "id": int
}
```
- **Sortie:**
```json
"string"
```
- **curl:**
```bash
curl -X POST -H "Authorization: Bearer {jwt}" -H "Content-Type: application/json" -d "{Request Body}" http://{server_IP}/rh/msg/remove
```
- **Test Script:**
```bash
bash tests/remove_request_rh.sh
```

#### /rh/msg/update

```python
@app.post('/rh/msg/update')
async def update_request_rh(request: UpdateRequestRH, token: Annotated[str, Depends(oauth2_scheme)])
```

- **URL:** '/rh/msg/update'
- **Méthode:** POST
- **Description:** Mets à jour une requête rh.
- **Request Body:**
```json
{
    "id": int,
    "content": "string"
}
```
- **Sortie:**
```json
"string"
```
- **curl:**
```bash
curl -X POST -H "Authorization: Bearer {jwt}" -H "Content-Type: application/json" -d "{Request Body}" http://{server_IP}/rh/msg/update
```
- **Test Script:**
```bash
bash tests/update_request_rh.sh
```

#### /rh/msg/

```python
@app.get('/rh/msg/')
async def get_request_rh(token: Annotated[str, Depends(oauth2_scheme)])
```

- **URL:** '/rh/msg/'
- **Méthode:** GET
- **Description:** Permet à l'utilisateur de récupérer l'ensemble des requêtes auxquelles il a accès.
- **Sortie:**
```json
[
    {
        "id": int,
        "user_id": int,
        "content": "string",
        "registration_date": "YYYY-MM-DD",
        "visibility": boolean,
        "close": boolean,
        "last_action": "YYYY-MM-DD",
        "content_history": [
        {
            "author": int,
            "content": "string",
            "date": "YYYY-MM-DD"
        },
        {
            "author": int,
            "content": "string",
            "date": "YYYY-MM-DD"
        }
        ],
        "delete_date": "YYYY-MM-DD"
    }
]
```
- **curl:**
```bash
curl -X GET -H "Authorization: Bearer {jwt}" http://{server_IP}/rh/msg/
```
- **Test Script:**
```bash
bash tests/get_requests_rh.sh
```