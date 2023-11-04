import os
import eel
from spiders.book_spider import main as spider_main  # 導入爬蟲的main()，並重新命名避免衝突
from utils import utils
# from PyQt5.QtWidgets import QWidget, QFileDialog  # pip install PyQt5
# from PyQt5.Qt import QApplication as QApp

import tkinter as tk
from tkinter import filedialog

eel.init(f'{os.path.dirname(os.path.realpath(__file__))}/web')  # 初始化Eel和Web資料夾


@eel.expose  # 使用這個裝飾器來讓JavaScript可以訪問這個Python函數
def start_crawl(output_path):
    def update_progress(message):
        eel.update_progress(message)

    spider_main(callback=update_progress)

@eel.expose
def select_output_folder():
    utils.select_folder()
# def select_output_folder():
#     _, folder = QApp(['./']), QFileDialog.getExistingDirectory(
#         parent=QWidget(), caption='Select a folder')
#     print(folder)
#     return folder





# eel.start('index.html', size=(500, 500), port=8001)
eel.start('index.html', mode='node_modules/electron', port=8002, cmdline_args=['--remote-debugging-port=9222'])
# eel.start('hello.html', mode='custom', cmdline_args=['node_modules/electron/dist/electron.exe', '.'], port=8002)