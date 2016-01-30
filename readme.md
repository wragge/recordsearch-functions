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

All there is so far is a function to save a summary of the agencies associated with a particular function to a CSV file:

* Start up Python, or preferably iPython -- `ipython`
* Import the analyse module -- `import analyse_functions`
* Create a CSV file for a single function, eg. MIGRATION -- `analyse_functions.write_csv('MIGRATION')`
* Create CSV files for all harvested functions -- `analyse_functions.write_csv()`

Look in the [data](https://github.com/wragge/recordsearch-functions/tree/master/data) directory for some example CSV files.





