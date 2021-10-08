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

with open("states_enum.json", 'r') as f:
    states_enum = json.loads(f.read())

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
    def arrival_day(self):
        arrival = self.get_date("arrival")
        return arrival.toordinal() - date(arrival.year, 1, 1).toordinal() + 1 #day of the year [1, 366]

    @property
    def num_days(self):
        return self.get_date("departure").toordinal() - self.get_date("arrival").toordinal()

    @property
    def states_sublist(self):
        state_num = states_enum.get(self.hotel_info.state_province)
        return state_num != None and ([0] * state_num + [1] + [0] * (56 - state_num)) or [0] * 57

    @property
    def model_parameters_list(self):
        return [
            len(self.rooms_requested),
            self.arrival_day,
            self.num_days ] + \
            self.states_sublist

def load_request_data():
    requestData = []
    with open("hsp_queue.dump", 'r') as f:
        for line in f.readlines():
            jsonObject = json.loads(line)
            if jsonObject["tag"] == "mystique.production.provider_event.emit_auction_summary":
                requestData.append(RoomRequest(**jsonObject))
    
    return requestData
