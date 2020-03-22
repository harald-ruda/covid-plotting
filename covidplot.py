

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.backends.backend_pdf import PdfPages



data_location = 'https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series'
confirmed = 'time_series_19-covid-Confirmed.csv'
recovered = 'time_series_19-covid-Recovered.csv'
deaths = 'time_series_19-covid-Deaths.csv'


plt.clf()

data = pd.read_csv('time_series_19-covid-Confirmed.csv')

pdat = data.loc[101][4:]
lll = pdat.tolist()

lll = np.array(lll)
sss = [ lll[1:], lll[1:] - lll[:-1] ]

plt.plot(np.transpose(sss))

plt.savefig('file.pdf')

