import datetime

from argon2 import PasswordHasher
from peewee import *

import config

DATABASE = SqliteDatabase("courses.sqlite")
HASHER = PasswordHasher()


class User(Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(unique=True)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password, **kwargs):
        email = email.lower()
        try:                                    ## ** means "like"
            cls.select().where(
                (cls.email == email)|(cls.username**username)).get
        except cls.DoesNotExist:
            user = cls(username=username, email=email)
            user.password = user.set_password(password)
            user.save()
            return user
        else:
            raise Exception("User already exist")

    ## this method is contained in the class but it does not care
    ## anything about the class
    @staticmethod
    def set_password(password):
        return HASHER.hash(password)

    def verify_password(self, password):
        return HASHER.verify(self.password, password)

class Course(Model):
    title = CharField()
    url = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE


class Review(Model):
    course = ForeignKeyField(Course, related_name="review_set")
    rating = IntegerField()
    comment = TextField(default="")
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Course, Review], safe=True)
    DATABASE.close()
