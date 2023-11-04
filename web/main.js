// Modules to control application life and create native browser window
const {app, dialog, BrowserWindow} = require('electron')

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow

function createWindow () {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 500,
    height: 500,
    webPreferences: {
      nodeIntegration: true
    }
  })

  // and load the index.html of the app.
  mainWindow.loadURL('http://localhost:8002/index.html');

  // Open the DevTools.
  // mainWindow.webContents.openDevTools()

  // Emitted when the window is closed.
  mainWindow.on('closed', function () {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null
  })
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', function () {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (mainWindow === null) createWindow()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.


let epub_path; // To save output location
let input_path; // To save the location of the epub to update

const form = document.getElementById('form')
form.addEventListener('submit',startCrawling)

const folderPickerButton = document.getElementById("folderPicker")
folderPickerButton.addEventListener("click", async () => {
    console.log("before getting folder path")
    epub_path = await getFolderPath()
    console.log("after getting folder path")
    if (epub_path) {
        console.log("epub_path")
        document.getElementById("folderPath").textContent = epub_path;
    }
})

const filePickerButton = document.getElementById("filePicker")
filePickerButton.addEventListener("click", async () => {
    console.log("before getting file path")
    input_path = await getFilePath()
    console.log("after getting file path")
    if (input_path) {
        console.log("input_path")
        document.getElementById("filePathDisplay").textContent = input_path;
    }
})



// // Listen to the change event of the folderPicker
// document.getElementById("folderPicker").addEventListener("change", (event) => {
//     if(event.target.files.length > 0) {
//         epub_path = event.target.files[0].webkitRelativePath.split('/')[0];
//         document.getElementById("folderPathDisplay").textContent = epub_path;
//     }
// });
// document.getElementById("folderPicker").addEventListener("change", (event) => {
//     if(event.target.files.length > 0) {
//         epub_path = event.target.files[0].webkitRelativePath.split('/')[0];
//         document.getElementById("folderPathDisplay").textContent = epub_path;
//     }
// });
// app.js
// function getFolderPath() {
//     eel.select_output_folder()(function(path) {
//         document.getElementById("folderPath").textContent = path;
//     });
// }

async function getFolderPath() {
    const result = await dialog.showOpenDialog(null, {
        properties: ['openDirectory']
    })
    console.log(result)
    if (result.canceled) {
        return null
    } else {
        const dir = result.filePaths[0]
        return dir
    }
}

async function getFilePath() {
    const result = await dialog.showOpenDialog(null, {
        properties: ['openFile']
    })
    console.log(result)
    if (result.canceled) {
        return null
    } else {
        const dir = result.filePaths[0]
        return dir
    }
}






// // Listen to the change event of the filePicker
// document.getElementById("filePicker").addEventListener("change", (event) => {
//     if(event.target.files.length > 0) {
//         input_path = event.target.files[0].webkitRelativePath;
//         document.getElementById("filePathDisplay").textContent = input_path;
//     }
// });


async function startCrawling(e) {
    const epubPath = document.getElementById('epub_path').value;
    const inputPath = document.getElementById('input_path').value;
    let action="get";
    if (inputPath) {
        action="update";
    }
    document.getElementById('progress').style.display = 'block';
    const data={"action": action, "epub_path": epubPath, "input_path": inputPath}
    await eel.start_crawl(data)();
}

eel.expose(update_progress)
function update_progress(message) {
    document.getElementById('progress_message').innerText = message;
}
