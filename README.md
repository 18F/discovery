# Discovery: OASIS Market Research
[![CircleCI](https://circleci.com/gh/PSHCDevOps/discovery/tree/master.svg?style=svg)](https://circleci.com/gh/PSHCDevOps/discovery/tree/master)

Welcome to the wonderful world of procurement, a mechanism by which the government buys goods and services from the private sector. The procurement process is made up of several stages, one of the earliest being market research. Market Research is an attempt to predict what qualified bidders your solicitation for goods or services will attract. It helps acquisition personnel make decisions regarding various aspects of their particular procurement. Ideally, a solicitation should be structured so that it attracts a enough experienced bidders to be truly competitive.

After researching the marketplace, procurement officers may decide to break their solicitation up into smaller chunks, or choose one vehicle or schedule over another. Procurement vehicles and schedules are large umbrella contracts, with a set of vendors that have "pre-competed" for work in a general category. Discovery was developed to serve the [OASIS family of  vehicles](http://www.gsa.gov/portal/content/161367), which has many vendors capable of providing integrated professional services. OASIS is actually two vehicles, OASIS SB, which includes small businesses only, and OASIS unrestricted, which includes a wider array of vendors.

Discovery is live at (https://discovery.gsa.gov). You can file issues on this repo, or you can check out our [Trello board](https://trello.com/b/AEoWtET7/discovery-20), which contains our product backlog to see what we have planned in the future.

Currently, Discovery makes use of vendor information from the System for Award Management (SAM) and historical contract information the Federal Procurement Data System (FPDS). There are a few management commands that load the initial data, but we also provide a SQL dump since the loading of data from FPDS for the past decade can take several hours.

This project uses [Django](https://www.djangoproject.com/), a Python framework. You can get started by:

 * Installing PostgreSQL (installation guides [here](https://wiki.postgresql.org/wiki/Detailed_installation_guides))
 * Installing virtualenv and creating a virtual environment ([hitchhiker's guide to virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/))
 * Installing the python requirements with ```pip install -r requirements.txt```

 * Creating a postgresql database and storing the settings in a ```local_settings.py``` file, a sibling of ```settings.py```
 * Run ```manage.py migrate``` to set up the database and ```manage.py createcachetable``` to set up caching

 * Loading a [SQL dump](https://s3.amazonaws.com/mirage-gsa-gov/discovery.sql.gz) to get some data into the project
 * Run `manage.py runserver` to start the server. Optionally specify a host and port to serve on. For example `0.0.0.0:8888`

## Requirements

This project supports Python 2.7+. However for one package, there are different versions for Python 2 vs Python 3 package support, so there is a base `requirements.txt` file for all of the common dependencies, and `requirements_py2.txt` for python 2.7 and `requirements_py3.txt` for python 3. There is also a `requirements-test.txt` file for the testing packages (see below under Testing).

## Getting the Data

The project comes with everything you need to get started, including fixtures for some static information, and management commands to load the rest of the data. The OASIS vehicles are broken out into categories or pools, which are enumerated in a fixture. The pools are defined by groups of [NAICS codes](http://www.naics.com/sic-codes-industry-drilldown/). Vendors in the OASIS SB vehicle may also have certain setasides, such as women owned, service disabled veteran owned, etc. These setaside codes are also included in their own fixture. All of these fixtures can be found in `vendors/fixtures/`.

You have to options for getting the data. You can load the [SQL dump provided above](https://s3.amazonaws.com/mirage-gsa-gov/discovery.sql.gz) and get everything at once, or you can load the data manually.
To load the data manually, load each of the fixtures inside the `/vendor/fixtures/` directory. You can load these using the `loaddata` manage command like so:

`manage.py loaddata vendor/fixtures/naics.json`

Make sure to load naics.json, pools.json, and setasides.json (in that order).

Now you can run the ```load_vendors``` manage command. This loads in the vendors on OASIS (included in the repo on several CSVs that are grouped by pool), and fetches extra information about the vendors from SAM.

```
manage.py load_vendors
```

Note that this manage command requires you to specify a ```SAM_API_KEY``` variable in your local settings file as shown in local_settings.example.py. This value should be a valid [Data.gov API key](https://api.data.gov/signup/). Left to its own devices, the loader runs slightly faster than the rate limiting on api.data.gov, so there is a sleep statement in the loader to keep it in check.

Once the server is started you can query the api at
`http://localhost:8000/api/vendors/`

Providing no query parameters will return all vendors. However you can also filter by NAICS shortcode or by setaside code.

For example:
`http://localhost:8000/api/vendors/?setasides=A5,QF&naics=541330`
will return vendors that have the setaside codes A5 and QF and also do business under the NAICS code 541330.

Once you've loaded the basic data, you'll need to load the contract history records for the Vendor detail pages. This is accomplished using the following manage command:
`manage.py load_fpds`

Currently the `load_fpds` command is configured to load ten years of contract history for each vendor so it takes some time (potentiall several hours). However, upon each successful run, a load object with the date and time is stored. Upon subsequent runs, the loader will only load contracts that have been created or modified since the last load date. You can also pass in parameters to modify the loader.

```
./manage.py --load_all
```
The --load_all flag forces a load of all contracts, regardless of last load date

```
 ./manage.py --id=ID
 ```
The --id parameter only loads contractors for vendors with an id greater than or equal to ID, where ID is the vendor's id in the vendor table. Contracts are loaded in order of vendor id.

## Deploying to cloud.gov

If the app does not yet exist in the target space, first create it:

```
cf push -f manifest.yml --no-start
```

Next, create and bind a database to the application:

```
cf create-service aws-rds shared-psql discovery-db
cf bind-service acquisitions-staging discovery-db
```

Set some necessary environment variables:
```
cf set-env discovery-prod SAM_API_KEY [an api.data.gov key]
cf set-env discovery-prod SECRET_KEY [a secret key]
cf set-env discovery-prod API_HOST ""
```

Now, get the app up and running:
```
cf push -f manifest.yml
```

To load some data, SSH into the application using `cf ssh discovery-prod` and follow the instructions above. See the cloud.gov documentation for [additional information about working with databases](https://cloud.gov/docs/services/relational-database/).

## Static Assets
Assets can be loaded locally, or from an S3 bucket. The default settings in settings.py and local_settings.example.py are set to force local assets to be loaded. To use S3, update the AWS settings in the local_settings.py file, and uncomment the `DEFAULT_FILE_STORAGE` and `STATICFILES_STORAGE` lines.

## Testing
The tests can be run using Django's built in testing infrastructure:
```
./manage.py test
```

You can test specific apps by passing in the app name to the testing command. Valid values are `api`, `vendor`, `contract`, `selenium_tests` (requires additional setup).

### Deploying
See [deploy.sh](https://github.com/18F/discovery/blob/master/deploy.sh).

### Selenium testing
#### Locally with PhantomJS
 * Install python testing requirements with ```pip install -r requirements-test.txt```
 * Install [Phantom JS](http://phantomjs.org/download.html)
 * From the project directory, run ```manage.py test selenium_tests```

 #### Remotely using Sauce Labs
 * In `local_settings.py` change `SAUCE = False` to `SAUCE = True`
 * Set `SAUCE_USERNAME` and `SAUCE_ACCESS_CODE` and `DOMAIN_TO_TEST` variables
 * From the project directory, run ```manage.py test selenium_tests```

### Public domain

This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.md):

This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
