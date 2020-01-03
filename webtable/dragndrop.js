let dropArea = null;

function initDropArea() {
  dropArea = document.getElementById('drop-area');

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false)
  });

  ['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false)
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false)
  });

  dropArea.addEventListener('drop', dropHandler, false);
}

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function highlight(e) {
  dropArea.classList.add('highlight')
}

function unhighlight(e) {
  dropArea.classList.remove('highlight')
}

function dropHandler(e) {
  // Prevent default behavior (Prevent file from being opened)
  e.preventDefault();
  if (e.dataTransfer.items) {
    // Use DataTransferItemList interface to access the file(s)
    if (e.dataTransfer.items.length == 1) {
      let file = e.dataTransfer.items[0].getAsFile();
      console.log('... file.name = ' + file.name);
      uploadFile(file);

    }
  } else {
    // Use DataTransfer interface to access the file(s)
    for (var i = 0; i < e.dataTransfer.files.length; i++) {
      console.log('... file[' + i + '].name = ' + e.dataTransfer.files[i].name);
    }
  }
}

function uploadFile(file) {
  let url = "/upload/toswl";
  let formData = new FormData();

  formData.append("file", file);
  fetch(url, {method: "POST", body: formData})
      .then(() => {initTable();})
      .catch(() => {alert("Failed!");})
}
