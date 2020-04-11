
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
# print(df)

df['state'] == 'Massachusetts'

rows = df['state'] == 'Massachusetts'
print(df[rows])

deaths = df[rows]['deaths']
cases = df[rows]['cases']
date = df[rows]['date']

