import scrapy
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider
from wordspider.items import WordspiderItem
from helpers import yesno_prompt, colors, is_valid_list


divider1 = colors.information("&" * 100)


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
                raise CloseSpider(
                    'Maxmimum iterations exceeded; while loop broken')
                break
            for num, sentence in enumerate(output_list):
                print(f'{num} - {sentence[:-1]}')
            print()
            userchoice = input(
                colors.prompt('Enter the numbers of the examples above which'
                              'you would like to save, separated by commas: ')
                )
            iter4 = 0
            while not is_valid_list(userchoice, output_list):
                iter4 += 1
                if iter4 > 1000:
                    raise CloseSpider(
                        'Maxmimum iterations exceeded; while loop broken')
                    break
                userchoice = input(
                    colors.warning(
                        'Invalid choice. Please enter the numbers of the '
                        'examples you would like to save separated by commas: '
                        ))
            userchoice = userchoice.split(',')
            userchoice = [int(s) for s in userchoice]
            userchoice = set(userchoice)
            # ask user to confirm
            print(colors.prompt("you selected:"))
            for num in userchoice:
                print(colors.parrot(f'{num} - {output_list[num]}'))
            if yesno_prompt(
                colors.prompt('Is that correct? y/n: '),
                colors.warning('Invalid entry. Please enter y or n: ')
            ):
                satisfied = True
        for num in userchoice:
            print()
            print(output_list[num])
            translation = input(
                colors.prompt(
                    "Please enter a translation for the sentence above: ")
            )

            satisfied = False
            iters3 = 0
            while not satisfied:
                iters3 += 1
                if iters3 > 1000:
                    raise CloseSpider(
                        'Maxmimum iterations exceeded; while loop broken')
                    break
                print()
                print(colors.prompt("you entered:"))
                print()
                print(colors.parrot(translation))

                if yesno_prompt(
                    'Is that correct? y/n: ',
                    'Invalid selection. Please enter y or n: '
                ):
                    satisfied = True
                else:
                    print(output_list[num])
                    translation = input(
                        colors.prompt(
                            'Please enter a translation for the sentence '
                            'above: ')
                    )
            l = ItemLoader(item=WordspiderItem(), response=response)
            l.add_value('example', output_list[num][:-1])
            l.add_value('translation', translation)
            yield l.load_item()
