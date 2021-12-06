from app import db
from flask_login import UserMixin
from datetime import datetime as dt, timedelta
import secrets
from passlib.hash import sha256_crypt


followers = db.Table(
    'followers',
    db.Column('follower_id',db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id',db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    username = db.Column(db.String(200), unique=True, index=True)
    password = db.Column(db.String(200))
    icon = db.Column(db.Integer)
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('User',
                    secondary = followers,
                    primaryjoin=(followers.c.follower_id == id),
                    secondaryjoin=(followers.c.followed_id == id),
                    backref=db.backref('followers',lazy='dynamic'),
                    lazy='dynamic'
                    )
    token = db.Column(db.String, index=True, unique=True)
    token_exp = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)


    def get_token(self, exp=86400):
        current_time = dt.utcnow()
        # give the user their token if the token is not expired
        if self.token and self.token_exp > current_time + timedelta(seconds=60):
            return self.token
        # if not a token create a token and exp date
        self.token = secrets.token_urlsafe(32)
        self.token_exp = current_time + timedelta(seconds=exp)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_exp = dt.utcnow() - timedelta(seconds=61)

    @staticmethod
    def check_token(token):
        u = User.query.filter_by(token=token).first()
        if not u or u.token_exp < dt.utcnow():
            return None
        return u


    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            db.session.commit()

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)
            db.session.commit()

    def followed_posts(self):
        followed = Post.query.join(followers, (Post.user_id == followers.c.followed_id)).filter(followers.c.follower_id == self.id)
        self_posts = Post.query.filter_by(user_id=self.id)

        all_posts = followed.union(self_posts).order_by(Post.date_created.desc())
        return all_posts


    def from_dict(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.username = data["username"]
        if data['password']!=None:
            self.password = sha256_crypt.encrypt(data['password'])
        if data['icon']!=None:
            self.icon = int(data['icon'])
        if type(data['is_admin'])==str:
            admin = data['is_admin'].lower() in ('true', '1')
            self.is_admin = admin
        elif type(data['is_admin'])==bool:
            admin = data['is_admin']
            self.is_admin = admin
        
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "icon": self.icon,
            "created_on": self.created_on,
            "is_admin": self.is_admin
            }

    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def get_icon_url(self):
        return f'https://avatars.dicebear.com/api/micah/{self.icon}.svg'

    def __repr__(self):
        return f'<User: {self.id} | {self.email}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=dt.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def edit(self, new_body):
        self.body=new_body
        self.save()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        return f'<id:{self.id} | Post: {self.body[:15]}>'
