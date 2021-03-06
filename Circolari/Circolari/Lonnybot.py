#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import Circolari
import random
import time
import sys
import emoji
import telepot
import logging
import argparse
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

"""
Python 3.5 skeleton for school polls bot
"""

message_with_inline_keyboard = None
poll_of_the_day = None
markup = None
risultati = {}
votanti = {}

# Deafults
LOG_FILENAME = './Lonnybot.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO,format='%(asctime)s %(levelname)-8s %(message)s')

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="My simple Python Telegram bot")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
parser.add_argument("-T", "--TOKEN", help="bot TOKEN identifier")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
    LOG_FILENAME = args.log
if args.TOKEN:
	TOKEN = args.TOKEN
else:
	logging.error('No TOKEN specified')
	print("You must specify the bot's TOKEN")
	sys.exit(0)

logger = logging.getLogger(__name__)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
	def __init__(self, logger, level):
		#Needs a logger and a logger level.
		self.logger = logger
		self.level = level

	def write(self, message):
		# Only log if there is a message (not just a new line)
		if message.rstrip() != "":
			self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
#sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

#Record everyone that writes to your bot
def chatter(msg, first_name, from_id):
	content_type, chat_type, chat_id = telepot.glance(msg)

	try:
		if msg['from']['username']:
			user_name = msg['from']['username']
			if chat_type == 'private':
				person = user_name + ': ' + str(from_id)
			elif chat_type == 'group' or chat_type == 'supergroup':
				group_name = msg['chat']['title']
				person = user_name + ': ' + str(from_id) + ' @ ' + group_name + ', ' + str(chat_id)
	except KeyError:
		if chat_type == 'private':
			person = 'No username - ' + str(first_name) + ': ' + str(from_id)
		elif chat_type == 'group' or chat_type == 'supergroup':
			group_name = msg['chat']['title']
			person = 'No username - ' + str(first_name) + ': ' + str(from_id) + ' @ ' + group_name + ', ' + str(chat_id)
	with open("./contatti.txt", "a") as myfile:
				myfile.write(person + '\n')

#Handle all messages starting with '/poll'
def poll(msg, chat_id, chat_type, from_id):
	global poll_of_the_day
	global markup
	global risultati
	global message_with_inline_keyboard

	if chat_type == 'group' or chat_type == 'supergroup':
		try:
			message_with_inline_keyboard = bot.sendMessage(chat_id, poll_of_the_day, reply_markup=markup) if (from_id == 66441008) or (from_id == 163329729) else bot.sendMessage(chat_id, 'Solo il Gran Maestro del Concilio può indire un sondaggio')
		except telepot.exception.TelegramError:
			bot.sendMessage(chat_id, 'Nessun sondaggio impostato')
	if chat_type == 'private':
		if (chat_id != 66441008) and (chat_id != 163329729):
			bot.sendMessage(chat_id, 'Lascia lavorare i grandi, bimbo')
		else:
			if poll_of_the_day == None:
				lista = msg['text'].split('&@')
				poll_of_the_day = lista[0][6:]
				del lista[0]
				risultati = {}	

				buttons = []
				for e in lista:
					risultati[e] = 0
					buttons.append([InlineKeyboardButton(text=str(e) + ' (' + str(risultati[e]) + ')', callback_data=e)])
				markup = InlineKeyboardMarkup(inline_keyboard=buttons)
				bot.sendMessage(chat_id, 'Sondaggio registrato')
			else:
				bot.sendMessage(chat_id, 'C\'� gi� un sondaggio in corso')

def ongoing(chat_id, from_id, chat_type):
	try:
		bot.sendMessage(chat_id, poll_of_the_day, reply_markup=markup)
	except telepot.exception.TelegramError:
		bot.sendMessage(chat_id, 'Nessun sondaggio impostato')

#Close poll and generate the result
def exitpoll(msg, chat_id, from_id):
	if (from_id != 66441008) and (from_id != 163329729):
		bot.sendMessage(chat_id, 'Solo il Gran Maestro pu� chiudere un sondaggio in corso')
		if from_id == 146874789:
			risp = ['Bea piantala', 'Ti ho detto che solo il Gran Maestro pu� ordinarlo', 'Non sei un Gran Maestro.', 'Che scassamaroni', 'testarda eh', 'Solo il Gran Maestro!', 'Non ti obbedir� mai']
			bot.sendMessage(chat_id, random.choice(risp))
	else:
		global poll_of_the_day
		global risultati
		global markup
		global votanti
		global message_with_inline_keyboard
		try:
			exit_poll = poll_of_the_day + '\n'
			for e in risultati.keys():
				exit_poll += e + ': ' + str(risultati[e]) + '\n'
			bot.sendMessage(chat_id, exit_poll)
			poll_of_the_day = None
			risultati = {}
			markup = None
			votanti = {}
			message_with_inline_keyboard = None
		except TypeError:
			bot.sendMessage(chat_id, 'Nessun sondaggio in corso')

#Handle votes and prevent double voters, but allow to change vote
def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    info = 'Callback query: ' + str(query_id) + ', ' + str(from_id) + ', ' + str(data)
    logging.info(info)
    global message_with_inline_keyboard
    global markup
    global poll_of_the_day
    global risultati
    try:
        if from_id not in votanti.keys():
            risultati[data] += 1
            votanti[from_id] = data
            bot.answerCallbackQuery(query_id, text=data + ': ' + str(risultati[data]))
            buttons = []
            for e in risultati.keys():
                buttons.append([InlineKeyboardButton(text=str(e) + ' (' + str(risultati[e]) + ')', callback_data=e)])
            markup = InlineKeyboardMarkup(inline_keyboard=buttons)
            msg_idf = telepot.message_identifier(message_with_inline_keyboard)
            bot.editMessageText(msg_idf, poll_of_the_day, reply_markup=markup)
        else:
            if votanti[from_id] == data:
                bot.answerCallbackQuery(query_id, text=msg['from']['username'] + ' ha gi� espresso il suo voto')
            else:
                risultati[data] += 1
                risultati[votanti[from_id]] -= 1
                votanti[from_id] = data
                bot.answerCallbackQuery(query_id, text=data + ': ' + str(risultati[data]))
                buttons = []
                for e in risultati.keys():
                    buttons.append([InlineKeyboardButton(text=str(e) + ' (' + str(risultati[e]) + ')', callback_data=e)])
                markup = InlineKeyboardMarkup(inline_keyboard=buttons)
                msg_idf = telepot.message_identifier(message_with_inline_keyboard)
                bot.editMessageText(msg_idf, poll_of_the_day, reply_markup=markup)

    except KeyError:
        bot.answerCallbackQuery(query_id, text='Sondaggio chiuso')
def on_chat_message(msg):
    first_name = msg['from']['first_name']
    from_id = msg['from']['id']
    content_type, chat_type, chat_id = telepot.glance(msg)
    info = 'Chat Message: ' + content_type + ' ' + chat_type + ' ' + str(chat_id)
    logging.info(info)
    logging.debug(msg)
    chatter(msg, first_name, from_id)
    text = msg['text'].replace('@Lonnybot', '')
    if text[:5] == '/poll':
        poll(msg, chat_id, chat_type, from_id)
    elif text == '/exitpoll':
        exitpoll(msg, chat_id, from_id)
    elif text == '/ongoing':
        ongoing(chat_id, from_id, chat_type)
    elif text == '/check':
        circ = Circolari.ondemand(TOKEN, chat_id)
        if circ:
            for e in circ:
                bot.sendMessage(chat_id, e.replace("@n", "\n"), parse_mode='HTML')
        else:
            bot.sendMessage(chat_id, '<i>Nessun nuovo avviso</i>', parse_mode='HTML')

bot = telepot.Bot(TOKEN)

#updates = bot.getUpdates()

#if updates:
#    last_update_id = updates[-1]['update_id']
#    bot.getUpdates(offset=last_update_id+1)

bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})

logging.info('Bot started.')
bot.sendMessage('163329729', 'Up and running')
bot.sendMessage('66441008', 'Up and running')

# Keep the program running.
while 1:
    time.sleep(10)
