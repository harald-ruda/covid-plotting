

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# IMPORTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


import sys
import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# https://stackoverflow.com/questions/41245330/check-if-a-country-entered-is-one-of-the-countries-of-the-world

from iso3166 import countries as Countries
from us_states import states as States
from datetime import datetime


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CONSTANTS -- avoid mis-typed dict keys
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


LOCATION = 'location'

PDF = 'pdf'
XKCD = 'xkcd'
INFO = 'info'

NAME = 'name'
ABBREVIATION = 'abbreviation'

STATE = 'state'
DEATHS = 'deaths'
CASES = 'cases'
DATE = 'date'
FAMILY = 'family'
SERIF = 'serif'

LASTDAY = 'last-day'
STARTDATE = 'start-date'

COUNTRY_REGION = 'Country/Region'
PROVINCE_STATE = 'Province/State'

YLIMIT = 'y-limit'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# DATA SOURCES - always get the latest available data
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# NYT DATA -- good data for US states

StateDataLocation = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/'
StateFile = 'us-states.csv'


# Johns Hopkins DATA -- good data for most countries

GlobalDataLocation = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'
ConfirmedFile = 'time_series_covid19_confirmed_global.csv'
DeathsFile = 'time_series_covid19_deaths_global.csv'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# EXCEPTIONS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# common name -> name in data-file

LocationExceptions = { 'UK': 'United Kingdom',
                       'Korea': 'Korea, South',
                       'SKorea': 'Korea, South',
                       'SouthKorea': 'Korea, South',
                       'South-Korea': 'Korea, South',
                       'South Korea': 'Korea, South',
                       'Zaandam': 'MS Zandaam', 
                     }


# official country name -> name in data-file

CountryExceptions = { 'United States of America': 'US', 
                      'Russian Federation': 'Russia',
                      'Taiwan, Province of China': 'Taiwan*', 
                      'Iran, Islamic Republic of': 'Iran',
                      'Bolivia, Plurinational State of': 'Bolivia', 
                      'Brunei Darussalam': 'Brunei', 
                      'Myanmar': 'Burma', 
                      'Congo': 'Congo (Brazzaville)', 
                      'Congo, Democratic Republic of the': 'Congo (Kinshasa)', 
                      "Côte d'Ivoire": "Cote d'Ivoire", 
                      'Iran, Islamic Republic of': 'Iran', 
                      'Korea, Republic of': 'Korea, South', 
                      "Lao People's Democratic Republic": 'Laos', 
                      'Moldova, Republic of': 'Moldova', 
                      'Russian Federation': 'Russia', 
                      'Syrian Arab Republic': 'Syria', 
                      'Taiwan, Province of China': 'Taiwan*', 
                      'Tanzania, United Republic of': 'Tanzania', 
                      'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom', 
                      'Venezuela, Bolivarian Republic of': 'Venezuela', 
                      'Viet Nam': 'Vietnam', 
                      'Palestine, State of': 'West Bank and Gaza', 
                    }

# these names in data-file are not in the country names

"""
Bolivia -> Bolivia, Plurinational State of
Brunei -> Brunei Darussalam
Burma -> Myanmar
Congo (Brazzaville) -> Congo -> Congo, Republic of the -> Congo Republic -> RotC -> Congo-Brazzaville
Congo (Kinshasa) -> Congo, Democratic Republic of the -> DR Congo -> DRC -> DROC -> Congo-Kinshasa
Cote d'Ivoire -> Côte d'Ivoire
Iran -> Iran, Islamic Republic of
Korea, South -> Korea, Republic of
Laos -> Lao People's Democratic Republic
MS Zaandam -> Zaandam
Moldova -> Moldova, Republic of
Russia -> Russian Federation
Syria -> Syrian Arab Republic
Taiwan* -> Taiwan, Province of China -> Taiwan
Tanzania -> Tanzania, United Republic of
United Kingdom -> United Kingdom of Great Britain and Northern Ireland
Venezuela -> Venezuela, Bolivarian Republic of
Vietnam -> Viet Nam
West Bank and Gaza -> Palestine, State of
"""


PlotExceptions = { 'Korea, South': 'South Korea',
                   'Taiwan*': 'Taiwan',
                   'US-NY': "US except for NY",
                 }


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# DATA
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def get_data(parameters):
    """
    Look up data for location.
    Location can be US states: MA, Ohio, NY, New Jersey, etc. abreviation or full name
    Location can also be country or province, or some common abbreviation
    US states get precedence for abreviations, i.e. CA is California, not Canada
    """
    global States, Countries

    alternatives = []
    location = parameters[LOCATION]
    startdate = parameters.get(STARTDATE, '2020-03-15')

    if location == 'US-NY':

        parameters.update({LOCATION: 'US'})
        us_cases, us_deaths, us_xvalues = get_data(parameters)
        parameters.update({LOCATION: 'NY'})
        ny_cases, ny_deaths, ny_xvalues = get_data(parameters)
        parameters.update({LOCATION: location})

        return us_cases - ny_cases, us_deaths - ny_deaths, us_xvalues

    if location in States:   # US States

        state = States[location]
        location = state[NAME]
        alternatives = [state[ABBREVIATION]]

        df = pd.read_csv(StateDataLocation + StateFile)
        rows = df[STATE] == location

        cumul_deaths = df[rows][DEATHS].tolist()
        cumul_cases = df[rows][CASES].tolist()
        dates = df[rows][DATE].tolist()
        parameters[LASTDAY] = dates[-1]

        since_startdate =  np.where(np.array(dates) >= startdate)
        cumul_deaths = np.array(cumul_deaths)[since_startdate]
        cumul_cases = np.array(cumul_cases)[since_startdate]
        dates = np.array(dates)[since_startdate]

        daily_cases = [0] + list(np.array(cumul_cases)[1:] - np.array(cumul_cases)[:-1])
        daily_deaths = [0] + list(np.array(cumul_deaths)[1:] - np.array(cumul_deaths)[:-1])
        xvalues = [x for x in range(- len(daily_deaths) + 1, 1)]

    else:   # Country or Province or Region outside of US

        global_cases = pd.read_csv(GlobalDataLocation + ConfirmedFile)
        global_deaths = pd.read_csv(GlobalDataLocation + DeathsFile)
        country_list = global_deaths[COUNTRY_REGION].tolist()
        province_list = global_deaths[PROVINCE_STATE].tolist()

        if location in country_list:

            column = COUNTRY_REGION

        elif location in province_list:

            column = PROVINCE_STATE

        elif location in Countries:

            # print("Country:", location)
            country = Countries.get(location)
            alternatives = [ location, country.name, country.alpha2, country.alpha3 ]   # there is also: numeric, apolitical
            location = country.name

            if location in CountryExceptions.keys():
                location = CountryExceptions[location]

            if location in country_list:
                column = COUNTRY_REGION
            elif location in province_list:
                column = PROVINCE_STATE
            else:
                print("No data available for:", location, "May need to add to CountryExceptions.")
                return None, None, None

        elif location in LocationExceptions.keys():

            # print("LocationException:", location)
            location = LocationExceptions[location]
            column = COUNTRY_REGION

        else:

            print("Unknown location:", location, ". Please add to <LocationExceptions>.")
            print("Abort")
            return None, None, None

        if len(alternatives) == 0 and location in Countries:
            country = Countries.get(location)
            alternatives = [ location, country.name, country.alpha2, country.alpha3 ]   # there is also: numeric, apolitical

        # now finally get the data for the location!

        matching_rows = global_cases[column] == location
        row = list(matching_rows[matching_rows == True].index)
        if len(row) == 0:
            print("Please add", location, "to <CountryExceptions>. for looking up the data coreectly.")
            return None, None, None

        if len(row) > 1 and column == COUNTRY_REGION:
            states = [str(state) for state in global_cases[PROVINCE_STATE][row].tolist() if not isinstance(state, float)]
            print(location, "includes:", ', '.join(states))

        cases = np.array(global_cases.iloc[row, 4:].sum().tolist())
        cumul_cases = np.transpose(cases[1:])
        daily_cases = [0] + list(np.transpose(cases[1:] - cases[:-1]))

        deaths = np.array(global_deaths.iloc[row, 4:].sum().tolist())
        cumul_deaths = np.transpose(deaths[1:])
        daily_deaths = [0] + list(np.transpose(deaths[1:] - deaths[:-1]))

        dates = global_deaths.loc[row[0]][4:].index.tolist()[1:]
        dates = [datetime.strptime(x, '%m/%d/%y') for x in dates]
        parameters[LASTDAY] = "Yesterday" if len(dates) == 0 else dates[-1].strftime("%Y-%m-%d")

        since_startdate = np.where(np.array(dates) >= datetime.strptime(startdate, '%Y-%m-%d'))
        daily_deaths = np.array(daily_deaths)[since_startdate]
        daily_cases = np.array(daily_cases)[since_startdate]
        xvalues = [x for x in range(- len(daily_deaths) + 1, 1)]

    # by now we have: location, alternatives, daily_cases, daily_deaths, xvalues, cumul_deaths, cumul_cases

    alternatives = [item for item in alternatives if item != location]
    alternatives = '(' + ', '.join(alternatives) + ')' if len(alternatives) > 0 else ''
    if False and len(alternatives) == 0:
        print(parameters[LOCATION], '->', location, '->', PlotExceptions[location] if location in PlotExceptions.keys() else location, "|", alternatives, cumul_deaths[-1], "dead")
    parameters[LOCATION] = location

    if True:
        print("for", location, alternatives, "as of", parameters[LASTDAY])
        print("latest daily DEATHS:", daily_deaths[-1], "total DEATHS:", cumul_deaths[-1])
        print("latest daily CASES:", daily_cases[-1], "total CASES:", cumul_cases[-1])

    return daily_cases, daily_deaths, xvalues


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PLOT
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def rolling_mean(x, N):
    # from https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
    sum = np.cumsum(np.insert([float(value) for value in x], 0, [0.0] * N)) 
    return (sum[N:] - sum[:-N]) / float(N)


def plot_data(cases, deaths, xvalues, parameters):
    """
    """
    rolling_window = 7
    rolling_cases = rolling_mean(cases, rolling_window)
    rolling_deaths = rolling_mean(deaths, rolling_window)

    cases = [max(0, value) for value in cases]
    deaths = [max(0, value) for value in deaths]

    location = parameters[LOCATION]
    if location in PlotExceptions.keys():
        location = PlotExceptions[location]

    font = {'color': 'darkred', 'weight': 'normal', 'size': 16 }

    if parameters[XKCD]:
        plt.xkcd()
    else:
        font[FAMILY] = SERIF

    fig, ax = plt.subplots()

    ax.bar(xvalues, cases, label='Daily Cases', width=0.5, color='c')
    ax.bar(xvalues, deaths, label='Daily Deaths', width=0.5, color='r')
    ax.plot(xvalues, rolling_cases, label='Cases ' + str(rolling_window) + '-Day Average', color='c')
    ax.plot(xvalues, rolling_deaths, label='Deaths ' + str(rolling_window) + '-Day Average', color='r')

    ax.grid()
    ax.legend(title='Where:')
    plt.ylabel('Number of Cases', fontdict=font)
    plt.xlabel('Days Before ' + parameters[LASTDAY], fontdict=font)
    plt.title(location + ' COVID-19 Cases', fontdict=font)
    plt.subplots_adjust(left=0.15)

    if YLIMIT in parameters:
        topval = float(parameters[YLIMIT])
        plt.ylim(bottom=0, top=topval)
    else:
        plt.ylim(bottom=0)

    if parameters[PDF]:
        fig.savefig(location + '-covid.pdf')

    plt.show()   # display plot on screen


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ARGUMENTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def process_arguments(argv):
    """
    Process command line arguments, put into a {dict}
    Remaining arguments become the location.
    """
    parameters = {}

    parameters[PDF] = PDF in argv
    parameters[XKCD] = XKCD in argv
    parameters[INFO] = INFO in argv

    for item in [PDF, XKCD, INFO]:
        if item in argv:
            argv.remove(item)

    for item in [YLIMIT]:
        if item in argv[:-1]:
            num = argv.index(item)
            val = argv[num + 1]
            del argv[num+1]
            del argv[num]
            parameters[YLIMIT] = val

    parameters[LOCATION] = 'Massachusetts' if len(argv) == 0 else ' '.join(argv)

    return parameters


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TESTING
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def testing():
    """
    """
    global_cases = pd.read_csv(GlobalDataLocation + ConfirmedFile)
    global_deaths = pd.read_csv(GlobalDataLocation + DeathsFile)

    country_list = global_deaths[COUNTRY_REGION].tolist()
    province_list = global_deaths[PROVINCE_STATE].tolist()

    # print()
    # print("country-list:", sorted(list(set(country_list))))
    # print()
    # print("province-list:", sorted(list(set([p for p in province_list if not isinstance(p, float)]))))
    # print()

    # print("Please choose from: ", confirmed_data['Country/Region'].tolist())
    names = country_list
    names = sorted(list(set(names)))
    for n in names:
        get_data({LOCATION:n})
   
    return

    # Country(name='Zimbabwe', alpha2='ZW', alpha3='ZWE', numeric='716', apolitical_name='Zimbabwe')
    for c in Countries:
        # print()
        names = [ c.name, c.alpha2, c.alpha3, c.numeric, c.apolitical_name ]
        if c.name != c.apolitical_name:
            print(c.name, c.apolitical_name)
        for n in names[:1]:
            get_data({LOCATION:n})
        

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# MAIN
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == "__main__":

    # testing()
    # exit()

    parameters = process_arguments(sys.argv[1:])
    cases, deaths, xvalues = get_data(parameters)
    if not(cases is None):
        plot_data(cases, deaths, xvalues, parameters)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
