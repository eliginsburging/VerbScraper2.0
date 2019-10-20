import scrapy
import csv
import logging
import urllib
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider
from helpers import input_isvalid, yesno_prompt, color_stress, man_stress, needs_stress, colors
from wordspider.items import StressspiderItem

sentence_list = []
logger = logging.getLogger(__name__)
logging.basicConfig(filename='stresspider.log')


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
                sentence = sentence.replace('(', '')
                sentence = sentence.replace(')', '')
                sentence = sentence.replace('[', '')
                sentence = sentence.replace(']', '')
                sentence = sentence.replace('/', '')
                sentence = sentence.lower()
                words = sentence.split()
                # create list of only words that need stress
                targetwords = [word for word in words if needs_stress(word)]
                targetwords = set(targetwords)
                urls += [baseurl + word + '/' for word in targetwords]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        word_of_interest = urllib.parse.unquote(response.url)[49:-1]
        if response.status == 404:
            warning = f'\n\n\nWARNING: {word_of_interest} failed\n\n\n'
            self.logger.warning(warning)
            print(colors.prompt(
                f"It appears no stress could be found for {word_of_interest}"))
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
                        raise CloseSpider('Maxmimum iterations exceeded; while loop broken')
                        break
                    for letter in word_of_interest:
                        print(colors.parrot(f'{letter:3s}'), end=" ")
                    print(' ')
                    for i in range(len(word_of_interest)):
                        print(colors.parrot(f'{str(i):3s}'), end=" ")
                    print(' ')
                    stress_choice = input(colors.prompt(
                        "Please enter the number of the letter you wish to stress: "))
                    iters2 = 0
                    while not input_isvalid(stress_choice, word_of_interest):
                        iters2 += 1
                        if iters2 > 1000:
                            raise CloseSpider('Maxmimum iterations exceeded; while loop broken')
                            break
                        for letter in word_of_interest:
                            print(colors.parrot(f'{letter:3s}'), end=" ")
                        print()
                        for i in range(len(word_of_interest)):
                            print(colors.parrot(f'{str(i):3s}'), end=" ")
                        print()
                        stress_choice = input(colors.warning(
                            "Invalid entry. Please select one of the numbers listed above "))
                    if yesno_prompt(colors.prompt(
                        f"You want to place the stress on '{word_of_interest[int(stress_choice)]}' at position {stress_choice}, correct? y/n "),
                        colors.warning("Invalid entry. Please enter y or n: ")
                    ):
                        user_satisfied = True
                        target_word_stressed = man_stress(word_of_interest,
                                                          int(stress_choice))
                        print(colors.warning(target_word_stressed))
                        l = ItemLoader(item=StressspiderItem(), response=response)
                        l.add_value('stressed', target_word_stressed)
                        l.add_value('clean', word_of_interest)
                        yield l.load_item()
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
