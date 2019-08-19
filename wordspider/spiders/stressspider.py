import scrapy
import csv
import logging
from urllib import parse
from scrapy.loader import ItemLoader
from wordspider.items import StressspiderItem

vowels = 'аяэеоуюиы'  # used to check if word needs stress
sentence_list = []
"""used for displaying the sentence the word came from if two or more stress
variants appear. The user will be prompted to choose the variant appropriate
for the sentence"""
logger = logging.getLogger(__name__)
logging.basicConfig(filename='stresspider.log')


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


# def clean_scraped(scrapedstring):
#     """
#     takes a scraped string and removes html tags, newlines, and tags.
#     Returns the cleaned up string
#     """
#     scrapedstring = scrapedstring.replace('<div class="word">', '')
#     scrapedstring = scrapedstring.replace('</div>', '')
#     scrapedstring = scrapedstring.replace('\n', '')
#     scrapedstring = scrapedstring.replace('\t', '')
#     scrapedstring = scrapedstring.replace('<div class="rule ">', '')
#     scrapedstring = scrapedstring.replace('<b>', '')
#     scrapedstring = scrapedstring.replace('</b>', '')
#     return scrapedstring


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


class StressSpider(scrapy.Spider):
    name = 'stressspider'
    custom_settings = {
        'FEED_URI': 'stresses.csv'
    }
    handle_httpstatus_list = [404]

    def start_requests(self):
        """
        The code below will need to be rewritten once the wordspider
        outputs csv with examples and translations. At present it takes input
        from a file containing example sentences on new lines, splits each line
        into words and removes punctuation marks, and generates urls based on
        the words.
        """
        with open('examples.csv', 'r') as file:
            fieldnames = []
            for i, l in enumerate(file):
                fieldnames.append(i)
        with open('examples.csv') as csv_file:
            reader = csv.DictReader(csv_file)
            urls = []
            baseurl = 'https://' + 'где-ударение.рф/в-слове-'
            for row in reader:
                sentence = row['example']
                sentence_list.append(sentence.lower())
                sentence = sentence.replace(',', '')
                sentence = sentence.replace('.', '')
                sentence = sentence.replace('!', '')
                sentence = sentence.replace('?', '')
                sentence = sentence.replace('—', '')
                sentence = sentence.replace('«', '')
                sentence = sentence.replace('»', '')
                sentence = sentence.replace(':', '')
                sentence = sentence.replace(';', '')
                sentence = sentence.lower()
                words = sentence.split()
                # create list of only words that need stress
                targetwords = [word for word in words if needs_stress(word)]
                targetwords = set(targetwords)
                urls += [baseurl + word + '/' for word in targetwords]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        word_of_interest = parse.unquote(response.url)[49:-1]
        if response.status == 404:
            warning = f'\n\n\nWARNING: {word_of_interest} failed\n\n\n'
            self.logger.warning(warning)
            print(f"It appears no stress could be found for {word_of_interest}")
            manual_stress = input("Would you like to enter a stress manually? y/n: ")
            while not yesno_isvalid(manual_stress):
                manual_stress = input(
                    "Invalid entry. Please enter y or n: ")
            if manual_stress in "yY":
                user_satisfied = False
                while not user_satisfied:
                    for letter in word_of_interest:
                        print(f'{letter:3s}', end=" ")
                    print(' ')
                    for i in range(len(word_of_interest)):
                        print(f'{str(i):3s}', end=" ")
                    print(' ')
                    stress_choice = input(
                        "Please enter the number of the letter you wish to stress: ")
                    while not input_isvalid(stress_choice, word_of_interest):
                        for letter in word_of_interest:
                            print(f'{letter:3s}', end=" ")
                            print(' ')
                        for i in range(len(word_of_interest)):
                            print(f'{str(i):3s}', end=" ")
                            print(' ')
                        stress_choice = input(
                            "Invalid entry. Please select one of the numbers listed above")
                    is_satisfied = input(
                        f"You want to place the stress on '{word_of_interest[int(stress_choice)]}' at position {stress_choice}, correct? y/n "
                    )
                    while not yesno_isvalid(is_satisfied):
                        is_satisfied = input(
                            "Invalid entry. Please enter y or n: "
                        )
                    if is_satisfied in "yY":
                        user_satisfied = True
                        target_word_stressed = man_stress(word_of_interest,
                                                          int(stress_choice))
                        l.add_value('stressed', target_word_stressed)
                        l.add_value('clean', word_of_interest)
                        return l.load_item()
        else:
            # will output items with a clean (unstressed) version and a stressed version
            explanations = response.xpath('//div[@class="word"]').getall()
            """
            creates a list of the HTML elements containing the explanation of the
            stress, e.g.,
            ['<div class="word">\n\t\t\t<b>I.</b> горы́\n\t\t\t\t\t\t\t— родительный
            падеж слова гора\t\t\t\t\t</div>',
            '<div class="word">\n\t\t\t<b>II.</b> го́ры\n\t\t\t\t\t\t\t—
            множественное число слова гора\t\t\t\t\t</div>']
            """
            stresses = response.xpath(
                "//div[@class='rule ']").getall()
            """
            Creates a list of the HTML elements containing the stress, e.g.,
            ['<div class="rule ">\n\t\n\t\t В указанном выше варианте ударение
            падает на слог с буквой Ы — гор<b>Ы</b>. \n\t\t\t</div>',
            '<div class="rule ">\n\t\n\t\t В таком варианте ударение следует
            ставить на слог с буквой О — г<b>О</b>ры. \n\t\t\t</div>']
            """
            if len(stresses) > 1:
                # if there is more than one stress variant, add all options
                for line in stresses:
                    l = ItemLoader(item=StressspiderItem(), response=response)
                    target_word_stressed = color_stress(line)
                    l.add_value('stressed', target_word_stressed)
                    print(f'added {target_word_stressed} and {word_of_interest}')
                    l.add_value('clean', word_of_interest)
                    yield l.load_item()
            else:
                l = ItemLoader(item=StressspiderItem(), response=response)
                # if only one option for stress exists, add it
                stressed_line = stresses[0]
                # isolate target word and mark stress with color html tag
                target_word_stressed = color_stress(stressed_line)
                l.add_value('stressed', target_word_stressed)
                l.add_value('clean', word_of_interest)
                print(f'added {target_word_stressed} and {word_of_interest}')
                yield l.load_item()
