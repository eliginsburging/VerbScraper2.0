from scrapy.exceptions import CloseSpider


vowels = 'аяэеоуюиы'  # used to check if word needs stress


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
        raise RuntimeError('User input validation failed; validator returned none!')
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
    stressed_line = stressed_line.lower()
    for word in stressed_line.split():
        if '<b>' in word:
            target = word.replace('<b>', "<font color='#0000ff'>")
            target = target.replace('</b>', '</font>')
            return target


def man_stress(word, index):
    """
    takes a string and an int that is an index of that string;
    returns a copy of the string where the character at that
    index has been surrounded by an html font tag
    """
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