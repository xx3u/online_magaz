from peewee import (
    Model, SqliteDatabase,
    CharField, DateField, IntegerField, ForeignKeyField,
    BooleanField, DecimalField
)
from flask_security import UserMixin

from playhouse.signals import Model, post_save


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
    price = DecimalField()
    in_stock = IntegerField(null=True)

    def __str__(self):
        return self.name


class Customer(BaseModel):
    name = CharField()
    birthday = DateField()

    def __str__(self):
        return self.name


class Cart(BaseModel):
    customer = ForeignKeyField(Customer, backref='carts')
    amount = DecimalField(null=True)
    paid = BooleanField(default=False)

    def __str__(self):
        return 'Cart {}'.format(self.id)


class CartItem(BaseModel):
    cart = ForeignKeyField(Cart, backref='items')
    item = ForeignKeyField(Item, backref='carts')
    quantity = IntegerField()

    def __str__(self):
        return str(self.item)


@post_save(sender=CartItem)
def on_save_handler(model_class, instance, created):
    cart = instance.cart
    total = [
        item.item.price * item.quantity for item in cart.items
    ]
    instance.cart.amount = sum(total)
    instance.cart.save()
#    item = instance.item
#    closing_balance = [
#        item.item.stock - item.quantity for item in cart.items
#    ]
#    instance.item.in_stock = sum(closing_balance)
#    instance.item.save()
