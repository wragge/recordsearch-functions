import time
from recordsearch_tools.client import RSAgencySearchClient, RSItemClient, RSSeriesClient, UsageError
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from credentials import MONGOLAB_URL
import random
import re
from datetime import datetime

class FunctionHarvester():
    """
    Harvest the details of 'Closed' files from RecordSearch.
    Saves to MongoDB.
    harvester = SearchHarvester(harvest='2015-12-31')
    harvester.start_harvest()
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
        self.client.search_agencies(results_per_page=0,function=self.function)
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