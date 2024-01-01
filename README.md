# Ebook Crawler

## How to bundle the app with PyInstaller

Bundle both the frontend and backend together
`python3 -m PyInstaller --onefile --windowed --add-data 'web:web' main.py`

Bundle python script to one binary file
- Dev
`pyinstaller --clean --onefile -y -n "binary_name" --add-data="resources\any_static_assets.txt;resources" python_script.py`

## Use the app

Start Tauri development window 
`npm run tauri dev`