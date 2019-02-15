import os
import telegram
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from models import Item, Customer, Cart, CartItem


token = os.environ['BOT_TOKEN']
bot = telegram.Bot(token=token)
print(bot.get_me())
{"first_name": "Alashop.kz", "username": "Alashopkz_bot"}

updater = Updater(token=token)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s'
                    ' - %(message)s',
                    level=logging.INFO)


def start(bot, update):
    # Bot presents itself, go to List of items through url,
    # and provide more detailed instructions through /guidance command

    bot.send_message(chat_id=update.message.chat_id,
                     text='Alashopkz is a bot for online shopping,'
                     ' welcome on board!'
                     '\nFirst of all, you want to see our List of Products. '
                     'So please Go to link: http://127.0.0.1:5000/items/'
                     '\nFor detailed instructions, please refer to /guidance'
                     )


def guidance(bot, update):
    # Function which prescribed detailed guidance
    # how to use commands and navigate through Bot functionalities

    bot.send_message(chat_id=update.message.chat_id,
                     text='We have guidance for you:'
                     '\n-> If you want to review our list of products,'
                     ' please Go to link: ''http://127.0.0.1:5000/items/'
                     '\n-> If you want to register, please use '
                     '/register Your name and Your birthday (YEAR-MM-DD). '
                     '\nAfter registration you receive '
                     'Cart # to continue for shopping. '
                     '\nIf you already registered in our shop, '
                     'you will be notified. '
                     '\n-> If you want to add products to Your Cart, '
                     'please use /add Your Cart # Product name and Quantity'
                     '\n-> If you want to go to review Your Cart, please use '
                     '/cart Cart#'
                     '\n-> If you want to view Total amount of Your Cart, '
                     '\n please use /buy'
                     '\n-> If you want to pay, please use /pay'
                     )


def register(bot, update, args):
    # Function to register new customer and define Cart # for further shopping
    # In addition, it finds already registered Customer and return their Cart #
    try:
        name = args[0]
        birthday = args[1]
        if Customer.select().where(
            Customer.name == name
        ) and Customer.select().where(
            Customer.birthday == birthday
        ):
                cart_id = Customer.get(
                    Customer.name == name,
                    Customer.birthday == birthday).id
                bot.send_message(
                    chat_id=update.message.chat_id,
                    text='Dear, {}! You are already registered in our shop =) '
                    'Glad to see you again! '
                    'Please use Your Cart #: {} for all purchases.'
                    '\nIf you need help, please use /guidance'
                    .format(
                        name, cart_id
                    )
                )
        else:
            customer = Customer(
                name=name, birthday=birthday
            )
            customer.save()
            cart = Cart(customer=customer.id)
            cart.save()
            bot.send_message(
                chat_id=update.message.chat_id,
                text='Congratulations, {}! You are registered and '
                'can continue shopping :) '
                'Please use Your Cart #: {} for all purchases.'
                '\nIf you need help, please use /guidance'
                .format(name, cart.id)
            )
    except IndexError:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Please use proper format: '
            'Your name Your birthday (YEAR-MM-DD). ')


def add(bot, update, args):
    # Function to add to certain Cart # product and quantity
    try:
        if len(args) == 3:
            cart_id = args[0]
            cart = Cart.select().where(
                Cart.id == cart_id
            )[0]
            item_name = args[1]
            item = Item.select().where(
                Item.name == item_name
            )[0]
            quantity = args[2]
            cart_item = CartItem(
                cart=cart,
                item=item,
                quantity=quantity
            )
            cart_item.save()
            bot.send_message(
                chat_id=update.message.chat_id,
                text='{}, thanks for shopping with us! '
                'Product: {} in quantity of: {} added to Your Cart {}.'
                '\nIf you need help, please use /guidance'
                .format(
                    cart.customer, cart_item.item,
                    cart_item.quantity, cart_id)
            )
    except IndexError:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Please use proper format: '
            '/add Your Cart # Product name Quantity ')


def cart(bot, update, args):
    # Function to review all products and quantity by Cart id #
    try:
        cart_id = args[0]
        cartitems = (CartItem.select().join(Cart).where(Cart.id == cart_id))
        cartitems = ', '.join([str(cartitem) for cartitem in cartitems])
        quantities = (CartItem.select().join(Cart).where(
            Cart.id == cart_id)
        )
        quantities = ', '.join(
            [str(quantity.quantity) for quantity in quantities]
        )
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Your Cart includes the following products: {} '
            'in quantities: {} respectively. '
            '\nIf you want to continue shopping, please use /guidance'
            '\nIf you want to know Your Cart Amount, please use /buy'
            .format(cartitems, quantities)
        )
    except IndexError:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Please use proper format: '
            '/cart Your Cart # ')


def buy(bot, update, args):
    # Function to calculate total amount of certain cart
    try:
        cart_id = args[0]
        cart = Cart.select().where(Cart.id == cart_id)[0]
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Dear {}, total amount of Your Cart # {} is {} LC. '
            '\nIf you want to pay, please use /pay'
            '\nIf you want to continue shopping, please use /guidance'
            .format(cart.customer, cart_id, cart.amount)
        )
    except IndexError:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Please use proper format: '
            '/buy Your Cart # ')


def pay(bot, update, args):
    try:
        cart_id = args[0]
        cart = Cart.update(paid=True).where(Cart.id == cart_id)
        cart.execute()
        cart = Cart.select().where(Cart.id == cart_id)[0]
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Thank you for shopping with us! '
            'Your Payment in amount of {} LC confirmed.'
            '\nIf you need help, please use /guidance'
            .format(cart.amount),
        )
    except IndexError:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Please use proper format: '
            '/pay Your Cart # ')


def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


start_handler = CommandHandler('start', start)
guidance_handler = CommandHandler('guidance', guidance)
register_handler = CommandHandler('register', register, pass_args=True)
add_handler = CommandHandler('add', add, pass_args=True)
cart_handler = CommandHandler('cart', cart, pass_args=True)
buy_handler = CommandHandler('buy', buy, pass_args=True)
pay_handler = CommandHandler('pay', pay, pass_args=True)
echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(guidance_handler)
dispatcher.add_handler(register_handler)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(cart_handler)
dispatcher.add_handler(buy_handler)
dispatcher.add_handler(pay_handler)
dispatcher.add_handler(echo_handler)


if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
