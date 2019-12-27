from statistics import mean

#need to read the temp_file file to list of lists:
tin = [['ahoj', 1], ['ahoj', 2], ['fakof', -3], ['ahoj', 5]]
tinx = []

def read_temp_file(fpath):
    with open(fpath, 'r', encoding='utf8') as f:
        for line in f:
            tinx.append(line.split())

read_temp_file('./data_output/czech_adjectives_only_rated_for_valence.txt')
print(tinx)

def data_processor():
    #1 read the temp output file written by scraper
    #2 mean valence value calculation for each word
    #3 write to final file

    dict = {}
    for elem in tin:
        if elem[0] not in dict:
            dict[elem[0]] = []
        dict[elem[0]].append(elem[1:])

    for key in dict:
        dict[key] = [mean(i) for i in zip(*dict[key])]
        # print(dict)

    with open('./data_output/czech_adjectives_only_rated_for_valence.txt', 'w', encoding='utf8') as fw:
        for key, value in dict.items():
            # print(key + ' ' + str(value[0]))
            fw.write(key + ' ' + str(int(value[0])) + '\n')

data_processor()
