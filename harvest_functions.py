import time
from recordsearch_tools.client import RSAgencySearchClient, RSItemClient, RSSeriesClient, RSSearchClient, RSSeriesSearchClient, UsageError, TooManyError
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from credentials import MONGOLAB_URL
import random
import re
from datetime import datetime
import pprint

pp = pprint.PrettyPrinter(indent=4)


class FunctionHarvester():
    """
    Harvest the details of agencies associated with a particular function.
    """
    def __init__(self, function):
        self.function = function
        self.total_pages = None
        self.pages_complete = 0
        self.client = RSAgencySearchClient()
        self.prepare_harvest()
        db = self.get_db()
        self.functions = db.functions
        self.agencies = db.agencies
        self.agencies.create_index('agency_id', unique=True)

    def get_db(self):
        dbclient = MongoClient(MONGOLAB_URL)
        db = dbclient.get_default_database()
        return db

    def get_total(self):
        return self.client.total_results

    def prepare_harvest(self):
        self.client.search_agencies(results_per_page=0, function=self.function)
        total_results = self.client.total_results
        print '{} agencies'.format(total_results)
        self.total_pages = (int(total_results) / self.client.results_per_page) + 1
        print '{} pages'.format(self.total_pages)

    def start_harvest(self, page=None):
        if not page:
            page = self.pages_complete + 1
        else:
            self.pages_complete = page - 1
        while self.pages_complete < self.total_pages:
            response = self.client.search_agencies(page=page, function=self.function)
            agencies = []
            for result in response['results']:
                print result['agency_id']
                agency = {'agency_id': result['agency_id'], 'title': result['title']}
                agency['agency_status'] = result['agency_status']
                agency['location'] = result['location']
                agency['start_date'] = result['dates']['start_date']
                agency['end_date'] = result['dates']['end_date']
                for function in result['functions']:
                    if function['identifier'] == self.function:
                        agency['function_start'] = function['start_date']
                        agency['function_end'] = function['end_date']
                agencies.append(agency)
                try:
                    self.agencies.insert(result)
                except DuplicateKeyError:
                    pass
            self.functions.update_one({'function': self.function}, {'$push': {'agencies': {'$each': agencies}}}, upsert=True)
            self.pages_complete += 1
            page += 1
            print '{} pages complete'.format(self.pages_complete)
            time.sleep(1)


class SeriesHarvester():
    """
    Works through agencies associated with a harvested function.
    Grabs series in the function date range and gets some details.
    """

    def __init__(self, function):
        self.function = function
        self.total_pages = 0
        self.pages_complete = 0
        self.series_client = RSSeriesSearchClient()
        self.search_client = RSSearchClient()
        db = self.get_db()
        self.functions = db.functions
        self.series = db.series
        self.series.create_index('identifier', unique=True)

    def get_db(self):
        dbclient = MongoClient(MONGOLAB_URL)
        db = dbclient.get_default_database()
        return db

    def start_harvest(self):
        # Get agencies in function
        function = self.functions.find_one({'function': self.function})
        agencies = []
        for agency in function['agencies']:
            if agency['agency_id'] == 'CA 51':
                self.pages_complete = 0
                page = 1
                if not agency['function_start']['date']:
                    function_start = '1900'
                else:
                    function_start = str(agency['function_start']['date'].year)
                if not agency['function_end']['date']:
                    function_end = datetime.datetime.now().year
                else:
                    function_end = str(agency['function_end']['date'].year)
                series_list = []
                self.prepare_harvest(agency, function_start, function_end)
                while self.pages_complete < self.total_pages:
                    response = self.series_client.search_series(page=page, agency_recording=agency['agency_id'], date_from=function_start, date_to=function_end)
                    for result in response['results']:
                        if result['items_digitised'] == '20000+':
                            result['items_digitised'] = 20000
                        elif result['items_digitised'] is None:
                            result['items_digitised'] = 0
                        series = {
                            'series_id': result['identifier'],
                            'title': result['title'],
                            'items_described': int(result['items_described']['described_number']),
                            'items_digitised': result['items_digitised']
                        }
                        try:
                            self.search_client.search(digitised=False, series=result['identifier'], date_from=function_start, date_to=function_end)
                            series['items_described_in_period'] = int(self.search_client.total_results)
                        except TooManyError:
                            series['items_described_in_period'] = 20000
                        try:
                            self.search_client.search(digitised=False, series=result['identifier'], date_from=function_start, date_to=function_end, digital=['on'])
                            series['items_digitised_in_period'] = int(self.search_client.total_results)
                        except TooManyError:
                            series['items_digitised_in_period'] = 20000
                        pp.pprint(series)
                        series_list.append(series)
                        try:
                            self.series.insert(result)
                        except DuplicateKeyError:
                            pass
                    self.pages_complete += 1
                    page += 1
                    time.sleep(1)
                agency['series'] = series_list
                agencies.append(agency)
            self.functions.update_one({'function': self.function}, {'$set': {'agencies': agencies}})

    def get_total(self):
        return self.client.total_results

    def prepare_harvest(self, agency, function_start, function_end):
        self.pages_complete = 0
        print agency['agency_id']
        self.series_client.search_series(results_per_page=0, agency_recording=agency['agency_id'], date_from=function_start, date_to=function_end)
        total_results = self.series_client.total_results
        if total_results is not None:
            print '{} series'.format(total_results)
            self.total_pages = (int(total_results) / self.series_client.results_per_page) + 1
            print '{} pages'.format(self.total_pages)
        else:
            print 'No series'
