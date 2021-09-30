from sklearn.linear_model import LogisticRegression
import pickle
import data_reader

requestData = data_reader.load_request_data()

def filter_conditions(request):
    return request.hotel_info.country == "US"

parameterMatrix = [request.model_parameters_list for request in requestData if filter_conditions(request)]
successVector = [len(request.rooms_found) > 0 and 1 or 0 for request in requestData if filter_conditions(request)]

model = LogisticRegression().fit(parameterMatrix, successVector)

print("Mean Accuracy:", model.score(parameterMatrix, successVector))

with open("models/latest_model.pickle", 'wb') as file:
    pickle.dump(model, file)
    print("Model pickled in \"models/latest_model.pickle\".")
