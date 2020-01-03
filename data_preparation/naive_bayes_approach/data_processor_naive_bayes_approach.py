"""
data processor
"""
import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
#from sklearn.feature_extraction.text import CountVectorizer
from imblearn.over_sampling import SMOTE
from sklearn.naive_bayes import MultinomialNB


CZECH_STOPWORDS_FILE_PATH = '../czech_stopwords.txt'
TEMP_FILE_PATH = '../bag_of_words_small.txt'
OUTPUT_FILE_PATH = '../naive_bayes_approach/data_output/bag_of_words_output.txt'

INPUT_WORDS = []
TEMP_FILE_WORDS = []
CZECH_STOPWORDS = []


def _read_temp_file_generator():
    """
    read temp file generator
    :return: yield rows
    """
    for row in open(TEMP_FILE_PATH, encoding="utf8"):
        try:
            yield (row.split()[0].replace('"','').replace("'",'').replace('$','').replace('-','').replace(' ','')
                   , -1 if int(row.split()[1]) <= 0 else 1)
        except IndexError:
            yield '#NA'


def word_valence_calculator():
    """
    function for mean valence value calculation for each word
    :return: 0
    """
    # 1 read czech_stopwords.txt file and load it to the CZECH_STOPWORDS list
    with open(CZECH_STOPWORDS_FILE_PATH, 'r', encoding='utf8') as stop_word_file:
        for line in stop_word_file:
            CZECH_STOPWORDS.append(line[:-1])

    print(f'{datetime.datetime.now()} step #1 completed')

    # 2 read temp file line by line through it's generator
    # in case it cannot fit into memory at once and load the values
    # into a Pandas data frame
    temp_file_gen = _read_temp_file_generator()

    for tfg in temp_file_gen:
        if str(tfg[0]) not in CZECH_STOPWORDS:
            if len(tfg) == 2:
                TEMP_FILE_WORDS.append(tfg)

    # print(TEMP_FILE_WORDS)
    df_temp_file = pd.DataFrame(TEMP_FILE_WORDS, columns=['word', 'bsent'])
    # print(df_temp_file)
    print(df_temp_file.head())

    #Todo value counts not well distributed :
    #1 : 1714348
    #-1 : 457699
    print(df_temp_file.bsent.value_counts())

    X = df_temp_file.word
    y = df_temp_file.bsent
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    #
    # vect = CountVectorizer(max_features=1000, binary=True)
    #
    # X_train_vect = vect.fit_transform(X_train)

    counts = df_temp_file.bsent.value_counts()
    print(counts)

    print("\nPredicting only -1 = {:.2f}% accuracy".format(counts[-1] / sum(counts) * 100))


    print(f'{datetime.datetime.now()} step #2 completed')

    nb = MultinomialNB()
    print(X_train)
    print(y_train)
    nb.fit(X_train, y_train)

    nb.score(X_train, y_train)

    # 3 read input file line by line through it's generator
    # in case it cannot fit into memory at once and load the values
    # into a Pandas data frame
    # input_file_gen = _read_input_file_generator()

    # for ifg in input_file_gen:
    #     INPUT_WORDS.append(ifg)

    # df_input_file = pd.DataFrame(INPUT_WORDS, columns=['word'])
    #
    # print(f'{datetime.datetime.now()} step #3 completed')

    # 4 merge the 2 Pandas data frames inner-join style on the column "word"
    # df_merged = pd.merge(df_temp_file, df_input_file, how='inner', on=['word'])
    #
    # print(f'{datetime.datetime.now()} step #4 completed')

    # 5 calculate the mean valence for each word using Pandas "group by" and mean methods
    # and write the data frame with the matched words and their calculated valence values
    # into the output file
    # df_merged_grouped = df_merged.groupby('word').mean()
    # df_merged_grouped = df_temp_file.groupby('word').mean()

    # df_merged_grouped.to_csv(OUTPUT_FILE_PATH, encoding='utf8', header=False,
    #                          sep=' ', line_terminator='\n')
    df_temp_file.to_csv(OUTPUT_FILE_PATH, encoding='utf8', header=False,
                        sep=',', line_terminator='\n', index=True)

    print(f'{datetime.datetime.now()} step #5 completed')













    return 0


if __name__ == "__main__":
    if word_valence_calculator() == 0:
        print("Data processing phase complete.")
