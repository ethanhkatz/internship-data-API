from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
import pickle
import json
import data_reader
import significance_test

def filter_conditions(request):
    return request.hotel_info.country.lower() == "us" or request.hotel_info.country.lower() == "united states"

def get_next_column(tested_parameters):
    next_column = 3
    while next_column in tested_parameters:
        next_column += 1
    return next_column

def significant_parameters(request, tested_parameters, column):
    significant = lambda i: i < 3 or i == column or i < column and tested_parameters[i] < 0.05
    return [parameter for i, parameter in enumerate(request.model_parameters_list) if significant(i)]

def get_matrix(tested_parameters, column):
    requestData = data_reader.load_request_data()
    parameterMatrix = [significant_parameters(request, tested_parameters, column) for request in requestData if filter_conditions(request)]
    resultVector = [len(request.rooms_found) > 0 and 1 or 0 for request in requestData if filter_conditions(request)]
    return (parameterMatrix, resultVector)

def train_model(parameterMatrix, resultVector):
    scaler = preprocessing.StandardScaler().fit(parameterMatrix)
    normalizedMatrix = scaler.transform(parameterMatrix)
    model = LogisticRegression().fit(normalizedMatrix, resultVector)
    score = model.score(normalizedMatrix, resultVector)
    print("Score on training data:", score)
    return (model, score)

def save_model(model, name, manifest_message):
    with open("models/" + name + ".pickle", 'wb') as file:
        pickle.dump(model, file)
        print("Model pickled in \"models/" + name + ".pickle\".")
    with open("models/" + name + ".manifest", 'w') as file:
        file.write(manifest_message)

def update_model():
    try:
        with open("tested_parameters.json", 'r') as infile:
            tested_parameters = {int(key): value for key, value in json.load(infile).items()}
    except:
        tested_parameters = {}
    
    column = get_next_column(tested_parameters)
    test_mode = column < data_reader.num_parameters
    if test_mode:
        print("Testing column "+str(column)+" ...")
    
    (parameterMatrix, resultVector) = get_matrix(tested_parameters, column)

    if test_mode:
        p_value = significance_test.binary_test([r[-1] for r in parameterMatrix], resultVector)
        print("p-value:", p_value)
    
    if not test_mode or p_value < 0.05:
        print("Training model ...")
        (model, score) = train_model(parameterMatrix, resultVector)
        
        if test_mode:
            save_model(model, "parameter_"+str(column), \
                "Model using every parameter in columns "+str(column)+" and under. The p-value for column "+str(column)+" was "+str(p_value)+"."\
                +"\nScore on training data: %f" % score)
        else:
            save_model(model, "latest_model", "Score on training data: %f" % score)

    if test_mode:
        tested_parameters.update({column: p_value})
        with open("tested_parameters.json", 'w') as outfile:
            json.dump(tested_parameters, outfile)

    return column

#while update_model() < data_reader.num_parameters-1:
#    print()
