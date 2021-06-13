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
            l = ItemLoader(item=StressspiderItem(), response=response)
            l.add_value('stressed', word_of_interest)
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
                "//div[@class='rule']").getall()
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
                    l.add_value('stressed', target_word_stressed_list[0])
                    print(f'added {target_word_stressed_list[0]} and {word_of_interest}')
                    l.add_value('clean', word_of_interest)
                    yield l.load_item()
            else:
                target_word_stressed_list = color_stress(stresses[0])
                # check to see if multiple options were included in the same div
                # as for some words with multiple acceptable variants, both
                # options are in the same div (e.g. держитесь)
                if len(target_word_stressed_list) > 1:
                    assert len(target_word_stressed_list) == 2
                    l1 = ItemLoader(item=StressspiderItem(),
                                    response=response)
                    l2 = ItemLoader(item=StressspiderItem(),
                                    response=response)
                    l1.add_value('stressed', target_word_stressed_list[0])
                    print(f'added {target_word_stressed_list[0]} and {word_of_interest}')
                    l1.add_value('clean', word_of_interest)
                    l2.add_value('stressed', target_word_stressed_list[1])
                    print(f'added {target_word_stressed_list[1]} and {word_of_interest}')
                    l2.add_value('clean', word_of_interest)
                    for item in (l1.load_item(), l2.load_item()):
                        yield item
                else:
                    l = ItemLoader(item=StressspiderItem(), response=response)
                    # if only one option for stress exists, add it
                    stressed_line = stresses[0]
                    # isolate target word and mark stress with color html tag
                    target_word_stressed_list = color_stress(stressed_line)
                    l.add_value('stressed', target_word_stressed_list[0])
                    l.add_value('clean', word_of_interest)
                    print(f'added {target_word_stressed_list[0]} and {word_of_interest}')
                    yield l.load_item()
