"""
data processor for logistic regression
"""
import random
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics,model_selection
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
                   0 if int(row.split(',')[1]) <0 else 1)
        except IndexError:
            yield '#NA'


def naive_bayes():
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


    temp_file_reviews_work = [x for x in temp_file_reviews_work if x[1] == 0][:14000] + \
                         [x for x in temp_file_reviews_work if x[1] == 1][:14000]

    random.shuffle(temp_file_reviews_work)

    Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split([x[0] for x in temp_file_reviews_work],
                                                                        [x[1] for x in temp_file_reviews_work],
                                                                                       test_size=0.2)

    vect = CountVectorizer()
    Train_X = vect.fit_transform([x for x in Train_X])
    Test_X = vect.transform([x for x in Test_X])

    nb = MultinomialNB()
    nb.fit(Train_X, Train_Y)

    # # accuracy score calculation: 0.896
    # predictions = nb.predict(Test_X)
    # fpr, tpr, thresholds = metrics.roc_curve([x for x in Test_Y], predictions, pos_label=1)
    # print("Multinomial naive bayes AUC: {0}".format(metrics.auc(fpr, tpr)))

    # # adhoc input prediction:
    # input_string = input_string[0]
    # input_string = [x for x in input_string.split()]
    # print(input_string)
    # print("prediction: {}". format(nb.predict(vect.transform(input_string))))

    if PERSIST_MODEL_TO_FILE:
        pickle.dump(vect, open('vectorizer.pkl', 'wb'))
        pickle.dump(nb, open('model.pkl','wb'))


naive_bayes()