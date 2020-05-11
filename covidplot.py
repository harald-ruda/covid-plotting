
# IMPORTS

import sys, math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# https://stackoverflow.com/questions/41245330/check-if-a-country-entered-is-one-of-the-countries-of-the-world
from iso3166 import countries

from us_states import states

# not needed
# from matplotlib.backends.backend_pdf import PdfPages   # only neede for multipage PDFs, plt.close() for each page

# CONSTANTS

# NYTDATA
DataLocation1 = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/'
StateFile = 'us-states.csv'

# Johns Hopkins DATA
DataLocation2 = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'

ConfirmedFile = 'time_series_covid19_confirmed_global.csv'
DeathsFile = 'time_series_covid19_deaths_global.csv'

# ConfirmedFile = 'time_series_19-covid-Confirmed.csv'
# RecoveredFile = 'time_series_19-covid-Recovered.csv'
# DeathsFile = 'time_series_19-covid-Deaths.csv'


LocationExceptions = { 'Russia': 'Russian Federation' }

# COMMAND LINE

location = sys.argv[-1] if len(sys.argv) > 1 else 'Massachusetts'
lastday = ""

if location in LocationExceptions.keys():
    location = LocationExceptions[location]

# DATA

if location in states:   # US State

    location = states[location]['name']


    # df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
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

    # print(np.array(cases).shape, np.array(cumul_confirmed).shape, np.array(cumul_deaths).shape, np.array(daily_confirmed).shape)
    xvalues = [x for x in range(len(daily_confirmed))]

elif location in countries:   # Country

    # print(location, "=", countries.get(location))
    location = countries.get(location).name

    CountryExceptions = { 'United States of America': 'US', 'Russian Federation': 'Russia' }
    if location in CountryExceptions.keys():
        location = CountryExceptions[location]

    confirmed_data = pd.read_csv(DataLocation2 + ConfirmedFile)
    deaths_data = pd.read_csv(DataLocation2 + DeathsFile)

    rows = confirmed_data['Country/Region'] == location
    # print(rows[rows == True].head())
    # print(list(rows[rows == True].index))
    row = list(rows[rows == True].index)
    if len(row) == 0:
        print("Please add", location, "to <CountryExceptions>. for looking up the data coreectly.")
        print("Please choose from: ", confirmed_data['Country/Region'].tolist())

    # print(row)
    if len(row) > 1:
        states = [str(state) for state in confirmed_data['Province/State'][row].tolist() if not isinstance(state, float)]
        print(location, "includes:", ', '.join(states))
    # print("row =", row)
    # print(confirmed_data.loc[row][:2].tolist())

    # location1 = confirmed_data[location][:2].tolist()
    # print("location1:", location1)
    # print("last value:", confirmed_data.loc[row][-1].tolist())
    # print(confirmed_data.iloc[row0:rowN][4:].sum())
    # print(confirmed_data.iloc[92:95, 4:].sum())   # works
    # print(confirmed_data.iloc[row, 4:].sum())  # works

    confirmed = np.array(confirmed_data.iloc[row, 4:].sum().tolist())
    cumul_confirmed = np.transpose(confirmed[1:])
    daily_confirmed = np.transpose(confirmed[1:] - confirmed[:-1])

    # recovered = np.array(recovered_data.loc[row][4:].tolist())
    # cumul_recovered = np.transpose(recovered[1:])

    deaths = np.array(deaths_data.iloc[row, 4:].sum().tolist())
    cumul_deaths = np.transpose(deaths[1:])
    daily_deaths = np.transpose(deaths[1:] - deaths[:-1])

    xvalues = [x for x in range(len(daily_confirmed))]
    lastday = deaths_data.loc[row[0]][4:].index.tolist()[-1]

else:
    print("Unknown location:", location, ". Please add to <LocationExceptions>.")
    print("Abort")
    # print("states:", states)
    print("choose one of these countries:")
    for c in countries:
        print("  ", c)
    exit()

print("for", location, "as of", lastday)
print("latest daily DEATHS:", daily_deaths[-1], "total DEATHS:", cumul_deaths[-1])
print("latest daily CASES:", daily_confirmed[-1], "total CASES:", cumul_confirmed[-1])

# PLOT

font = {'family': 'serif', 'color': 'darkred', 'weight': 'normal', 'size': 16 }
font = {'family': 'serif', 'color': 'darkred', 'weight': 'normal' }

fig, ax = plt.subplots()

# ax.plot(cumul_confirmed, label='Cumulative Cases', color='b')
ax.bar(xvalues, daily_confirmed, label='Daily New Cases', width=0.4, color='c')
# ax.plot(cumul_deaths, label='Cumulative Deaths', color='r')
ax.bar(xvalues, daily_deaths, label='Daily Deaths', width = 0.8, color='r')
# ax.plot(daily_deaths, label='Daily Deaths', color='r')

ax.grid()
ax.legend(title='Where:')
plt.ylabel('Number of Cases', fontdict=font)
plt.xlabel('Days Since Jan 21st', fontdict=font)
plt.title(location + ' COVID-19 Cases', fontdict=font)

plt.subplots_adjust(left=0.15)

# fig.savefig(location + '-cases.pdf')
plt.show()

