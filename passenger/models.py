from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from schedule.models import Branch
from django.db import models
from django.utils import timezone
import datetime
import uuid
#from simple_history.models import HistoricalRecords
import re

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    bid = models.IntegerField(null=True)
    aid = models.IntegerField(null=True)
    cid = models.IntegerField(null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def set_current_date_time():
    return str(timezone.now())[:19]

class Group(models.Model):
    gname = models.CharField(max_length = 80, null = True, blank = True)
    academies = ArrayField(models.CharField(max_length = 30, null = True, blank = True))
    gid = models.IntegerField(null=True, blank = True)
    bid = models.IntegerField()

class Academy(models.Model):
    name = models.CharField(max_length = 50)
    address = models.CharField(max_length = 50)
    phone_1 = models.CharField(max_length = 30)
    phone_2 = models.CharField(max_length = 30, null = True, blank = True)
    gid = models.IntegerField(null=True, blank=True)
    gname = models.CharField(max_length = 80, null = True, blank = True)
    lon = models.FloatField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    bid = models.IntegerField()
    maxvehicle = models.IntegerField(default=1)

class Commute(models.Model):
    name = models.CharField(max_length = 10)
    a_name = models.CharField(max_length = 50)
    day = models.CharField(max_length = 20)
    stime = models.IntegerField(null = True, blank = True)
    etime = models.IntegerField(null = True, blank = True)
    aid = models.IntegerField()
    onlocation = models.CharField(max_length = 50,null = True, blank = True)
    offlocation = models.CharField(max_length = 50,null = True, blank = True)
    on_lon = models.FloatField(null=True, blank=True, default = 0)
    on_lat = models.FloatField(null=True, blank=True, default = 0)
    off_lon = models.FloatField(null=True, blank=True, default = 0)
    off_lat = models.FloatField(null=True, blank=True, default = 0)
    etc = models.TextField(null = True, blank = True)
    #history = HistoricalRecords()

#class PhoneList(models.Model):
    #aca = Academy.objects.all()
    #ACA = ()
    #ACA_2 = ()
    #for a in aca:
        #ACA = ACA + ((a.id, a.name),)
        #ACA_2 = ACA_2 + ((a.name, a.name),)
    ##print(ACA)
    #name = models.CharField(max_length = 10)
    #aid = models.IntegerField(choices = ACA)
    #aname = models.CharField(choices = ACA_2, max_length=30)
    #phone1 = models.CharField(max_length = 30, null = True, blank = True)
    #phone2 = models.CharField(max_length = 30, null = True, blank = True)

class Schedule(models.Model):
    name = models.CharField(max_length = 50)
    s_name = models.CharField(max_length = 50)
    location = models.CharField(max_length = 50)
    s_phone = models.CharField(max_length = 30, null = True, blank = True)
    m_phone = models.CharField(max_length = 30, null = True, blank = True)
    f_phone = models.CharField(max_length = 30 , null = True, blank = True)
    schedule = ArrayField(models.CharField(max_length = 30, null = True, blank = True))
    load = models.CharField(max_length = 10, null = True, blank = True)
    unload = models.CharField(max_length = 10, null = True, blank = True)
    academy_id = models.IntegerField(blank=True, null=True)
    gid = models.IntegerField(blank=True, null = True)
    l_lon = models.FloatField(null=True, blank=True)
    l_lat = models.FloatField(null=True, blank=True)
    u_lon = models.FloatField(null=True, blank=True)
    u_lat = models.FloatField(null=True, blank=True)
    bid = models.IntegerField(null=True, default = 1)

class Attendance(models.Model):
    name = models.CharField(max_length = 10)
    a_name = models.CharField(max_length = 50)
    schedule = models.CharField(max_length = 50)
    absence = models.IntegerField()
    d_date = models.DateField()
    student_id = models.IntegerField()
    academy_id = models.IntegerField()

class Shuttle(models.Model):
    name = models.CharField(max_length = 10)
    car_number = models.CharField(max_length = 10)

class Driver(models.Model):
    name = models.CharField(max_length = 10)
    phone = models.CharField(max_length = 30)
    age = models.CharField(max_length = 10)
    address = models.CharField(max_length = 50)
    rating = models.IntegerField()

class Passenger(models.Model):
    name = models.CharField(max_length = 10)
    age = models.CharField(max_length = 10)
    phone = models.CharField(max_length = 30)
    address = models.CharField(max_length = 50)
    rating = models.IntegerField()

class Daily(models.Model):
    shuttle_id = models.IntegerField()
    driver_id = models.IntegerField()
    passenger_id = models.IntegerField()
    academy_id = models.IntegerField()
    driver_rating = models.IntegerField()
    driver_velocity_rating = models.IntegerField()
    passenger_rating = models.IntegerField()
    before_1 = models.IntegerField()
    before_2 = models.IntegerField(null = True, blank = True)
    before_3 = models.IntegerField(null = True, blank = True)
    before_4 = models.IntegerField(null = True, blank = True)
    after_1 = models.IntegerField()
    after_2 = models.IntegerField(null = True, blank = True)
    after_3 = models.IntegerField(null = True, blank = True)
    after_4 = models.IntegerField(null = True, blank = True)
    total_load = models.IntegerField()
    load_num = models.IntegerField()
    total_unload = models.IntegerField()
    unload_num = models.IntegerField()
    unload_stu = models.CharField(max_length = 100)
    good_stu = models.CharField(max_length = 10)

class ShuttleSchedule(models.Model):
    #aca = Academy.objects.all()
    grp = Group.objects.all()

    GID = ()
    #ACA = ()
    #ACA_2 = ()

    for g in grp:
        GID = GID + ((g.gid, g.gname),)

    #for a in aca:
        #ACA = ACA + ((a.id, a.name),)

    a_name = models.CharField(max_length = 30)
    day = models.CharField(max_length = 10)
    time = models.IntegerField()
    schedule = models.TextField()
    gid = models.IntegerField(choices = GID)
    #aid = models.IntegerField(choices = ACA)
    aid = models.IntegerField()
    slist = ArrayField(models.IntegerField(null = True, blank = True, default=0))
    p_schedule = models.TextField(null = True, blank = True)
    alist = ArrayField(models.IntegerField(null = True, blank = True, default=0))
    memo = models.TextField(null = True, blank = True)
    bid = models.IntegerField(null=True, blank = 1)

class Grade(models.Model):
    name = models.CharField(max_length = 30)

class PersonalInfo(models.Model):
    #pass
    pin_number = models.CharField(max_length = 7)
    created_time = models.CharField(max_length = 19, default = set_current_date_time())

class StudentInfo(models.Model):
    aid = models.ForeignKey('Academy', null=True)
    bid = models.IntegerField()
    aname = models.CharField(max_length = 20)
    bname = models.CharField(max_length = 20)
    sname = models.CharField(max_length = 10)
    grade = models.IntegerField(null = True, blank = True)
    phone1 = models.IntegerField()
    phonelist = ArrayField(models.IntegerField(null = True, blank = True,default=0),default=0)
    pin_number = models.CharField(max_length = 20, default=uuid.uuid4().hex[:10].upper())
    deleted_date = models.DateField(null=True)
    personinfo = models.ForeignKey(PersonalInfo, null=True)
    parents_phonenumber = models.CharField(max_length=15, null = True)
    grandparents_phonenumber = models.CharField(max_length=15, null = True)
    self_phonenumber = models.CharField(max_length=15, null = True)
    care_phonenumber = models.CharField(max_length=15, null = True)

    birth_year = models.CharField(max_length=4, null=True)
    birth_day = models.CharField(max_length=4, null=True)
    billing_date = models.CharField(max_length=2, null=True)

    created_time = models.CharField(max_length = 19, default = set_current_date_time())
    sended_time = models.CharField(max_length = 20, null = True)

    def __unicode__(self):
        return u"{0} // {1} // {2} // {3} // {4}".format(self.bname,self.aname,self.sname,self.grade,self.phone1)

class AcademySchedule(models.Model):
    gid = models.IntegerField()
    aid =  models.CharField(max_length = 20,null = True, blank = True)
    aname = ArrayField(models.CharField(max_length = 20,null = True, blank = True))
    schedule1 = ArrayField(models.CharField(max_length = 20, null = True, blank = True))
    schedule2 = ArrayField(models.CharField(max_length = 20, null = True, blank = True))
    schedule3 = ArrayField(models.CharField(max_length = 20, null = True, blank = True))
    schedule4 = ArrayField(models.CharField(max_length = 20, null = True, blank = True))
    schedule5 = ArrayField(models.CharField(max_length = 20, null = True, blank = True))
    schedule6 = ArrayField(models.CharField(max_length = 20, null = True, blank = True))

class ScheduleDate(models.Model):
    a_name = models.CharField(max_length = 30)
    day = models.CharField(max_length = 10)
    time = models.IntegerField()
    schedule = models.TextField()
    gid = models.IntegerField()
    aid = models.IntegerField()
    slist = ArrayField(models.IntegerField(null = True, blank = True, default=0))
    p_schedule = models.TextField(null = True, blank = True)
    alist = ArrayField(models.IntegerField(null = True, blank = True, default=0))
    memo = models.TextField(null = True, blank = True)
    date = models.CharField(max_length = 30)
    today = models.DateField(default=datetime.date.today)

class Community(models.Model):
    aname = models.CharField(max_length=50)
    datetime = models.DateTimeField(default=datetime.date.today)
    complain = models.TextField()
    plan = models.TextField()
    showdate = models.CharField(max_length=50)
    clike = models.IntegerField(default=0)
    dlike = models.IntegerField(default=0)
    disuserid = ArrayField(models.IntegerField(null=True,default=0))
    likeuserid = ArrayField(models.IntegerField(null=True,default=0))
    disuser = ArrayField(models.CharField(null=True,max_length=30,default=''))
    likeuser = ArrayField(models.CharField(null=True,max_length=30,default=''))
