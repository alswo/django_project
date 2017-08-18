import re

def CleanPhoneNumber(phone_number):
	if not phone_number:
		return phone_number
	clean_phone_number = re.sub(r'[^0-9]+', '', phone_number)
	return clean_phone_number

def FormatPhoneNumber(phone_number):
	format_phone_number = re.sub(r'^(02|0\d{2})(\d{3,4})(\d{4})$', r'\1-\2-\3', phone_number)
	return format_phone_number
