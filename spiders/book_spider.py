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

def append_chapters_to_epub(epub_path, new_chapters):
    book = epub.read_epub(epub_path)
    
    # 循環添加新章節
    for title, content in new_chapters:
        c = epub.EpubHtml(title=title, file_name=f"{title}.xhtml", lang="hr")
        c.content = f'<h1>{title}</h1><p>{content}</p>'
        book.add_item(c)
    
    # 重新保存書籍
    epub.write_epub(epub_path, book)


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


def fetch_one_chapter_content(chapter_url):
    logger.info(f"Fetching content from chapter URL: {chapter_url}")
    response = requests.get(chapter_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    content = soup.select_one('#nr1')
    result = soup.select_one('#nr1')

    return result


def get_chapter_size(chapter):
    book_temp = epub.EpubBook()
    epubhtml = epub.EpubHtml(title='Temp', file_name='temp.xhtml', content=chapter)
    book_temp.add_item(epubhtml)
    buffer = io.BytesIO()
    epub.write_epub(buffer, book_temp)
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
            return abs(last_chapter_number-latest_chapter_number)
        else:
            logger.info(
                "Calculate chapters to update: No chapter number found.")
            print("No chapter number found.")
    else:
        return 0


def save_epub(output_path, epub_chapters, book_info, book, book_counter):
    logger.info("Saving EPUB file.")
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
    logger.info(f"Epub file is saved at {path}.")

def save_updated_epub(output_path, epub_chapters, book_info, book, book_counter):
    logger.info("Saving updated EPUB file.")
    output_dir = output_path
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    path = os.path.abspath(output_dir) + f'/{book_info["book_title"]}({book_counter}).epub'
    # Add navigation files
    book.toc.extend(epub_chapters)
    # book.add_item(epub.EpubNcx())
    # book.add_item(epub.EpubNav())

    # Define CSS style
    # style = 'body { font-family: Times, Times New Roman, serif; }'
    # nav_css = epub.EpubItem(
    #     uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    # book.add_item(nav_css)

    # Update spine
    book.spine.extend(epub_chapters)
    print(book.spine)

    # Write to EPUB file
    epub.write_epub(path, book)
    logger.info(f"Updated Epub file is saved at {path}.")


def create_epub(book_info, book_count=1):
    logger.info("Creating EPUB file.")

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
    
    # Adding chapters to the book
    # epub_chapters = []
    # for title, content in chapters:
    #     chapter_size = get_chapter_size(content)
    #     if current_size + chapter_size > MAX_SIZE:
    #         # epub.write_epub(
    #         # path + f'/{book_info["book_title"]}({book_counter}).epub', book, {})
    #         save_epub(
    #             path + f'/{book_info["book_title"]}({book_counter}).epub', epub_chapters, book)
    #         book_counter += 1
    #         book = epub.EpubBook()
    #         book.set_identifier(book_info['book_title']+book_counter)
    #         book.set_title(book_info['book_title'])
    #         book.add_author(book_info['book_author'])
    #         book.set_language('zh')
    #         epub_chapters = []
    #         current_size = 0
    #     content = f'<h1>{title}</h1><p>{content}</p>'
    #     c = epub.EpubHtml(title=title, file_name=title +
    #                       '.xhtml', content=content)
    #     book.add_item(c)
    #     epub_chapters.append(c)
    #     current_size += chapter_size

    # # Add navigation files
    # book.toc = epub_chapters
    # book.add_item(epub.EpubNcx())
    # book.add_item(epub.EpubNav())

    # # # Define CSS style

    # # # Create spine

    # # Compile the book

    # if book.items:
    #     save_epub(
    #         path + f'/{book_info["book_title"]}({book_counter}).epub', epub_chapters, book)

def get_epub(book_url, epub_path, callback=None):
    book_info = fetch_book_info(book_url)
    chapters_info = fetch_chapters_list(book_url)
    total_chapters = len(chapters_info)
    chapters = []
    # # Testing
    # for n in range(10):
    #     title = chapters_info[n][0]
    #     url = chapters_info[n][1]
    #     content = fetch_one_chapter_content(url)
    #     chapters.append((title, content))

    # # Production
    for idx, (title, url) in enumerate(chapters_info):
        content = fetch_one_chapter_content(url)
        chapters.append((title, content))

        # 這裡使用回調函數來更新進度
        if callback:
            progress = ((idx + 1) / total_chapters) * 100  # 計算進度百分比
            callback(
                f"Downloading chapter {idx+1} of {total_chapters}, {progress:.2f}% complete")

    
    current_size = 0
    book_count = 1
    epub_chapters = []
    book = create_epub(book_info, book_count)
    for title, content in chapters:
        chapter_size = get_chapter_size(content)
        if current_size + chapter_size > MAX_SIZE:
            save_epub(epub_path, epub_chapters, book_info, book, book_count)
            book_count += 1
            book = create_epub(book_info, chapters)
            epub_chapters = []
            current_size = 0
        content = f'<h1>{title}</h1><p>{content}</p>'
        c = epub.EpubHtml(title=title, file_name=title +
                        '.xhtml')
        c.content = content
        book.add_item(c)
        epub_chapters.append(c)
        current_size += chapter_size
    
    save_epub(epub_path, epub_chapters, book_info, book, book_count)
    

    logger.info("Ebook creation process completed.")


def update_epub(book_url, epub_path, input_path):
    number_to_update = calculate_chapters_to_update(book_url, input_path)
    if number_to_update > 0:
        chap_list = fetch_chapters_list(book_url)
        chap_list_to_update = chap_list[-abs(number_to_update)::1]
        chap_content_to_update = []
        for idx, (title, url) in enumerate(chap_list_to_update):
            content = fetch_one_chapter_content(url)
            chap_content_to_update.append((title, content))
        current_size = os.stat(input_path).st_size
        book = epub.read_epub(input_path)
        book_title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else None
        book_author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else None
        book_info = {"book_title": book_title, "book_author": book_author}
        book_count = int(re.search(r'\d+', book_title))
        update_start_from = book_count
        epub_chapters = []
        for title, content in chap_content_to_update:    
            chapter_size = get_chapter_size(content)
            if current_size + chapter_size > MAX_SIZE:
                save_updated_epub(epub_path, epub_chapters, book_info, book, book_count)
                book_count += 1
                book = create_epub(book_info, book_count)
                current_size = 0
                epub_chapters = []
            else:
                # for loop to append one chapter
                content = f'<h1>{title}</h1><p>{content}</p>'
                c = epub.EpubHtml(title=title, file_name=f"{title}.xhtml", content=content)
                book.add_item(c)
                epub_chapters.append(c)
                current_size += chapter_size
                # size within limit -> continue to append chapter

        save_updated_epub(epub_path, epub_chapters, book_info, book, book_count)

    else:
        logger.info("EPUB file already up to date")



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
            content = fetch_one_chapter_content(url)
            chapters.append((title, content))

            # 這裡使用回調函數來更新進度
            if callback:
                progress = ((idx + 1) / total_chapters) * 100  # 計算進度百分比
                callback(
                    f"Downloading chapter {idx+1} of {total_chapters}, {progress:.2f}% complete")

        
        current_size = 0
        book_count = 0
        epub_chapters = []
        book = create_epub(book_info, book_count)
        for title, content in chapters:
            chapter_size = get_chapter_size(content)
            if current_size + chapter_size > MAX_SIZE:
                save_epub(epub_path + f'/{book_info["book_title"]}({book_counter}).epub', epub_chapters, book)
                book_count += 1
                book = create_epub(book_info, chapters)
                epub_chapters = []
                current_size = 0
            content = f'<h1>{title}</h1><p>{content}</p>'
            c = epub.EpubHtml(title=title, file_name=title +
                          '.xhtml', content=content)
            book.add_item(c)
            epub_chapters.append(c)
            current_size += chapter_size
        
        save_epub(epub_path + f'/{book_info["book_title"]}({book_counter}).epub', epub_chapters, book)
        

        logger.info("Ebook creation process completed.")

    elif action == "update":
        print("update")
        update_epub(book_url, epub_path, input_path)
        # number_to_update = calculate_chapters_to_update(input_path)
        # if number_to_update > 0:
        #     chap_list = fetch_chapters_list(book_url)
        #     chap_list_to_update = chap_list[-abs(number_to_update)::1]
        #     chap_content_to_update = []
        #     for idx, (title, url) in enumerate(chap_list_to_update):
        #         content = fetch_one_chapter_content(url)
        #         chap_content_to_update.append((title, content))
        #     current_size = os.stat(input_path).st_size
        #     book = epub.read_epub(input_path)
        #     book_title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else None
        #     book_author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else None
        #     book_info = {"book_title": book_title, "book_author": book_author}
        #     book_count = int(re.search(r'\d+', book_title))
        #     update_start_from = book_count
        #     epub_chapters = []
        #     for title, content in chap_content_to_update:    
        #         chapter_size = get_chapter_size(content)
        #         if current_size + chapter_size > MAX_SIZE:
        #             save_epub(epub_path, epub_chapters, book_info, book, book_count)
        #             book_count += 1
        #             book = create_epub(book_info, book_count)
        #             current_size = 0
        #             epub_chapters = []
        #         else:
        #             # for loop to append one chapter
        #             content = f'<h1>{title}</h1><p>{content}</p>'
        #             c = epub.EpubHtml(title=title, file_name=f"{title}.xhtml", content=content)
        #             book.add_item(c)
        #             epub_chapters.append(c)
        #             current_size += chapter_size
        #             # size within limit -> continue to append chapter

        #     save_epub(epub_path, epub_chapters, book_info, book, book_count)

        # else:
        #     logger.info("EPUB file already up to date")
        # get chap list
        # 
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
        get_epub('https://m.bqg9527.com/zh_hant/book/118028/', './')
        # main()
        # test()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
