import secrets
from app import db
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


# create a class called User 
class User(db.Model):
    # create a table called users with the following columns
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(120), index=True)
    lastName = db.Column(db.String(120), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(120), nullable=False)
    posts = db.relationship('Post', back_populates='author')
    comments = db.relationship('Comment', back_populates='user')
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs.get('password', ''))

    
    def __repr__(self):
        return f"<User {self.id}|{self.username}>"
    
    # create a method to set the password
    def set_password(self, plaintext_password):
        self.password = generate_password_hash(plaintext_password)
        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()

    
    # create a method to check the password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # create a method to get a token
    def get_token(self):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration > now + timedelta(minutes=1):
            return {"token": self.token, "tokenExpiration": self.token_expiration}
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(hours=1)
        self.save()
        return {"token": self.token, "tokenExpiration": self.token_expiration}
    
    
    # create a method to get the user as a dictionary
    def to_dict(self):
        data = {
            'id': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'email': self.email
        }
        return data
    
    # create a method to update the user
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'password':
                self.set_password(value)
            else:
                setattr(self, key, value)
        db.session.add(self)
    
    # create a method to delete the user
    def delete(self):
        db.session.delete(self)
    
    # create a method to get a user by id
    # @staticmethod
    # def get_user(user_id):
    #     return db.session.get(User, user_id)
    
    # # create a method to get a user by email
    # @staticmethod
    # def get_user_by_email(email):
    #     return User.query.filter_by(email=email).first()

# create a class called Post
class Post(db.Model):
    # create a table called posts with the following columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post')
    
    # create a method to get the post as a dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'author': self.author.to_dict(),
            'comments': [comment.to_dict() for comment in self.comments]
        }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Post {self.id}|{self.title}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        allowed_fields = {'title', 'body'}

        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

# create a class called Comment
class Comment(db.Model):
    # create a table called comments with the following columns
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='comments')
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', back_populates='comments')
    
    # create a method to get the comment as a dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'body': self.body,
            'user': self.user.to_dict(),
            'post': self.post.to_dict(),
            'post_id': self.post_id,
        }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Comment {self.id}|{self.body}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        allowed_fields = {'body'}

        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()