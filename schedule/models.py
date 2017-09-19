from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
#from simple_history.models import HistoricalRecords

class Inventory(models.Model):
    carnum = models.IntegerField()
    bid = models.IntegerField()
    snum = models.IntegerField()
    day = models.CharField(max_length=5)
    alist = ArrayField(models.IntegerField())
    anamelist = ArrayField(models.CharField(max_length = 10, default={'none'}),default={'none'})
    slist = ArrayField(models.IntegerField())
    stime = models.IntegerField()
    etime = models.IntegerField()
    week1 = models.IntegerField()
    week2 = models.IntegerField()
    week3 = models.IntegerField()
    #building = models.IntegerField()
    req = models.TextField()
    memo = models.TextField(null=True,blank=True)
    #history = HistoricalRecords()

    def __unicode__(self):
        return "[{0}] [{1}] {2} {3}~{4}".format(self.bid, self.carnum, self.day, self.stime, self.etime)

    class Meta:
        ordering = ['day', 'stime']

class ScheduleTable(models.Model):
    iid = models.ForeignKey(Inventory,related_name='scheduletables')
    time = models.CharField(max_length = 10,null=True,blank=True)
    addr = models.CharField(max_length = 60,null=True,blank=True)
    req = models.CharField(max_length = 20,null=True,blank=True)
    alist = ArrayField(models.IntegerField(null=True,blank=True),null=True,blank=True)
    anamelist = ArrayField(models.CharField(max_length = 10, null=True, blank=True),null=True, blank=True)
    slist = ArrayField(models.IntegerField(null=True,blank=True),null=True,blank=True)
    sname = ArrayField(models.CharField(max_length = 10,null=True,blank=True),null=True,blank=True)
    tflag = ArrayField(models.IntegerField(null=True,blank=True),null=True,blank=True)
    lflag = models.IntegerField()
    #history = HistoricalRecords()

    def __unicode__(self):
        return u"{0} {1} {2} - {3}".format(self.time,self.iid, self.addr , ",".join(self.sname))

    class Meta:
        ordering = ['iid', 'time']

class EditedInven(models.Model):
    carnum = models.IntegerField()
    bid = models.IntegerField()
    snum = models.IntegerField()
    iid = models.ForeignKey(Inventory,related_name='editedinvens', null = True)
    day = models.CharField(max_length=5)
    alist = ArrayField(models.IntegerField())
    anamelist = ArrayField(models.CharField(max_length = 10, default={'none'}),default={'none'})
    slist = ArrayField(models.IntegerField())
    stime = models.IntegerField()
    etime = models.IntegerField()
    week = models.IntegerField()
    req = models.TextField()
    memo = models.TextField(null=True,blank=True)

    def __unicode__(self):
        return "[{0}] [{1}] {2} {3}~{4}".format(self.bid, self.carnum, self.day, self.stime, self.etime)

    def get_cname(self):
        class_name = 'editedinven'
        return class_name

class EditedScheduleTable(models.Model):
    ieid = models.ForeignKey(EditedInven,related_name='editedscheduletables')
    time = models.CharField(max_length = 10,null=True,blank=True)
    addr = models.CharField(max_length = 60,null=True,blank=True)
    req = models.CharField(max_length = 20,null=True,blank=True)
    alist = ArrayField(models.IntegerField(null=True,blank=True),null=True,blank=True)
    anamelist = ArrayField(models.CharField(max_length = 10, null=True, blank=True),null=True, blank=True)
    slist = ArrayField(models.IntegerField(null=True,blank=True),null=True,blank=True)
    sname = ArrayField(models.CharField(max_length = 10,null=True,blank=True),null=True,blank=True)
    tflag = ArrayField(models.IntegerField(null=True,blank=True),null=True,blank=True)
    lflag = models.IntegerField()

    def __unicode__(self):
        return u"{0} {1} {2} - {3}".format(self.time,self.ieid, self.addr , ",".join(self.sname))

    class Meta:
        ordering = ['ieid', 'time']

class HistoryScheduleTable(models.Model):
    #date = models.DateField(auto_now=True)
    date = models.CharField(max_length=10,null=True,blank=True)
    #iid = models.ForeignKey(Inventory,related_name='historyscheduletables')
    iid_id = models.IntegerField()
    carnum = models.IntegerField()
    time = models.CharField(max_length = 10,null=True,blank=True)
    addr = models.CharField(max_length = 60,null=True,blank=True)
    req = models.CharField(max_length = 20,null=True,blank=True)
    alist = ArrayField(models.IntegerField(null=True,blank=True),null=True,blank=True)
    academies = models.ManyToManyField('passenger.Academy')
    #members = models.ManyToManyField('passenger.StudentInfo')
    members = models.ManyToManyField('passenger.StudentInfo', related_name='scheduled_members')
    offmembers = models.ManyToManyField('passenger.StudentInfo', related_name='off_members')
    tflag = ArrayField(models.IntegerField(null=True,blank=True),null=True,blank=True)
    lflag = models.IntegerField()

    def __unicode__(self):
        return u"{0} {1} {2}".format(self.time,self.iid_id, self.addr)
        #return u"{0} {1} {2}".format(self.time,self.iid, self.addr)

    class Meta:
        ordering = ['iid_id', 'time']
        #ordering = ['iid', 'time']

class InventoryRequest(models.Model):
    iid = models.ForeignKey(Inventory,related_name='inventoryrequest')
    aid = models.IntegerField()
    aname = models.CharField(max_length=10)
    sid = models.IntegerField()
    sname = models.CharField(max_length=10)
    kind = ArrayField(models.IntegerField())
    contents = models.TextField()
    done = models.IntegerField()
    towho = models.IntegerField()

class Area(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class Branch(models.Model):
    bname = models.CharField(max_length = 15)
    areaid = models.ForeignKey(Area,default=0)
    #location seoul, kyungi
    location = models.CharField(max_length = 15)
    lon = models.FloatField()
    lat = models.FloatField()

    def __unicode__(self):
        return self.bname

class Car(models.Model):
    carname = models.IntegerField(unique=True)
    branchid = models.ForeignKey(Branch)
    driver = models.IntegerField(default=0)
    passenger = models.IntegerField(default=0)

    class Meta:
        ordering=['carname']

class Building(models.Model):
    #branch = Branch.objects.all()

    #BRANCH = ()

    #for b in branch:
        #BRANCH = BRANCH + ((b.id, b.bname),)

    branchid = models.IntegerField(default=1)
    name = models.CharField(max_length=20)
    lon = models.FloatField()
    lat = models.FloatField()

class RealtimeLocation(models.Model):
    carnum = models.IntegerField()
    date = models.CharField(max_length=10)
    schedule_time = models.CharField(max_length=10)
    departure_time = models.CharField(max_length=10)

class TodayLoadTimeLog(models.Model):
    sid = models.ForeignKey('passenger.StudentInfo')
    stable = models.ForeignKey(ScheduleTable)
    reqtime = models.CharField(max_length = 20)

