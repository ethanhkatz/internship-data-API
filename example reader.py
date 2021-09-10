import json

jsonArray = []

with open("examples.json", 'r') as f:
    for line in f.readlines():
        jsonObject = json.loads(line)
        jsonArray.append(jsonObject)

class RequestedRoom:
    def __init__(self, room):
        self.num_adults = room.get("adults")
        self.child_ages = room.get("child_ages")

    def display(self):
        print("num_adults: %s\nchild_ages: %s" % (self.num_adults, tuple(self.child_ages)))

class FoundRoom:
    def __init__(self, raw_rate):
        self.room_id = raw_rate.get("id")
        self.provider = raw_rate.get("provider")
        self.category = raw_rate.get("category")
        self.room = raw_rate.get("room")

    def display(self):
        print("id: %s\nprovider: %s\ncategory: %s\nroom: %s" % (self.room_id, self.provider, self.category, self.room))

class Hotel:
    def __init__(self, compact_hotel_info):
        self.chain = compact_hotel_info.get("parent_chain_name")
        self.name = compact_hotel_info.get("name")
        self.id = compact_hotel_info.get("display_id")
        
        self.country = compact_hotel_info.get("country")
        self.state_province = compact_hotel_info.get("state_province")
        self.city = compact_hotel_info.get("city")

        self.latitude = compact_hotel_info.get("latitude")
        self.longitude = compact_hotel_info.get("longitude")

    def display(self):
        print("chain: %s\nname: %s\nid: %s\ncity: %s\tstate_province: %s\tcountry: %s\nlatitude:\t%6.2f\nlongitude:\t%6.2f" % (self.chain, self.name, self.id, self.city, self.state_province, self.country, self.latitude, self.longitude))

#class only intended for those with tag emit_auction_summary
class RoomRequest:
    def __init__(self, **jsonObj):
        raw_rooms = jsonObj.get("rooms")
        if (raw_rooms != None):
            self.rooms_requested = [RequestedRoom(room) for room in jsonObj.get("rooms")]
        else:
            self.rooms_requested = []
        
        self.potential_providers = jsonObj.get("potential_providers")

        compact_hotel_info = jsonObj.get("compact_hotel_info")
        if (compact_hotel_info != None):
            self.hotel_info = Hotel(compact_hotel_info)
        else:
            self.hotel_info = None

        raw_rates = jsonObj.get("raw_rates")
        if (raw_rates != None):
            self.rooms_found = [FoundRoom(rate) for rate in jsonObj.get("raw_rates")]
        else:
            self.rooms_found = []
        
    def model_parameters_list(self):
        ret = []
        ret.append(len(rooms_requested))
        ret.append(hotel_info.latitude)
        ret.append(hotel_info.longitude)
        

requestData = []
for request in jsonArray:
    if request["tag"] == "mystique.production.provider_event.emit_auction_summary":
        requestData.append(RoomRequest(**request))
