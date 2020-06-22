from flask import jsonify, request

from app import app
from app import db
from app.models.user import User
from app.models.user import UserToken
from app.utilities.response import ResponseUtilities as ru
from app.utilities.validation import ValidationUtilities as vu

role_values = {'admin': 1, 'finance_manager': 2, 'manager': 3, 'employee': 4}
role_values_reverse = {1: 'admin' , 2: 'finance_manager' , 3: 'manager', 4: 'employee'}

status_values = {'deactivated': 0, 'activated': 1, 'blocked': 2}
status_values_reverse = {0: 'deactivated', 1: 'activated', 2: 'blocked'}

@app.route('/api/users/login', methods=['POST'])
def user_login():

    #TODO: separate to a validation class
    if request.get_json() is None:
        return ru.http_unsupported_media_type()

    if request.get_json().get('email') is None:
        return ru.http_bad_gateway()
    
    if not vu.is_valid_email(request.get_json().get('email')):
        return ru.http_bad_gateway()
    
    #TODO: improve validation for password
    if request.get_json().get('password') is None:
        return ru.http_bad_gateway()

    if len(request.get_json().get('password')) < 8:
        return ru.http_bad_gateway(message="Password must be a minimum of 8 characters")
    

    user = User.is_valid_user(request.get_json().get('email'), request.get_json().get('password'))

    if user is None:
        return ru.http_unauthorized(message="Email and password is not valid")

    token = UserToken.generate_token()
    if UserToken.create_token(
            user=user.id,
            token=token
            ):
        ru.http_conflict(message="Failed to create a user token")

    return ru.http_success(meta={'uid': user.uid, 'token': token, 'role': role_values_reverse.get(user.role)})


@app.route('/api/admin/users/registration', methods=['POST'])
def user_registration_for_admin():

    #TODO: separate to a validation class
    if request.get_json() is None:
        return ru.http_unsupported_media_type()

    if request.get_json().get('email') is None:
        return ru.http_bad_gateway(message="Email must not be empty")
    
    if not vu.is_valid_email(request.get_json().get('email')):
        return ru.http_bad_gateway(message="Email is invalid")
    
    #TODO: improve validation for password
    if request.get_json().get('password') is None:
        return ru.http_bad_gateway(message="Password must not be empty")

    if len(request.get_json().get('password')) < 8:
        return ru.http_bad_gateway(message="Password must be a minimum of 8 characters")
    
    if request.get_json().get('first_name') is None:
        return ru.http_bad_gateway(message="First name must not be empty")
    
    if request.get_json().get('last_name') is None:
        return ru.http_bad_gateway(message="Last name must not be empty")
    
    if request.get_json().get('role') is None:
        return ru.http_bad_gateway(message="Role must not be empty")
    
    if request.get_json().get('role') not in role_values:
        return ru.http_bad_gateway(message="Role value is not valid")
    
    if request.headers.get('authorization') is None:
        return ru.http_unauthorized()


    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])


    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    if User.is_existing_email(request.get_json().get('email')):
        return ru.http_conflict(message="Email is already existing")
    
    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()

    if not user.is_admin:
        return ru.http_forbidden()

    if not User.create_user(
            email=request.get_json().get('email'), 
            password=User.generate_password(request.get_json().get('password')), 
            uid=User.generate_uid(), 
            first_name=request.get_json().get('first_name'), 
            last_name=request.get_json().get('last_name'),
            role=role_values.get(request.get_json().get('role')),
            #status default = 2 for the meantime when there is no email validation yet
            status=1
            ):
        ru.http_conflict(message="Failed to create the resource")

    return ru.http_created()


@app.route('/api/admin/users', methods=['GET'])
def get_users_for_admin():

    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()

    if not user.is_admin:
        return ru.http_forbidden()

    #TODO: pagination
    #request.args.get('offset'), request.args.get('limit')
    all_users = User.get_all()
    meta = []
    if all_users is not None:
        for row in all_users:
            meta.append({'uid': row.uid, 'first_name': row.first_name, 'last_name': row.last_name, 'email': row.email, 'role': role_values_reverse.get(row.role), 'status': status_values_reverse.get(row.status)})

    return ru.http_success(meta=meta)


@app.route('/api/admin/users/<string:uid>', methods=['GET'])
def user_details_for_admin(uid):
    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_unauthorized(message="Token is invalid")

    search_user = User.find_by_uid(uid)

    if not user.is_admin:
        return ru.http_forbidden(message="You are not allowed to access this data")

    return ru.http_success(meta={'uid': search_user.uid, 'first_name': search_user.first_name, 'last_name': search_user.last_name, 'email': search_user.email, 'role': role_values_reverse.get(search_user.role), 'status': status_values_reverse.get(search_user.status)})


@app.route('/api/admin/users/<string:uid>', methods=['PUT'])
def user_details_update_for_admin(uid):

    #TODO: separate to a validation class
    if request.get_json() is None:
        return ru.http_unsupported_media_type()

    if request.get_json().get('email') is None:
        return ru.http_bad_gateway(message="Email must not be empty")
    
    if not vu.is_valid_email(request.get_json().get('email')):
        return ru.http_bad_gateway(message="Email is invalid")
    
    if request.get_json().get('first_name') is None:
        return ru.http_bad_gateway(message="First name must not be empty")
    
    if request.get_json().get('last_name') is None:
        return ru.http_bad_gateway(message="Last name must not be empty")
    
    if request.get_json().get('role') is None:
        return ru.http_bad_gateway(message="Role must not be empty")
    
    if request.get_json().get('role') not in role_values:
        return ru.http_bad_gateway(message="Role value is not valid")
    
    if request.headers.get('authorization') is None:
        return ru.http_unauthorized()

    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    if User.is_existing_email_for_update_by_uid(uid, request.get_json().get('email')):
        return ru.http_conflict(message="Email is already existing")
    
    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()

    if not user.is_admin:
        return ru.http_forbidden()

    if not User.update_user_by_uid(
            uid,
            email=request.get_json().get('email'), 
            first_name=request.get_json().get('first_name'), 
            last_name=request.get_json().get('last_name'),
            role=role_values.get(request.get_json().get('role'))
            ):
        ru.http_conflict(message="Failed to update the resource")

    return ru.http_success(message="Successful updated")


@app.route('/api/admin/users/<string:uid>/password', methods=['PUT'])
def user_password_update_for_admin(uid):

    #TODO: separate to a validation class
    if request.get_json() is None:
        return ru.http_unsupported_media_type()

    #TODO: improve validation for password
    if request.get_json().get('password') is None:
        return ru.http_bad_gateway(message="Password must not be empty")

    if len(request.get_json().get('password')) < 8:
        return ru.http_bad_gateway(message="Password must be a minimum of 8 characters")
    
    if request.headers.get('authorization') is None:
        return ru.http_unauthorized()

    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()

    if not user.is_admin:
        return ru.http_forbidden()

    if not User.update_user_password_by_uid(
            uid,
            User.generate_password(request.get_json().get('password'))
            ):
        ru.http_conflict(message="Failed to update the resource")

    return ru.http_success(message="Successful updated password")


@app.route('/api/users', methods=['GET'])
def user_details(uid):
    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_unauthorized(message="Token is invalid")

    return ru.http_success(meta={'uid': user.uid, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'role': role_values_reverse.get(user.role), 'status': status_values_reverse.get(user.status)})


@app.route('/api/users', methods=['PUT'])
def user_details_update():

    #TODO: separate to a validation class
    if request.get_json() is None:
        return ru.http_unsupported_media_type()

    if request.get_json().get('email') is None:
        return ru.http_bad_gateway(message="Email must not be empty")
    
    if not vu.is_valid_email(request.get_json().get('email')):
        return ru.http_bad_gateway(message="Email is invalid")
    
    if request.get_json().get('first_name') is None:
        return ru.http_bad_gateway(message="First name must not be empty")
    
    if request.get_json().get('last_name') is None:
        return ru.http_bad_gateway(message="Last name must not be empty")
    
    if request.get_json().get('role') is None:
        return ru.http_bad_gateway(message="Role must not be empty")
    
    if request.get_json().get('role') not in role_values:
        return ru.http_bad_gateway(message="Role value is not valid")
    
    if request.headers.get('authorization') is None:
        return ru.http_unauthorized()

    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    if User.is_existing_email_for_update_by_id(token.user, request.get_json().get('email')):
        return ru.http_conflict(message="Email is already existing")
    
    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()

    if not User.update_user_by_id(
            user.id,
            email=request.get_json().get('email'), 
            first_name=request.get_json().get('first_name'), 
            last_name=request.get_json().get('last_name'),
            role=user.role
            ):
        ru.http_conflict(message="Failed to update the resource")

    return ru.http_success(message="Successful updated")


@app.route('/api/users/password', methods=['PUT'])
def user_password_update():

    #TODO: separate to a validation class
    if request.get_json() is None:
        return ru.http_unsupported_media_type()

    #TODO: improve validation for password
    if request.get_json().get('password') is None:
        return ru.http_bad_gateway(message="Password must not be empty")

    if len(request.get_json().get('password')) < 8:
        return ru.http_bad_gateway(message="Password must be a minimum of 8 characters")
    
    if request.headers.get('authorization') is None:
        return ru.http_unauthorized()

    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()

    if not User.update_user_password_by_id(
            user.id,
            User.generate_password(request.get_json().get('password'))
            ):
        ru.http_conflict(message="Failed to update the resource")

    return ru.http_success(message="Successful updated password")


@app.route('/api/users/roles/<string:role>', methods=['GET'])
def get_users_by_roles(role):

    if role is None:
        ru.http_bad_gateway(message="Role is required")

    if role not in role_values:
        ru.http_bad_gateway(message="Role is invalid")

    if request.headers.get('authorization') is None:
        return ru.http_unauthorized()

    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()

    if user.is_admin:
        meta = []
        for row in User.find_by_role(role_values.get(role)):
            meta.append({"email": row.email, "uid": row.uid})
        return ru.http_success(message="Successful fetching of data", meta=meta)

    if user.is_employee and role == 'manager':
        meta = []
        for row in User.find_by_role(role_values.get(role)):
            meta.append({"first_name": row.first_name, "last_name": row.last_name, "email": row.email, "uid": row.uid})
        return ru.http_success(message="Successful fetching of data", meta=meta)

    
    if user.is_manager and role == 'finance_manager':
        meta = []
        for row in User.find_by_role(role_values.get(role)):
            meta.append({"email": row.email, "uid": row.uid})
        return ru.http_success(message="Successful fetching of data", meta=meta)

    return ru.http_bad_gateway(message="Invalid role")


