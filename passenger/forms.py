from django import forms
from django.utils.safestring import mark_safe
from passenger.models import StudentInfo, Branch, Profile, Academy
from schedule.models import Area
from django.contrib.auth.models import User
from django.template.loader import render_to_string

class CustomModelChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s" % (obj.name)

class StudentInfoForm(forms.ModelForm):
    aid = CustomModelChoiceField(queryset=Academy.objects.all())

    class Meta:
        model = Academy
        fields = "__all__"

class ProfileInfoWidget(forms.Widget):
    template_name = "profile_widget.html"

    def render(self, name, value , attrs=None):
        bid = Branch.objects.all()
        context = {'bid':bid}
        return mark_safe(render_to_string(self.template_name, context))

class ProfileInfoForm(forms.ModelForm):
    academySelection = forms.CharField(widget=ProfileInfoWidget,required=False)

    class Meta:
        model = Profile
        fields = "__all__"

class AcademyWidget(forms.Widget):
    template_name = "academy_widget.html"


    def render(self, name, value , attrs=None):
        branch = Branch.objects.all()
        context = {'branch':branch}
        return mark_safe(render_to_string(self.template_name, context))

class AcademyForm(forms.ModelForm):
    branchSelection = forms.CharField(widget=AcademyWidget,required=False)

    class Meta:
        model = Academy
        fields = "__all__"
