import scrapy
import os
from scrapy.loader import ItemLoader
from wordspider.items import WordspiderItem


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


class WordSpider(scrapy.Spider):
    name = 'wordspider'

    def start_requests(self):
        print(os.path.dirname(__file__))
        with open('wordspider/toscrape.txt', 'r') as f:
            words = f.readlines()
        urls = ['https://kartaslov.ru/предложения-со-словом/' +
                word[:-1] for word in words]
        for url in urls:
            print(url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        output_list = []
        examples = response.xpath(
            "//div[@class='v2-sentence-box'][not(@style='display: inline-block;')][not(@style='height: 317px; padding-bottom: 25px;  padding-top: 5px; display: inline-block;')]").getall()
        for verbose_example in examples:
            '''
            further refine selection, as div contains mostly unwanted content.
            Div looks like this

            <div class="v2-sentence-box">
                Прошло время, <b>птенцы</b> выросли и улетели...
                <div class="v2-sentence-source">
                    <a href="/книги/Крайон_Сказки_рассказы_притчи_для_больших
                    и_маленьких/5#p53" onclick="plantHlTag('/книги/
                    Крайон_Сказки_рассказы_притчи_для_больших_и_маленьких/
                    5#p53', 5616462)"> Крайон, Сказки, рассказы, притчи для
                    больших и&nbsp;маленьких</a>
                </div>
            </div>

            We want to remove everything after <div class='v2-setence-source'>
            and before the example
            '''
            target = verbose_example.split('<div class="v2-sentence-source">',
                                           1)[0]
            target = target.split('\n', 1)[1].strip() + '\n'
            target = target.replace('<b>', '')
            target = target.replace('</b>', '')
            output_list.append(target)
        print('\n')
        print('\n')
        for num, sentence in enumerate(output_list):
            print(f'{num} - {sentence[:-1]}')
        print('\n')
        print('\n')
        userchoice = input('Enter the numbers of the examples above which you would like to save, separated by commas: ')
        while not is_valid_list(userchoice, output_list):
            userchoice = input('It seems what you entered is not valid.Please enter the numbers of the xamples you would like to save separated by commas: ')
        userchoice = userchoice.split(',')
        userchoice = [int(s) for s in userchoice]
        userchoice = set(userchoice)
        for num, example in enumerate(output_list):
            if num in userchoice:
                print(example)
                translation = input(
                    "Please enter a translation for the sentence above: "
                )

                satisfied = False
                while not satisfied:
                    print("\nyou entered:\n")
                    print(translation)
                    confirm = input("Is that correct? y/n: ")
                    while confirm != 'y' and confirm != 'n':
                        confirm = input(
                            "\ninvalid selection. Please enter y or n. ")
                    if confirm == 'y':
                        satisfied = True
                    else:
                        print(example)
                        translation = input(
                            "Please enter a translation for the sentence above: "
                        )
                l = ItemLoader(item=WordspiderItem(), response=response)
                l.add_value('example', example[:-1])
                l.add_value('translation', translation)
                yield l.load_item()
