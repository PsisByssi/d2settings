from pprint import pprint
import csv
import time


def first_letter(row):
	'''Returns the first letter of first item in a list'''
	try:
		return row[0][0]
	except IndexError:
		pass

def read_settings():
	cfg_settings = {}
	with open('autoexec.cfg', 'r', newline='') as f:
		reader = csv.reader(f, delimiter=' ')
		for i, row in enumerate(reader):
			char = first_letter(row)
			if char not in ('/','\\', '','') and char:	# Ignore Comments and blank lines
				setting = row[0]
				cfg_values = row[1:]
				for i, value in enumerate(row[1:]):
					del cfg_values[i]					# remove the old string contain tabs
					for j, sub_sec in enumerate(value.split('\t')):
						cfg_values.insert(i+j, sub_sec)	# add the newly split peaces in sameorder
				cfg_settings[setting] = cfg_values		# save the setting and values 
	return cfg_settings
			

def save_settings(self, selected_setting):
	f = open('autoexec.cfg', 'w+')
	reader = csv.reader(f, delimiter=' ')
	for row in reader:
		print (row[0], selected_setting[0])
		if row[0] == selected_setting[0]:
			row[1] = selected_setting[1]
		f.writerow(row)
	read_settings()
