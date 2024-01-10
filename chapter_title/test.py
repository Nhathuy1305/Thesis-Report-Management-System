import unittest
from processor import check_with_template

class TestProcessor(unittest.TestCase):
    def test_check_with_template(self):
        template_titles = ["Chapter 1: Introduction", "Chapter 2: Literature Review", "Chapter 3: Methodology"]
        chapter_titles = ["Chapter 1: Introduction", "Chapter 2: Literature Review", "Chapter 3: Methodology"]
        expected_result = ({}, [], 300)

        result = check_with_template(template_titles, chapter_titles)

        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()