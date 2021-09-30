from sklearn.linear_model import LogisticRegression
import pickle
import data_reader

requestData = data_reader.load_request_data()

parameterMatrix = [request.model_parameters_list for request in requestData]
successVector = [len(request.rooms_found) > 0 and 1 or -1 for request in requestData]

model = LogisticRegression().fit(parameterMatrix, successVector)

print("Mean Accuracy:", model.score(parameterMatrix, successVector))

with open("models/latest_model.pickle", 'wb') as file:
    pickle.dump(model, file)
    print("Model pickled in \"models/latest_model.pickle\".")
