import requests
import logging
import io
import os
import re
from bs4 import BeautifulSoup
from ebooklib import epub
from ebooklib import ITEM_DOCUMENT, ITEM_NAVIGATION, ITEM_STYLE

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

MAX_SIZE = 3 * 1024 * 1024



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

    chapter_tags = soup.select(
        'ul.chapter[id!="last12"] > li > a[href!="#header"]')
   
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


def get_last_chapter_id_number(book: 'EpubBook') -> int:
    logger.info("Getting last chapter id...")

    # Retrieve all items in spine
    spine_items = book.spine

    # Check if spine is empty
    if not spine_items:
        logger.info("No items found in the spine.")
        return None

    # Get the last item in spine
    last_spine_item = spine_items[-1]

    # Inspect type of the last item and get the id (It could be tuple or others like EpubHtml)
    if isinstance(last_spine_item, tuple):
        last_item_id = last_spine_item[0]
    else:
        last_item_id = last_spine_item.get_id()
    
    last_id_num = re.search(r'\d+', last_item_id).group(0)
    logger.info(f"The id of the last chapter is: {last_item_id}")
    logger.info(f"The id number of the last chapter is: {last_id_num}")

    return int(last_id_num)


def get_last_chapter_title_epub(path):
    book = epub.read_epub(path)

    # Get the id of the last chapter item in the spine
    last_item_id = book.spine[-1][0]

    # Get the chapter item from the book with Id
    last_item = book.get_item_with_id(last_item_id)

    # Get the title of the chapter
    content = last_item.get_body_content().decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    h1_tag = soup.find('h1')  # find the first <h1> tag

    if h1_tag:
        title = h1_tag.text  
        logger.info(f"Get last chapter title: Title is {title}")
        
    else:
        logger.info(f"Get last chapter title: No <h1> tag found.")
        
    return title


def get_latest_chapter_from_web(book_url):
    response = requests.get(book_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    latest_chapter = soup.select_one('p:-soup-contains("最新") a').text
    return latest_chapter

def calculate_chapters_to_update(book_url, path):
    last_title = get_last_chapter_title_epub(path)
    latest_title = get_latest_chapter_from_web(book_url)
    logger.info(f"Last chapter title of the Epub file: {last_title}")
    logger.info(f"Latest chapter title from web: {latest_title}")
    logger.info(f"The two titles are the same: {last_title == latest_title}")
    logger.info(f"The two titles are different: {last_title != latest_title}")
    if last_title != latest_title:
        
        # parse to get number and calculate how many chapters need to be added
        last_chapter_match = re.search(r'\d+', last_title)
        latest_chapter_match = re.search(r'\d+', latest_title)
        logger.info(f"Last chapter match: {last_chapter_match}")
        logger.info(f"Latest chapter match: {latest_chapter_match}")
        if last_chapter_match and latest_chapter_match:
            last_chapter_number = int(
                last_chapter_match.group(0))  # 获取匹配到的数字字符串
            latest_chapter_number = int(
                latest_chapter_match.group(0))  # 将字符串转为整数
            logger.info(f"chapter number: {last_chapter_number} vs {latest_chapter_number}")
            diff = last_chapter_number-latest_chapter_number
            logger.info(f"difference: {diff}")
            return abs(diff)
        else:
            logger.info(
                "Calculate chapters to update: No chapter number found.")
    else:
        return 0
    


def create_epub(book_info, book_count=1):
    logger.info("Creating EPUB file.")

    # Set the book info
    book = epub.EpubBook()
    book.set_identifier(book_info['book_title'] + str(book_count))
    book.set_title(book_info['book_title'])
    book.add_author(book_info['book_author'])
    book.set_language('zh')

    return book


def create_and_transfer_from_old_book(old_book: 'EpubBook', book_info, book_count) -> 'EpubBook':
    book_title = book_info['book_title']
    book_author = book_info['book_author']

    logger.info("Creating EPUB file.")
    new_book = epub.EpubBook()
    new_book.set_identifier(book_title + str(book_count))
    new_book.set_title(book_title)
    new_book.add_author(book_author)
    new_book.set_language('zh')

    # Prepare lists for TOC and spine
    toc_chapters = []
    spine = ['nav']  # initiate spine with default 'nav'

    # Store the chapter id and chapter content in a dict for searching later
    chapters_dict = {item.get_id(): item for item in old_book.get_items() if isinstance(item, epub.EpubHtml) and item.is_chapter()}

    logger.info("Copying spine and content")
    # Loop through the spine and copy chapter to new book if the item is in the dict created before
    for spine_item in old_book.spine:
        item_id = spine_item[0]  # get the id of the item
        if item_id in chapters_dict:
            chapter = chapters_dict[item_id]
            logger.info("EpubHtml found.")
            logger.info(f"Item id: {item_id}")
            logger.info(f"Chapter: {chapter}")
                
            # Create the chapter to add to the target book
            new_book_chapter = epub.EpubHtml(title=chapter.title, file_name=chapter.file_name)
            new_book_chapter.content = chapter.content  
            new_book.add_item(new_book_chapter)
            
            # Add the copied chapter to TOC and spine
            toc_chapters.append(new_book_chapter)
            spine.append(new_book_chapter)
        else:
            logger.info(f"Spine item: {spine_item}")
    
    # Decide the order of every chapter in new book based on the spine
    new_book.spine = spine

    logger.info("EPUB file transferring finished.")

    return new_book


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
    book.toc += epub_chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = 'body { font-family: Times, Times New Roman, serif; }'
    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Update spine
    book.spine += epub_chapters
    logger.info(f"book spine {book.spine}")
    

    # Write to EPUB file
    epub.write_epub(path, book)
    logger.info(f"Updated Epub file is saved at {path}.")


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

        # Use callback function to update progress for display on the client side
        if callback:
            progress = ((idx + 1) / total_chapters) * 100  # calculate the Ebook complete percentage
            callback(
                f"Downloading chapter {idx+1} of {total_chapters}, {progress:.2f}% complete")

    
    current_size = 0
    book_count = 1
    epub_chapters = []

    if callback:
        callback("Creating Ebook...")
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
    
    if callback:
        callback("Ebook completed.")

    logger.info("Ebook creation process completed.")


def update_epub(book_url, epub_path, input_path, callback=None):
    if callback:
        callback("Checking new chapters...")

    number_to_update = calculate_chapters_to_update(book_url, input_path)
    logger.info(f"Number of chapters to update: {number_to_update}")

    # Start to update the ebook if new chapters are available on the web
    if number_to_update > 0:
        if callback:
            callback("Fetching new chapters...")

        chap_list = fetch_chapters_list(book_url)

        # Slice the list with only new chapters left
        chap_list_to_update = chap_list[-abs(number_to_update)::1]

        # Fetch title and content of the chapters for update
        chap_content_to_update = []
        for idx, (title, url) in enumerate(chap_list_to_update):
            content = fetch_one_chapter_content(url)
            chap_content_to_update.append((title, content))
        
        if callback:
            callback("Updating the Ebook...")
        # Get the size of the source book and book info from it
        current_size = os.stat(input_path).st_size

        old_book = epub.read_epub(input_path)
        book_title = old_book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else None
        book_author = old_book.get_metadata('DC', 'creator')[0][0] if old_book.get_metadata('DC', 'creator') else None
        book_info = {"book_title": book_title, "book_author": book_author}
        book_count = int(re.search(r'\d+', book_title).group(0))

        if current_size > MAX_SIZE:
            book_count += 1
            book = create_epub(book_info, book_count)
        else:
            book = create_and_transfer_from_old_book(old_book, book_info, book_count)
        
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
        logger.info("EPUB file is updated.")
        if callback:
            callback("Update completed.")

    else:
        logger.info("EPUB file already up to date")
        if callback:
            callback("Ebook is already up to date.")



def main(params, callback=None):
    # Get params
    action = params.get("action")
    epub_path = params.get("epub_path")
    input_path = params.get("input_path")

    book_url = 'https://m.bqg9527.com/zh_hant/book/118028/'

    if action == "get":
        logger.info(" Action is: Get Ebook ")
        get_epub(book_url, epub_path, callback)
        # book_info = fetch_book_info(book_url)
        # chapters_info = fetch_chapters_list(book_url)
        # total_chapters = len(chapters_info)
        # chapters = []
    # # Testing
    # for n in range(10):
    #     title = chapters_info[n][0]
    #     url = chapters_info[n][1]
    #     content = fetch_chapter_content(url)
    #     chapters.append((title, content))

    # Production
        # for idx, (title, url) in enumerate(chapters_info):
        #     content = fetch_one_chapter_content(url)
        #     chapters.append((title, content))

        #     # 這裡使用回調函數來更新進度
        #     if callback:
        #         progress = ((idx + 1) / total_chapters) * 100  # 計算進度百分比
        #         callback(
        #             f"Downloading chapter {idx+1} of {total_chapters}, {progress:.2f}% complete")

        
        # current_size = 0
        # book_count = 0
        # epub_chapters = []
        # book = create_epub(book_info, book_count)
        # for title, content in chapters:
        #     chapter_size = get_chapter_size(content)
        #     if current_size + chapter_size > MAX_SIZE:
        #         save_epub(epub_path + f'/{book_info["book_title"]}({book_counter}).epub', epub_chapters, book)
        #         book_count += 1
        #         book = create_epub(book_info, chapters)
        #         epub_chapters = []
        #         current_size = 0
        #     content = f'<h1>{title}</h1><p>{content}</p>'
        #     c = epub.EpubHtml(title=title, file_name=title +
        #                   '.xhtml', content=content)
        #     book.add_item(c)
        #     epub_chapters.append(c)
        #     current_size += chapter_size
        
        # save_epub(epub_path + f'/{book_info["book_title"]}({book_counter}).epub', epub_chapters, book)
        

        logger.info("Ebook creation process completed.")

    elif action == "update":
        logger.info(" Action is: Update Ebook ")
        update_epub(book_url, epub_path, input_path, callback)

        logger.info("Ebook update completed.")


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
