from django.test import TestCase
from passenger.models import StudentInfo
# Create your tests here.

sinfo = StudentInfo.objects.all()

for s in sinfo:
    if len(s.aid) > 1:
        s.id

