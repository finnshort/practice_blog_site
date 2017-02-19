import datetime
import uuid

from flask import session

from src.common.database import Database
from src.models.blog import Blog
from src.models.post import Post


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            print("got data by email from database")
            return cls(**data)
        else:
            return None

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @classmethod
    def register(cls, email, password):
        user = cls.get_by_email(email)
        if user is not None:
            # user already exists so we can't create a new account
            return False
        else:
            # can create a new user
            new_user = cls(email, password)
            new_user.save_to_mongo()
            session['email'] = email
            return True


    @staticmethod
    def login_valid(email, password):
        # check whether a user's password matches their email
        user = User.get_by_email(email)
        if user is not None:
            # check password
            return user.password == password
        return False


    @staticmethod
    def login(user_email):
        # validation has already been called
        session['email'] = user_email


    @staticmethod
    def logout():
        session['email'] = None

    @staticmethod
    def new_post(blog_id, title, content, date=datetime.datetime.utcnow()):
        blog = Blog.from_mongo(blog_id)
        blog.new_post(title=title,
                      content=content,
                      date=date)

    def json(self):
        return {
            "email": self.email,
            "_id": self._id,
            "password": self.password
        }

    def save_to_mongo(self):
        Database.insert(collection='users', data=self.json())

    def get_blogs(self):
        blog = Blog.find_by_author_id(self._id)
        print("got the blog")
        return blog

    def new_blog(self, title, description):
        blog = Blog(author=self.email,
                    title=title,
                    description=description,
                    author_id=self.author_id)
        blog.save_to_mongo()

    @staticmethod
    def get_users():
        return Database.find(collection='users', query={})
