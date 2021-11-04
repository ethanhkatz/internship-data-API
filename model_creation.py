import warnings
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
import pickle
import json
import data_reader
import significance_test

warnings.filterwarnings("error")

def filter_conditions(request):
    return request.hotel_info.country.lower() == "us" or request.hotel_info.country.lower() == "united states"

def get_next_column(tested_parameters):
    next_column = 3
    while next_column in tested_parameters:
        next_column += 1
    assert next_column < data_reader.num_parameters
    return next_column

def significant_parameters(request, tested_parameters, column):
    significant = lambda i: i < 3 or i == column or i < column and tested_parameters[i] < 0.05
    return [parameter for i, parameter in enumerate(request.model_parameters_list) if significant(i)]

def update_model():
    try:
        with open("tested_parameters.json", 'r') as infile:
            tested_parameters = {int(key): value for key, value in json.load(infile).items()}
    except:
        tested_parameters = {}
    
    column = get_next_column(tested_parameters)
    print("Testing column "+str(column)+" ...")
    
    requestData = data_reader.load_request_data()
    parameterMatrix = [significant_parameters(request, tested_parameters, column) for request in requestData if filter_conditions(request)]
    resultVector = [len(request.rooms_found) > 0 and 1 or 0 for request in requestData if filter_conditions(request)]

    p_value = significance_test.binary_test([r[-1] for r in parameterMatrix], resultVector)
    print("p-value:", p_value)
    
    if p_value < 0.05:
        print("Training model ...")
        scaler = preprocessing.StandardScaler().fit(parameterMatrix)
        model = LogisticRegression().fit(scaler.transform(parameterMatrix), resultVector)
        
        with open("models/parameter_"+str(column)+".pickle", 'wb') as file:
            pickle.dump(model, file)
            print("Model pickled in \"models/parameter_"+str(column)+".pickle\".")
        
        with open("models/parameter_"+str(column)+".manifest", 'w') as file:
            score = model.score(parameterMatrix, resultVector)
            print("Score on training data:", score)
            file.write("Model using every parameter in columns "+str(column)+" and under. The p-value for column "+str(column)+" was "+str(p_value)+"."\
+"\nScore on training data: %f" % score)
    
    tested_parameters.update({column: p_value})
    with open("tested_parameters.json", 'w') as outfile:
        json.dump(tested_parameters, outfile)

    return column

while update_model() < data_reader.num_parameters-1:
    print()
