import unittest
from unittest.mock import patch, MagicMock
import re
from ebooklib import epub
from ebooklib import ITEM_NAVIGATION, ITEM_STYLE
import spiders.book_spider as spider

"""
Don't run all tests in one go, some are dependent on some existing Ebook.
Make sure you have it before running the test, or you can modify it to test on Ebook of other name.
"""

class TestSpider(unittest.TestCase):
    
    def setUp(self):
        self.mocks = [patch('spiders.book_spider.fetch_book_info', MagicMock(return_value={'book_title': 'Title 1', 'book_author': 'Author 1'})),
                      patch('spiders.book_spider.fetch_chapters_list', MagicMock(return_value=[("第2章 測試1-1", "https://example.com.tw/2"), ("第33章 測試1-2", "https://example.com.tw/33")])),
                      patch('spiders.book_spider.fetch_one_chapter_content'), MagicMock(return_value='<p>Helou, this is my book! There are many books, but this one is mine.</p>')]  # fixed value
        for mock in self.mocks:
            mock.start()
    def test_get_epub_last_chap_title(self):
        """
        Test that it can get the last chapter title of ebook
        """
        result = spider.get_last_chapter_title_epub("./test.epub")
        self.assertEqual(result, '第233章 測試用')

    def test_get_last_chapter_id(self):
        """
        Test that it can get the id of the last chapter
        """
        book = epub.read_epub("./Title 1(1).epub")
        result = spider.get_last_chapter_id_number(book)
        self.assertEqual(result, 0)

    def test_remove_nav_and_style_items(self):
        """
        Test that it can successfully remove navigation and style files
        """
        book = epub.read_epub("./Title 1(2)test.epub")
        spider.remove_nav_and_style_items(book)
        
        # new_book = epub.read_epub("./Title 1(2)nav_removed.epub")
        ncx_items = list(book.get_items_of_type(ITEM_NAVIGATION))
        style_items = list(book.get_items_of_type(ITEM_STYLE))
        nav_item = book.get_item_with_id('nav')
        epub.write_epub('./Title 1(2)nav_removed.epub', book)
        self.assertTrue(len(ncx_items) == 0)
        self.assertTrue(len(style_items) == 0)
        self.assertIsNone(nav_item)

    def test_create_and_transfer_from_old_book(self):
        book = epub.read_epub("./Sample book_save(1).epub")
        book_title = book.get_metadata('DC', 'title')[0][0]
        book_author = book.get_metadata('DC', 'creator')[0][0]
        book_info = {"book_title": book_title, "book_author": book_author}
        book_count = 1

        new_book = spider.create_and_transfer_from_old_book(book, book_info, book_count)
        new_book.add_item(epub.EpubNcx())
        new_book.add_item(epub.EpubNav())
        epub.write_epub("./Sample book_save(1)transfer.epub", new_book)

        # Ensure the title and author are the same as the source book
        created_title = new_book.get_metadata('DC', 'title')[0][0]
        created_author = new_book.get_metadata('DC', 'creator')[0][0]

        self.assertEqual(created_title, book_title)
        self.assertEqual(created_author, book_author)
        
        # Ensure id assigned to the chapter is tha same as the source book
        book_item0 = book.get_item_with_id('chapter_0')
        created_item0 = new_book.get_item_with_id('chapter_0')
        book_item1 = book.get_item_with_id('chapter_1')
        created_item1 = new_book.get_item_with_id('chapter_1')

        self.assertEqual(created_item0.get_name(), book_item0.get_name())
        self.assertEqual(created_item1.get_name(), book_item1.get_name())

        # After the book is written to a file, the items in the spine will be transformed to tuple from EpubHtml object
        # self.assertEqual(new_book.spine, book.spine)
        
        # EpubBook._id_html will be reset as 0 once the book is written to file. 
        # Before that, EpubBook._id_html will increase by 1 as new Epubhtml is added to the book
        created = epub.read_epub('./Sample book_save(1)transfer.epub')
        self.assertEqual(created._id_html, book._id_html)
        # self.assertEqual(new_book._id_html, book._id_html)

    def test_get_epub(self):
        """
        Test that it can successfully create an epub file
        """
        spider.get_epub('book_url.com.tw', './')
    
    @patch('spiders.book_spider.get_chapter_size')
    def test_get_epub_over_limit(self, mock_get_chapter_size):
        """
        Test that it can create a new epub file if the size of the existing epub file is beyond limit.
        """
        mock_get_chapter_size.return_value = 2 * 1024 * 1024

        spider.get_epub('book_url.com.tw', './')

    @patch('spiders.book_spider.get_latest_chapter_from_web')
    @patch('spiders.book_spider.get_last_chapter_title_epub')
    def test_update_epub(self, mock_get_last_chapter_title_epub, mock_get_latest_chapter_from_web):
        mock_get_last_chapter_title_epub.return_value = '第2章'
        mock_get_latest_chapter_from_web.return_value = '第3章'
        spider.update_epub('book_url.com.tw', './', './Title 1(1).epub')

        book = epub.read_epub('./Title 1(1).epub')
        gen = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        gen_list = list(gen)
        # docs.remove('nav.xhtml')
        chap_num = len(gen_list)
        self.assertEqual("第2章", "第3章")
        self.assertEqual(chap_num, 2)
        docs = []
        for doc in gen:
            docs.append(doc.get_name())
        self.assertEqual(docs[0], '第2章 測試1-1.xhtml')
        self.assertEqual(docs[1], '第33章 測試1-2.xhtml')




    def tearDown(self):
        for mock in self.mocks:
            mock.stop()

if __name__ == '__main__':
    unittest.main()