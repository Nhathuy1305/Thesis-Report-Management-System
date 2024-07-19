import unittest
from processor import check_citations

class TestProcessor(unittest.TestCase):
    def test_check_citations(self):
        citations = [
            {'raw_ref': ['Smith (2020) https://example.com']},
            {'raw_ref': ['Smith. 2020.']},
            {'raw_ref': ['Smith 2020, https://example.com']},
            {'raw_ref': ['[1] Smith']},
            {'raw_ref': ['[1] https://example.com']}
        ]

        expected_result = [
            ("APA Style (Website)", 'Smith (2020) https://example.com'),
            ("MLA Style", 'Smith. 2020.'),
            ("MLA Style (Website)", 'Smith 2020, https://example.com'),
            ("IEEE Style", '[1] Smith'),
            ("IEEE Style (Website)", '[1] https://example.com')
        ]

        result = check_citations(citations)

        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()