from helpers import *
from implementations import *
from preprocessing import *
#from cross_val import *

def run(methods, params):
    PATH_TRAIN= '../data/train.csv'
    PATH_TEST = '../data/test.csv'

    # Loading data
    target_train, features_train, id_train = load_csv_data(PATH_TRAIN, sub_sample=False)
    _, features_test, id_test = load_csv_data(PATH_TEST, sub_sample=False)

    ## Preprocess data
    preprocessed_features_train,preprocessed_features_test,preprocessed_y, test_masks = preprocess_data_new(
        features_train, 
        features_test,
        target_train, 
        sampling_strategy = None
    )

    test_prediction = np.zeros(shape=(features_test.shape[0],))
    groups = ['group_0', 'group_1', 'group_2', 'group_3']
    for i, group in enumerate(groups):
        method = methods[i]
        param = params[i]

        degree = param['degree']
        del param['degree']

        fourier = param['fourier']
        del param['fourier']

        #Offset 
        offset=param['offset']
        del param['offset']

        print(group)
        ##Poly
        tx_tr = build_poly(preprocessed_features_train[group], degree)
        tx_te = build_poly(preprocessed_features_test[group], degree)

        tx_tr = fourier_encoding(tx_tr, fourier)
        tx_te = fourier_encoding(tx_te, fourier)

        ##standarization
        tx_tr_std, mean, std= standardize(tx_tr)
        tx_te_std, _, _= standardize(tx_te, mean, std)
        
        if(offset):
            tx_tr_std =  add_offset(tx_tr_std)
            tx_te_std =  add_offset(tx_te_std)
        
        W, loss = method(preprocessed_y[group], tx_tr_std, **param)
        test_prediction[test_masks[group]] = predict(tx_te_std, W)

    create_csv_submission(id_test, np.sign(test_prediction), 'submission_utlimatum.csv')


if __name__ == "__main__":
    methods = [ridge_regression, ridge_regression, least_squares, least_squares]
    params = [
        {'offset': True, 'degree': 9, 'lambda_': 1e-8, 'fourier':1},
        {'offset': True, 'degree': 9, 'lambda_': 1e-8, 'fourier':2},
        {'offset': True, 'degree': 9, 'fourier':0},
        {'offset': True, 'degree': 9, 'fourier':0},

    ]
    run(methods, params)