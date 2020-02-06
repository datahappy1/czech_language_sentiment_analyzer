"""
data processor for logistic regression
"""
import random
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import model_selection,linear_model
from utils.utils import _read_czech_stopwords, _replace_all


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
                   "neg" if int(row.split(',')[1]) <0 else "pos")
        except IndexError:
            yield '#NA'


def logistic_regression():
    """
    function for training and testing the ML model
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

    vect = CountVectorizer(min_df=5, ngram_range=(2, 2))
    Train_X = vect.fit(Train_X).transform(Train_X)
    Test_X = vect.transform(Test_X)

    param_grid = {'C': [0.001, 0.01, 0.1, 1, 10]}
    grid = model_selection.GridSearchCV(linear_model.LogisticRegression(max_iter=1000), param_grid, cv=5)
    grid.fit(Train_X, Train_Y)
    lr = grid.best_estimator_
    lr.fit(Train_X, Train_Y)

    # # accuracy score calculation: 0.840
    # lr.predict(Test_X)
    # print("Score: {:.2f}".format(lr.score(Test_X, Test_Y)))

    # # adhoc input prediction:
    # input_string = input_string[0]
    # input_string = [x for x in input_string.split()]
    # print(input_string)
    # print("prediction: {}". format(lr.predict(vect.transform(input_string))))

    if PERSIST_MODEL_TO_FILE:
        pickle.dump(vect, open('vectorizer.pkl', 'wb'))
        pickle.dump(lr, open('model.pkl','wb'))


logistic_regression()