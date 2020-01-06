"""
data processor for logistic regression
"""
import random
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB


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
                   0 if int(row.split(',')[1]) <0 else 1)
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


def naive_bayes():
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

    temp_file_review_work = [x for x in temp_file_review_work if x[1] == 0][:14000] + \
                         [x for x in temp_file_review_work if x[1] == 1][:14000]

    random.shuffle(temp_file_review_work)
    # print(temp_file_review_work[:10])

    temp_file_reviews = [x[0] for x in temp_file_review_work]
    temp_file_class = [x[1] for x in temp_file_review_work]
    # print(temp_file_reviews[:10])
    # print(temp_file_class[:10])

    train_data_X = temp_file_reviews[:14000]
    train_data_y = temp_file_class[:14000]
    test_data_X = temp_file_reviews[14001:28000]
    test_data_y = temp_file_class[14001:28000]
    # print(train_data)
    # print(test_data)


    vect = CountVectorizer()
    X_train = vect.fit_transform([x for x in train_data_X])
    X_test = vect.transform([x for x in test_data_X])

    y_train = train_data_y
    y_test = test_data_y
    # print(y_train)
    nb = MultinomialNB()
    nb.fit(X_train, y_train)

    predictions = nb.predict(X_test)
    # print([x for x in y_test])
    # fpr, tpr, thresholds = metrics.roc_curve([x for x in y_test], predictions, pos_label=1)
    # print("Multinomial naive bayes AUC: {0}".format(metrics.auc(fpr, tpr)))

    # xv = nb.predict(vect.transform(input_string))
    # print(xv)

    # input_string = ["some input string of czech text"]
    # print("prediction: {}". format(nb.predict(vect.transform(input_string))))
    pickle.dump(vect, open('vectorizer.pkl', 'wb'))
    pickle.dump(nb, open('model.pkl','wb'))
