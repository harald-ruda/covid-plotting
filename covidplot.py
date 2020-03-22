
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

fig, ax = plt.subplots()

ax.plot(cumul_confirmed, label='Cumulative Cases')
ax.plot(daily_confirmed, label='Daily New Cases')
ax.plot(cumul_recovered, label='Cumulative Recovered')
ax.plot(cumul_deaths, label='Cumulative Deaths')

ax.grid()
ax.legend(title='Where:')
ax.set(ylabel='Number of Cases', xlabel='Day Number', title=RowLocation + ' COVID-19 Cases')

fig.savefig('file.pdf')
plt.show()

