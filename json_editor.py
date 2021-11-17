import json

us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}

def update_keys(keys):
    #remove states with low number of samples
    for key in ['Alaska', 'Delaware', 'Idaho', 'Montana', 'North Dakota', 'Rhode Island', 'South Dakota', 'West Virginia', 'Wyoming', 'District of Columbia']:
        keys.remove(key)
        keys.remove(us_state_to_abbrev[key])

def remove_states():
    with open("states_enum.json", 'r') as infile:
        old = json.load(infile)

    keys = list(old.keys())
    update_keys(keys)
    #enumerate only the abbreviations first
    states_enum = {key: index for index, key in enumerate(keys) if key not in us_state_to_abbrev.keys()}
    states_enum.update({state: states_enum.get(us_state_to_abbrev[state]) for state in us_state_to_abbrev.keys() if states_enum.get(us_state_to_abbrev[state]) != None})

    with open("states_enum.json", 'w') as outfile:
        json.dump(states_enum, outfile)

def invert_order():
    with open("providers_enum.json", 'r') as infile:
        old = json.load(infile)

    new = {index: key for key, index in old.items()}

    with open("providers_enum.json", 'w') as outfile:
        json.dump(new, outfile)

def enumerate_chains():
    chains = ['Starwood Preferred Guest', 'Marriott', 'Wyndham Hotels', 'Best Western', 'Choice Hotels', 'Hilton', 'Motel 6', 'IHG', 'Hyatt']
    chains_enum = {key: index for index, key in enumerate(chains)}
    with open("suggested_chains_enum.json", 'w') as outfile:
        json.dump(chains_enum, outfile)
