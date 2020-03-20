"""
data processor for logistic regression
"""
import random
import pickle
import os
from langdetect import detect, lang_detect_exception
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics,model_selection
from utils.utilities import ProjectCommon

CZECH_STOPWORDS_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                                         'data_preparation', 'czech_stopwords.txt'))

TEMP_FILE_PATH = '../../data_preparation/reviews_with_ranks.csv'
PERSIST_MODEL_TO_FILE = True


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


def naive_bayes(persist_model_to_file):
    """
    function for training and testing the ML model
    :param persist_model_to_file:
    :return:
    """
    temp_file_reviews_work = []

    temp_file_gen = _read_temp_file_generator()

    for tfg in temp_file_gen:
        if len(tfg) == 2:
            try:
                _detected_lang = detect(ProjectCommon.remove_non_alpha_chars_and_html(tfg[0]))
            except lang_detect_exception.LangDetectException:
                continue
            if  _detected_lang == 'cs':
                temp_file_reviews_work.append((ProjectCommon.remove_all(tfg[0]), tfg[1]))

    temp_file_reviews_work = [x for x in temp_file_reviews_work if x[1] == 0][:11500] + \
                         [x for x in temp_file_reviews_work if x[1] == 1][:11500]

    random.shuffle(temp_file_reviews_work)

    Train_X, Test_X, Train_Y, Test_Y = model_selection.\
        train_test_split([x[0] for x in temp_file_reviews_work],
                         [x[1] for x in temp_file_reviews_work],
                         test_size=0.2)

    vect = CountVectorizer()
    Train_X = vect.fit_transform([x for x in Train_X])
    Test_X = vect.transform([x for x in Test_X])

    nb = MultinomialNB()
    nb.fit(Train_X, Train_Y)

    if persist_model_to_file:
        pickle.dump(vect, open('vectorizer.pkl', 'wb'))
        pickle.dump(nb, open('model.pkl','wb'))

    # # accuracy score calculation: 0.897
    predictions = nb.predict(Test_X)
    fpr, tpr, thresholds = metrics.roc_curve([x for x in Test_Y], predictions, pos_label=1)
    # print("Multinomial naive bayes AUC: {0}".format(metrics.auc(fpr, tpr)))

    # # adhoc input prediction:
    # input_string = input_string[0]
    # input_string = [x for x in input_string.split()]
    # print(input_string)
    # print("prediction: {}". format(nb.predict(vect.transform(input_string))))

    # return accuracy score
    return metrics.auc(fpr, tpr)


if __name__ == "__main__":
    naive_bayes(PERSIST_MODEL_TO_FILE)
