import csv
import shlex
import os
from subprocess import Popen
from helpers import colors
from helpers import yesno_isvalid, yesno_prompt, gather_man_input, write_man_input


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
    returns true if the string can be converted to an int
    which is a valid index of target
    """
    try:
        numstr = int(numstr)
    except ValueError:
        return False
    return numstr - 1 >= 0 and numstr - 1 <= len(target) - 1


def visual_stress(word):
    """
    Takes a string and returns that string without html font tags
    and with the content which was surrounded by those tags capitalized
    """
    stress_index = word.index('>') + 1
    marked_stress = (word[:stress_index] +
                     word[stress_index].capitalize() +
                     word[stress_index + 1:])
    marked_stress = marked_stress.replace("<font color='#0000ff'>", "")
    return marked_stress.replace("</font>", "")


def success_banner(message):
    """
    Takes a string and prints that string surrounded by a green box of &s
    """
    message_len = len(message)
    spacer = '   '
    print(colors.information('&' * (message_len + 8)))
    print(colors.information('&') +
          (' ' * (message_len + 6)) +
          colors.information('&'))
    print(colors.information('&') +
          spacer +
          message +
          spacer +
          colors.information('&'))
    print(colors.information('&') +
          (' ' * (message_len + 6)) +
          colors.information('&'))
    print(colors.information('&' * (message_len + 8)))


def weave():
    """
    runs word spider and stress spider, generating csv files.
    combines information from csv files to create text file
    with stressed examples and tranlsations which can be uploaded
    to Anki
    """
    # remove examples.csv and stresses.csv if they exist
    os.system('rm examples.csv')
    os.system('rm stresses.csv')
    # run crawls in separate processes and wait for the results
    cmd = shlex.split('scrapy crawl wordspider')
    p = Popen(cmd)
    p.wait()
    # prompt user for manually added examples in addition to crawled examples
    man_examples = gather_man_input()
    if len(man_examples['example']) > 0:
        write_man_input(man_examples, 'examples.csv')
    # if len dictionary lists > 0, write dictionary lists to examples.csv
    cmd2 = shlex.split('scrapy crawl stressspider')
    p2 = Popen(cmd2)
    p2.wait()
    with open('examples.csv') as ex:
        with open('stresses.csv') as stresses:
            exreader = csv.DictReader(ex)
            streader = csv.DictReader(stresses)
            stress_dict = {}
            linestowrite = []
            """
            create master dictionary of stresses. keys are unstressed words
            and values are lists of potential stresses for the word
            """
            for row in streader:
                if row['clean'] in stress_dict.keys():
                    stress_dict[row['clean']].append(row['stressed'])
                else:
                    stress_dict[row['clean']] = [row['stressed'], ]
            for row in exreader:
                tentative_text = row['example']
                example_words = word_list(row['example'])
                for i, word in enumerate(example_words):
                    if word in stress_dict.keys() or word.lower() in stress_dict.keys():
                        if len(stress_dict[word.lower()]) > 1:
                            print()
                            print(colors.parrot(row['example']))
                            print(colors.parrot(row['translation']))
                            print()
                            print(colors.prompt(
                                f'Word {i + 1} in the example above has '
                                f'{len(stress_dict[word.lower()])} stress options'
                            ))
                            print()
                            for e, option in enumerate(stress_dict[word.lower()]):
                                print(
                                    colors.prompt(f'{e + 1} -- '
                                                  f'{visual_stress(option)}'))
                                print()
                            user_in = input(
                                colors.prompt(
                                    f'Please enter the appropriate stress '
                                    f'for word {i +1}: '
                                )
                            )
                            while not input_isvalid(user_in, stress_dict[word.lower()]):
                                user_in = input(
                                    colors.warning(
                                        'Invalid entry. Please enter a number '
                                        'corresponding to a choice above: '
                                    )
                                )
                            tentative_text = tentative_text.replace(
                                word.lower(), stress_dict[word.lower()][int(user_in) - 1], 1
                            )
                            tentative_text = tentative_text.replace(
                                word.capitalize(),
                                stress_dict[word.lower()][int(user_in) -1].capitalize(),
                                1
                            )
                        else:
                            tentative_text = tentative_text.replace(
                                word.lower(), stress_dict[word.lower()][0], 1
                            )
                            tentative_text = tentative_text.replace(
                                word.capitalize(),
                                stress_dict[word.lower()][0].capitalize(),
                                1
                            )
                linestowrite.append(
                    tentative_text + ';' + row['translation'] + '\n')
            cards_written = 0
            with open('flashcards.txt', 'w') as f:
                for line in linestowrite:
                    f.write(line)
                    cards_written += 1
            if cards_written == 1:
                message = (f'Success! {cards_written} card written to '
                           f'flashcards.txt')
            else:
                message = (f'Success! {cards_written} cards written to '
                           f'flashcards.txt')
            success_banner(message)
    os.system('rm examples.csv')
    os.system('rm stresses.csv')


weave()
