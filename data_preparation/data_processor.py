from statistics import mean

words = []


def word_valence_calculator(input_file_path, output_file_path):
    """
    function for mean valence value calculation for each word
    :return: 0
    """

    # 1 open input_file_path text file and store it as a list of lists of words
    # with the corresponding movie review values, eg.[['word1', 2],['word2', -1]]
    with open(input_file_path, 'r', encoding='utf8') as f:
        for line in f:
            words.append([line.split()[0],int(line.split()[1])])

    # 2 calculate the mean valence for each word
    dict = {}
    for elem in words:
        if elem[0] not in dict:
            dict[elem[0]] = []
        dict[elem[0]].append(elem[1:])

    for key in dict:
        dict[key] = [mean(i) for i in zip(*dict[key])]

    # 3 save the calculated results to the output_file_path text file
    with open(output_file_path, 'w', encoding='utf8') as fw:
        for key, value in dict.items():
            fw.write(key + ' ' + str(int(value[0])) + '\n')

    return 0


if __name__ == "__main__":
    word_valence_calculator(input_file_path = './data_temp/temp_file.txt',
                            output_file_path = './data_output/czech_adjectives_only_rated_for_valence.txt')
