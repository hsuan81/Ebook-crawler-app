import sys

import ebooklib
from ebooklib import epub
from ebooklib.utils import debug


# read book
book = epub.read_epub(sys.argv[1])

debug(book.metadata)
print("spine")
debug(book.spine)
print("Toc")
debug(book.toc)

for x in book.get_items_of_type(ebooklib.ITEM_IMAGE):
    debug(x)

for x in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    debug(x)
