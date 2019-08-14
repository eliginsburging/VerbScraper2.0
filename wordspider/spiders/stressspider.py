import scrapy
import csv
from scrapy.loader import ItemLoader
from wordspider.items import StressspiderItem

vowels = 'аяэеоуюиы'  # used to check if word needs stress
sentence_list = []
"""used for displaying the sentence the word came from if two or more stress
variants appear. The user will be prompted to choose the variant appropriate
for the sentence"""


def input_isvalid(numstr, targetlist):
    """
    takes a string of user input and returns true if it can be converted to
    an int which is a valid index of targetlist
    """
    try:
        numstr = int(numstr)
    except ValueError:
        return False
    return numstr - 1 in range(len(targetlist))


def clean_scraped(scrapedstring):
    """
    takes a scraped string and removes html tags, newlines, and tags.
    Returns the cleaned up string
    """
    scrapedstring = scrapedstring.replace('<div class="word">', '')
    scrapedstring = scrapedstring.replace('</div>', '')
    scrapedstring = scrapedstring.replace('\n', '')
    scrapedstring = scrapedstring.replace('\t', '')
    scrapedstring = scrapedstring.replace('<div class="rule ">', '')
    scrapedstring = scrapedstring.replace('<b>', '')
    scrapedstring = scrapedstring.replace('</b>', '')
    return scrapedstring


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


class WordSpider(scrapy.Spider):
    name = 'stressspider'

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
            baseurl = 'https://где-ударение.рф/в-слове-'
            for row in reader:
                sentence = row['example']
                sentence_list.append(sentence.lower())
                sentence = sentence.replace(',', '')
                sentence = sentence.replace('.', '')
                sentence = sentence.replace('!', '')
                sentence = sentence.replace('?', '')
                sentence = sentence.replace('-', '')
                sentence = sentence.replace('«', '')
                sentence = sentence.replace('»', '')
                sentence = sentence.replace(':', '')
                sentence = sentence.replace(';', '')
                sentence = sentence.lower()
                words = sentence.split()
                # create list of only words that need stress
                targetwords = [word for word in words if needs_stress(word)]
                urls += [baseurl + word + '/' for word in targetwords]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        l = ItemLoader(item=StressspiderItem(), response=response)
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
        """
        Some code here to isolate the text explanation and the stressed form
        For the stresssed form, replace bold tag with colored font tag
        """
        explanations_clean = [] # will hold cleaner versions of lists above
        stresses_clean = []
        for item in explanations:
            explanations_clean.append(clean_scraped(item))
        for item in stresses:
            stresses_clean.append(clean_scraped(item))
        if len(stresses_clean) > 1:
            """Identify the target word. So that the full example sentence
            from which it came can be desplayed to the user when prompting
            selection of stress where there are multiple options. Apparently
            the site with the stresses violates the principles allowed by idna,
            so rather than decoding the url  (cyrillic urls are displayed in
            punycode(?)), just find the word in the scraped content with the
            bold tag. Then see which example contains that word and print it"""
            for item in stresses:
                for word in item.split():
                    if '<b>' in word:
                        word_of_interest = word.replace('<b>', '')
                        word_of_interest = word_of_interest.replace(
                            '</b>', '').lower()
                        word_of_interest = word_of_interest.replace('.', '')
                        break
                break
            for sentence in sentence_list:
                if word_of_interest in sentence:
                    print('\n' + sentence + '\n')
            """Prompt user with choice of stress based on example sentence"""
            for i in range(len(stresses_clean)):
                print(f'{i + 1} - {explanations_clean[i]}')
                print(f'{i + 1} - {stresses_clean[i]}')
            userselect = input('It appears there is more than one option for stressing this word. Please enter the number corresponding to the appropriate stress in the sentence above: ')
            while not input_isvalid(userselect, stresses_clean):
                userselect = input('It appears you did not enter a valid choice. Please enter the number corresponding to the appropriate stress in the sentence above: ')
            # if there are multiple options for stress, use the user's choice
            stressed_line = stresses[int(userselect) - 1]
        else:
            # if only one option for stress exists, use that
            stressed_line = stresses[0]
        # remove all words but the target and replace bold tag with color
        target_word_stressed = color_stress(stressed_line)
        # create version of word with no html tag which will also be saved
        target_word_clean = target_word_stressed.replace(
            "<font color='#0000ff'>", '')
        target_word_clean = target_word_clean.replace('</font>', '')
        l.add_value('stressed', target_word_stressed)
        l.add_value('clean', target_word_clean)
        return l.load_item()
        # filename = 'stresses.txt'
        # with open(filename, 'a') as f:
        #     f.write(target_word_stressed + '\n')

        # for verbose_stress in stresses:
        #
        #     target = verbose_example.split('<div class="v2-sentence-source">',
        #                                    1)[0]
        #     target = target.split('\n',1)[1].strip() + '\n'
        #     output_list.append(target)
        # with open(filename, 'w') as f:
        #     for example in output_list:
        #         f.write(example)
        # self.log(f'Saved file {filename}')
