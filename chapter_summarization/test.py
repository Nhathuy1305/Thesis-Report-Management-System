import unittest
from processor import summarize_text, get_summaries

class TestProcessor(unittest.TestCase):

    def test_summarize_text(self):
        text = "This is a test text. It has multiple sentences. The purpose is to test the summarize_text function."
        summary = summarize_text(text)
        self.assertIsInstance(summary, str)

    def test_get_summaries(self):
        chapter_content = [
            ["Chapter 1", "This is the content of chapter 1."],
            ["Chapter 2", "This is the content of chapter 2."],
        ]
        summaries = get_summaries(chapter_content)
        self.assertIsInstance(summaries, str)

if __name__ == '__main__':
    unittest.main()