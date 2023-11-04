from ebooklib import epub

def append_chapters_to_epub(epub_path, new_chapters):
    book = epub.read_epub(epub_path)
    
    # Loop to add new chapters
    for title, content in new_chapters:
        c = epub.EpubHtml(title=title, file_name=f"{title}.xhtml", lang="hr")
        c.content = f'<h1>{title}</h1><p>{content}</p>'
        book.add_item(c)
    
    epub.write_epub(epub_path, book)

def get_chapters_in_order(epub_book: 'EpubBook') -> tuple[list, list] :
    ordered_chapters = []
    ordered_chapter_spine = []

    # Traverse spine to get id of items in order as the toc of the book
    for item_id in epub_book.spine:
        item = epub_book.get_item_with_id(item_id)
        # Only retrieve chapter content with type of EpubHtml
        if item and isinstance(item, epub.EpubHtml):  
            ordered_chapters.append(item)
            ordered_chapter_spine.append(item)

    return ordered_chapters, ordered_chapter_spine

def remove_nav_and_style_items(book):
    # 使用get_items_of_type()找到特定类型的所有项
    ncx_to_remove = list(book.get_items_of_type(ITEM_NAVIGATION))
    style_to_remove = list(book.get_items_of_type(ITEM_STYLE))
    nav_to_remove = book.get_item_with_id('nav')
    items_to_remove = ncx_to_remove + style_to_remove

    if nav_to_remove:
        items_to_remove.append(nav_to_remove)

    logger.info(f"number of ncx to remove: {len(ncx_to_remove)}")
    logger.info(f"number of style to remove: {len(style_to_remove)}")
    logger.info(f"nav to remove: {nav_to_remove}")

    # 如果找到了要删除的项
    if items_to_remove:
        # 从书的items列表中删除它们
        for item in items_to_remove:
            if item in book.items:
                book.items.remove(item)