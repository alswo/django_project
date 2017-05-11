from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import ArrayField

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
    #building = models.IntegerField()

    class Meta:
        ordering = ['stime']

class ScheduleTable(models.Model):
    iid = models.ForeignKey(Inventory,related_name='scheduletables')
    time = models.CharField(max_length = 10,null=True,blank=True)
    addr = models.CharField(max_length = 30,null=True,blank=True)
    alist = ArrayField(models.IntegerField(null=True,blank=True),null=True,blank=True)
    anamelist = ArrayField(models.CharField(max_length = 10, null=True, blank=True),null=True, blank=True)
    slist = ArrayField(models.IntegerField(null=True,blank=True),null=True,blank=True)
    sname = ArrayField(models.CharField(max_length = 10,null=True,blank=True),null=True,blank=True)
    tflag = ArrayField(models.IntegerField(null=True,blank=True),null=True,blank=True)
    lflag = models.IntegerField()

    class Meta:
        ordering = ['id']

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
    carlist = ArrayField(models.IntegerField())
    alist = ArrayField(models.IntegerField())

class Building(models.Model):
    branch = Branch.objects.all()

    BRANCH = ()

    for b in branch:
        BRANCH = BRANCH + ((b.id, b.bname),)

    branchid = models.IntegerField(choices = BRANCH,default=1)
    name = models.CharField(max_length=20)
    lon = models.FloatField()
    lat = models.FloatField()
