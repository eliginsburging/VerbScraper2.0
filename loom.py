import csv
import shlex
import os
import sys
from pyfiglet import Figlet
from subprocess import Popen
from helpers import colors
from helpers import (gather_man_input,
                     write_man_input,
                     word_list,
                     input_isvalid,
                     visual_stress,
                     validate_word,
                     success_banner,
                     needs_stress,
                     yesno_prompt,
                     man_stress)


def weave():
    """
    runs word spider and stress spider, generating csv files.
    combines information from csv files to create text file
    with stressed examples and tranlsations which can be uploaded
    to Anki
    """
    banner_fig = Figlet(font='banner3-D', width=120)
    warning_fig = Figlet(font='xcourb', width=120)
    print(colors.information(banner_fig.renderText('VerbScraper2.0')))
    # check to see if toscrape.txt exists and warn user if not
    if not os.path.exists('toscrape.txt'):
        print(colors.warning(
            warning_fig.renderText('Warning: toscrape.txt not found')))
        print(colors.warning('In order to scrape example sentences, you must '
                             'first create a file in the same directory as '
                             'loom.py that contains a list of single Russian '
                             'words, each on its own line. Since this file '
                             'is missing, you will be prompted to enter '
                             'your own examples manually.'))
        toscrape = False
    else:
        toscrape = True
        with open('toscrape.txt') as f:
            warning1 = "toscrape.txt improperly formatted"
            warning2 = ("It appears that toscrape.txt is improperly formatted."
                        " the file should contain only single Russian words on"
                        " new lines. Launching in manual entry only mode.")
            if f.read() == '':
                print(colors.warning(warning1 + '\n' + warning2))
                toscrape = False
            else:
                for line in f:
                    if not validate_word(line):
                        toscrape = False
                        print(colors.warning(warning1 + '\n' + warning2))
                        break
        if toscrape:
            with open('toscrape.txt') as f:
                print(colors.prompt(
                    "toscrape.txt appears to be valid and contains the "
                    "words listed below."))
                for l in f:
                    print(
                        colors.information(
                            l.replace('\n', '')),)
                print()
                answer = input(colors.prompt(
                    'Would you like to:\n'
                    '1 - proceed with these words (you will be prompted for '
                    'optional manual entries as well)\n'
                    '2 - proceed with manual entries only\n'
                    'alternatively, enter "exit" to exit.\n'
                ))
                iterbreak = 0
                while answer not in ["1", "2", "exit", "Exit", "EXIT"]:
                    iterbreak += 1
                    if iterbreak > 1000:
                        raise RuntimeError(
                            "Max iterations exceded! Loop borken")
                        break
                    answer = input(colors.prompt(
                        'Invalid entry. Please enter 1, 2, or exit\n'
                    ))
                if answer in ["exit", "Exit", "EXIT"]:
                    sys.exit(0)
                if answer == "2":
                    toscrape = False
    # remove examples.csv and stresses.csv if they exist
    os.system('rm examples.csv >/dev/null 2>&1')
    os.system('rm stresses.csv >/dev/null 2>&1')
    if toscrape:
        # if the user has supplied toscrape.txt and opted to use it, run
        # wordspider
        cmd = shlex.split('scrapy crawl wordspider')
        p = Popen(cmd)
        p.wait()
    # prompt user for manually added examples in addition to crawled examples
    man_examples = gather_man_input()
    if not toscrape and len(man_examples['example']) < 1:
        raise RuntimeError('No examples provided!')
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
                        try:
                            target_word = stress_dict[word][0]
                        except KeyError:
                            target_word = stress_dict[word.lower()][0]
                        if "</font>" not in target_word.lower():
                            print()
                            print(colors.prompt(
                                f"It appears no stress was found for {word}"))
                            if yesno_prompt(
                                colors.prompt(
                                    'Would you like to enter a stress mannually? y/n: '),
                                colors.warning(
                                    'Invalid entry. Please enter y or n: ')):
                                user_satisfied = False
                                iters = 0
                                while not user_satisfied:
                                    iters += 1
                                    if iters > 1000:
                                        print("max iterations exceeded; break")
                                        break
                                    for letter in target_word.lower():
                                        print(colors.parrot(f'{letter:3s}'), end=" ")
                                    print(' ')
                                    for i in range(len(target_word)):
                                        print(colors.parrot(f'{str(i + 1):3s}'), end=" ")
                                    print(' ')
                                    stress_choice = input(colors.prompt(
                                        "Please enter the number of the letter you wish to stress: "))
                                    iters2 = 0
                                    while not input_isvalid(stress_choice, target_word):
                                        iters2 += 1
                                        if iters2 > 1000:
                                            print('Maxmimum iterations exceeded; while loop broken')
                                            break
                                        for letter in target_word.lower():
                                            print(colors.parrot(f'{letter:3s}'), end=" ")
                                        print()
                                        for i in range(len(target_word)):
                                            print(colors.parrot(f'{str(i + 1):3s}'), end=" ")
                                        print()
                                        stress_choice = input(colors.warning(
                                            "Invalid entry. Please select one of the numbers listed above "))
                                    if yesno_prompt(colors.prompt(
                                        f"You want to place the stress on '{word[int(stress_choice) - 1]}' at position {stress_choice}, correct? y/n "),
                                        colors.warning("Invalid entry. Please enter y or n: ")
                                    ):
                                        user_satisfied = True
                                        stress_dict[target_word.lower()][0] = man_stress(target_word.lower(),
                                                                       int(stress_choice) - 1)
                                        print()
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
                                word.lower(),
                                stress_dict[word.lower()][int(user_in) - 1], 1
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
