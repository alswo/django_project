from util.PhoneNumber import CleanPhoneNumber, FormatPhoneNumber

def run():
	for phone_number in ["010-5397-7071", "02-5397--7071"]:
		clean_phone_number = CleanPhoneNumber(phone_number)
		print "clean_phone_number = " + clean_phone_number
		format_phone_number = FormatPhoneNumber(clean_phone_number)
		print "format_phone_number = " + format_phone_number
