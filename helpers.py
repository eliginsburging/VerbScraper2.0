import csv
from scrapy.exceptions import CloseSpider


vowels = 'аяэеоуюиыАЯЭЕОУЮИЫ'  # used to check if word needs stress
rusalph = 'аАбБвВгГдДеЕёЁжЖзЗиИйЙкКлЛмМнНоОпПрРсСтТуУфФхХцЦчЧшШщЩъЪыЫьЬэЭюЮяЯ'


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


def yesno_isvalid(userstring):
    """
    returns true if userstring is 'Y','y','n', or 'N'; false otherwise
    """
    userstring = userstring.lower()
    if len(userstring) != 1:
        return False
    if userstring in "yYnN":
        return True
    return False


def yesno_prompt(prompt, errorprompt):
    """
    prompt - a string posing a yes/no question
    errorprompt - a string to display if the user enters an invalid response
    returns True if the user answers y and False if the user enters f
    """
    userstring = input(prompt)
    userstring = userstring.lower()
    repetitions = 0
    while not yesno_isvalid(userstring):
        repetitions += 1
        if repetitions > 1000:
            raise RuntimeError('Maximum iterations exceeded; loop broken')
            raise CloseSpider
            break
        userstring = input(errorprompt)
        userstring = userstring.lower()
    if userstring == "y":
        return True
    if userstring == "n":
        return False
    else:
        raise RuntimeError(
            'User input validation failed; validator returned none!')
        raise CloseSpider


def color_stress(stressed_line):
    """
    takes a string containing a scraped html element with the correct stress
    for the target word (marked with a bold html tag)
    (e.g. '<div class="rule ">\n\t\n\t\t В таком варианте ударение следует
    ставить на слог с буквой О — г<b>О</b>ры. \n\t\t\t</div>')
    returns a string containing just the target word with the bold tag replaced
    by a color tag and the stressed vowel in lower case.
    """
    stressed_line = stressed_line.replace('<div class="rule ">', '')
    stressed_line = stressed_line.replace('</div>', '')
    stressed_line = stressed_line.replace('\n', '')
    stressed_line = stressed_line.replace('\t', '')
    stressed_line = stressed_line.replace('.', '')
    stressed_line = stressed_line.replace(',', '')
    stressed_line = stressed_line.lower()
    targets = []
    for word in stressed_line.split():
        if '<b>' in word:
            target = word.replace('<b>', "<font color='#0000ff'>")
            target = target.replace('</b>', '</font>')
            targets.append(target)
    return targets


def man_stress(word, index):
    """
    takes a string and an int that is an index of that string;
    returns a copy of the string where the character at that
    index has been surrounded by an html font tag
    """
    assert type(word) == str and len(word) > 2
    assert index in range(len(word))
    return (
        word[:index] +
        "<font color='#0000ff'>" +
        word[index] +
        "</font>" +
        word[index + 1:]
    )


def needs_stress(word):
    """
    Takes a string containing a Russian word. Returns True if the word needs
    stress marked (i.e. has more than 1 vowel and does not contain ё). returns
    False otherwise
    """
    if 'ё' in word:
        return False
    vowel_count = 0
    for letter in word:
        if letter in vowels:
            vowel_count += 1
    if vowel_count > 1:
        return True
    return False


def is_valid_list(userin, example_list):
    """
    takes a users string input, attempts to split it into numbers and validate
    that those numbers are valid indexes of example_list
    """
    try:
        numlist = userin.split(',')
        numlist = [int(s) for s in numlist]
        numlist = set(numlist)
    except ValueError:
        return False
    for num in numlist:
        if num < 0 or num > len(example_list) - 1:
            return False
    return True


def validate_word(word):
    """
    Takes a string. Removes newlines and returns True if all remaining
    characters are in the russian alphabet; false otherwise
    """
    word = word.replace('\n', '')
    for letter in word:
        if letter not in rusalph:
            return False
    return True


def gather_man_input():
    """
    user prompts to manually gather a collection of manually entered examples;
    returns a dictionary where the keys are 'examples' and 'translation'
    and the values are lists of corresponding exmples and translations,
    respectively
    """
    manual_dict = {'example': [],
                   'translation': []}
    try:
        # check whether manualexamples.txt exists. If so prompt user whether
        # they want to import it
        with open("manualexamples.txt", 'r') as m:
            manexlist = m.readlines()
            itercount = 0
            if len(manexlist) > 0:
                enough = False
                print("It appears manualexamples.txt exists and contains the "
                      "following contents:")
                ruexlist = []
                enexlist = []
                for ex in manexlist:
                    ruex, enex = ex[:-1].split("|")
                    ruexlist.append(ruex)
                    enexlist.append(enex)
                    print(colors.parrot(ruex))
                    print(enex)
            else:
                enough = True
            while not enough:
                itercount += 1
                if itercount > 1000:
                    raise RuntimeError(
                        'something went wrong. Max iterations exceeded when '
                        'seeking user confirmation regarding '
                        'manualexamples.txt!'
                    )
                user_in = yesno_prompt(
                    colors.prompt('It appears manualexamples.txt exists. '
                                  'Would you like to  import it? y/n: '),
                    colors.warning('Invalid entry. Please enter y or n: ')
                )
                if user_in:
                    manual_dict['example'] += ruexlist
                    manual_dict['translation'] += enexlist
                    enough = True
                else:
                    enough = True
    except IOError:
        pass
    enough = False
    itercount = 0
    while not enough:
        itercount += 1
        if itercount > 1000:
            raise RuntimeError(
                'Something went wrong. Maximum iterations exceeded when '
                'seeking user generated examples!')
        user_in = yesno_prompt(
            colors.prompt(
                'Would you like to enter any examples '
                'manually? y/n: '),
            colors.warning('Invalid entry. Please enter y or n: '))
        if not user_in:
            enough = True
        else:
            acceptable = False
            acciter = 0
            while not acceptable:
                acciter += 1
                if acciter > 1000:
                    raise RuntimeError(
                        'Maximum iterations exceeded; loop broken'
                    )
                    break
                user_ex = input(
                    colors.prompt(
                        "Enter an example in Russian or 'c' to cancel: "
                    )
                )
                if user_ex != 'c':
                    print("You entered:")
                    print(colors.parrot(user_ex))
                    exok = yesno_prompt(
                        colors.prompt('Is that correct? y/n: '),
                        colors.warning(
                            'Invalid entry. Please enter y or n: ')
                    )
                    if exok:
                        acceptable = True
                else:
                    break
                if acceptable:
                    tr_accept = False
                    triter = 0
                    while not tr_accept:
                        print(colors.parrot(user_ex))
                        triter += 1
                        if triter > 1000:
                            raise RuntimeError(
                                'Maximum iterations exceeded; loop borken'
                            )
                            break
                        user_trans = input(
                            colors.prompt(
                                'Please enter a translation of the example '
                                'above: '
                                )
                        )
                        print(colors.prompt('You entered: '))
                        print(
                            colors.parrot(
                                user_trans
                            )
                        )
                        conf = yesno_prompt(
                            colors.prompt(
                                "Is that correct? y/n: "
                            ),
                            colors.warning(
                                'Invalid entry. Please enter y or n: '
                            )
                        )
                        if conf:
                            tr_accept = True
            if user_ex != 'c':
                manual_dict['example'].append(user_ex)
                manual_dict['translation'].append(user_trans)
    return manual_dict


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


def write_man_input(dictionary, filename):
    """
    takes a dictionary where each key is a csv table column and each value is a
    list of objects to be placed in that column
    opens csv file with name filename and appends values with corresponding
    indexes as rows in the dicionary
    for instance, the dictionary might look like:
    {'example': ['Russian example 1', 'Russian example 2'],
    'translation': ['translation 1', 'translation 2']}
    """
    try:
        with open(filename, 'r') as csvfile:
            count = 0
            for i in enumerate(csvfile):
                count += 1
    except FileNotFoundError:
        with open(filename, 'w') as csvfile:
            csvfile.write('example,translation\n')
    with open(filename, 'a') as csvfile:
        fieldnames = ['example', 'translation']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i in range(len(dictionary['example'])):
            writer.writerow({'example': dictionary['example'][i],
                             'translation': dictionary['translation'][i]})


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


class colors:
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    magenta = "\033[35m"
    cyan = "\033[36m"
    white = "\033[37m"
    reset = "\033[0m"

    def warning(message):
        """
        takes a string and returns that string surrounded by magenta and reset
        ANSI codes
        """
        return colors.magenta + message + colors.reset

    def information(message):
        """
        takes a string and returns that string surrounded by green and reset
        ANSI codes
        """
        return colors.green + message + colors.reset

    def prompt(message):
        """
        takes a string and returns that string surrounded by cyan and reset
        ANSI codes
        """
        return colors.cyan + message + colors.reset

    def parrot(message):
        """
        takes a string and returns that string surrounded by yellow and reset
        ANSI codes
        """
        return colors.yellow + message + colors.reset
