import sys

import ebooklib
from ebooklib import epub
from ebooklib.utils import debug
from bs4 import BeautifulSoup


# read book
book = epub.read_epub(sys.argv[1])

# debug(book.metadata)
# print("spine")
# debug(book.spine)
# print("Toc")
# debug(book.toc)

last_item_id = book.spine[-1][0]

# 使用 ID 從書籍物件中獲取對應的項目
last_item = book.get_item_with_id(last_item_id)

# 返回項目（章節）的標題
content = last_item.get_body_content().decode('utf-8')
soup = BeautifulSoup(content, 'html.parser')
h1_tag = soup.find('h1').text
print(h1_tag)

for x in book.get_items_of_type(ebooklib.ITEM_IMAGE):
    debug(x)

for x in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    debug(x)
