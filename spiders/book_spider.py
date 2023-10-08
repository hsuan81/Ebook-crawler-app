import requests
import logging
import io
import os
import re
from bs4 import BeautifulSoup
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

MAX_SIZE = 2 * 1024 * 1024


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

    chapter_tags = soup.select(
        'ul.chapter[id!="last12"] > li > a[href!="#header"]')
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


def get_chapter_size(chapter):
    book_temp = epub.EpubBook()
    book_temp.add_item(chapter)
    buffer = io.BytesIO()
    epub.write_epub(buffer, book_temp, {})
    size = buffer.tell()
    buffer.close()
    return size


def get_last_chapter_title_epub(path):
    book = epub.read_epub(path)

    # 獲取 spine 中的最後一個項目的 ID
    last_item_id = book.spine[-1][0]

    # 使用 ID 從書籍物件中獲取對應的項目
    last_item = book.get_item_with_id(last_item_id)

    # 返回項目（章節）的標題
    content = last_item.get_body_content().decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    h1_tag = soup.find('h1')  # 找到第一个<h1>标签

    if h1_tag:  # 确保找到了一个<h1>标签
        title = h1_tag.text  # 获取标签内的文本
        logger.info(f"Get last chapter title: Title is {title}")
        print(f"The title is: {title}")
    else:
        logger.info(f"Get last chapter title: No <h1> tag found.")
        print("No <h1> tag found.")
    return title


def get_latest_chapter_from_web(book_url):
    response = requests.get(book_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    latest_chapter = soup.select_one('p:-soup-contains("最新") a').text
    return latest_chapter


def calculate_chapters_to_update(book_url, path):
    last_title = get_last_chapter_title_epub(path)
    latest_title = get_latest_chapter_from_web(book_url)
    if last_title != latest_title:
        # parse to get number and calculate how many chapters need to be added
        # 使用正则表达式找到数字
        last_chapter_match = re.search(r'\d+', last_title)
        latest_chapter_match = re.search(r'\d+', last_title)

        if last_chapter_match and latest_chapter_match:
            last_chapter_number = int(
                last_chapter_match.group(0))  # 获取匹配到的数字字符串
            latest_chapter_number = int(
                latest_chapter_match.group(0))  # 将字符串转为整数
            return abs(last_chapter_number, latest_chapter_number)
        else:
            logger.info(
                "Calculate chapters to update: No chapter number found.")
            print("No chapter number found.")
    else:
        return 0


def save_epub(path, epub_chapters, book):
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
    epub.write_epub(path, book, {})


def create_epub(book_info, chapters):
    logger.info("Creating EPUB file.")

    # Set the output path
    output_dir = './output/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    path = os.path.abspath(output_dir)

    # Set the counter of the book to create
    book_counter = 1
    current_size = 0

    # Set the book info
    book = epub.EpubBook()
    book.set_identifier(book_info['book_title']+book_counter)
    book.set_title(book_info['book_title'])
    book.add_author(book_info['book_author'])
    book.set_language('zh')

    # Adding chapters to the book
    epub_chapters = []
    for title, content in chapters:
        chapter_size = get_chapter_size(content)
        if current_size + chapter_size > MAX_SIZE:
            # epub.write_epub(
            # path + f'/{book_info["book_title"]}({book_counter}).epub', book, {})
            save_epub(
                path + f'/{book_info["book_title"]}({book_counter}).epub', epub_chapters, book)
            book_counter += 1
            book = epub.EpubBook()
            book.set_identifier(book_info['book_title']+book_counter)
            book.set_title(book_info['book_title'])
            book.add_author(book_info['book_author'])
            book.set_language('zh')
            epub_chapters = []
            current_size = 0
        content = f'<h1>{title}</h1><p>{content}</p>'
        c = epub.EpubHtml(title=title, file_name=title +
                          '.xhtml', content=content)
        book.add_item(c)
        epub_chapters.append(c)
        current_size += chapter_size

    # # Add navigation files
    # book.toc = epub_chapters
    # book.add_item(epub.EpubNcx())
    # book.add_item(epub.EpubNav())

    # # Define CSS style

    # # Create spine

    # Compile the book

    if book.items:
        save_epub(
            path + f'/{book_info["book_title"]}({book_counter}).epub', epub_chapters, book)


# def update_epub(book_url, path):
#     number_to_update = calculate_chapters_to_update(path)
#     if number_to_update > 0:
#         fetch_chapters_list(book_url)


def main(params, callback=None):
    # Get params
    action = params.get("action")
    epub_path = params.get("epub_path")
    input_path = params.get("input_path")

    book_url = 'https://m.bqg9527.com/zh_hant/book/118028/'

    if action == "get":
        book_info = fetch_book_info(book_url)
        chapters_info = fetch_chapters_list(book_url)
        total_chapters = len(chapters_info)
        chapters = []
    # # Testing
    # for n in range(10):
    #     title = chapters_info[n][0]
    #     url = chapters_info[n][1]
    #     content = fetch_chapter_content(url)
    #     chapters.append((title, content))

    # Production
        for idx, (title, url) in enumerate(chapters_info):
            content = fetch_chapter_content(url)
            chapters.append((title, content))

            # 這裡使用回調函數來更新進度
            if callback:
                progress = ((idx + 1) / total_chapters) * 100  # 計算進度百分比
                callback(
                    f"Downloading chapter {idx+1} of {total_chapters}, {progress:.2f}% complete")

        create_epub(book_info, chapters)
        # create_epub('Sample eBook', chapters)
        logger.info("Ebook creation process completed.")

    elif action == "update":
        print("update")
        # epub_count = get_epub_chapter_count(epub_path)
        # web_count = get_website_chapter_count(book_url)

        # if epub_count == web_count:
        #     eel.show_status("The ebook is already up-to-date.")
        # else:
        #     eel.show_status("Updating ebook...")
        #     update_epub(epub_path, book_url)
        #     eel.show_status("Update complete.")


def test():
    print("Start")
    html = """
    <html>
    <head></head>
    <body>
    <div class="block">
        <div class="block_img2"><img alt="上門龍婿" src="/files/article/image/118/118028/118028s.jpg" border="0" width="100" height="130"></div>
        <div class="block_txt2">
            <h2><a>上門龍婿</a></h2>
            <p>作者：<a href="/zh_hant/author/葉辰/">葉辰</a></p>
            <p>分類：<a href="/zh_hant/sort/3/">都市言情</a></p>
            <p>狀態：連載中</p>
            <p>更新：2023-09-15</p>
            <p>最新：<a href="209265592.html">第2874章 送給公子的禮物</a></p>
        </div>
    </div>
    </body>
    </html>
    """
    soup = BeautifulSoup(html, 'lxml')
    print("setup soup")
    print(soup.select_one('p:-soup-contains("最新") a').text)


if __name__ == '__main__':
    try:
        main()
        # test()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
