import sys
import json


def af(sent_file):
    #afinnfile = open("AFINN-111.txt")
    afinnfile = sent_file

    scores = {}  # initialize an empty dictionary
    for line in afinnfile:
        term, score = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
        scores[term] = int(score)  # Convert the score to an integer.

    # print(scores.items())  # Print every (term, score) pair in the dictionary
    return scores.items()


def tf(sent_file, tweet_file):
    scores = af(sent_file)
    for line in tweet_file:
        tweet_file_str = json.loads(line)
        tweet_file_str = tweet_file_str.get('text')
        try:
            line_stack = 0
            for word in tweet_file_str.split():
                for score in scores:
                    if word in score:
                        line_stack += score[1]
            print(line_stack)

        except AttributeError:
            print(0)


def lines(fp):
    print(str(len(fp.readlines())))


def main():
    sent_file = open(sys.argv[1])
    tweet_file = open(sys.argv[2])
    #TODO fuzzy or exact match
    tf(sent_file, tweet_file)


if __name__ == '__main__':
    main()
