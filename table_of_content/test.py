import unittest
from unittest.mock import patch, MagicMock
import processor

class TestDocumentProcessing(unittest.TestCase):

    @patch('processor.pdfplumber.open')
    def test_extract_chapter_titles(self, mock_pdf_open):
        # Setup mock PDF content
        mock_pdf = MagicMock()
        mock_pdf.pages = [MagicMock()]
        mock_pdf.pages[0].extract_text.return_value = "Chapter 1 Introduction to Testing\nSome content here"
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        expected = [{'title': 'CHAPTER 1', 'page': 0}]
        result = processor.extract_chapter_titles("dummy_file_path")
        self.assertEqual(result, expected)


    def test_check_chapter_titles(self):
        chapter_titles = [{'title': 'CHAPTER 1', 'page': 1}]
        table_chapter_titles = [{'title': 'CHAPTER 1', 'page': 1}, {'title': 'CHAPTER 2', 'page': 5}]
        expected_result = ([], {'CHAPTER 1': False})  # Updated expected result
        result = processor.check_chapter_titles(chapter_titles, table_chapter_titles)
        self.assertEqual(result, expected_result)



if __name__ == '__main__':
    unittest.main()
