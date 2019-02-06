import os
import telegram
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from models import Item, Customer, Cart, CartItem

from uuid import uuid4


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
    bot.send_message(chat_id=update.message.chat_id,
                     text='Alashopkz is a bot for online shopping,'
                     ' welcome on board!'
                     '\nWe have guidance for you.'
                     '\nIf you want to review our list of items,'
                     ' please use /items'
                     '\nIf you want to register, please use '
                     '/customer Your name Your age'
                     '\nIf you want to add to cart, please use '
                     '/add Your name Item name'
                     '\nIf you want to go to Your Cart, please use /cart'
                     '\nIf you want to buy, please use /buy')


def items(bot, update, args):
    try:
        items = Item.select()
        items = '\n'.join([str(item) for item in items])
        bot.send_message(
            chat_id=update.message.chat_id,
            text='{}'.format(items)
        )

    except Exception as e:
        logging.error(e, exc_info=True)
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Fail {}'.format(e)
        )


def customer(bot, update, args):
    try:
        name = args[0]
        age = args[1]
        customer = Customer(
            name=name,
            age=age
        )
        customer.save()
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Congratulations, {}! You are registered and '
            'can continue shopping :)'
            .format(name))
    except Exception as e:
        logging.error(e, exc_info=True)
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Fail {}'.format(e))


def add(bot, update, args):
    try:
        if len(args) == 2:
            customer_name = args[0]
            customer = Customer.select().where(
                Customer.name == customer_name
            )[0]
            item_name = args[1]
            logging.info('items_name: {}'.format(item_name))
            item = Item.select().where(
                Item.name == item_name
            )[0]
            cart = Cart(customer=customer)
            cart.save()
            cart_item = CartItem(
                cart=cart,
                item=item,
                quantity=1
            )
            cart_item.save()
            bot.send_message(
                chat_id=update.message.chat_id,
                text='{}, thanks for shopping with us. '
                'Item: {} added to Your Cart.'.
                format(cart.customer, cart_item.item)
            )
    except Exception as e:
        logging.error(e, exc_info=True)
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Fail {}'.format(e))


def cart(bot, update, args):
    pass


def put(bot, update, user_data):
    """Usage: /put value"""
    # Generate ID and seperate value from command
    key = str(uuid4())
    value = update.message.text.partition(' ')[2]

    # Store value
    user_data[key] = value

    update.message.reply_text(key)


def get(bot, update, user_data):
    """Usage: /get uuid"""
    # Seperate ID from command
    key = update.message.text.partition(' ')[2]

    # Load value
    try:
        value = user_data[key]
        update.message.reply_text(value)

    except KeyError:
        update.message.reply_text('Not found')


def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


start_handler = CommandHandler('start', start)
items_handler = CommandHandler('items', items, pass_args=True)
customer_handler = CommandHandler('customer', customer, pass_args=True)
add_handler = CommandHandler('add', add, pass_args=True)
echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(items_handler)
dispatcher.add_handler(customer_handler)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(echo_handler)


if __name__ == '__main__':
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('put', put, pass_user_data=True))
    dp.add_handler(CommandHandler('get', get, pass_user_data=True))

    updater.start_polling()
    updater.idle()
