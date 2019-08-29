import unittest
import helpers
from helpers import vowels

class TestHelper(unittest.TestCase):

    def test_input_isvalid(self):
        testlist = [i for i in range(5)]
        for a in range(1, 6):
            self.assertTrue(helpers.input_isvalid(str(a), testlist))
        self.assertFalse(helpers.input_isvalid('a', testlist))
        self.assertFalse(helpers.input_isvalid('7', testlist))
        self.assertFalse(helpers.input_isvalid('-3', testlist))

    def test_yesno_isvalid(self):
        self.assertTrue(helpers.yesno_isvalid('y'))
        self.assertTrue(helpers.yesno_isvalid('n'))
        self.assertTrue(helpers.yesno_isvalid('N'))
        self.assertTrue(helpers.yesno_isvalid('Y'))
        self.assertFalse(helpers.yesno_isvalid(''))
        self.assertFalse(helpers.yesno_isvalid('a'))

    def test_color_stress(self):
        scraped = ('''<div class="rule ">\n\t\n\t\t В таком варианте '''
                   '''ударение следует ставить на слог с буквой О — '''
                   '''г<b>О</b>ры. \n\t\t\t</div>''')
        self.assertEqual("""г<font color='#0000ff'>о</font>ры""",
                         helpers.color_stress(scraped))

    def test_man_stress(self):
        self.assertEqual(helpers.man_stress('cat', 1),
                         "c<font color='#0000ff'>a</font>t")
        self.assertEqual(helpers.man_stress('software', 5),
                         "softw<font color='#0000ff'>a</font>re")
        with self.assertRaises(AssertionError):
            helpers.man_stress('cat', 4)
        with self.assertRaises(AssertionError):
            helpers.man_stress('', 4)

    def test_needs_stress(self):
        self.assertTrue(helpers.needs_stress('города'))
        self.assertFalse(helpers.needs_stress(''))
        self.assertFalse(helpers.needs_stress('a'))
        self.assertFalse(helpers.needs_stress('ёлка'))
        self.assertTrue(helpers.needs_stress('Окно'))
        self.assertTrue(helpers.needs_stress('Южный'))

    def test_is_valid_list(self):
        self.assertTrue(
            helpers.is_valid_list('1,2,3', [1, 2, 3, 4])
        )
        self.assertTrue(
            helpers.is_valid_list('1, 2, 3', [1, 2, 3, 4])
        )
        self.assertFalse(
            helpers.is_valid_list('1,2,4', [1, 2])
        )
        self.assertFalse(
            helpers.is_valid_list('a;alkjdf', [1, 2, 3])
        )


if __name__ == '__main__':
    unittest.main()
