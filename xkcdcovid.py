
# IMPORTS

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# from matplotlib.backends.backend_pdf import PdfPages   # only neede for multipage PDFs, plt.close() for each page

# CONSTANTS

DataLocation = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'

ConfirmedFile = 'time_series_19-covid-Confirmed.csv'
RecoveredFile = 'time_series_19-covid-Recovered.csv'
DeathsFile = 'time_series_19-covid-Deaths.csv'

# DATA

row = 101  
KnownLocations = {17: 'Sweden', 101: 'Massachusetts'}
RowLocation = KnownLocations[row]

confirmed_data = pd.read_csv(DataLocation + ConfirmedFile)
recovered_data = pd.read_csv(DataLocation + RecoveredFile)
deaths_data = pd.read_csv(DataLocation + DeathsFile)

confirmed = np.array(confirmed_data.loc[row][4:].tolist())
cumul_confirmed = np.transpose(confirmed[1:])
daily_confirmed = np.transpose(confirmed[1:] - confirmed[:-1])

recovered = np.array(recovered_data.loc[row][4:].tolist())
cumul_recovered = np.transpose(recovered[1:])

deaths = np.array(deaths_data.loc[row][4:].tolist())
cumul_deaths = np.transpose(deaths[1:])

# PLOT

with plt.xkcd():
    fig, ax = plt.subplots()

    xvalues = [x for x in range(len(daily_confirmed))]

    ax.plot(cumul_confirmed, label='Cumulative Cases', color='b')
    ax.bar(xvalues, daily_confirmed, label='Daily New Cases', width=0.4, color='c')
    ax.plot(cumul_recovered, label='Cumulative Recovered', color='g')
    ax.plot(cumul_deaths, label='Cumulative Deaths', color='r')

    ax.grid()
    ax.legend(title='Where:')
    ax.set(ylabel='Number of Cases', xlabel='Number of Days since Jan 21', title=RowLocation + ' COVID-19 Cases')

    fig.savefig('xkcd.pdf')
    plt.show()

