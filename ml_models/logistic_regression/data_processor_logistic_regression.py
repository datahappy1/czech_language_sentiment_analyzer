"""
data processor for logistic regression
"""
import random
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import mglearn


CZECH_STOPWORDS_FILE_PATH = '../../data_preparation/czech_stopwords.txt'
TEMP_FILE_PATH = '../../data_preparation/reviews_with_ranks.csv'
CZECH_STOPWORDS = []


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


def _read_czech_stopwords():
    """
    function reading czech stopwords file and storing it to a list
    :return:0 on success
    """
    with open(CZECH_STOPWORDS_FILE_PATH, 'r', encoding='utf8') as stop_word_file:
        for line in stop_word_file:
            CZECH_STOPWORDS.append(line[:-1])
    return 0


def logistic_regression():
    """
    function for training and testing the ML model
    :return:
    """
    temp_file_review_work = []

    temp_file_gen = _read_temp_file_generator()
    _read_czech_stopwords()

    for tfg in temp_file_gen:
        if len(tfg) == 2:
            if tfg[0] not in CZECH_STOPWORDS:
                temp_file_review_work.append(tfg)

        temp_file_review_work = [x for x in temp_file_review_work if x[1] == 'neg'][:14000] + \
                             [x for x in temp_file_review_work if x[1] == 'pos'][:14000]

    random.shuffle(temp_file_review_work)
    # print(TEMP_FILE_REVIEWS_WORK[:10])

    temp_file_reviews = [x[0] for x in temp_file_review_work]
    temp_file_class = [x[1] for x in temp_file_review_work]
    # print(TEMP_FILE_REVIEWS[:10])
    # print(TEMP_FILE_CLASS[:10])

    train_data_X = temp_file_reviews[:14000]
    train_data_y = temp_file_class[:14000]
    test_data_X = temp_file_reviews[14001:28000]
    test_data_y = temp_file_class[14001:28000]
    # print(train_data)
    # print(test_data)

    vect = CountVectorizer(min_df=5, ngram_range=(2, 2))
    X_train = vect.fit(train_data_X).transform(train_data_X)
    X_test = vect.transform(test_data_X)

    y_train = train_data_y
    y_test = test_data_y

    # print("Vocabulary size: {}".format(len(vect.vocabulary_)))
    # print("X_train:\n{}".format(repr(X_train)))
    # print("X_test: \n{}".format(repr(X_test)))

    # feature_names = vect.get_feature_names()
    # print("Number of features: {}".format(len(feature_names)))

    param_grid = {'C': [0.001, 0.01, 0.1, 1, 10]}
    grid = GridSearchCV(LogisticRegression(max_iter=1000), param_grid, cv=5)
    grid.fit(X_train, y_train)

    # print("Best cross-validation score: {:.2f}".format(grid.best_score_))
    # print("Best parameters: ", grid.best_params_)
    # print("Best estimator: ", grid.best_estimator_)

    # mglearn.tools.visualize_coefficients(grid.best_estimator_.coef_, feature_names, n_top_features=25)
    # plt.show()
    # print(X_test)
    lr = grid.best_estimator_
    lr.fit(X_train, y_train)
    lr.predict(X_test)
    # print("Score: {:.2f}".format(lr.score(X_test, y_test)))

    # input_string = ["some input string of czech text"]
    # print("prediction: {}". format(lr.predict(vect.transform(input_string))))
    pickle.dump(vect, open('vectorizer.pkl', 'wb'))
    pickle.dump(lr, open('model.pkl','wb'))
