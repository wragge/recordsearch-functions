# RecordSearch Functions

Some code to harvest and play around with the functions associated with Australian government agencies in the National Archives of Australia's RecordSearch database.

See here for a [list of the functions](https://github.com/wragge/recordsearch-functions/blob/master/functions.txt) in use.

## Requirements

To set up your own harvest you'll need my [RecordSearch Tools repository](https://github.com/wragge/recordsearch_tools). Just `git clone` it into your working directory. A list of [other requirements is here](https://github.com/wragge/recordsearch-functions/blob/master/requirements.txt).

## Setting things up

Assuming you have Python, Git, Pip and Virtualenv installed, and you know how to use the command line:

* Create a new working directory with virtualenv -- `virtualenv mynewdirectory`
* Move to the new directory -- `cd mynewdirectory`
* Activate your environment -- `source bin/activate`
* Clone this repo -- `git clone https://github.com/wragge/recordsearch-functions.git`
* Move to the repo directory -- `cd recordsearch-functions`
* Clone RecordSearch Tools -- `git clone https://github.com/wragge/recordsearch_tools.git`
* Install other requirements -- `pip install -r requirements.txt`

The harvester is expecting to save data to a MongoDB database hosted by [MongoLab](https://mongolab.com/). You can set up a sandbox database for free. Once you've created your database, you'll need to add a user who can access it. Then just:

* Copy the MongoDB URI from your database's control panel to the `credentials_blank.py` file.
* Replace `<dbuser>` and `<dbpassword>` in the URI with your database user's details. 
* Rename `credentials_blank.py` to `credentials.py`.

Of course you can change this to point to a local MongoDB instance, or anywhere else really.

## Starting a harvest

Assuming you're in the `recordsearch-functions` directory, just:

* Start up Python, or preferably iPython -- `ipython`
* Import the harvest module -- `import harvest_functions`
* Set up a harvester instance, supplying the name of the function you want to harvest, eg. MIGRATION -- `harvester = harvest_functions.FunctionHarvester(function='MIGRATION')`
* If everything's working you'll see the number of agencies that are going to be harvested, and the number of results pages that will be processed.
* Then just start the harvest -- `harvester.start_harvest()`

## Analysing the harvested data

Save a summary of the agencies associated with a particular function to a CSV file:

* Start up Python, or preferably iPython -- `ipython`
* Import the analyse module -- `import analyse_functions`
* Create a CSV file for a single function, eg. MIGRATION -- `analyse_functions.write_csv('MIGRATION')`
* Create CSV files for all harvested functions -- `analyse_functions.write_csv()`

Look in the [data](https://github.com/wragge/recordsearch-functions/tree/master/data) directory for some example CSV files.

Aggregate agencies associated with a particular function by their status, eg. 'Department of State', or 'Head Office':

* Start up Python, or preferably iPython -- `ipython`
* Import the analyse module -- `import analyse_functions`
* Aggregate agencies for a single function, eg. 'INTERNAL SECURITY' -- `analyse_functions.calculate_status_totals('INTERNAL SECURITY')`

The results look something like this:

```python
[
    {u'agency_status': u'Regional or State Office', u'total': 22},
    {u'agency_status': u'Head Office', u'total': 10},
    {u'agency_status': u'Local Office', u'total': 1},
    {u'agency_status': u'Judicial Court or Tribunal', u'total': 1},
    {u'agency_status': u'Department of State', u'total': 1}
]
 ```

Retrieve a list of agencies by function and agency status:

* Start up Python, or preferably iPython -- `ipython`
* Import the analyse module -- `import analyse_functions`
* Retrieve agencies with a particular status, associated with a specific function -- `analyse_functions.get_agencies('MIGRATION', status='Department of State')`

The result is a list of agencies, something like this:

```python
[
    {
        u'agency_id': u'CA 9152',
        u'agency_status': u'Department of State',
        u'end_date': {
            u'date': datetime.datetime(2013, 9, 18, 0, 0),
            u'day': True,
            u'month': True
            },
        u'function_end': {
            u'date': datetime.datetime(2013, 9, 18, 0, 0),
            u'day': True,
            u'month': True
            },
        u'function_start': {
            u'date': datetime.datetime(2007, 1, 30, 0, 0),
            u'day': True,
            u'month': True},
        u'location': u'Australian Capital Territory',
        u'start_date': {
            u'date': datetime.datetime(2007, 1, 30, 0, 0),
            u'day': True,
            u'month': True
            },
        u'title': u'Department of Immigration and Citizenship, Central Office'
    },
    {
        u'agency_id': u'CA 9431',
        u'agency_status': u'Department of State',
        u'end_date': {
            u'date': None, 
            u'day': False, 
            u'month': False
            },
        u'function_end': {
            u'date': None, 
            u'day': False, 
            u'month': False
            },
        u'function_start': {
            u'date': datetime.datetime(2013, 9, 18, 0, 0),
            u'day': True,
            u'month': True
            },
        u'location': u'Australian Capital Territory',
        u'start_date': {
            u'date': datetime.datetime(2013, 9, 18, 0, 0),
            u'day': True,
            u'month': True
            },
        u'title': u'Department of Immigration and Border Protection, Central Office'
    }
]
```

Plot a list of agencies by function and agency status:

* Start up Python, or preferably iPython -- `ipython`
* Import the analyse module -- `import analyse_functions`
* Retrieve agencies with a particular status, associated with a specific function -- `analyse_functions.plot_agencies('MIGRATION', status='Department of State')`

Note that this uses [Plot.ly](http://plot.ly) to generate the charts. You'll have to sign up for a free account and install the necessary Python modules.

Here's the result:

[![](https://dl.dropbox.com/s/tatks4mk7qgcvzc/agencies-migration-department_of_state-2016-01-31.png)](https://plot.ly/~wragge/384/commonwealth-agencies-department-of-state-associated-with-the-function-migration/)




