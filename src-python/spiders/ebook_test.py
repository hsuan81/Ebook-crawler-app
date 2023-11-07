# coding=utf-8
import sys
import os
import ebooklib
from ebooklib import epub
from ebooklib.utils import debug


def create_epub(book_info, book_count=1):
    # logger.info("Creating EPUB file.")

    # Set the output path
    # output_dir = './output/' if output_path is None else output_path
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)
    # path = os.path.abspath(output_dir)


    # Set the book info
    book = epub.EpubBook()
    book.set_identifier(book_info['book_title'] + str(book_count))
    book.set_title(book_info['book_title'])
    book.add_author(book_info['book_author'])
    book.set_language('zh')

    return book

def save_epub(output_path, epub_chapters, book_info, book, book_counter):
    output_dir = output_path
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    path = os.path.abspath(output_dir) + f'/{book_info["book_title"]}({book_counter}).epub'
    # Add navigation files
    book.toc = epub_chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = 'body { font-family: Times, Times New Roman, serif; }'
    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Create spine
    book.spine = ['nav'] + epub_chapters

    # Write to EPUB file
    epub.write_epub(path, book)
    
if __name__ == '__main__':
    # book = epub.EpubBook()

    # # add metadata
    # book.set_identifier('sample123_save')
    # book.set_title('Sample book_save')
    # book.set_language('en')

    # book.add_author('Aleksandar Erkalovic')

    book = create_epub({'book_title': 'sample123_create2', 'book_author': 'Aleksandar Erkalovic'})

    # intro chapter
    c1 = epub.EpubHtml(title='Introduction',
                       file_name='intro.xhtml', lang='en')
    c1.content = '<html><head></head><body><h1>Introduction</h1><p>Introduction paragraph where i explain what is happening.</p></body></html>'

    # about chapter
    c2 = epub.EpubHtml(title='第2章 測試用', file_name='about.xhtml')
    c2.content = '<h1>第2章 測試用</h1><p>Helou, this is my book! There are many books, but this one is mine.</p>'

    c3 = epub.EpubHtml(title='第233章 測試用', file_name='chap23.xhtml')
    c3.content = '<h1>第233章 測試用</h1><p>Helou, this is my book! There are many books, but this one is mine.</p>'

    # add chapters to the book
    book.add_item(c1)
    book.add_item(c2)
    book.add_item(c3)

    chaps = [c1, c2, c3]

    save_epub('./', chaps, {'book_title': 'sample123_create2', 'book_author': 'Aleksandar Erkalovic'}, book, 1)

    # create table of contents
    # - add section
    # - add auto created links to chapters

#     book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'),
#                 (epub.Section('Languages'),
#                  (c1, c2, c3))
#                 )

#     # add navigation files
#     book.add_item(epub.EpubNcx())
#     book.add_item(epub.EpubNav())

#     # define css style
#     style = '''
# @namespace epub "http://www.idpf.org/2007/ops";

# body {
#     font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
# }

# h1 {
#      text-align: left;
#      text-transform: uppercase;
#      font-weight: 200;     
# }

# ol {
#         list-style-type: none;
# }

# ol > li:first-child {
#         margin-top: 0.3em;
# }


# nav[epub|type~='toc'] > ol > li > ol  {
#     list-style-type:square;
# }


# nav[epub|type~='toc'] > ol > li > ol > li {
#         margin-top: 0.3em;
# }

# '''

#     # add css file
#     nav_css = epub.EpubItem(
#         uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
#     book.add_item(nav_css)

#     # create spine
#     book.spine = ['nav', c1, c2, c3]

#     # create epub file
#     epub.write_epub('test.epub', book, {})
