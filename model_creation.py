from sklearn.linear_model import LogisticRegression
import data_reader

requestData = data_reader.load_request_data()

parameterMatrix = [request.model_parameters_list for request in requestData]
successVector = [len(request.rooms_found) > 0 and 1 or -1 for request in requestData]

model = LogisticRegression().fit(parameterMatrix, successVector)

print("Actual:\t", successVector, sep='\t')
print("Predicted:", list(model.predict(parameterMatrix)), sep = '\t')
print("Mean Accuracy:", model.score(parameterMatrix, successVector))
