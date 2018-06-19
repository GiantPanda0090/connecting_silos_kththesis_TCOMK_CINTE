# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

class Allowed_course_id(models.Model):
  course_id_install = models.IntegerField()
  

class Related_assignment_id(models.Model):
  course_id_install =models.ManyToManyField(Allowed_course_id, through='U_1data')
  assignment_id = models.IntegerField()
  assignment_id_beta = models.IntegerField()
  assignment_id_thesis = models.IntegerField()

class U_1data(models.Model):
    course_id_install = models.ForeignKey(Allowed_course_id, on_delete=models.CASCADE)	
    related_assignment_id = models.ForeignKey(Related_assignment_id, on_delete=models.CASCADE)

