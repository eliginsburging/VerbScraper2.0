# VerbScraper2.0
Scraping the internet to create stressed Russian vocabulary flashcards for Anki

The basic idea of this tool is fairly simple -- it takes one input (a list of Russian words in a text file) and (with user input along the way) generates a text file which can be uploaded to Anki to quickly create flashcards of example sentences (with stresses marked) containing those words. The tool also allows for manual entry of example sentences,which will automatically be stressed.

## The Input - toscrape.txt
This file should contain a list of Russian words on newlines. These are the target words for flashcard creation. A snippet from this file might look as follows:

**----------------------**<br>
говорить<br>
сказать<br>
покупать<br>
купить<br>
**----------------------**<br>
It should be noted that the words do not in principle have to be any specific part of speech or any particular form, though I would recommend using nominative singular forms for nouns and infinitives for verbs.

## The Output -- flashcards.txt
The end result of this process will be another text file. This file will contain example sentences with the words from toscrape.txt and translations of those example sentences. Each example sentence and its corresponding translation will appear on a single line separated by a semicolon. Stressed vowels in Russian words containing more than one vowel will be surrounded by html tags so that they appear in blue in the resulting Anki flashcard.
A snippet from this file might look as follows:

**----------------------**<br>
`Мы не см<font color='#0000ff'>е</font>ем говор<font color='#0000ff'>и</font>ть.;We dare not speak.`<br>
`Я <font color='#0000ff'>э</font>то сказ<font color='#0000ff'>а</font>л в м<font color='#0000ff'>а</font>рте.;I said that in March.`<br>
`Что вам сказ<font color='#0000ff'>а</font>ла хоз<font color='#0000ff'>я</font>йка?;What did the hostess tell you?`<br>
`Сначала никт<font color='#0000ff'>о</font> не хот<font color='#0000ff'>е</font>л покуп<font color='#0000ff'>а</font>ть дом — п<font color='#0000ff'>о</font>сле тог<font color='#0000ff'>о</font>, что случ<font color='#0000ff'>и</font>лось с н<font color='#0000ff'>а</font>ми.;At first no one wanted to buy a house -- after what happened to us.`<br>
`Знаешь, мне куп<font color='#0000ff'>и</font>ли пл<font color='#0000ff'>а</font>тье (летнее).;You know, they bought me a dress (for summer)`<br>
**----------------------**<br>

## What this tool *will* do
* Fetch approximately multiple example sentences per word you feed in from kartaslov.ru, display them in descending order of length, and allow you to choose which examples to use as flash cards.
* Prompt you to enter your own examples (optional)
* Fetch stresses for the words in the example sentences you choose/enter (from где-ударение.рф)
* Allow you to manually select the stresses for words which do not appear on где-ударение.рф

## What this tool *won't* do
* Translate the examples you select
  * you will be prompted to enter your own translations
* Choose which stress is appropriate in your selected examples when multiple stress options appear on где-ударение.рф
  * you will be prompted to select the stress variant appropriate to the example you selected
* Determine what stress is appropriate if a word does not appear on где-ударение.рф
  * you will be prompted to select the appropriate stress for such words
  
## A few caveats
* I have only tested this code on Manjaro Linux. Because the code relies on subprocesses and shell commands to run scrapy spiders (and ANSI escape codes to color terminal output), I cannot guarantee that it will work on Mac or Windows.
* This tool relies on two packages which are not in the standard python library -- Scrapy and Pyfiglet. I recommend you install requirements.txt in a virtual environment.
* This tool can retrieve information from the websites noted above. What you choose to do with that inforamtion after it has been retrieved is your responsibility. I do not advocate publishing shared decks based on Anki cards created with this tool. This tool was developed to automate a process I was previously carrying out manually to create a personal deck. I have not published any cards gathered with this tool apart from the examples listed in this readme file above.

## Instructions for use
* Install scrapy and pyfiglet (preferably in a virtual environment)
* Place desired target words on new lines in a file named toscrape.txt (as described above).
  * This file should be in the same directory as loom.py
* Within your terminal (with your virtual environment activated) run loom.py
* Follow the prompts.
* Once the process has completed, use Anki's ["Import File"](https://apps.ankiweb.net/docs/manual.html#importing-text-files) feature to upload flashcards.txt.
  * **Make sure to select the "Allow HTML in fields" option** in Anki's upload dialog
  * Anki should automatically recongize that the examples and translations are separated by semicolons
