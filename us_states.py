

# https://gist.githubusercontent.com/tlancon/9794920a0c3a9990279de704f936050c/raw/dd7f7db501af25287a0daeaf3d90185a695d85ea/us_states_dict.py
# Inspired by https://gist.github.com/JeffPaine/3083347
# Access full state names using us_states.keys()
# Access all state abbreviations using us_states.values()

us_states = {
	'Alabama': 'AL',
	'Alaska': 'AK',
	'Arizona': 'AZ',
	'Arkansas': 'AR',
	'California': 'CA',
	'Colorado': 'CO',
	'Connecticut': 'CT',
	'Delaware': 'DE',
	'District of Columbia': 'DC',
	'Florida': 'FL',
	'Georgia': 'GA',
	'Hawaii': 'HI',
	'Idaho': 'ID',
	'Illinois': 'IL',
	'Indiana': 'IN',
	'Iowa': 'IA',
	'Kansas': 'KS',
	'Kentucky': 'KY',
	'Louisiana': 'LA',
	'Maine': 'ME',
	'Maryland': 'MD',
	'Massachusetts': 'MA',
	'Michigan': 'MI',
	'Minnesota': 'MN',
	'Mississippi': 'MS',
	'Missouri': 'MO',
	'Montana': 'MT',
	'Nebraska': 'NE',
	'Nevada': 'NV',
	'New Hampshire': 'NH',
	'New Jersey': 'NJ',
	'New Mexico': 'NM',
	'New York': 'NY',
	'North Carolina': 'NC',
	'North Dakota': 'ND',
	'Ohio': 'OH',
	'Oklahoma': 'OK',
	'Oregon': 'OR',
	'Pennsylvania': 'PA',
	'Rhode Island': 'RI',
	'South Carolina': 'SC',
	'South Dakota': 'SD',
	'Tennessee': 'TN',
	'Texas': 'TX',
	'Utah': 'UT',
	'Vermont': 'VT',
	'Virginia': 'VA',
	'Washington': 'WA',
	'West Virginia': 'WV',
	'Wisconsin': 'WI',
	'Wyoming': 'WY'
}


states = {}
for state in us_states:
    states[state] = {'name': state, 'abbreviation': us_states[state]}
    states[us_states[state]] = {'name': state, 'abbreviation': us_states[state]}


# print(states)

"""
class States():

    def __init__(self):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.data)
"""

