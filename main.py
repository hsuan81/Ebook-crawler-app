import os
import eel
from spiders.book_spider import main as spider_main  # 導入爬蟲的main()，並重新命名避免衝突

eel.init(f'{os.path.dirname(os.path.realpath(__file__))}/web')  # 初始化Eel和Web資料夾


@eel.expose  # 使用這個裝飾器來讓JavaScript可以訪問這個Python函數
def start_crawl(output_path):
    def update_progress(message):
        eel.update_progress(message)

    spider_main(callback=update_progress)


eel.start('index.html', size=(300, 200), port=8001)
