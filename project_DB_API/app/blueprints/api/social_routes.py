from . import bp as api
from app.models import *
from flask import make_response, request

# returns all the posts the users they are following, takes id of user who is following them.
@api.get('/following/posts/<int:user_id>')
def get_all_posts(user_id):
    user = User.query.get(user_id)
    posts = user.followed_posts()
    response_list = []
    for post in posts:
        post_dict={
            "id":post.id,
            "body":post.body,
            "date_created":post.date_created,
            "date_updated":post.date_updated,
            "author": post.author.first_name + " " + post.author.last_name,
            "user_id": post.author.id,
            "author_icon": post.author.icon
        }
        response_list.append(post_dict)
    return make_response({"posts":response_list},200)

@api.get('/user/<int:user_id>/posts')
def get_posts_of_user(user_id):
    user = User.query.get(user_id)
    posts = user.posts
    response_list = []
    for post in posts:
        post_dict={
            "id":post.id,
            "body":post.body,
            "date_created":post.date_created,
            "date_updated":post.date_updated,
            "author": post.author.first_name + " " + post.author.last_name,
            "user_id": post.author.id
        }
        response_list.append(post_dict)
    return make_response({"posts":response_list},200)


# returns a single post take a post id
@api.get('/posts/<int:post_id>')
def get_single_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return make_response(f"Post ID: {post_id} does not exist", 404)
    response_dict={
        "id":post.id,
        "body":post.body,
        "date_created":post.date_created,
        "date_updated":post.date_updated,
        "author": post.author.first_name + " " + post.author.last_name,
        "user_id": post.author.id
    }
    return make_response(response_dict,200)


# POST => [BASE_URL]/posts?body=[POST_TEXT]&user_id=[ID_OF_CREATOR]
@api.post('/posts')
def post_post():
    posted_data = request.args
    u = User.query.get(int(posted_data['user_id']))
    if not u:
        return make_response(f"User id: {posted_data['user_id']} does not exist", 404)
    post = Post(**posted_data)
    post.save()
    print(post)
    return make_response(f"Post id: {post.id} created", 200)


# DELETE => [BASE_URL]/posts?id=[ID_OF_POST_TO_DELETE]
@api.delete('/posts')
def delete_post():
    posted_data = request.args
    id = int(posted_data['id'])
    post = Post.query.get(id)
    if not post:
        return make_response(f"Post id: {id} does not exist", 404)
    post.delete()
    return make_response(f"Post id: {id} has been deleted",200)

# PUT => [BASE_URL]/posts/[ID_TO_EDIT]?body=[DIF_POST_TEXT]&user_id=[ID_OF_CREATOR]
@api.put('/posts/<int:post_id>')
def put_post(post_id):
    posted_data = request.args
    post = Post.query.get(post_id)
    if not post:
        return make_response(f"Post id: {int(posted_data['id'])} does not exist", 404)
    u = User.query.get(int(posted_data['user_id']))
    if not u:
        return make_response(f"User id: {int(posted_data['user_id'])} does not exist", 404)
    post.user_id = int(posted_data['user_id'])
    post.body = posted_data['body']
    post.save()
    return make_response(f"Post id: {post.id} has been changed", 200)




# is this user following that user?
@api.get('/isfollowing/<int:this_user_id>/<int:that_user_id>')
def is_following(this_user_id, that_user_id):
    this_user = User.query.get(this_user_id)
    that_user = User.query.get(that_user_id)
    if not this_user:
        return make_response(f"User id: {this_user_id} does not exist", 404)
    if not that_user:
        return make_response(f"User id: {that_user_id} does not exist", 404)
    return make_response(f"{this_user.is_following(that_user)}", 200)

# make this user follow that user
@api.put('/follow/<int:this_user_id>/<int:that_user_id>')
def follow(this_user_id, that_user_id):
    this_user = User.query.get(this_user_id)
    that_user = User.query.get(that_user_id)
    if not this_user:
        return make_response(f"User id: {this_user_id} does not exist", 404)
    if not that_user:
        return make_response(f"User id: {that_user_id} does not exist", 404)
    this_user.follow(that_user)
    this_user.save()
    return make_response(f"User #{this_user_id} is now following user #{that_user_id}.", 200)
    
# make this user unfollow that user
@api.put('/unfollow/<int:this_user_id>/<int:that_user_id>')
def unfollow(this_user_id, that_user_id):
    this_user = User.query.get(this_user_id)
    that_user = User.query.get(that_user_id)
    if not this_user:
        return make_response(f"User id: {this_user_id} does not exist", 404)
    if not that_user:
        return make_response(f"User id: {that_user_id} does not exist", 404)
    this_user.unfollow(that_user)
    this_user.save()
    return make_response(f"User #{this_user_id} is no longer following user #{that_user_id}.", 200)