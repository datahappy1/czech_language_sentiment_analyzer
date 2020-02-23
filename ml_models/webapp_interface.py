"""
ml models interface for Flask web application
"""
import os
import pickle


def _pickle_load(model_type, file_name):
    """
    load pickled data model file function
    :param model_type:
    :param file_name:
    :return:
    """
    return pickle.load(open(os.path.abspath(os.path.join(os.path.dirname(__file__), model_type, file_name)), 'rb'))


# pickle load ml models
VECTOR_NB = _pickle_load('naive_bayes', 'vectorizer.pkl')
MODEL_NB = _pickle_load('naive_bayes', 'model.pkl')
VECTOR_LR = _pickle_load('logistic_regression', 'vectorizer.pkl')
MODEL_LR = _pickle_load('logistic_regression', 'model.pkl')
MODEL_SVM = _pickle_load('support_vector_machine', 'model.pkl')

# prepare the overall sentiment model weights
PRECISION_NB = 0.902
PRECISION_LR = 0.850
PRECISION_SVM = 0.828
PRECISION_SUM = PRECISION_NB + PRECISION_LR + PRECISION_SVM
PRECISION_NB_WEIGHT_AVG = PRECISION_NB / PRECISION_SUM
PRECISION_LR_WEIGHT_AVG = PRECISION_LR / PRECISION_SUM
PRECISION_SVM_WEIGHT_AVG = PRECISION_SVM / PRECISION_SUM


def ml_model_evaluator(input_string):
    """
    function for machine learning model evaluation
    :param input_string:
    :return: prediction_output dict
    """
    prediction_output = dict()
    # prediction_naive_bayes = MODEL_NB.predict(VECTOR_NB.transform(input_string))
    # prediction_logistic_regression = MODEL_LR.predict(VECTOR_LR.transform(input_string))
    # prediction_support_vector_machine = MODEL_SVM.predict(input_string)

    prediction_naive_bayes_prob = MODEL_NB.predict_proba(VECTOR_NB.transform(input_string))[0][0]
    prediction_logistic_regression_prob = MODEL_LR.predict_proba(VECTOR_LR.transform(input_string))[0][0]
    prediction_support_vector_machine_prob = MODEL_SVM.predict_proba(input_string)[0][0]

    prediction_output_overall_proba = round((prediction_naive_bayes_prob * PRECISION_NB_WEIGHT_AVG) + \
                                            (prediction_logistic_regression_prob * PRECISION_LR_WEIGHT_AVG) + \
                                            (prediction_support_vector_machine_prob * PRECISION_SVM_WEIGHT_AVG), 2)

    if prediction_output_overall_proba < 0.48:
        prediction_output['overall_sentiment'] = {'sentiment': 'positive',
                                                  'probability': prediction_output_overall_proba}
    elif prediction_output_overall_proba > 0.52:
        prediction_output['overall_sentiment'] = {'sentiment': 'negative',
                                                  'probability': prediction_output_overall_proba}
    else:
        prediction_output['overall_sentiment'] = {'sentiment': 'uncertain',
                                                  'probability': prediction_output_overall_proba}

    return prediction_output
