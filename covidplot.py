

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

COUNTRY_REGION = 'Country/Region'
PROVINCE_STATE = 'Province/State'


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

LocationExceptions = { 'Russia': 'Russian Federation', 
                       'Korea': 'Korea, South',
                       'SKorea': 'Korea, South',
                       'SouthKorea': 'Korea, South',
                       'South-Korea': 'Korea, South',
                       'South Korea': 'Korea, South',
                       'Iran': 'Iran, Islamic Republic of',
                     }


# official country name -> name in data-file

CountryExceptions = { 'United States of America': 'US', 
                      'Russian Federation': 'Russia',
                      'Korea, Republic of': 'Korea, South',
                      'Taiwan, Province of China': 'Taiwan*', 
                      'Iran, Islamic Republic of': 'Iran',
                    }


PlotExceptions = { 'Korea, South': 'South Korea',
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

    location = parameters[LOCATION]

    if location in States:   # US States

        state = States[location]
        location = state[NAME]
        alternatives = [state[ABBREVIATION]]

        df = pd.read_csv(StateDataLocation + StateFile)
        rows = df[STATE] == location

        cumul_deaths = df[rows][DEATHS].tolist()
        cumul_cases = df[rows][CASES].tolist()
        dates = df[rows][DATE].tolist()
        lastday = dates[-1]

        daily_cases = [0] + list(np.array(cumul_cases)[1:] - np.array(cumul_cases)[:-1])
        daily_deaths = [0] + list(np.array(cumul_deaths)[1:] - np.array(cumul_deaths)[:-1])
        xvalues = [x for x in range(len(daily_deaths))]

    else:   # Country or Province or Region outside of US

        global_cases = pd.read_csv(GlobalDataLocation + ConfirmedFile)
        global_deaths = pd.read_csv(GlobalDataLocation + DeathsFile)

        country_list = global_deaths[COUNTRY_REGION].tolist()
        province_list = global_deaths[PROVINCE_STATE].tolist()

        alternatives = []

        if location in country_list:

            column = COUNTRY_REGION

        elif location in province_list:

            column = PROVINCE_STATE

        elif location in Countries:

            print("Country:", location)
            country = Countries.get(location)
            location = country.name
            alternatives = [ country.alpha2, country.alpha3 ]   # there is also: numeric, apolitical

            if location in CountryExceptions.keys():
                location = CountryExceptions[location]

            if location not in country_list:
                print("No data available for:", location, "May need to add to CountryExceptions.")
                return None, None, None

            column = COUNTRY_REGION

        elif location in LocationExceptions.keys():

            print("LocationException:", location)
            location = LocationExceptions[location]
            column = COUNTRY_REGION

        else:

            print("Unknown location:", location, ". Please add to <LocationExceptions>.")
            print("Abort")
            return None, None, None

        # now finally get the data for the location!

        matching_rows = global_cases[column] == location
        row = list(matching_rows[matching_rows == True].index)
        if len(row) == 0:
            print("Please add", location, "to <CountryExceptions>. for looking up the data coreectly.")
            # print("Please choose from: ", confirmed_data['Country/Region'].tolist())
            return None, None, None

        if len(row) > 1 and column == COUNTRY_REGION:
            states = [str(state) for state in global_cases[PROVINCE_STATE][row].tolist() if not isinstance(state, float)]
            print(location, "includes:", ', '.join(states))

        cases = np.array(global_cases.iloc[row, 4:].sum().tolist())
        cumul_cases = np.transpose(cases[1:])
        daily_cases = np.transpose(cases[1:] - cases[:-1])

        deaths = np.array(global_deaths.iloc[row, 4:].sum().tolist())
        cumul_deaths = np.transpose(deaths[1:])
        daily_deaths = np.transpose(deaths[1:] - deaths[:-1])

        xvalues = [x for x in range(len(daily_cases))]
        days = global_deaths.loc[row[0]][4:].index.tolist()
        lastday = "" if len(days) == 0 else days[-1]
        # lastday = deaths_data.loc[row[0]][4:].index.tolist()[-1]

    # by now we have: location, alternatives, daily_cases, daily_deaths, xvalues, cumul_deaths, cumul_cases

    parameters[LOCATION] = location
    alternatives = '(' + ', '.join(alternatives) + ')' if len(alternatives) > 0 else ''

    if True:
        print("for", location, alternatives, "as of", lastday)
        print("latest daily DEATHS:", daily_deaths[-1], "total DEATHS:", cumul_deaths[-1])
        print("latest daily CASES:", daily_cases[-1], "total CASES:", cumul_cases[-1])

    return daily_cases, daily_deaths, xvalues


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PLOT
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def plot_data(cases, deaths, xvalues, parameters):
    """
    """
    location = parameters[LOCATION]

    if location in PlotExceptions.keys():
        location = PlotExceptions[location]

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
    plt.title(location + ' COVID-19 Cases', fontdict=font)
    plt.subplots_adjust(left=0.15)

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

    parameters[LOCATION] = 'Massachusetts' if len(argv) == 0 else ' '.join(argv)

    return parameters


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TESTING
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def testing():
    """
    """
    # print("Please choose from: ", confirmed_data['Country/Region'].tolist())
    names = ['Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Australia', 'Australia', 'Australia', 'Australia', 'Australia', 'Australia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Canada', 'Canada', 'Canada', 'Canada', 'Canada', 'Canada', 'Canada', 'Canada', 'Canada', 'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'China', 'Colombia', 'Congo (Brazzaville)', 'Congo (Kinshasa)', 'Costa Rica', "Cote d'Ivoire", 'Croatia', 'Diamond Princess', 'Cuba', 'Cyprus', 'Czechia', 'Denmark', 'Denmark', 'Denmark', 'Djibouti', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France', 'France', 'France', 'France', 'France', 'France', 'France', 'France', 'France', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Guatemala', 'Guinea', 'Guyana', 'Haiti', 'Holy See', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Korea, South', 'Kuwait', 'Kyrgyzstan', 'Latvia', 'Lebanon', 'Liberia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar', 'Malaysia', 'Maldives', 'Malta', 'Mauritania', 'Mauritius', 'Mexico', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Namibia', 'Nepal', 'Netherlands', 'Netherlands', 'Netherlands', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'San Marino', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Singapore', 'Slovakia', 'Slovenia', 'Somalia', 'South Africa', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Taiwan*', 'Tanzania', 'Thailand', 'Togo', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'Uruguay', 'US', 'Uzbekistan', 'Venezuela', 'Vietnam', 'Zambia', 'Zimbabwe', 'Canada', 'Dominica', 'Grenada', 'Mozambique', 'Syria', 'Timor-Leste', 'Belize', 'Canada', 'Laos', 'Libya', 'West Bank and Gaza', 'Guinea-Bissau', 'Mali', 'Saint Kitts and Nevis', 'Canada', 'Canada', 'Kosovo', 'Burma', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'MS Zaandam', 'Botswana', 'Burundi', 'Sierra Leone', 'Netherlands', 'Malawi', 'United Kingdom', 'France', 'South Sudan', 'Western Sahara', 'Sao Tome and Principe', 'Yemen', 'Comoros', 'Tajikistan']
    for n in names:
        get_data({LOCATION:n})

    return

    # Country(name='Zimbabwe', alpha2='ZW', alpha3='ZWE', numeric='716', apolitical_name='Zimbabwe')
    for c in Countries:
        names = [ c.name, c.alpha2, c.alpha3, c.numeric, c.apolitical_name ]
        if c.name != c.apolitical_name:
            print(c.name, c.apolitical_name)
        for n in names:
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
