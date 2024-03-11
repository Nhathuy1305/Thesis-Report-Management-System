import unittest
from unittest.mock import patch, MagicMock
import processor

class TestDocumentProcessing(unittest.TestCase):

    @patch('pdfplumber.open')
    def test_extract_figure_titles(self, mock_pdf_open):
        # Mock pdfplumber open and its returned object
        mock_pdf = MagicMock()
        mock_pdf.pages = [MagicMock(), MagicMock()]
        # Mock the text on each page
        mock_pdf.pages[0].extract_text.return_value = "Some text with contents"
        mock_pdf.pages[1].extract_text.return_value = "Figure 1: Example"
        # Mock image data
        mock_pdf.pages[1].images = [{'x0': 0, 'bottom': 100, 'x1': 200, 'top': 0}]
        # Mock title_crop to return a string
        title_crop_mock = MagicMock()
        title_crop_mock.extract_text.return_value = "Figure 1: Example"
        # Set within_bbox to return the mocked title_crop
        mock_pdf.pages[1].within_bbox.return_value = title_crop_mock
        # Return the mock pdf object when pdfplumber.open is called
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        expected = ["Figure 1: Example"]
        result = processor.extract_figure_titles("dummy_file_path")
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()