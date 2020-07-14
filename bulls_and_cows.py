from sys import platform
from colorama import Fore, Back, Style
import os
import random
import time
import requests
import json
import configparser
import re

# consts
RED = Fore.RED + Back.BLACK
BLUE = Fore.BLUE + Back.BLACK
GREEN = Fore.GREEN + Back.BLACK
CYAN = Fore.CYAN + Back.BLACK
WHITE = Fore.WHITE + Back.BLACK
YELLOW = Fore.YELLOW + Back.BLACK
COLORS = (RED, BLUE, GREEN, CYAN, WHITE, YELLOW)
BG_YELLOW = Back.YELLOW + Fore.WHITE

version = 0
records = []
time_out = 0
language = 'ru'
transfer = True
data_game = []
data_game_first = []
data_game_second = []

# funcions
def clear_screen(): # очистка экрана
	if platform == 'win32':
		os.system('cls')
	else:
		os.system('clear')

def avoid_fatal_error(): # избежать фатальной ошибки при чтении conf.ini
	config = configparser.ConfigParser()
	if not os.path.exists('conf.ini'):
		restore_default_settings()
	else:
		try:
			config.read('conf.ini')
			sets = []
			sets.append(re.fullmatch(r'\d+.?\d+?', config['VERSION']['version']))
			sets += [re.fullmatch(r'(\d+-\w+)|0', config['STATS'][f'record{i}']) for i in range(1, 6)]
			sets.append(re.fullmatch(r'\d+.?\d+?', config['OTHER']['timeout']))
			sets.append(re.fullmatch(r'\w{2}', config['OTHER']['language']))
			if None in sets:
				restore_default_settings()
		except:
			restore_default_settings()

def restore_default_settings(): # востановление настроек по-умолчанию в conf.ini
	with open('conf.ini', 'w') as f:
		f.write('[VERSION]\n[STATS]\n[OTHER]')
	config = configparser.ConfigParser()
	config.read('conf.ini')
	config.set('VERSION', 'version', '0.5')
	[config.set('STATS', f'record{i}', '0') for i in range(1, 6)]
	config.set('OTHER', 'timeout', '0.3')
	config.set('OTHER', 'language', 'ru')
	with open('conf.ini', 'w') as f:
		config.write(f)
	error('файл conf.ini был повреждён', end = 'восстановлено значение по умолчанию')

def set_const(): # получение настроек
	global version, records, time_out, language
	config = configparser.ConfigParser()
	config.read('conf.ini')
	version = config['VERSION']['version']
	records = [config['STATS'][f'record{i}'] for i in range(1, 6)]
	time_out = float(config['OTHER']['timeout'])
	language = config['OTHER']['language']

def check_internet_connection(): # проверка подключения к интернету
	global transfer
	try:
		requests.get('https://google.com')
		return True
	except requests.exceptions.ConnectionError as e:
		transfer = False
		error('отсутствует подключение к сети', end = 'установлен язык по-умолчанию (русский)')
		return False

def translate(text): # перевод текста
	if language != 'ru' and transfer:
		if check_internet_connection():
			url = 'https://translate.yandex.net/api/v1.5/tr.json/translate?' 
			key = 'trnsl.1.1.20190227T075339Z.1b02a9ab6d4a47cc.f37d50831b51374ee600fd6aa0259419fd7ecd97'
			lang = f'ru-{language}' 
			r = requests.post(url, data={'key': key, 'text': text, 'lang': lang}).json()
			text = r['text'][0]
	return text

def timeout(sec = None): # таймаут при выводе строк
	if sec == None:
		sec = time_out
	time.sleep(sec)

def multi_colored_text(text): # окрашивание теста в разные цвета
	colored_text = ''
	for char in text:
		colored_text += random.choice(COLORS) + char
	return colored_text

def preview(): # вывод начального текста
	figlet = BLUE + '''    ____        ____                        __   ______
   / __ )__  __/ / /____   ____ _____  ____/ /  / ____/___ _      _______
  / __  / / / / / / ___/  / __ `/ __ \\/ __  /  / /   / __ \\ | /| / / ___/
 / /_/ / /_/ / / (__  )  / /_/ / / / / /_/ /  / /___/ /_/ / |/ |/ (__  )
/_____/\\__,_/_/_/____/   \\__,_/_/ /_/\\__,_/   \\____/\\____/|__/|__/____/
''' 
	figlet += RED + 'Version ' + multi_colored_text(str(version)) + RED + '\nGame by ' + multi_colored_text('RedSenior')
	print(figlet)

def proposition(question, *args): # выбор из нескольких вопросов
	while True:
		print()
		if question != None:
			print(GREEN + '[+] ' + CYAN + translate(question.capitalize()) + ':')
		for answer in args:
			timeout()
			print(BLUE + f'[{args.index(answer) + 1}] ' + CYAN + translate(answer.capitalize()))
		answer = input(GREEN + '[>] ' + WHITE)
		if answer in [str(i) for i in range(1, len(args) + 1)]:
			return int(answer)
		else:
			error('указан неверный вариант')

def message(mess, pause = False):
	print(GREEN + '[!] ' + CYAN + translate(mess.capitalize()))
	if pause:
		input()

def enter(question, re_str = None): # ввод определённых данных
	while True:
		print()
		answer = input(GREEN + '[+] ' + CYAN + translate(question.capitalize()) + ' : ' + WHITE)
		if not re_str or re.fullmatch(re_str, answer):
			break
		else:
			error('неверно указана строка')
	return answer

def error(text, end = None): # вывод сообщения об ошибке
	if end == None:
		input(RED + '[!] ' + CYAN + translate(text.capitalize() + '. Повторите попытку!'))
	else:
		input(RED + '[!] ' + CYAN + translate(text.capitalize() + f'. {end.capitalize()}.'))

def BaC_calc_1(number, user_num):
	global data_game
	bulls = 0
	cows = 0
	for i in range(4):
		if str(number)[i] == str(user_num)[i]:
			bulls += 1
		elif str(user_num)[i] in str(number):
			cows += 1
	data_game.append([user_num, bulls, cows])
	# print(number)
	message(f'{bulls} быка, {cows} коровы', pause = True)
	if bulls == 4:
		data_game = []
		return True
	return False

def BaC_calc_2(number, user_num, n):
	global data_game_first, data_game_second
	bulls = 0
	cows = 0
	for i in range(4):
		if str(number)[i] == str(user_num)[i]:
			bulls += 1
		elif str(user_num)[i] in str(number):
			cows += 1
	if n == 1:
		data_game_first.append([user_num, bulls, cows])
	elif n == 2:
		data_game_second.append([user_num, bulls, cows])
	# print(number)
	message(f'{bulls} быка, {cows} коровы', pause = True)
	if bulls == 4:
		if n == 1:
			data_game_first = []
		elif n == 2:
			data_game_second = []
		return True
	return False

def add_new_record(point, name):
	global records
	new_record = False
	for i in records:
		if (i == '0' or int(i.split('-')[0]) > point):
			new_record = True
			j = i
			records[records.index(i)] = f'{point}-{name}'
			point = int(j.split('-')[0])
			if point == 0:
				break
			else:
				name = j.split('-')[1]
	config = configparser.ConfigParser()
	config.read('conf.ini')
	[config.set('STATS', f'record{i}', f'{records[i - 1]}') for i in range(1, 6)]
	with open('conf.ini', 'w') as f:
		config.write(f)
	if new_record:
		message('результат записан в таблицу рекордов', pause = True)

# view fuctions
def menu():
	clear_screen()
	preview()
	option = proposition('меню', 'играть', 'статистика', 'настройки', 'выход')
	if option == 1:
		main()
	elif option == 2:
		statistics()
	elif option == 3:
		settings()

def statistics():
	clear_screen()
	preview()
	message('статистика')
	for record in records:
		if record != '0':
			timeout()
			print(BLUE + f'[{records.index(record) + 1}] ' + CYAN + ' — '.join(record.split('-')))

	if records == ['0' for i in range(5)]:
		error('у вас пока нет рекордов', end = 'сыграйте в первую игру')

	timeout(3)
	option = proposition(None, 'назад в меню', 'выход из игры')
	if option == 1:
		menu()

def settings():
	global time_out, language
	clear_screen()
	preview()
	option = proposition('настройки', f'язык ({language})', f'время построчного вывода ({time_out})', 'сбросить настройки', 'назад в меню')
	if option == 1:
		answer = proposition('выберете язык', 'русский', 'английский', 'польский', 'немецкий', 'французский', 'румынский')
		language = ('ru', 'en', 'pl', 'de', 'fr', 'ro')[answer - 1]
		config = configparser.ConfigParser()
		config.read('conf.ini')
		config.set('OTHER', 'language', language)
		with open('conf.ini', 'w') as f:
			config.write(f)
		message(f'язык успешно изменён на {language}')
		settings()
	elif option == 2:
		time_out = float(enter('введите время построчного вывода в секудах (например: 0.5)', re_str = r'\d+\.?(\d+)?'))
		config = configparser.ConfigParser()
		config.read('conf.ini')
		config.set('OTHER', 'timeout', str(time_out))
		with open('conf.ini', 'w') as f:
			config.write(f)
		message(f'время построчного вывода успешно изменено на {time_out}')
		settings()
	elif option == 3:
		option = proposition('вы уверены, что хотите вернуть настройки по-умолчанию (сброс настроек приведёт к обнулению рекордов)', 'сбросить настройки', 'отмена')
		if option == 1:
			restore_default_settings()
			set_const()
			message('настройки по-умолчанию восстановлены')
		settings()
	else:
		menu()

def main():
	global data_game, data_game_first, data_game_second
	clear_screen()
	mode = proposition('выберите режим игры', 'одиночная', 'игра на двоих')
	if mode == 1:
		name = enter('введите имя игрока')
		clear_screen()
		message('компьютер задумал число', pause = True)
		i = 0
		while True:
			number = random.randint(1000, 9999)
			if [str(number).count(ch) for ch in str(number)] == [1, 1, 1, 1]:
				break
		while True:
			i += 1
			message(f'ход №{i}')
			for j in data_game:
				print(BLUE + f'[{data_game.index(j) + 1}] ' + CYAN + translate(f'{j[0]} — {j[1]} быка, {j[2]} коровы'))
			user_num = enter('введите число', re_str = r'\d{4}')
			if BaC_calc_1(number, user_num):
				message(f'победа! число попыток: {i}', pause = True)
				add_new_record(i, name)
				break
			clear_screen()
		option = proposition(None, 'новая игра', 'назад в меню', 'выход из игры')
		if option == 1:
			main()
		elif option == 2:
			menu()
	else:
		name1 = enter('введите имя первого игрока')
		name2 = enter('введите имя второго игрока')
		clear_screen()
		while True:
			number1 = enter(f'{name1}, введите число')
			if [str(number1).count(ch) for ch in str(number1)] == [1, 1, 1, 1]:
				break
			else:
				error('число должно состоять из 4 неповторяющихся цифр') 
		clear_screen()
		while True:
			number2 = enter(f'{name2}, введите число')
			if [str(number2).count(ch) for ch in str(number2)] == [1, 1, 1, 1]:
				break
			else:
				error('число должно состоять из 4 неповторяющихся цифр') 
		clear_screen()
		i = 0
		exit = False
		while True:
			i += 1

			message(f'ход №{i}; игрок {name1}')
			for j in data_game_first:
				print(BLUE + f'[{data_game_first.index(j) + 1}] ' + CYAN + translate(f'{j[0]} — {j[1]} быка, {j[2]} коровы'))
			user_num1 = enter(f'{name1}, введите число', re_str = r'\d{4}')
			if BaC_calc_2(number2, user_num1, 1):
				message(f'угадал! число попыток: {i}', pause = True)
				add_new_record(i, name1)
				exit = True

			clear_screen()

			message(f'ход №{i}; игрок {name2}')
			for j in data_game_second:
				print(BLUE + f'[{data_game_second.index(j) + 1}] ' + CYAN + translate(f'{j[0]} — {j[1]} быка, {j[2]} коровы'))
			if exit:
				print()
				message('противник угадал ваше число: у вас последняя попытка!')
			user_num2 = enter(f'{name2}, введите число', re_str = r'\d{4}')
			if BaC_calc_2(number1, user_num2, 2):
				message(f'угадал! число попыток: {i}', pause = True)
				add_new_record(i, name2)
				exit = True

			if exit:
				message(f'{name1} загадал {number1}, {name2} загадал {number2}', pause = True)
				break
			clear_screen()
		clear_screen()
		if data_game_first == [] and data_game_second == []:
			message(f'{name1} и {name2} сыграли в ничью за {i} ходов!')
		elif data_game_first == []:
			message(f'{name1} победил за {i} ходов!')
			data_game_second = []
		elif data_game_second == []:
			message(f'{name2} победил за {i} ходов!')
			data_game_first = []
		option = proposition(None, 'новая игра', 'назад в меню', 'выход из игры')
		if option == 1:
			main()
		elif option == 2:
			menu()

avoid_fatal_error()

check_internet_connection()

set_const()

menu()

message('выход из игры')

print(Style.RESET_ALL)