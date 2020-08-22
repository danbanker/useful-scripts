import os
import sys
import time
from datetime import datetime, date, timedelta


class DateTimeTools():
    def __init__(self):
        os.environ['TZ'] = 'US/Eastern'
        self.current = datetime.now()
        self.current_date = date.today()
        self.tomorrow = self.current_date + timedelta(days=1)
        self.yesterday = self.current_date + timedelta(days=-1)
        self.current_year = self.current_date.year
        self.current_month = self.current_date.month
        self.current_fulltime = str(datetime.now().strftime("%A, %B %d, %Y %I:%M%p"))
        self.current_day = str(datetime.now().strftime("%A"))
        self.current_hour = str(datetime.now().strftime("%I"))
        self.current_minute = str(datetime.now().strftime("%M"))
        self.current_AMPM = str(datetime.now().strftime("%p"))
        self.BoT = datetime.utcfromtimestamp(0).date()  # Beginning of time
        self.current_yyyymmdd = self.format_undashed_yyyymmdd(self.current_date)
        self.current_yyyymmddhhmmss = self.format_undashed_yyyymmddhhmmss(self.current)
        self.current_yyyymmdd_dashed = self.format_dashed_yyyymmdd(self.current_date)
        self.yesterday_yyyymmdd_dashed = self.format_dashed_yyyymmdd(self.yesterday)

    def parse_date_args(self, start_date=None, end_date=None, pull_all=None):
        if start_date:
            start_date = start_date.date()

        if end_date:
            end_date = end_date.date()

        if not any([start_date, end_date, pull_all]):
            start_d = end_d = self.current_date
        elif start_date and end_date and not pull_all:
            start_d = start_date
            end_d = end_date
        elif start_date and not any([end_date, pull_all]):
            start_d = start_date
            end_d = self.current_date
            # print(start_d)
            # print(end_d)
            # print('this')
        elif end_date and not any([start_date, pull_all]):
            start_d = self.BoT
            end_d = end_date
        elif pull_all:
            start_d = self.BoT
            end_d = self.current_date
            # print(start_d)
            # print(end_d)
        else:
            print("Error: No valid input for parse_date_args.")
            sys.exit(1)
        return start_d, end_d

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days) + 1):
            yield self.format_for_pgsql(start_date + timedelta(n))

    def format_dashed_yyyymmdd(self, input_date):
        return_date = input_date.strftime('%Y-%m-%d')
        return return_date

    def format_undashed_yyyymmdd(self, input_date):
        return_date = input_date.strftime('%Y%m%d')
        return return_date

    def format_undashed_yyyymmddhhmmss(self, input_date):
        return_date = input_date.strftime('%Y%m%d%H%M%S')
        return return_date

    def format_dashcolon_yyyymmddhhmmss(self, input_date):
        return_date = input_date.strftime('%Y-%m-%d %H:%M:%S')
        return return_date