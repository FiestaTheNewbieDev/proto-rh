'''
Main module for ProtoRH.
'''

import os
import json
import hashlib
from datetime import date, datetime, timedelta
import jwt
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database
import sys
from io import BytesIO
from PIL import Image

src_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(src_dir)

from base_controller import get_base
from classes.user import *
from classes.department import *
from classes.request_rh import *

load_dotenv('protorh.env')

DATABASE_URL = [
    'postgresql://',
    f"{os.getenv('DATABASE_USER')}:",
    f"{os.getenv('DATABASE_PASSWORD')}@",
    f"{os.getenv('DATABASE_HOST')}:",
    f"{os.getenv('DATABASE_PORT')}/",
    f"{os.getenv('DATABASE_NAME')}"
]

engine = create_engine(''.join(DATABASE_URL), echo=True)
if not database_exists(engine.url):
    create_database(engine.url, template="template0")


Base = get_base()
Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def user_exists(email: str) -> bool:
    '''
    Check if user exists by checking if his email is already taken.
    Args:
        email (str): Email to check.
    Returns:
        bool: True if exists, False if not.
    '''

    query = text('SELECT id FROM users WHERE email = :email;')

    with engine.begin() as connection:
        result = connection.execute(query, {"email": email}).fetchone()

    return result is not None


def calculate_age(birthday_date: date) -> int:
    '''
    Calculate age by taking a birthday date.
    Args:
        birthday_date (date): Birthday date on which we calculate.
    Returns:
        int: Calculation result.
    '''

    today = date.today()

    return today.year - birthday_date.year - (
        (today.month, today.day) < (birthday_date.month, birthday_date.day))


def gen_token(email: str, firstname: str, lastname: str) -> str:
    '''
    Gen djb2 hash by taking email, firstname and lastname and salt in parameter.
    Args:
        email (str): Email.
        firstname (str): Firstname.
        lastname (str): Lastname.
    Returns:
        str: Hashed string.
    '''

    string = email + firstname + lastname + os.getenv('salt')

    hash_code = 5381
    for char in string:
        hash_code = (hash_code * 33) ^ ord(char)
    result = hash_code & 0xFFFFFFFF

    return result


def gen_password(password: str) -> str:
    '''
    Gen md5 hash by taken string in parameter.
    Args:
        password (str): String to hash.
    Returns:
        str: Hashed string.
    '''

    string = password + os.getenv('salt')

    hash_md5 = hashlib.md5()
    hash_md5.update(string.encode('utf-8'))
    result = hash_md5.hexdigest()

    return result


def gen_jwt(id: int, email: str, role: str) -> str:
    '''
    Gen a JWT with an id, an email and a role in his payload.
    Args:
        id (int): Id to add in payload.
        email (str): Email to add in payload.
        role (str): Role to add in payload.
    Returns:
        str: JWT.
    '''

    payload = {
        'id': id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(minutes=10)
    }

    token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')

    return token


def get_image_dimensions(image_content: bytes):
    """
    Get the dimensions (width and height) of an image from its binary content.

    Args:
        image_content (bytes): The binary content of the image.

    Returns:
        tuple: A tuple containing the width and height of the image.
    """
    with BytesIO(image_content) as image_stream:
        image = Image.open(image_stream)
        width, height = image.size
        return width, height


def save_image(file_name: str, file_content: str):
    if not os.path.exists('assets/picture/profiles'):
        os.makedirs('assets/picture/profiles')

    file_path = os.path.join('assets/picture/profiles', file_name)

    with open(file_path, 'wb') as file:
        file.write(file_content)

    return file_path


# Endpoint : /hello
# Type : GET
# This endpoint returns a json string containing "Hello World !"
@app.get('/hello')
async def hello():
    return {'Hello World !'}


# Endpoint : /user/create
# Type : POST
# This endpoint creates an user in the database
@app.post('/user/create')
async def create_user(request: CreateUser):
    query = text('''
        INSERT INTO users (email, password, firstname, lastname,birthday_date,
            adress, postal_code, age, meta, registration_date, token, role)
        VALUES (:email, :password, :firstname, :lastname, :birthday_date,
            :adress, :postal_code, :age, :meta, :registration_date, :token,
            :role)
    ''')

    if len(request.email) > 320:
        raise HTTPException(status_code=400, detail='Too long email adress')

    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail='Too short password')

    if await user_exists(request.email):
        raise HTTPException(status_code=400, detail='Email already taken')

    values = {
        'email': request.email,
        'password': gen_password(request.password),
        'firstname': request.firstname,
        'lastname': request.lastname,
        'birthday_date': request.birthday_date,
        'adress': request.adress,
        'postal_code': request.postal_code,
        'age': calculate_age(request.birthday_date),
        'meta': json.dumps({}),
        'registration_date': date.today(),
        'token': gen_token(request.email, request.firstname, request.lastname),
        'role': 'user'
    }

    with engine.begin() as connection:
        connection.execute(query, values)
        return {'User created with success'}


# Endpoint : /connect
# Type : POST
# This endpoint returns a JSON Web Token which guarantee that you are allowed
# to use the API
@app.post('/connect')
async def connect(request: Connect):
    password = gen_password(request.password)

    query = text('''
        SELECT id, role FROM users
        WHERE email = :email AND password = :password;
    ''')

    with engine.begin() as connection:
        result = connection.execute(
            query, {"email": request.email,
                    "password": password}).mappings().one_or_none()

    if result:
        jwt = gen_jwt(result['id'], request.email, result['role'])
        return {jwt}

    raise HTTPException(status_code=401)


# Endpoint : /user/{user_id}
# Type : GET
# This endpoint returns informations about specified user
@app.get('/user/{user_id}')
async def get_user(user_id: int,
                   token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        token = jwt.decode(token, os.getenv('SECRET_KEY'),
                           algorithms=["HS256"])

        query = text('SELECT * FROM users WHERE id = :user_id')

        with engine.begin() as connection:
            result = connection.execute(
                query, {"user_id": user_id}).mappings().one_or_none()

        if not result:
            raise HTTPException(status_code=404, detail='User not found')

        if token.get('role') == 'admin':
            values = {
                'email': result['email'],
                'firstname': result['firstname'],
                'lastname': result['lastname'],
                'birthday_date': result['birthday_date'],
                'adress': result['adress'],
                'postal_code': result['postal_code'],
                'age': result['age'],
                'meta': result['meta'],
                'registration_date': result['registration_date'],
                'token': result['token'],
                'role': result['role']
            }
        else:
            values = {
                'email': result['email'],
                'firstname': result['firstname'],
                'lastname': result['lastname'],
                'age': result['age'],
                'registration_date': result['registration_date'],
                'role': result['role']
            }

        return values

    except jwt.ExpiredSignatureError as exception:
        raise HTTPException(status_code=401,
                            detail='Expired token') from exception
    except jwt.DecodeError as exception:
        raise HTTPException(status_code=401,
                            detail='Invalid token') from exception


# Endpoint : /user/update/
# Type : POST
# This endpoint updates values of an user
@app.post('/user/update')
async def update_user(request: UpdateUser,
                      token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        token = jwt.decode(token, os.getenv('SECRET_KEY'),
                           algorithms=["HS256"])

        values = {}

        if token.get('role') == 'admin':
            if request.id:
                values['id'] = request.id
            else:
                values['id'] = token.get('id')
            if request.firstname:
                values['firstname'] = request.firstname
            if request.lastname:
                values['lastname'] = request.lastname
            if request.role:
                values['role'] = request.role
        else:
            if request.id:
                raise HTTPException(status_code=401,
                                    detail='You can only update yourself')
            if request.firstname or request.lastname:
                raise HTTPException(status_code=401,
                                    detail='Not allowed to update your name')
            if request.role:
                raise HTTPException(status_code=401,
                                    detail='Not allowed to update your role')

        if request.email:
            if request.email and len(request.email) > 320:
                raise HTTPException(status_code=400,
                                    detail='Too long email adress')
            if request.email and await user_exists(request.email):
                raise HTTPException(status_code=400,
                                    detail='Email already taken')
            values['email'] = request.email
        if request.birthday_date:
            values['birthday_date'] = request.birthday_date
            values['age'] = calculate_age(request.birthday_date)
        if request.adress:
            values['adress'] = request.adress
        if request.postal_code:
            values['postal_code'] = request.postal_code

        updates = ', '.join(f'{key} = :{key}' for key in values.keys())
        query = text(f'UPDATE users SET {updates} WHERE id = :id')

        with engine.begin() as connection:
            connection.execute(query, values)
            return {'User updated with success'}

    except jwt.ExpiredSignatureError as exception:
        raise HTTPException(status_code=401,
                            detail='Expired token') from exception
    except jwt.DecodeError as exception:
        raise HTTPException(status_code=401,
                            detail='Invalid token') from exception


# Endpoint : /user/password
# Type : POST
# This endpoint updates password of an user
@app.post('/user/password')
async def update_password(request: UpdatePassword):
    password = gen_password(request.password)
    new_password = gen_password(request.new_password)
    repeat_new_password = gen_password(request.repeat_new_password)

    query = text('''
        SELECT id FROM users WHERE email = :email AND password = :password;
    ''')

    with engine.begin() as connection:
        result = connection.execute(
            query, {"email": request.email,
                    "password": password}).mappings().one_or_none()

        if not result:
            raise HTTPException(status_code=401)

        if new_password == repeat_new_password:
            query = text('''
                UPDATE users
                SET password = :password
                WHERE email = :email;
            ''')

            connection.execute(
                query, {"email": request.email, "password": new_password})
            return {'Password updated'}

        raise HTTPException(status_code=400,
                            detail='New passwords should be same')


# Endpoint : /upload/picture/user/{user_id}
# Type : POST
# This endpoint download profile picture of an user
@app.post('/upload/picture/user/{user_id}')
async def upload_profile_picture(user_id: int, file: UploadFile = File(...)):
    with engine.begin() as connection:
        user = connection.execute(text('SELECT token FROM users WHERE id = :user_id'), {"user_id": user_id}).mappings().one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        allowed_extensions = ['gif', 'png', 'jpg', 'jpeg']
        file_extension = file.filename.split('.')[-1]
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400)

        if not file.file.readable():
            raise HTTPException(status_code=400)

        picture = file.file.read()

        width, height = get_image_dimensions(picture)
        if width > 800 and height > 800:
            raise HTTPException(status_code=400)

        for file_name in os.listdir('assets/picture/profiles'):
            if file_name.startswith(user['token'] + '.'):
                os.remove('assets/picture/profiles/' + file_name)

        saved_picture_path = save_image((user['token'] + '.' + file_extension), picture)

        return {saved_picture_path}


# Endpoint : /picture/user/{user_id}
# Type : GET
# This endpoint return the profile picture of an user
@app.get('/picture/user/{user_id}')
async def get_profile_picture(user_id: int):
    with engine.begin() as connection:
        user = connection.execute(text('SELECT token FROM users WHERE id = :user_id'),
                                  {"user_id": user_id}).mappings().one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        for file_name in os.listdir('assets/picture/profiles'):
            if file_name.startswith(user['token'] + '.'):
                return {'assets/picture/profiles' + file_name}

        return {'assets/picture/profiles/pdp_base.png'}


# Endpoint : /departements/{department_id}/users/add
# Type : POST
# This endpoint add a list of users into a department
@app.post('/departements/{department_id}/users/add')
async def add_users_to_department(department_id: int,
                                  request: AddUserToDepartment,
                                  token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        token = jwt.decode(token, os.getenv('SECRET_KEY'),
                           algorithms=["HS256"])

        if token.get('role') != 'admin':
            raise HTTPException(status_code=400,
                                detail='You are not allowed to add user to department')

        with engine.begin() as connection:
            department = connection.execute(
                text('SELECT id FROM departments WHERE id = :id;'),
                {"id": department_id}).mappings().one_or_none()

            if not department:
                raise HTTPException(status_code=404,
                                    detail='Department not found')

            query = text(f'''
                INSERT INTO user_department (user_id, department_id)
                VALUES (:user_id, :department_id)
                ON CONFLICT (user_id, department_id) DO NOTHING
                RETURNING user_id;
            ''')

            new_users = []

            for user_id in request.user_ids:
                result = connection.execute(
                    query, {"user_id": user_id,
                            "department_id": department_id
                            }).mappings().one_or_none()
                if result:
                    new_users.append(result)

            query = text(f'''
                SELECT id, email, firstname, lastname
                FROM users
                WHERE id = :id;
            ''')

            output = []

            for user in new_users:
                result = connection.execute(query, {
                    "id": user['user_id']}).mappings().one_or_none()
                if result:
                    output.append(result)

            return output

    except jwt.ExpiredSignatureError as exception:
        raise HTTPException(status_code=401,
                            detail='Expired token') from exception
    except jwt.DecodeError as exception:
        raise HTTPException(status_code=401,
                            detail='Invalid token') from exception


# Endpoint : /departements/{department_id}/users/remove
# Type : POST
# This endpoint remove a list of users from a department
@app.post('/departements/{department_id}/users/remove')
async def remove_users_from_department(department_id: int,
                                       request: RemoveUserFromDepartment,
                                       token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        token = jwt.decode(token, os.getenv('SECRET_KEY'),
                           algorithms=["HS256"])

        if token.get('role') != 'admin':
            raise HTTPException(status_code=400,
                                detail='You are not allowed to add user to department')

        with engine.begin() as connection:
            department = connection.execute(
                text('SELECT id FROM departments WHERE id = :id;'),
                {"id": department_id}).mappings().one_or_none()

            if not department:
                raise HTTPException(status_code=404,
                                    detail='Department not found')

            query = text(f'''
                DELETE FROM user_department
                WHERE department_id = :department_id AND user_id = :user_id;
            ''')

            deleted_users = []

            for user_id in request.user_ids:
                result = connection.execute(
                    query, {"department_id": department_id,
                            "user_id": user_id}).rowcount
                if result > 0:
                    deleted_users.append(user_id)

            query = text(f'''
                SELECT id, email, firstname, lastname
                FROM users
                WHERE id = :id;
            ''')

            output = []

            for user in deleted_users:
                result = connection.execute(query,
                                            {"id": user}).mappings().one_or_none()
                if result:
                    output.append(result)

            return output

    except jwt.ExpiredSignatureError as exception:
        raise HTTPException(status_code=401,
                            detail='Expired token') from exception
    except jwt.DecodeError as exception:
        raise HTTPException(status_code=401,
                            detail='Invalid token') from exception


# Endpoint : /departements/{department_id}/users
# Type : GET
# This endpoint returns the users of a department
@app.get('/departements/{department_id}/users')
async def get_users_from_department(department_id: int,
                                    token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        token = jwt.decode(token, os.getenv('SECRET_KEY'),
                           algorithms=["HS256"])

        if token.get('role') != 'admin':
            raise HTTPException(status_code=400,
                                detail='You are not allowed to remove user from department')

        with engine.begin() as connection:
            department = connection.execute(
                text('SELECT id FROM departments WHERE id = :id;'),
                {"id": department_id}).mappings().one_or_none()

            if not department:
                raise HTTPException(status_code=404,
                                    detail='Department not found')

            query = text('''
                SELECT * FROM users
                JOIN user_department ON users.id = user_department.user_id
                WHERE user_department.department_id = :department_id;
            ''')

            result = connection.execute(query,
                                        {"department_id": department_id})

            output = []

            if token.get('role') == 'admin':
                for row in result:
                    values = {
                        'email': row.email,
                        'firstname': row.firstname,
                        'lastname': row.lastname,
                        'birthday_date': row.birthday_date,
                        'adress': row.adress,
                        'postal_code': row.postal_code,
                        'age': row.age,
                        'meta': row.meta,
                        'registration_date': row.registration_date,
                        'token': row.token,
                        'role': row.role
                    }
                    output.append(values)
            else:
                for row in result:
                    values = {
                        'email': row.email,
                        'firstname': row.firstname,
                        'lastname': row.lastname,
                        'age': row.age,
                        'registration_date': row.registration_date,
                        'role': row.role
                    }
                    output.append(values)

            return output

    except jwt.ExpiredSignatureError as exception:
        raise HTTPException(status_code=401,
                            detail='Expired token') from exception
    except jwt.DecodeError as exception:
        raise HTTPException(status_code=401,
                            detail='Invalid token') from exception


# Endpoint : /rh/msg/add
# Type : POST
# This endpoint add a request rh to the database
@app.post('/rh/msg/add')
async def add_request_rh(request: CreateRequestRH,
                         token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        token = jwt.decode(token, os.getenv('SECRET_KEY'),
                           algorithms=["HS256"])

        if token.get('role') != 'manager' and token.get('role') != 'admin':
            raise HTTPException(status_code=400,
                                detail='You are not allowed to add request rh')

        query = text('''
            INSERT INTO requests_rh (user_id, content, registration_date,
                visibility, close, last_action, content_history)
            VALUES (:user_id, :content, :registration_date, :visibility, :close,
                :last_action, :content_history)
        ''')

        values = {
            'user_id': request.user_id,
            'content': request.content,
            'registration_date': date.today(),
            'visibility': True,
            'close': False,
            'last_action': date.today(),
            'content_history': json.dumps([{'author': request.user_id, 'content': request.content, 'date': date.today().isoformat()}])
        }

        with engine.begin() as connection:
            connection.execute(query, values)
            return {'Request RH created with success'}

    except jwt.ExpiredSignatureError as exception:
        raise HTTPException(status_code=401,
                            detail='Expired token') from exception
    except jwt.DecodeError as exception:
        raise HTTPException(status_code=401,
                            detail='Invalid token') from exception


# Endpoint : /rh/msg/remove
# Type : POST
# This endpoint close a request rh but don't remove it from the database
@app.post('/rh/msg/remove')
async def remove_request_rh(request: RemoveRequestRH,
                            token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        token = jwt.decode(token, os.getenv('SECRET_KEY'),
                           algorithms=["HS256"])

        with engine.begin() as connection:
            request_rh = connection.execute(
                    text('SELECT id FROM requests_rh WHERE id = :id;'),
                    {"id": request.id}).mappings().one_or_none()

            if not request_rh:
                raise HTTPException(status_code=404,
                                    detail='Request RH not found')

            query = text('''
                UPDATE requests_rh
                SET visibility = :visibility, close = :close, last_action = :last_action, delete_date = :delete_date
                WHERE id = :id
            ''')

            values = {
                'id': request.id,
                'visibility': False,
                'close': True,
                'last_action': date.today(),
                'delete_date': date.today()
            }

            connection.execute(query, values)
            return {'Request RH removed with success'}

    except jwt.ExpiredSignatureError as exception:
        raise HTTPException(status_code=401,
                            detail='Expired token') from exception
    except jwt.DecodeError as exception:
        raise HTTPException(status_code=401,
                            detail='Invalid token') from exception


@app.post('/rh/msg/update')
async def update_request_rh(request: UpdateRequestRH,
                            token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        token = jwt.decode(token, os.getenv('SECRET_KEY'),
                           algorithms=["HS256"])

        with engine.begin() as connection:
            request_rh = connection.execute(
                text('SELECT id, content_history FROM requests_rh WHERE id = :id;'),
                {"id": request.id}).mappings().one_or_none()

            if not request_rh:
                raise HTTPException(status_code=404,
                                    detail='Request RH not found')

            query = text('''
                UPDATE requests_rh
                SET content = :content, last_action = :last_action, content_history = :content_history
                WHERE id = :id
            ''')

            request_rh['content_history'].append({'author': request.id,
                                                  'content': request.content,
                                                  'date': date.today().isoformat()})

            values = {
                'id': request.id,
                'content': request.content,
                'content_history': json.dumps(request_rh['content_history']),
                'last_action': date.today(),
            }

            connection.execute(query, values)
            return {'Request RH removed with success'}

    except jwt.ExpiredSignatureError as exception:
        raise HTTPException(status_code=401,
                            detail='Expired token') from exception
    except jwt.DecodeError as exception:
        raise HTTPException(status_code=401,
                            detail='Invalid token') from exception


@app.get('/rh/msg/')
async def get_request_rh(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        token = jwt.decode(token, os.getenv('SECRET_KEY'),
                           algorithms=["HS256"])

        with engine.begin() as connection:
            requests_rh = connection.execute(text('SELECT * FROM requests_rh;'))

            output = []

            for row in requests_rh:
                if token.get('role') == 'admin':
                    values = {
                        'id': row.id,
                        'user_id': row.user_id,
                        'content': row.content,
                        'registration_date': row.registration_date,
                        'visibility': row.visibility,
                        'close': row.close,
                        'last_action': row.last_action,
                        'content_history': row.content_history,
                        'delete_date': row.delete_date
                    }
                    output.append(values)
                elif token.get('role') == 'manager' and not row.close:
                    values = {
                        'id': row.id,
                        'user_id': row.user_id,
                        'content': row.content,
                        'registration_date': row.registration_date,
                        'visibility': row.visibility,
                        'close': row.close,
                        'last_action': row.last_action,
                        'content_history': row.content_history,
                        'delete_date': row.delete_date
                    }
                    output.append(values)
                elif token.get('id') == row.user_id and not row.close:
                    values = {
                        'id': row.id,
                        'user_id': row.user_id,
                        'content': row.content,
                        'registration_date': row.registration_date,
                        'visibility': row.visibility,
                        'close': row.close,
                        'last_action': row.last_action,
                        'content_history': row.content_history,
                        'delete_date': row.delete_date
                    }
                    output.append(values)

            return output

    except jwt.ExpiredSignatureError as exception:
        raise HTTPException(status_code=401,
                            detail='Expired token') from exception
    except jwt.DecodeError as exception:
        raise HTTPException(status_code=401,
                            detail='Invalid token') from exception
