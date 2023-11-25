# coding=utf-8
import requests
import sys
import os
import re
import ebooklib
from ebooklib import epub
from ebooklib.utils import debug
from bs4 import BeautifulSoup
from diskcache import Deque, Index


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}



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

def fetch_chapters_list(book_url):
    print(f"Fetching chapters list from URL: {book_url}")
    response = requests.get(book_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    chapter_tags = soup.select(
        'ul.chapter[id!="last12"] > li > a[href!="#header"]')
    
    
    # urls = Deque(chapter_tags, 'data/urls')
    results = Index('data/results')
    # url = urls.popleft()
    
    for tag in chapter_tags:
        # try:
        #     url = urls.popleft()
        # except IndexError:
        #     break
        # print("tag", tag)
        chapter_url = 'https://m.bqg9527.com' + tag['href']
        chapter_name = tag.text
        # print(chapter_name)
        match = re.search(r"\d+", chapter_name)
        if match:
            chapter_number = int(match.group())
            # print(chapter_number, chapter_number)

        else:
            continue
        if chapter_number and chapter_number in results.keys():
            # print("duplicate", chapter_name)
            continue

        # urls.append(chapter_url)
        # print("Adding chapter name...", chapter_url, chapter_name)

        results[chapter_number] = (chapter_name, chapter_url)
    print(f"The number of chapters list from URL: {len(results)}")
    for key in results.keys():
        if key > int(len(results)):
            # print("delete", key)
            del results[key]
    print(f"The final number of chapters list from URL: {len(results)}")
    # results.clear()

    return len(results)

def chapters_to_update(book_url, path=None):
    # last_title = get_last_chapter_title_epub(path)
    last_title = "第104章"
    last_chapter_match = int(re.search(r'\d+', last_title).group(0))
    number_of_chapter = fetch_chapters_list(book_url)
    print(f"Last chapter title of the Epub file: {last_title}")
    print(last_chapter_match, number_of_chapter)
    # print(f"Latest chapter title from web: {latest_title}")
    # print(f"The two titles are the same: {last_title == latest_title}")
    # print(f"The two titles are different: {last_title != latest_title}")
    # if last_title != latest_title:
    if last_chapter_match != number_of_chapter:
        # return abs(last_chapter_match - number_of_chapter)
        # print(abs(last_chapter_match - number_of_chapter))
        return True, last_chapter_match
        # parse to get number and calculate how many chapters need to be added
        # last_chapter_match = re.search(r'\d+', last_title)
        # latest_chapter_match = re.search(r'\d+', latest_title)
        # if last_chapter_match and latest_chapter_match:
        #     last_chapter_number = int(
        #         last_chapter_match.group(0))  # 获取匹配到的数字字符串
        #     latest_chapter_number = int(
        #         latest_chapter_match.group(0))  # 将字符串转为整数
        #     logger.info(f"chapter number: {last_chapter_number} vs {latest_chapter_number}")
        #     diff = last_chapter_number-latest_chapter_number
        #     logger.info(f"difference: {diff}")
        #     return abs(diff)
        # else:
        #     logger.info(
        #         "Calculate chapters to update: No chapter number found.")
    else:
        return False, 0
        # print(0)

def fetch_one_chapter_content(chapter_url):
    # logger.info(f"Fetching content from chapter URL: {chapter_url}")
    response = requests.get(chapter_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    content = soup.select_one('#nr1')
    result = soup.select_one('#nr1')

    return result

    
def get_epub(book_url, epub_path=None, callback=None):
    # book_info = fetch_book_info(book_url)
    # chapters_info = fetch_chapters_list(book_url)
    total_chapters = fetch_chapters_list(book_url)
    chapters_info = Index('data/results')
    # ordered_chapters = sorted(chapters_info.items())
    
    # total_chapters = len(chapters_info)
    chapters = []
    # # Testing
    # for n in range(10):
    #     title = chapters_info[n][0]
    #     url = chapters_info[n][1]
    #     content = fetch_one_chapter_content(url)
    #     chapters.append((title, content))

    # # Production
    # for idx, (title, url) in enumerate(chapters_info):
    #     content = fetch_one_chapter_content(url)
    #     chapters.append((title, content))
    idx = 0
    # for (url, title) in chapters_info.popitem(last=False):
    for key in sorted(chapters_info.keys()):
        title, url = chapters_info[key]
        print(title, url)
        content = fetch_one_chapter_content(url)
        chapters.append((title, content))
        idx += 1
        # Use callback function to update progress for display on the client side
        # if callback:
        #     progress = ((idx + 1) / total_chapters) * 100  # calculate the Ebook complete percentage
        #     callback(
        #         f"Downloading chapter {idx+1} of {total_chapters}, {progress:.2f}% complete")
    print(len(chapters))
    print(chapters[0])
    print(chapters[-1])
    chapters_info.clear()

def update_epub(book_url):
    # if callback:
    #     callback("Checking new chapters...")

    to_update, chapter_num = chapters_to_update(book_url)
    # print(f"Number of chapters to update: {number_to_update}")
    print(to_update, chapter_num)

    # Start to update the ebook if new chapters are available on the web
    if to_update:
        # if callback:
        #     callback("Fetching new chapters...")

        # chap_list = fetch_chapters_list(book_url)
        chap_list = Index('data/results')
        # logger.info(f"First chapter in the list: {chap_list[0][0]}")

        # Slice the list with only new chapters left
        # chap_list_to_update = chap_list[-abs(number_to_update)::1]
        chap_list_to_update = [chap_list[key] for key in sorted(chap_list.keys()) if key > chapter_num]
        print(len(chap_list_to_update))
        print(chap_list_to_update[0])
        print(chap_list_to_update[-1])
        
        # logger.info(f"Total number of chapters to update: {len(chap_list_to_update)}")
        # logger.info(f"First chapter to update: {chap_list_to_update[0][0]}")

        # Fetch title and content of the chapters for update
        chap_content_to_update = []
        for idx, (title, url) in enumerate(chap_list_to_update):
            pass
            # print(url)
            # content = fetch_one_chapter_content(url)
            # chap_content_to_update.append((title, content))
        print("finished")


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
    # fetch_chapters_list('https://m.bqg9527.com/zh_hant/book/118028/')
    # get_epub('https://m.bqg9527.com/zh_hant/book/118028/')
    # chapters_to_update('https://m.bqg9527.com/zh_hant/book/118028/')
    update_epub('https://m.bqg9527.com/zh_hant/book/118028/')
    
if __name__ == '__test__':
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
