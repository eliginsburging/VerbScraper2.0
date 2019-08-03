import scrapy


class WordSpider(scrapy.Spider):
    name = 'wordspider'

    def start_requests(self):
        urls = ['https://xn----8sbhebeda0a3c5a7a.xn--p1ai/%D0%B2-%D1%81%D0%BB%D0%BE%D0%B2%D0%B5-%D0%BF%D1%82%D0%B5%D0%BD%D0%B5%D1%86/', ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = 'ptenetsstress.txt'
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
