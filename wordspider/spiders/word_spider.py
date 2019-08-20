import scrapy
import os
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider
from wordspider.items import WordspiderItem
from wordspider.spiders.stressspider import yesno_isvalid


class colors:
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    magenta = "\033[35m"
    cyan = "\033[36m"
    white = "\033[37m"
    reset = "\033[0m"


divider1 = colors.green + ("&" * 100) + colors.reset


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
    custom_settings = {
        'FEED_URI': 'examples.csv'
    }

    def start_requests(self):
        with open('toscrape.txt', 'r') as f:
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
        print(divider1)
        print(divider1)
        satisfied = False
        iters = 0
        while not satisfied:
            iters += 1
            if iters > 1000:
                raise CloseSpider('Maxmimum iterations exceeded; while loop broken')
                break
            for num, sentence in enumerate(output_list):
                print(f'{num} - {sentence[:-1]}')
            print()
            userchoice = input(colors.cyan + 'Enter the numbers of the examples above which you would like to save, separated by commas: ' + colors.reset)
            iter4 = 0
            while not is_valid_list(userchoice, output_list):
                iter4 += 1
                if iter4 > 1000:
                    raise CloseSpider('Maxmimum iterations exceeded; while loop broken')
                    break
                userchoice = input(colors.cyan + 'Invalid choice. Please enter the numbers of the xamples you would like to save separated by commas: ' + colors.reset)
            userchoice = userchoice.split(',')
            userchoice = [int(s) for s in userchoice]
            userchoice = set(userchoice)
            # ask user to confirm
            print(colors.cyan + "you selected:" + colors.reset)
            for num in userchoice:
                print(colors.yellow +
                      f'{num} - {output_list[num]}' +
                      colors.reset)
            examplesok = input('\n' +
                               colors.cyan +
                               "Is that correct? y/n: " +
                               colors.reset)
            iters2 = 0
            while not yesno_isvalid(examplesok):
                iters2 += 1
                if iters2 > 1000:
                    raise CloseSpider('Maxmimum iterations exceeded; while loop broken')
                    break
                examplesok = input(colors.cyan +
                                   "Invalid entry. Please enter y or n: " +
                                   colors.reset)
            if examplesok in "yY":
                satisfied = True
        for num in userchoice:
            print()
            print(output_list[num])
            translation = input(
                colors.cyan +
                "Please enter a translation for the sentence above: " +
                colors.reset
            )

            satisfied = False
            iters3 = 0
            while not satisfied:
                iters3 += 1
                if iters3 > 1000:
                    raise CloseSpider('Maxmimum iterations exceeded; while loop broken')
                    break
                print("\nyou entered:\n")
                print(colors.yellow + translation + colors.reset)
                confirm = input(
                    colors.cyan + "Is that correct? y/n: " + colors.reset)
                iter5 = 0
                while not yesno_isvalid(confirm):
                    iter5 += 1
                    if iter5 > 1000:
                        raise CloseSpider('Maxmimum iterations exceeded; while loop broken')
                        break
                    confirm = input(
                        "\n" +
                        colors.cyan +
                        "invalid selection. Please enter y or n. " +
                        colors.reset)
                if confirm in 'yY':
                    satisfied = True
                else:
                    print(output_list[num])
                    translation = input(
                        colors.cyan +
                        "Please enter a translation for the sentence above: " +
                        colors.reset
                    )
            l = ItemLoader(item=WordspiderItem(), response=response)
            l.add_value('example', output_list[num][:-1])
            l.add_value('translation', translation)
            yield l.load_item()
