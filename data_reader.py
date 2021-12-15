import requests
import json
from datetime import datetime, date

class RequestedRoom:
    def __init__(self, room):
        self.kw = room

    @property
    def num_adults(self):
        return self.kw.get("adults")

    @property
    def child_ages(self):
        return self.kw.get("child_ages")

    def display(self):
        print("num_adults: %s\nchild_ages: %s" % (self.num_adults, tuple(self.child_ages)))

class FoundRoom:
    def __init__(self, raw_rate):
        self.kw = raw_rate

    @property
    def room_id(self):
        return self.kw.get("id")

    @property
    def provider(self):
        return self.kw.get("provider")

    @property
    def category(self):
        return self.kw.get("category")

    @property
    def room_type(self):
        return self.kw.get("room")

    def display(self):
        print("id: %s\nprovider: %s\ncategory: %s\nroom: %s" % (self.room_id, self.provider, self.category, self.room))

class Hotel:
    def __init__(self, compact_hotel_info):
        self.kw = compact_hotel_info
    
    @property
    def chain(self):
        return self.kw.get("parent_chain_name") or ''

    @property
    def name(self):
        return self.kw.get("name") or ''

    @property
    def id(self):
        return self.kw.get("display_id") or ''

    @property
    def country(self):
        return self.kw.get("country") or ''

    @property
    def state_province(self):
        return self.kw.get("state_province") or ''

    @property
    def city(self):
        return self.kw.get("city") or ''

    @property
    def latitude(self):
        return self.kw.get("latitude") or 0

    @property
    def longitude(self):
        return self.kw.get("longitude") or 0

    @property
    def zip(self):
        return self.kw.get("postal_code") or ''
    
    def display(self):
        print("chain: %s\nname: %s\nid: %s\ncity: %s\tstate_province: %s\tcountry: %s\nlatitude:\t%6.2f\nlongitude:\t%6.2f" % (self.chain, self.name, self.id, self.city, self.state_province, self.country, self.latitude, self.longitude))

def parameter_list_from_enum(key, enum, n):
    num = enum.get(key)
    return num != None and ([0] * num + [1] + [0] * (n - 1 - num)) or [0] * n

#class only intended for those with tag emit_auction_summary
class RoomRequest:
    def __init__(self, **jsonObj):
        self.kw = jsonObj
    #property
        self.rooms_found = [FoundRoom(rate) for rate in jsonObj.get("raw_rates", [])]

    @property
    def rooms_requested(self):
        return [RequestedRoom(room) for room in self.kw.get("rooms", [])]

    @property
    def num_rooms_requested(self):
        #when processing a request I pass the number of rooms as a str in "rooms" argument, when training it's a list
        return isinstance(self.kw.get("rooms"), str) and int(rooms) or len(self.rooms_requested)

    @property
    def potential_providers(self):
        return self.kw.get("potential_providers")

    @property
    def hotel_info(self):
        return Hotel(self.kw.get("compact_hotel_info", {}))

    def get_date(self, key):
        return datetime.strptime(self.kw.get(key, ''), "%Y-%m-%d").date()
    
    @property
    def abs_days_summer(self):
        arrival = self.get_date("arrival")
        return abs(arrival.toordinal() - date(arrival.year, 7, 21).toordinal()) #days from summer solstice

    @property
    def num_days(self):
        return self.get_date("departure").toordinal() - self.get_date("arrival").toordinal()

    @property
    def states_sublist(self):
        return parameter_list_from_enum(self.hotel_info.state_province, states_enum, num_states)

    @property
    def chains_sublist(self):
        return parameter_list_from_enum(self.hotel_info.chain.lower(), chains_enum, num_chains)

    @property
    def zip_income(self):
        url = "https://api.census.gov"
        route = "/data/2019/acs/acs5/profile"
        params = {'get': "NAME"}
        "?get=NAME,DP03_0062E&for=zip%20code%20tabulation%20area:84096&in=state:49&key=d287601bbb2dca6a04d540ca9187edfd23de2136"
        

    @property
    def zip_population(self):
        "https://api.census.gov/data/2019/acs/acs5/profile?get=NAME,DP03_0001E&for=zip%20code%20tabulation%20area:84096&in=state:49&key=d287601bbb2dca6a04d540ca9187edfd23de2136"

    @property
    def model_parameters_list(self):
        return [
            self.num_rooms_requested,
            self.abs_days_summer,
            self.num_days ] + \
            self.states_sublist + \
            self.chains_sublist

with open("states_enum.json", 'r') as f:
    states_enum = json.loads(f.read())

with open("chains_enum.json", 'r') as f:
    chains_enum = json.loads(f.read())

num_misc_parameters = 3
num_states = 41
num_chains = 23

num_parameters = num_misc_parameters + num_states + num_chains

key = "d287601bbb2dca6a04d540ca9187edfd23de2136"

def load_request_data(filepath):
    requestData = []
    with open(filepath, 'r') as f:
        for line in f.readlines():
            jsonObject = json.loads(line)
            if jsonObject["tag"] == "mystique.production.provider_event.emit_auction_summary":
                requestData.append(RoomRequest(**jsonObject))
    
    return requestData

def enumerate_providers():
    requestData = load_request_data()
    providers_enum = {}
    i = 0
    for request in requestData:
        provider_names = [room.provider.lower() for room in request.rooms_found]
        for name in provider_names:
            if name not in providers_enum:
                providers_enum[name] = i
                i += 1
    
    with open("providers_enum.json", 'w') as outfile:
        json.dump(providers_enum, outfile)

def enumerate_chains():
    requestData = load_request_data()
    chains_enum = {}
    for request in requestData:
        chain_name = request.hotel_info.chain.lower()
        if chain_name != '' and chain_name != "unaffiliated" and chain_name not in chains_enum:
            chains_enum[chain_name] = 1
        elif chain_name in chains_enum:
            chains_enum[chain_name] += 1
    
    chains_list = list(chains_enum.items())
    chains_list.sort(key = (lambda chain: chain[1]), reverse=True)
    chains_enum = {chain[0]: (i, chain[1]) for i, chain in enumerate(chains_list)}
    
    with open("chains_enum_full.json", 'w') as outfile:
        json.dump(chains_enum, outfile)
    
    with open("chains_enum.json", 'w') as outfile:
        json.dump({key: value[0] for key, value in chains_enum.items() if value[1] > 10}, outfile)
