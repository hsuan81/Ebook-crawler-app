const { invoke } = window.__TAURI__.tauri;
const { open } = window.__TAURI__.dialog;
const { appDir } = window.__TAURI__.path;



let greetInputEl;
let greetMsgEl;

let epubPath;
let inputPath

async function greet() {
  // Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
  greetMsgEl.textContent = await invoke("greet", { name: greetInputEl.value });
}

// window.addEventListener("DOMContentLoaded", () => {
  // greetInputEl = document.querySelector("#greet-input");
  // greetMsgEl = document.querySelector("#greet-msg");
  // document.querySelector("#greet-form").addEventListener("submit", (e) => {
  //   e.preventDefault();
  //   greet();
  // });
  // document.getElementById('folderPath').style.visibility = 'hidden';
// });

// window.addEventListener("load", () => {
//   greetInputEl = document.querySelector("#greet-input");
//   greetMsgEl = document.querySelector("#greet-msg");
//   document.querySelector("#greet-form").addEventListener("submit", (e) => {
//     e.preventDefault();
//     greet();
//   });
//   document.getElementById('folderPath').style.visibility = 'hidden';
//   console.log('loaded')
// });

document.getElementById('filePicker').addEventListener("click", async () => {
  const path = await open({
    multiple: false,
    filters: [{
      name: 'Ebook',
      extensions: ['epub']
    }]
  });
  // document.getElementById('fileLocation').classList.remove('hidden');

  document.getElementById('fileLocation').textContent = `Epub檔案位置：${path}`;
  inputPath = path
});

document.getElementById('folderPicker').addEventListener('click', async () => {
  const dirPath = await open({
    directory: true,
    multiple: false,
    defaultPath: await appDir(),
  });

  // Do something with the result
  // document.getElementById('folderPath').style.visibility = undefined;
  // document.getElementById('folderPath').textContent = "Here"

  document.getElementById('folderPath').textContent = `儲存位置: ${dirPath}`
  epubPath = dirPath
})

async function getEpub(epubPath) {
  document.getElementById("getEpubResult").innerText = await invoke("py_get_epub", { epubPath: epubPath })
}

async function updateEpub(epubPath, inputPath) {
  document.getElementById("getEpubResult").innerText = await invoke("py_update_epub", { epubPath: epubPath, inputPath: inputPath })
}

document.getElementById('getEpub').addEventListener('click', async () => {
  const element = document.getElementById('progress_message')
  element.innerText = 'Fetching and Creating Ebook...'
  document.getElementById('progress').style.display = 'block'
  element.innerText = await getEpub(epubPath)
});

document.getElementById('updateEpub').addEventListener('click', async () => {
  const element = document.getElementById('progress_message')
  element.innerText = 'Fetching and Updating Ebook...'
  document.getElementById('progress').style.display = 'block'
  element.innerText = await updateEpub(epubPath, inputPath)
});