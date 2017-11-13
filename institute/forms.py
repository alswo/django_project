# -*- coding: utf-8 -*-
from django import forms
import os

IMPORT_FILE_TYPES = ['.xls', ]

class XlsInputForm(forms.Form):
	input_excel = forms.FileField(required = True, label = "Upload the file")

	def clean_input_excel(self):
		input_excel = self.cleaned_data['input_excel']
		extension = os.path.splitext(input_excel.name)[1]

		if not (extension in IMPORT_FILE_TYPES):
			raise forms.ValidationError()
		else:
			return input_excel
