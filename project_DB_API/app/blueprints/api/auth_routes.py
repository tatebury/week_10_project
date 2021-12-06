from . import bp as api
from app.models import User
from flask import make_response, request
from passlib.hash import sha256_crypt

@api.post('/token')
def get_token():
    u = User.query.filter_by(username=request.args.get("username")).first()
    stored_password = u.password
    if u and sha256_crypt.verify(request.args.get("password"), stored_password):
        token = u.get_token()
        id = u.id
        return make_response({"token":token, "currentUserID":id},200)
    else:
        return make_response("Unauthorized Access", 401)
    

    


@api.get('/users/<int:currentUserID>')
def get_users(currentUserID):
    users_data=[]
    current_user=User.query.get(currentUserID)
    for user in User.query.all():
        user_dict = user.to_dict()
        user_dict["is_following"]=current_user.is_following(user)
        users_data.append(user_dict)
    return make_response({"users":users_data}, 200)

@api.get('/user/<int:id>')
def get_user(id):
    return make_response(User.query.get(id).to_dict(), 200)

# create a new user from registration data
@api.post('/user')
def post_user():
    # query_params is an ImmutableMultiDict
    query_params = request.args
    new_data = {
        "first_name":None,
        "last_name":None,
        "username":None,
        "password":None,
        "icon":None,
        "is_admin":None
    }
    for key in query_params:
        value = query_params.get(key)
        new_data[key]=value
        
    # new_data['is_admin']=True
    
    new_user = User()
    new_user.from_dict(new_data)
    new_user.save()
    return make_response("New user created",200)

@api.put('/user/<int:id>')
def put_user(id):
    query_params = request.args
    user=User.query.get(id)
    dif_data = user.to_dict()
    for key in query_params:
        value = query_params.get(key)
        dif_data[key]=value
    dif_data['password']=None
    print(dif_data)
    user.from_dict(dif_data)
    user.save()
    return make_response("User modified",200)

@api.delete('/user/<int:id>')
def delete_user(id):
    User.query.get(id).delete()
    return make_response("User deleted",200)