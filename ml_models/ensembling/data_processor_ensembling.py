"""
data processor for ensembling naive bayes and logistic regression
"""
import random
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn import svm
from sklearn import model_selection

from utils.utils import _read_czech_stopwords, _replace_all


TEMP_FILE_PATH = '../../data_preparation/reviews_with_ranks.csv'
CZECH_STOPWORDS_FILE_PATH = '../../data_preparation/czech_stopwords.txt'
PERSIST_MODEL_TO_FILE = True


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


def ensemble():
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

    vect = CountVectorizer()
    Train_X = vect.fit_transform([x for x in Train_X])
    Test_X = vect.transform([x for x in Test_X])


    kfold_vc = model_selection.KFold(n_splits=10, random_state=10)
    estimators = []
    mod_lr = LogisticRegression()
    estimators.append(('logistic', mod_lr))
    mod_nb = MultinomialNB()
    estimators.append(('nb', mod_nb))
    # mod_svm = svm.SVC()
    # estimators.append(('svm', mod_svm))

    ensemble = VotingClassifier(estimators)
    results_vc = model_selection.cross_val_score(ensemble, Train_X, Train_Y, cv=kfold_vc)

    # # accuracy score calculation: 0.896
    # # print(results_vc.mean())

    # adhoc input prediction:
    input_string = ['jsi debil kokot hovno']
    input_string = input_string[0]
    input_string = [x for x in input_string.split()]
    print(input_string)
    print("prediction: {}". format(results_vc.predict(vect.transform(input_string))))

    if PERSIST_MODEL_TO_FILE:
        pickle.dump(vect, open('vectorizer.pkl', 'wb'))
        pickle.dump(results_vc, open('model.pkl','wb'))

#https://www.pluralsight.com/guides/ensemble-modeling-scikit-learn
ensemble()