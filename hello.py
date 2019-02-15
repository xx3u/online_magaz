import flask_admin
from flask import Flask
from flask import render_template
from flask import request, session, redirect, url_for
from flask_security import Security, PeeweeUserDatastore, login_required

from models import db, User, Role, UserRoles, Item, Customer, Cart, CartItem
from admin import Admin
from datetime import date


app = Flask(__name__)
# Set the secret key
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SECURITY_PASSWORD_HASH'] = 'sha256_crypt'
app.config['SECURITY_PASSWORD_SALT'] = 'salt'


# Setup Flask-Security
user_datastore = PeeweeUserDatastore(db, User, Role, UserRoles)
security = Security(app, user_datastore)


# Setup flask-admin
admin = flask_admin.Admin(app, name='Shop Admin')
admin.add_view(Admin(User))
admin.add_view(Admin(Item))
admin.add_view(Admin(Customer))
admin.add_view(Admin(Cart))
admin.add_view(Admin(CartItem))


# Create a user to test with
@app.before_first_request
def create_user():
    for Model in (Role, User, UserRoles, Item, Customer, Cart, CartItem):
        Model.drop_table(fail_silently=True)
        Model.create_table(fail_silently=True)
    user_datastore.create_user(
        email='test@test.com',
        password='password'
    )
    item1 = Item(name='notebook', stock=300, price=500)
    item1.save()
    item2 = Item(name='TV', stock=250, price=200)
    item2.save()
    item3 = Item(name='flash', stock=950, price=10)
    item3.save()
    item4 = Item(name='smartphone', stock=455, price=150)
    item4.save()
    item5 = Item(name='camera', stock=50, price=550)
    item5.save()
    customer = Customer(name='John', birthday=date(1990, 1, 15))
    customer.save()
    cart1 = Cart(customer=customer.id)
    cart1.save()
    cartitem = CartItem(cart=cart1, item=item1, quantity=3)
    cartitem.save()
    customer = Customer(name='Olivier', birthday=date(1995, 2, 22))
    customer.save()
    cart2 = Cart(customer=customer.id)
    cart2.save()
    cartitem = CartItem(cart=cart2, item=item5, quantity=45)
    cartitem.save()


# routing on index page
@app.route('/')
@login_required
def index():
    name = session.get('name')
    response = render_template('index.html', name=name)
    return response


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['name'] = request.form['name']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=text name=name>
            <p><input type=submit value=Login>
        </form>
    '''


@app.route('/items/', methods=['GET'])
def items():
    if request.method == 'GET':
        items = Item.select()
        return render_template('items.html', items=items)
