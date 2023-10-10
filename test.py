import unittest
from unittest.mock import patch, MagicMock
import ebooklib
from ebooklib import epub
import spiders.book_spider as spider


class TestSpider(unittest.TestCase):
    
    def setUp(self):
        self.mocks = [patch('spiders.book_spider.fetch_book_info', MagicMock(return_value={'book_title': 'Title 1', 'book_author': 'Author 1'})),
                      patch('spiders.book_spider.fetch_chapters_list', MagicMock(return_value=[("第2章 測試1-1", "https://example.com.tw/2"), ("第33章 測試1-2", "https://example.com.tw/33")])),
                      patch('spiders.book_spider.fetch_one_chapter_content'), MagicMock(return_value='<p>Helou, this is my book! There are many books, but this one is mine.</p>')]  # fixed value
        for mock in self.mocks:
            mock.start()
    # def test_get_epub_last_chap_title(self):
    #     """
    #     Test that it can get the last chapter title of ebook
    #     """
    #     result = spider.get_last_chapter_title_epub("./test.epub")
    #     self.assertEqual(result, '第233章 測試用')

    
    # def test_get_epub(self):
    #     """
    #     Test that it can successfully create an epub file
    #     """
    #     spider.get_epub('book_url.com.tw', './')
    
    # @patch('spiders.book_spider.get_chapter_size')
    # def test_get_epub_over_limit(self, mock_get_chapter_size):
    #     """
    #     Test that it can create a new epub file if the size of the existing epub file is beyond limit.
    #     """
    #     mock_get_chapter_size.return_value = 2 * 1024 * 1024

    #     spider.get_epub('book_url.com.tw', './')

    @patch('spiders.book_spider.get_latest_chapter_from_web')
    @patch('spiders.book_spider.get_last_chapter_title_epub')
    def test_update_epub(self, mock_get_last_chapter_title_epub, mock_get_latest_chapter_from_web):
        mock_get_last_chapter_title_epub.return_value = '第2章'
        mock_get_latest_chapter_from_web.return_value = '第3章'
        spider.update_epub('book_url.com.tw', './', './Title 1(1).epub')

        book = epub.read_epub('./Title 1(1).epub')
        gen = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        # result = len(docs)
        docs = []
        for doc in gen:
            docs.append(doc.get_name())
        self.assertEqual(docs[0], '第2章 測試1-1.xhtml')
        self.assertEqual(docs[1], '第33章 測試1-2.xhtml')
        # self.assertEqual(result, 2)




    def tearDown(self):
        for mock in self.mocks:
            mock.stop()

if __name__ == '__main__':
    unittest.main()