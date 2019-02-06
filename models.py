from peewee import (
    Model, SqliteDatabase,
    CharField, IntegerField, ForeignKeyField, BooleanField
)
from flask_security import UserMixin


db = SqliteDatabase('my_app.db')


class BaseModel(Model):
    class Meta:
        database = db


class Role(BaseModel):
    name = CharField(unique=True)
    description = CharField()


class User(BaseModel, UserMixin):
    email = CharField()
    password = CharField()
    active = BooleanField(default=True)


class UserRoles(BaseModel):
    # Because peewee does not come with built-in many-to-many
    # relationships, we need this intermediary class to link
    # user to roles.
    user = ForeignKeyField(User, backref='roles')
    role = ForeignKeyField(Role, backref='users')


class Item(BaseModel):
    name = CharField()
    stock = IntegerField()
    price = IntegerField()

    def __str__(self):
        return self.name


class Customer(BaseModel):
    name = CharField()
    age = IntegerField()

    def __str__(self):
        return self.name


class Cart(BaseModel):
    customer = ForeignKeyField(Customer, backref='carts')

    def __str__(self):
        return 'Cart {}'.format(self.id)


class CartItem(BaseModel):
    cart = ForeignKeyField(Cart, backref='items')
    item = ForeignKeyField(Item, backref='carts')
#    quantity = IntegerField()


class _FakeSignal(object):
    """If blinker is unavailable, create a fake class with the same
    interface that allows sending of signals but will fail with an
    error on anything else.  Instead of doing anything on send, it
    will just ignore the arguments and do nothing instead.
    """

    def __init__(self, name, doc=None):
        self.name = name
        self.__doc__ = doc

    def _fail(self, *args, **kwargs):
        raise RuntimeError('signalling support is unavailable '
                           'because the blinker library is '
                           'not installed.')
    send = lambda *a, **kw: None
    connect = disconnect = has_receivers_for = receivers_for = \
        temporarily_connected_to = connected_to = _fail
    del _fail
