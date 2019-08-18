import csv


def word_list(string):
    """
    Takes a string, removes any punctuation, and returns a list of the words
    """
    string = string.replace(',', '')
    string = string.replace('.', '')
    string = string.replace('!', '')
    string = string.replace('?', '')
    string = string.replace('—', '')
    string = string.replace('«', '')
    string = string.replace('»', '')
    string = string.replace(':', '')
    string = string.replace(';', '')
    return string.split()


def input_isvalid(numstr, target):
    """
    takes a string of user input and an iterable;
    returns true if it can be converted to an int
    which is a valid index of target
    """
    try:
        numstr = int(numstr)
    except ValueError:
        return False
    return numstr - 1 >= 0 and numstr - 1 <= len(target) - 1


with open('examples.csv') as ex:
    with open('stresses.csv') as stresses:
        exreader = csv.DictReader(ex)
        streader = csv.DictReader(stresses)
        stress_dict = {}
        linestowrite = []
        for row in streader:
            if row['clean'] in stress_dict.keys():
                stress_dict[row['clean']].append(row['stressed'])
            else:
                stress_dict[row['clean']] = [row['stressed'], ]
        for row in exreader:
            tentative_text = row['example']
            example_words = word_list(row['example'])
            for i, word in enumerate(example_words):
                if word in stress_dict.keys():
                    if len(stress_dict[word]) > 1:
                        print(row['example'])
                        print(row['translation'])
                        print(f'Word {i + 1} in the example above has {len(stress_dict[word])} stress options')
                        for e, option in enumerate(stress_dict[word]):
                            print(f'{e + 1} -- {option}')
                        user_in = input(
                            f'Please enter the appropriate stress for word {i +1}: '
                        )
                        while not input_isvalid(user_in, stress_dict[word]):
                            user_in = input(
                                'Invalid entry. Please enter a number corresponding to a choice above: '
                            )
                        tentative_text = tentative_text.replace(
                            word, stress_dict[word][int(user_in) - 1]
                        )
                    else:
                        tentative_text = tentative_text.replace(
                            word, stress_dict[word][0]
                        )
            linestowrite.append(
                tentative_text + ';' + row['translation'] + '\n')
        with open('flashcards.txt', 'w') as f:
            for line in linestowrite:
                f.write(line)
