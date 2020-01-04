"""
data processor
"""
import datetime
import pandas as pd
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import mglearn


CZECH_STOPWORDS_FILE_PATH = '../czech_stopwords.txt'
TEMP_FILE_PATH = '../reviews_with_ranks.csv'
OUTPUT_FILE_PATH = '../naive_bayes_approach/data_output/output.txt'
TEMP_FILE_REVIEWS_WORK = []
TEMP_FILE_REVIEWS = []
TEMP_FILE_CLASS = []
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
                    # -1 if int(row.split(',')[1]) < 0 else 1)
        except IndexError:
            yield '#NA'

with open(CZECH_STOPWORDS_FILE_PATH, 'r', encoding='utf8') as stop_word_file:
    for line in stop_word_file:
        CZECH_STOPWORDS.append(line[:-1])


temp_file_gen = _read_temp_file_generator()

for tfg in temp_file_gen:
    if len(tfg) == 2:
    # if tfg!='#NA':
        if tfg[0] not in CZECH_STOPWORDS:
            TEMP_FILE_REVIEWS_WORK.append(tfg)
            # TEMP_FILE_REVIEWS.append(tfg[0])
            # TEMP_FILE_CLASS.append(tfg[1])

# print(len([x for x in TEMP_FILE_REVIEWS_WORK if x[1] == 'pos']))
# print(len([x for x in TEMP_FILE_REVIEWS_WORK if x[1] == 'neg']))

# TEMP_FILE_REVIEWS_WORK_POS = [x for x in TEMP_FILE_REVIEWS_WORK if x[1] == 'pos']
# TEMP_FILE_REVIEWS_WORK_NEG = [x for x in TEMP_FILE_REVIEWS_WORK if x[1] == 'neg']
TEMP_FILE_REVIEWS_WORK = [x for x in TEMP_FILE_REVIEWS_WORK if x[1] == 'neg'][:14000] + \
                         [x for x in TEMP_FILE_REVIEWS_WORK if x[1] == 'pos'][:14000]

random.shuffle(TEMP_FILE_REVIEWS_WORK)
# print(TEMP_FILE_REVIEWS_WORK[:10])
TEMP_FILE_REVIEWS = [x[0] for x in TEMP_FILE_REVIEWS_WORK]
TEMP_FILE_CLASS = [x[1] for x in TEMP_FILE_REVIEWS_WORK]
# print(TEMP_FILE_REVIEWS[:10])
# print(TEMP_FILE_CLASS[:10])

# print(TEMP_FILE_REVIEWS[:-5])
# df_temp_file = pd.DataFrame(TEMP_FILE_REVIEWS, columns=['headline', 'label'], index=False)

# print(df_temp_file)
# print(df_temp_file.label.value_counts())
#TODO imbalanced dataset
#  1    35784
# -1    14503

train_data_X = TEMP_FILE_REVIEWS[:14000]
train_data_y = TEMP_FILE_CLASS[:14000]
test_data_X = TEMP_FILE_REVIEWS[14001:28000]
test_data_y = TEMP_FILE_CLASS[14001:28000]

# print(train_data)
# print(test_data)


vect = CountVectorizer(min_df=5, ngram_range=(2, 2))
X_train = vect.fit(train_data_X).transform(train_data_X)
X_test = vect.transform(test_data_X)

y_train = train_data_y
y_test = test_data_y

print("Vocabulary size: {}".format(len(vect.vocabulary_)))
print("X_train:\n{}".format(repr(X_train)))
print("X_test: \n{}".format(repr(X_test)))

feature_names = vect.get_feature_names()
print("Number of features: {}".format(len(feature_names)))



param_grid = {'C': [0.001, 0.01, 0.1, 1, 10]}
grid = GridSearchCV(LogisticRegression(), param_grid, cv=5)
grid.fit(X_train, y_train)

print("Best cross-validation score: {:.2f}".format(grid.best_score_))
print("Best parameters: ", grid.best_params_)
print("Best estimator: ", grid.best_estimator_)


mglearn.tools.visualize_coefficients(grid.best_estimator_.coef_, feature_names, n_top_features=25)
plt.show()

lr = grid.best_estimator_
lr.fit(X_train, y_train)
lr.predict(X_test)
print("Score: {:.2f}".format(lr.score(X_test, y_test)))

input_string = ["Venezuela už léta zápolí s politickou a ekonomickou krizí."]
print("prediction: {}". format(lr.predict(vect.transform(input_string))))