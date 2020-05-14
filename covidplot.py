

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# IMPORTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


import sys
import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# https://stackoverflow.com/questions/41245330/check-if-a-country-entered-is-one-of-the-countries-of-the-world

from iso3166 import countries
from us_states import states


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CONSTANTS -- avoid mis-typed dict keys
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


LOCATION = 'location'

PDF = 'pdf'
XKCD = 'xkcd'
INFO = 'info'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# DATA SOURCES
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# NYT DATA -- good data for US states
DataLocation1 = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/'
StateFile = 'us-states.csv'

# Johns Hopkins DATA -- good data for most countries
DataLocation2 = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'
ConfirmedFile = 'time_series_covid19_confirmed_global.csv'
DeathsFile = 'time_series_covid19_deaths_global.csv'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# EXCEPTIONS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


LocationExceptions = { 'Russia': 'Russian Federation', 
                       'Korea': 'Korea, Republic of',
                       'SKorea': 'Korea, Republic of',
                       'SouthKorea': 'Korea, Republic of',
                       'South-Korea': 'Korea, Republic of',
                       'South Korea': 'Korea, Republic of',
                       'Iran': 'Iran, Islamic Republic of',
                     }

NoDataExceptions = [ "Korea, Democratic People's Republic of", 
                   ]

CountryExceptions = { 'United States of America': 'US', 
                      'Russian Federation': 'Russia',
                      'Korea, Republic of': 'Korea, South',
                      'Taiwan, Province of China': 'Taiwan*', 
                      'Iran, Islamic Republic of': 'Iran',
                    }


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# DATA
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def get_data(parameters):
    """
    """
    global states, countries

    location = parameters[LOCATION]

    if location in LocationExceptions.keys():
        location = LocationExceptions[location]

    if location in states:   # US State

        location = states[location]['name']

        df = pd.read_csv(DataLocation1 + StateFile)
        rows = df['state'] == location

        deaths = df[rows]['deaths'].tolist()
        cases = df[rows]['cases'].tolist()
        dates = df[rows]['date'].tolist()
        lastday = dates[-1]

        xvalues = dates
        cumul_confirmed = cases
        cumul_deaths = deaths

        daily_confirmed = (np.array(cases)[1:] - np.array(cases)[:-1])
        daily_confirmed = [0] + list(daily_confirmed)

        daily_deaths = (np.array(deaths)[1:] - np.array(deaths)[:-1])
        daily_deaths = [0] + list(daily_deaths)

        xvalues = [x for x in range(len(daily_confirmed))]

    elif location in countries:   # Country

        location = countries.get(location).name

        if location in NoDataExceptions:
            print("No data available for:", location)
            return None, None, None

        if location in CountryExceptions.keys():
            location = CountryExceptions[location]

        confirmed_data = pd.read_csv(DataLocation2 + ConfirmedFile)
        deaths_data = pd.read_csv(DataLocation2 + DeathsFile)

        rows = confirmed_data['Country/Region'] == location
        row = list(rows[rows == True].index)
        if len(row) == 0:
            print("Please add", location, "to <CountryExceptions>. for looking up the data coreectly.")
            print("Please choose from: ", confirmed_data['Country/Region'].tolist())

        if len(row) > 1:
            states = [str(state) for state in confirmed_data['Province/State'][row].tolist() if not isinstance(state, float)]
            print(location, "includes:", ', '.join(states))

        confirmed = np.array(confirmed_data.iloc[row, 4:].sum().tolist())
        cumul_confirmed = np.transpose(confirmed[1:])
        daily_confirmed = np.transpose(confirmed[1:] - confirmed[:-1])

        deaths = np.array(deaths_data.iloc[row, 4:].sum().tolist())
        cumul_deaths = np.transpose(deaths[1:])
        daily_deaths = np.transpose(deaths[1:] - deaths[:-1])

        xvalues = [x for x in range(len(daily_confirmed))]
        lastday = deaths_data.loc[row[0]][4:].index.tolist()[-1]

    else:

        print("Unknown location:", location, ". Please add to <LocationExceptions>.")
        print("Abort")

        # print("states:")
        # for s in states:
        #     print("  ", s)

        # print("choose one of these countries:")
        # for c in countries:
        #     print("  ", c)

        return None, None, None

    parameters[LOCATION] = location

    print("for", location, "as of", lastday)
    print("latest daily DEATHS:", daily_deaths[-1], "total DEATHS:", cumul_deaths[-1])
    print("latest daily CASES:", daily_confirmed[-1], "total CASES:", cumul_confirmed[-1])

    return daily_confirmed, daily_deaths, xvalues


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PLOT
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def plot_data(cases, deaths, xvalues, parameters):
    """
    """
    font = {'family': 'serif', 'color': 'darkred', 'weight': 'normal', 'size': 16 }
    font = {'family': 'serif', 'color': 'darkred', 'weight': 'normal' }

    if parameters[XKCD]:
        plt.xkcd()

    fig, ax = plt.subplots()

    ax.bar(xvalues, cases, label='Daily Cases', width=0.5, color='c')
    ax.bar(xvalues, deaths, label='Daily Deaths', width=0.5, color='r')

    # ax.plot(daily_deaths, label='Daily Deaths', color='r')

    ax.grid()
    ax.legend(title='Where:')
    plt.ylabel('Number of Cases', fontdict=font)
    plt.xlabel('Days Since Jan 21st', fontdict=font)
    plt.title(parameters[LOCATION] + ' COVID-19 Cases', fontdict=font)
    plt.subplots_adjust(left=0.15)

    if parameters[PDF]:
        fig.savefig(parameters[LOCATION] + '-covid.pdf')

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

    parameters[LOCATION] = 'Massachusetts' if len(argv) == 0 else ' '.join(argv)

    return parameters


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# MAIN
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == "__main__":

    parameters = process_arguments(sys.argv[1:])
    print(parameters)
    cases, deaths, xvalues = get_data(parameters)
    if not(cases is None):
        plot_data(cases, deaths, xvalues, parameters)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
