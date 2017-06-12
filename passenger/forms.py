from django import forms
from django.utils.safestring import mark_safe
from passenger.models import StudentInfo, Branch
from django.contrib.auth.models import User
from django.template.loader import render_to_string

class StudentInfoWidget(forms.Widget):
    template_name = "studentInfo_widget.html"


    def render(self, name, value , attrs=None):
        branch = Branch.objects.all()
        context = {'branch':branch}
        return mark_safe(render_to_string(self.template_name, context))

class StudentInfoForm(forms.ModelForm):
    academySelection = forms.CharField(widget=StudentInfoWidget,required=False)

    class Meta:
        model = StudentInfo
        fields = "__all__"
