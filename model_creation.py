from sklearn.linear_model import LogisticRegression
import pickle
import data_reader
import significance_test

requestData = data_reader.load_request_data()

def filter_conditions(request):
    return request.hotel_info.country.lower() == "us" or request.hotel_info.country.lower() == "united states"

parameterMatrix = [request.model_parameters_list for request in requestData if filter_conditions(request)]
resultVector = [len(request.rooms_found) > 0 and 1 or 0 for request in requestData if filter_conditions(request)]

if significance_test.binary_test([s[0] for s in parameterMatrix], resultVector):
    model = LogisticRegression().fit(parameterMatrix, resultVector)
    
    with open("models/latest_model.pickle", 'wb') as file:
        pickle.dump(model, file)
        print("Model pickled in \"models/latest_model.pickle\".")
    
    with open("models/latest_model.manifest", 'w') as file:
        score = model.score(parameterMatrix, resultVector)
        print("Score on training data:", score)
        file.write("Score on training data: %f" % score)

#states to remove: ['Alaska', 'Delaware', 'Idaho', 'Montana', 'North Dakota', 'Rhode Island', 'South Dakota', 'West Virginia', 'Wyoming', 'District of Columbia']
#to count number of each state in data
#for i in range(0, 51):
#	count = 0
#	for sample in parameterMatrix:
#		if sample[3+i]:
#			count += 1
#	print(count)
