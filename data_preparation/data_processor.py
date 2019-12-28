from statistics import mean

input_words = []
input_words_reduced = []
czech_corpus_words = []
czech_stopwords = ['a', 'u', 'v', 'aby', 's', 'o', 'jak', 'to', 'ale', 'za', 've', 'i', ',',
                   'ja', 'ke', 'co', 'je', 'z', 'sa', 'na', 'ze', 'ač', 'že', 'či', 'který',
                   'nějaký', 'pouze', 'bez', 'si', 'jsem', 'já', 'jí', 'by', 'asi', 'být',
                   'mi', 'je', 'jim', 'mě', 'musí', 'se', 'dnes', 'cz', 'timto', 'budes',
                   'budem', 'byli', 'jses', 'muj', 'svym', 'ta', 'tomto', 'tohle', 'tuto',
                   'tyto', 'jej', 'zda', 'proc', 'mate', 'tato', 'kam', 'tohoto', 'kdo',
                   'kteri', 'mi', 'nam', 'tom', 'tomuto', 'mit', 'nic', 'proto', 'kterou',
                   'byla', 'toho', 'protoze', 'asi', 'ho', 'nasi', 'napiste', 're', 'coz',
                   'tim', 'takze', 'svych', 'jeji', 'svymi', 'jste', 'aj', 'tu', 'tedy',
                   'teto', 'bylo', 'kde', 'ke', 'prave', 'ji', 'nad', 'nejsou', 'ci', 'pod',
                   'tema', 'mezi', 'pres', 'ty', 'pak', 'vam', 'ani', 'kdyz', 'vsak', 'ne',
                   'jsem', 'tento', 'clanku', 'clanky', 'aby', 'jsme', 'pred', 'pta', 'jejich',
                   'byl', 'jeste', 'az', 'bez', 'take', 'pouze', 'prvni', 'vase', 'ktera', 'nas',
                   'novy', 'tipy', 'pokud', 'muze', 'design', 'strana', 'jeho', 'sve', 'jine',
                   'zpravy', 'nove', 'neni', 'vas', 'jen', 'podle', 'zde', 'clanek', 'uz', 'email',
                   'byt', 'vice', 'bude', 'jiz', 'nez', 'ktery', 'by', 'ktere', 'co', 'nebo', 'ten',
                   'tak', 'ma', 'pri', 'od', 'po', 'jsou', 'jak', 'dalsi', 'ale', 'si', 've', 'to',
                   'jako', 'za', 'zpet', 'ze', 'do', 'pro', 'je', 'na']


# 2 reduce the words list of lists to remove czech stopwords
# and remove words not in the czech adjectives corpus file
def _read_file_Generator(temp_file_path):
    file = temp_file_path
    for row in open(file, encoding="utf8"):
        yield row[:-1]


def word_valence_calculator(input_file_path, temp_file_path, output_file_path):
    """
    function for mean valence value calculation for each word
    :return: 0
    """

    # 1 open input_file_path text file and store it as a list of lists of words
    # with the corresponding movie review rating values, eg.[['word1', 2],['word2', -1]]
    with open(input_file_path, 'r', encoding='utf8') as f:
        for line in f:
            try:
                input_words.append([line.split()[0],int(line.split()[1])])
            except IndexError:
                pass

    print('step #1 completed')

    corpus_gen = _read_file_Generator(temp_file_path)
    for cg in corpus_gen:
        czech_corpus_words.append(cg)

    # with open(temp_file_path, 'r', encoding='utf8') as c:
    #     for line in c:
    #         czech_corpus_words.append(line)


    for item in czech_corpus_words:
        if item not in czech_stopwords:
            if item in input_words:
                input_words_reduced.append(item)

    print('step #2 completed')

    # 3 calculate the mean valence for each word
    dict = {}
    for elem in input_words_reduced:
        if elem[0] not in dict:
            dict[elem[0]] = []
        dict[elem[0]].append(elem[1:])

    for key in dict:
        dict[key] = [mean(i) for i in zip(*dict[key])]

    print('step #3 completed')

    # 4 save the calculated results to the output_file_path text file
    with open(output_file_path, 'w', encoding='utf8') as fw:
        for key, value in dict.items():
            fw.write(key + ' ' + str(int(value[0])) + '\n')

    print('step #4 completed')

    return 0


if __name__ == "__main__":
    res = word_valence_calculator(input_file_path = './data_input/czech_adjectives_only.txt',
                                  temp_file_path = './data_temp/temp_file.txt',
                                  output_file_path = './data_output/czech_adjectives_only_rated_for_valence.txt')
    if res == 0:
        print("Data processing phase complete.")
