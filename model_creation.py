from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
import pickle
import json
import data_reader
import significance_test

def get_tested_parameters(filepath):
    try:
        with open(filepath, 'r') as infile:
            return {int(key): value for key, value in json.load(infile).items()}
    except:
        return {}

def get_next_column(tested_parameters):
    next_column = 3
    while next_column in tested_parameters:
        next_column += 1
    return next_column

def significant_parameters(request, tested_parameters, column):
    significant = lambda i: i < 3 or i == column or i < column and tested_parameters[i] < 0.05 and tested_parameters[i] != -1
    return [parameter for i, parameter in enumerate(request.model_parameters_list) if significant(i)]

def get_matrix(tested_parameters, column, filepath, provider):
    requestData = data_reader.load_request_data(filepath)
    
    filter_conditions = lambda request: request.hotel_info.country.lower() == "us" or request.hotel_info.country.lower() == "united states"
    parameterMatrix = [significant_parameters(request, tested_parameters, column) for request in requestData if filter_conditions(request)]
    if provider:
        available = lambda request: provider in (room.provider.lower() for room in request.rooms_found)
    else:
        available = lambda request: len(request.rooms_found) > 0
    resultVector = [available(request) and 1 or 0 for request in requestData if filter_conditions(request)]
    
    return (parameterMatrix, resultVector)

def train_model(parameterMatrix, resultVector):
    scaler = preprocessing.StandardScaler().fit(parameterMatrix)
    normalizedMatrix = scaler.transform(parameterMatrix)
    model = LogisticRegression().fit(normalizedMatrix, resultVector)
    score = model.score(normalizedMatrix, resultVector)
    print("Score on training data:", score)
    return (model, score)

def save_model(model, provider, name, manifest_message):
    filepath = (provider and ("provider_models/" + provider + '/') or "models/") + name
    with open(filepath + ".pickle", 'wb') as file:
        pickle.dump(model, file)
        print("Model pickled in \"" + filepath + ".pickle\".")
    with open(filepath + ".manifest", 'w') as file:
        file.write(manifest_message)

def update_model(provider):
    tested_parameters_path = provider and ("provider_models/" + provider + "/tested_parameters.json") or "tested_parameters.json"
    tested_parameters = get_tested_parameters(tested_parameters_path)
    column = get_next_column(tested_parameters)
    test_mode = column < data_reader.num_parameters
    if test_mode:
        print("Testing column " + str(column) + " for provider \"" + provider + "\" ...")
    
    (parameterMatrix, resultVector) = get_matrix(tested_parameters, column, "hsp_queue.dump", provider)

    if test_mode:
        p_value = significance_test.binary_test([r[-1] for r in parameterMatrix], resultVector)
        print("p-value:", p_value)
    
    if not test_mode or p_value < 0.05 and p_value != -1:
        print("Training model ...")
        (model, score) = train_model(parameterMatrix, resultVector)
        
        if test_mode:
            save_model(model, provider, "parameter_"+str(column), \
                "Model using every significant parameter in columns "+str(column)+" and under. The p-value for column "+str(column)+" was "+str(p_value)+"."\
                +"\nScore on training data: %f" % score)
        else:
            save_model(model, provider, "latest_model", "Score on training data: %f" % score)

    if test_mode:
        tested_parameters.update({column: p_value})
        with open(tested_parameters_path, 'w') as outfile:
            json.dump(tested_parameters, outfile)

    return column

def loop_update_model():
    while update_model() < data_reader.num_parameters-1:
        print()

availability_cutoff = 0.50

def test_model(name, column = -1):
    #only test files that haven't been tested
    with open("models/" + name + ".manifest", 'r') as infile:
        if infile.read().find("Predicted\tObserved") != -1:
            return None
    
    with open("models/" + name + ".pickle", 'rb') as infile:
        model = pickle.load(infile)
    
    tested_parameters = get_tested_parameters()
    if column == -1:
        column = get_next_column(tested_parameters)
    (parameterMatrix, resultVector) = get_matrix(tested_parameters, column, "ethan_data_30days.json")
    scaler = preprocessing.StandardScaler().fit(parameterMatrix)
    normalizedMatrix = scaler.transform(parameterMatrix)

    probabilities = model.predict_proba(normalizedMatrix)
    counts = [0, 0, 0, 0] #[correct fail, incorrect fail, incorrect success, correct success]
    for i, prediction in enumerate(probabilities):
        if prediction[1] < availability_cutoff:
            if resultVector[i] == 0:
                counts[0] += 1
            else:
                counts[1] += 1
        else:
            if resultVector[i] == 0:
                counts[2] += 1
            else:
                counts[3] += 1
    
    percents = [count/len(probabilities) for count in counts]
    output = '''
With a decision cutoff of {8:.0%}:
Predicted\tObserved
     \t\t0   \t\t 1
0: {4:.2%} \t{0:.2%}   \t {1:.2%}
1: {5:.2%} \t{2:.2%}   \t {3:.2%}
     \t\t{6:.2%}   \t {7:.2%}
'''.format(percents[0], percents[1], percents[2], percents[3], percents[0]+percents[1], percents[2]+percents[3],\
        percents[0]+percents[2], percents[1]+percents[3], availability_cutoff)
    print(output)
    with open("models/" + name + ".manifest", 'a') as outfile:
        outfile.write('\n' + output)
    return counts

test_model("parameter_54")
