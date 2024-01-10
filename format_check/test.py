import unittest
from unittest.mock import patch, MagicMock
from processor import get_template, extract_chapter_titles, extract_section_titles

class TestProcessor(unittest.TestCase):
    @patch('processor.get_text_from_bucket')
    def test_get_template(self, mock_get_text_from_bucket):
        mock_get_text_from_bucket.return_value = "Chapter 1: Introduction\nChapter 2: Literature Review\nChapter 3: Methodology"
        result = get_template()
        self.assertEqual(result, ["Chapter 1: Introduction", "Chapter 2: Literature Review", "Chapter 3: Methodology"])

    @patch('pdfplumber.open')
    def test_extract_chapter_titles(self, mock_pdfplumber_open):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = 'Chapter 1: Introduction\nChapter 2: Literature Review\nChapter 3: Methodology'
        mock_pdf = mock_pdfplumber_open.return_value.__enter__.return_value
        mock_pdf.pages = [mock_page]
        result = extract_chapter_titles('dummy.pdf')
        self.assertEqual(result, [])  

    @patch('pdfplumber.open')
    def test_extract_section_titles(self, mock_pdfplumber_open):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = '1.1 Section One\n1.2 Section Two\n1.3 Section Three'
        mock_pdf = mock_pdfplumber_open.return_value.__enter__.return_value
        mock_pdf.pages = [mock_page]
        result = extract_section_titles('dummy.pdf')
        self.assertEqual(result, ['1.1 Section One', '1.2 Section Two']) 

if __name__ == '__main__':
    unittest.main()