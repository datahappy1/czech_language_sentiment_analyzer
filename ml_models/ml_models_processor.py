"""
the ml_models_processor module allows to update all of the used ml models from one location
"""
from ml_models.naive_bayes import data_processor_naive_bayes
from ml_models.logistic_regression import data_processor_logistic_regression
from ml_models.support_vector_machine import data_processor_support_vector_machine

PERSIST_MODEL_TO_FILE = False
output = {}

output['naive_bayes']['accuracy'] = data_processor_naive_bayes.naive_bayes(PERSIST_MODEL_TO_FILE)
output['naive_bayes']['accuracy'] = data_processor_logistic_regression.logistic_regression(PERSIST_MODEL_TO_FILE)
output['naive_bayes']['accuracy'] = data_processor_support_vector_machine.support_vector_machine(PERSIST_MODEL_TO_FILE)

print(output)