import unittest
from unittest.mock import patch, MagicMock
from processor import get_requirements, extract_chapter_pages, extract_chapter_length, check_with_requirements

class TestThesisProcessing(unittest.TestCase):

    @patch('processor.get_text_from_bucket')
    def test_get_requirements(self, mock_get_text):
        mock_get_text.return_value = "Introduction: 5\nChapter 1: 10\nConclusion: 3"
        expected = {'Introduction': 5, 'Chapter 1': 10, 'Conclusion': 3}
        self.assertEqual(get_requirements(), expected)

    @patch('pdfplumber.open')
    def test_extract_chapter_pages(self, mock_pdf_open):
        # Create a mock PDF with predictable chapter headings
        mock_pdf = MagicMock()
        mock_pdf.pages = [MagicMock(), MagicMock(), MagicMock()]
        mock_pdf.pages[0].extract_text.return_value = "Chapter 1: Introduction\nSome text here..."
        mock_pdf.pages[1].extract_text.return_value = "Some intermediate text..."
        mock_pdf.pages[2].extract_text.return_value = "Chapter 2: Methodology\nMore text..."
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        expected = [{'title': 'TOTAL', 'page': 3}]
        self.assertEqual(extract_chapter_pages("dummy_file_path"), expected)

    def test_extract_chapter_length(self):
        mock_chapter_pages = [{'title': 'TOTAL', 'page': 50}, {'title': 'CHAPTER 1', 'page': 0}, {'title': 'CHAPTER 2', 'page': 20}]
        expected = [{'title': 'TOTAL', 'length': 50}, {'title': 'CHAPTER 1', 'length': 20}, {'title': 'CHAPTER 2', 'length': 30}]
        self.assertEqual(extract_chapter_length(mock_chapter_pages), expected)

    def test_check_with_requirements(self):
        requirements = {'CHAPTER 1': 15, 'CHAPTER 2': 25}
        chapter_length = [{'title': 'CHAPTER 1', 'length': 20}, {'title': 'CHAPTER 2', 'length': 30}]
        expected_result = ([{'title': 'CHAPTER 1', 'length': 20, 'status': 'Exceeded'}, {'title': 'CHAPTER 2', 'length': 30, 'status': 'Exceeded'}], 100)
        self.assertEqual(check_with_requirements(requirements, chapter_length), expected_result)

if __name__ == '__main__':
    unittest.main()
