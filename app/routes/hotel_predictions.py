from flask import request
from app import app

import pickle
import model_creation
import data_reader

from datetime import datetime

def get_date(argument):
    return datetime.strptime(argument, "%Y-%m-%d").date()

class HotelPredictions:
    def __init__(self):
        self.quantity_argument = request.args.get('quantity')
        self.arrival_argument = request.args.get('arrival')
        self.departure_argument = request.args.get('departure')
        self.state_argument = request.args.get('state')
        self.chain_argument = request.args.get('parent_chain')

    def validate_arguments_exist(self):
        if not (self.quantity_argument and self.arrival_argument and self.departure_argument and self.state_argument):
            raise Exception("Missing arguments")

    def validate_request_arguments(self):
        self.room_request = data_reader.RoomRequest(rooms=self.quantity_argument, arrival=self.arrival_argument, departure=self.departure_argument,\
                                                compact_hotel_info={'state_province':self.state_argument, 'parent_chain_name':self.chain_argument})

    @property
    def response(self):
        with open("models/latest_model.pickle", 'rb') as infile:
            model = pickle.load(infile)
        tested_parameters = model_creation.get_tested_parameters("tested_parameters.json")
        column = model_creation.get_next_column(tested_parameters)
        parameters = model_creation.significant_parameters(self.room_request, tested_parameters, column)
        
        return {"likelihood": model.predict_proba(parameters)}

    def __call__(self):
        self.validate_arguments_exist(self)
        self.validate_request_arguments(self)
        
        return self.response


@app.route("/hotel_predictions", methods=["GET"])
def hotel_predictions():
    return HotelPredictions()
