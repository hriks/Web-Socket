# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class WorkBook(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    role = models.CharField(max_length=64)
    level = models.CharField(max_length=16)
    primary_skill = models.CharField(max_length=64)
    secondary_skill = models.CharField(max_length=64)
    description = models.TextField()
