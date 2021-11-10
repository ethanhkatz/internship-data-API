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
        return self.kw.get("parent_chain_name", '')

    @property
    def name(self):
        return self.kw.get("name", '')

    @property
    def id(self):
        return self.kw.get("display_id", '')

    @property
    def country(self):
        return self.kw.get("country", '')

    @property
    def state_province(self):
        return self.kw.get("state_province", '')

    @property
    def city(self):
        return self.kw.get("city", '')

    @property
    def latitude(self):
        return self.kw.get("latitude", 0)

    @property
    def longitude(self):
        return self.kw.get("longitude", 0)
    
    def display(self):
        print("chain: %s\nname: %s\nid: %s\ncity: %s\tstate_province: %s\tcountry: %s\nlatitude:\t%6.2f\nlongitude:\t%6.2f" % (self.chain, self.name, self.id, self.city, self.state_province, self.country, self.latitude, self.longitude))

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
        state_num = states_enum.get(self.hotel_info.state_province)
        return state_num != None and ([0] * state_num + [1] + [0] * (num_states - 1 - state_num)) or [0] * num_states

    @property
    def providers_sublist(self):
        #iterating over rooms for efficiency
        num_rooms_available = [0] * num_providers
        for room in self.rooms_found:
            provider_id = providers_enum.get(room.provider.lower())
            if provider_id != None:
                num_rooms_available[provider_id] += 1
        return num_rooms_available

    @property
    def model_parameters_list(self):
        return [
            len(self.rooms_requested),
            self.abs_days_summer,
            self.num_days ] + \
            self.states_sublist + \
            self.providers_sublist


num_misc_parameters = 3
num_states = 41
num_providers = 12

num_parameters = num_misc_parameters + num_states + num_providers

with open("states_enum.json", 'r') as f:
    states_enum = json.loads(f.read())

with open("providers_enum.json", 'r') as f:
    providers_enum = json.loads(f.read())

def load_request_data():
    requestData = []
    with open("hsp_queue.dump", 'r') as f:
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
    
    with open("providers_enum.json", 'w') as file:
        json.dump(providers_enum, file)
