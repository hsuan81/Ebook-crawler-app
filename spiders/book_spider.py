import requests
from bs4 import BeautifulSoup
import logging
import os
from ebooklib import epub

# 設定日誌
if not os.path.exists('logs'):
    os.makedirs('logs')
logging.basicConfig(filename='logs/spider.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def fetch_book_info(book_url):
    logger.info(f"Fetching book info from URL: {book_url}")
    response = requests.get(book_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    book_title = soup.select_one('.block_txt2 h2 a').text
    book_author = soup.select_one('.block_txt2 p a').text

    return {'book_title': book_title, 'book_author': book_author}


def fetch_chapters_list(book_url):
    logger.info(f"Fetching chapters list from URL: {book_url}")
    response = requests.get(book_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    # chapter_tags = soup.find_all('ul', attrs={'id': None, 'class': 'chapter'})

    chapter_tags = soup.select('ul.chapter > li > a')
    # print(chapter_tags)
    chapters = []
    for tag in chapter_tags:
        chapter_name = tag.text
        chapter_url = 'https://m.bqg9527.com' + tag['href']
        chapters.append((chapter_name, chapter_url))
    return chapters


def fetch_chapter_content(chapter_url):
    logger.info(f"Fetching content from chapter URL: {chapter_url}")
    response = requests.get(chapter_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    content = soup.select_one('#nr1')
    result = soup.select_one('#nr1')

    # 获取div内容并按<br><br>分隔
    # lines = str(content).split('<br><br>')

    # 删除每行开头的&nbsp;和其他HTML标签
    # processed_lines = [BeautifulSoup(line, 'html.parser').text.replace(
    #     '\xa0', '').strip() for line in lines]

    # 合并所有行并输出
    # result = '<br><br>'.join(processed_lines)
    return result


def create_epub(book_info, chapters):
    logger.info("Creating EPUB file.")
    book = epub.EpubBook()
    book.set_identifier('sample123456')
    book.set_title(book_info['book_title'])
    book.add_author(book_info['book_author'])
    book.set_language('zh')

    # Adding chapters to the book
    epub_chapters = []
    for title, content in chapters:
        content = f'<h1>{title}</h1><p>{content}</p>'
        c = epub.EpubHtml(title=title, file_name=title +
                          '.xhtml', content=content)
        book.add_item(c)
        epub_chapters.append(c)

    # # Add navigation files
    book.toc = epub_chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # # Define CSS style
    style = 'body { font-family: Times, Times New Roman, serif; }'
    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # # Create spine
    book.spine = ['nav'] + epub_chapters
    # Compile the book
    output_dir = './output/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    path = os.path.abspath(output_dir)
    print(path)
    epub.write_epub(path + f'/{book_info["book_title"]}.epub', book, {})


def main():
    book_url = 'https://m.bqg9527.com/zh_hant/book/118028/'
    book_info = fetch_book_info(book_url)
    chapters_info = fetch_chapters_list(book_url)
    chapters = []
    # # Testing
    # for n in range(10):
    #     title = chapters_info[n][0]
    #     url = chapters_info[n][1]
    #     content = fetch_chapter_content(url)
    #     chapters.append((title, content))

    # Production
    for title, url in chapters_info:
        content = fetch_chapter_content(url)
        chapters.append((title, content))

    create_epub(book_info, chapters)
    # create_epub('Sample eBook', chapters)
    logger.info("Ebook creation process completed.")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
