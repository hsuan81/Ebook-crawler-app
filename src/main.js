const { invoke } = window.__TAURI__.tauri;
const { open } = window.__TAURI__.dialog;
const { appDir } = window.__TAURI__.path;



let greetInputEl;
let greetMsgEl;

async function greet() {
  // Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
  greetMsgEl.textContent = await invoke("greet", { name: greetInputEl.value });
}

window.addEventListener("DOMContentLoaded", () => {
  // greetInputEl = document.querySelector("#greet-input");
  // greetMsgEl = document.querySelector("#greet-msg");
  // document.querySelector("#greet-form").addEventListener("submit", (e) => {
  //   e.preventDefault();
  //   greet();
  // });
});

document.getElementById('filePicker').addEventListener("click", async () => {
  const path = await open({
    multiple: false,
    filters: [{
      name: 'Ebook',
      extensions: ['epub']
    }]
  });
  
  document.getElementById('fileLocation').innerText = `Epub檔案位置：${path}`;
});

document.getElementById('folderPicker').addEventListener('click', async () => {
  const dirPath = await open({
    directory: true,
    multiple: false,
    defaultPath: await appDir(),
  });

  // Do something with the result

  document.getElementById('folderPath').innerText = `儲存位置: ${dirPath}`
  epubPath = dirPath
})

async function getEpub(epubPath) {
  document.getElementById("getEpubResult").innerText = await invoke("py_get_epub", { action: "get", epubPath: epubPath})
}

async function updateEpub(epubPath, inputPath) {
  document.getElementById("getEpubResult").innerText = await invoke("py_update_epub", { action: "update", epubPath: epubPath, inputPath: inputPath})
}

document.getElementById('getEpub').addEventListener('click', async () => {
  document.getElementById('progress').innerText = 'Fetching and Creating Ebook...'
  await getEpub(epubPath)
});

document.getElementById('updateEpub').addEventListener('click', async () => {
  document.getElementById('progress').innerText = 'Fetching and Updating Ebook...'
  await updateEpub(epubPath, inputPath)
});