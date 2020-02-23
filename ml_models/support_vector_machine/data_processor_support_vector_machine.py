"""
data processor for logistic regression
"""
import random
import pickle
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn import metrics, model_selection
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from utils.project_utils import _read_czech_stopwords, _replace_all


TEMP_FILE_PATH = '../../data_preparation/reviews_with_ranks.csv'
CZECH_STOPWORDS_FILE_PATH = '../../data_preparation/czech_stopwords.txt'
PERSIST_MODEL_TO_FILE = False


def _read_temp_file_generator():
    """
    read temp file generator
    :return: yield rows
    """
    for row in open(TEMP_FILE_PATH, encoding="utf8"):
        try:
            yield (row.split(',')[0].replace('"', ''),
                   'neg' if int(row.split(',')[1]) <0 else 'pos')
        except IndexError:
            yield '#NA'


def support_vector_machine(PERSIST_MODEL_TO_FILE):
    """
    function for training and testing the ML model
    :param PERSIST_MODEL_TO_FILE:
    :return:
    """
    temp_file_reviews_work = []

    temp_file_gen = _read_temp_file_generator()
    czech_stopwords = _read_czech_stopwords(CZECH_STOPWORDS_FILE_PATH)

    for tfg in temp_file_gen:
        if len(tfg) == 2:
            if _replace_all(tfg[0]) not in czech_stopwords:
                temp_file_reviews_work.append((_replace_all(tfg[0].rstrip(' ').lstrip(' ')),tfg[1]))

    temp_file_reviews_work = [x for x in temp_file_reviews_work if x[1] == 'neg'][:14000] + \
                         [x for x in temp_file_reviews_work if x[1] == 'pos'][:14000]

    random.shuffle(temp_file_reviews_work)

    Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split([x[0] for x in temp_file_reviews_work],
                                                                        [x[1] for x in temp_file_reviews_work],
                                                                        test_size=0.2)

    text_clf = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', SGDClassifier(loss='log', penalty='l2',
                              alpha = 1e-3, random_state = 42,
                              max_iter = 5, tol = None)),
    ])

    text_clf.fit(Train_X, Train_Y)
    predicted = text_clf.predict(Test_X)
    parameters = {
        'vect__ngram_range': [(1, 1), (1, 2)],
        'tfidf__use_idf': (True, False),
        'clf__alpha': (1e-2, 1e-3),
    }

    gs_clf = GridSearchCV(text_clf, parameters, cv=5, n_jobs=-1)
    gs_clf = gs_clf.fit(Train_X, Train_Y)

    if PERSIST_MODEL_TO_FILE:
        pickle.dump(gs_clf, open('model.pkl','wb'))

    # # accuracy score calculation: 0.822
    # print(np.mean(predicted == Test_Y))
    # print(metrics.classification_report(Test_Y, predicted, target_names = ['neg', 'pos']))

    # # adhoc input prediction:
    # input_string = ''
    # print(input_string)
    # print("prediction: {}". format(gs_clf.predict([input_string])[0]))

    return np.mean(predicted == Test_Y)


if __name__ == "__main__":
    support_vector_machine(PERSIST_MODEL_TO_FILE)