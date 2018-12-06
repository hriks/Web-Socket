# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.decorators import method_decorator
from django.shortcuts import render
from django import views
from django.http import JsonResponse

import StringIO
import csv
import xlrd
import json

from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher


class Dashboard(views.View):
    template_name = "dashboard.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    @method_decorator(views.decorators.csrf.csrf_exempt)
    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('files[]')
        counter = 0
        filepaths = []
        while counter < len(files):
            filepaths.append(self.save_filename(files[counter]))
            counter += 1
        self.process_workbook(filepaths)
        return JsonResponse({}, status=200)

    def save_filename(self, file):
        """
        Get file from request, saves in MEDIA_ROOT
        and return pull filepath.
        """
        fname = 'media/' + str(file)
        try:
            with open(fname, "w") as f:
                data = file.read()
                f.write(data)
            return fname
        except Exception:
            return False

    def process_workbook(self, filepaths):
        redis_publisher = RedisPublisher(
            facility='processing', **{'broadcast': True})
        counter = 1
        redis_data = {
            "total_rows": 0,
            "rows_processed": 0,
            "rows_ignored": 0,
            "jd_created": 0,
            "error": False,
            "error_message": ""
        }
        for filepath in filepaths:
            try:
                data = self.readxlsx(filepath)
                redis_data["total_rows"] += len(data)
                message = RedisMessage(json.dumps(redis_data))
                redis_publisher.publish_message(message)
                from core.models import WorkBook
                for row in data:
                    redis_data["rows_processed"] += 1
                    workbook, created = WorkBook.objects.get_or_create(
                        id=row['ID'])
                    if not created:
                        redis_data["rows_ignored"] += 1
                    else:
                        redis_data['jd_created'] += 1
                        workbook.role = row['Role']
                        workbook.level = row['Level']
                        workbook.primary_skill = row['Primary Skill']
                        workbook.secondary_skill = row['Secondary Skill']
                        workbook.description = row['Description']
                        workbook.save()
                    message = RedisMessage(json.dumps(redis_data))
                    redis_publisher.publish_message(message)
                counter += 1
            except KeyError:
                redis_data['error'] = True
                redis_data['error_message'] = "Some fields are missing in file %s<br>" % filepath.replace('media/', '')  # noqa
                message = RedisMessage(json.dumps(redis_data))
                redis_publisher.publish_message(message)
                continue
            except xlrd.XLRDError:
                redis_data['error'] = True
                redis_data['error_message'] += "Invalid File Provided %s<br>" % filepath.replace('media/', '')  # noqa
                message = RedisMessage(json.dumps(redis_data))
                redis_publisher.publish_message(message)
                continue

    def readxlsx(self, filename):
        """Read Excel file and return rows in list.
        """
        workbook = xlrd.open_workbook(filename)
        sheet_names = workbook.sheet_names()
        worksheet = workbook.sheet_by_name(sheet_names[0])
        f = StringIO.StringIO()
        wr = csv.writer(f)
        nrows = worksheet.nrows
        for rownum in xrange(nrows):
            wr.writerow(
                list(
                    x.encode('utf-8') if type(x) == type(u'') else x for x in worksheet.row_values(rownum)) # noqa
            )
        f.seek(0)
        input_file = csv.DictReader(f)
        data = []
        for row in input_file:
            data.append(row)
        return data
