// This is global variable to store the sequence of blocks after random selection that block will be removed from the sequence
const sequence = [
  "p0d0p0b0ct",
  "p0d0p0b1ct",
  "p0d0p0b2ct",
  "p0d0p0b3ct",
  "p0d0p1b0ct",
  "p0d0p1b1ct",
  "p0d0p1b2ct",
  "p0d0p1b3ct",
  "p0d1p0b0ct",
  "p0d1p0b1ct",
  "p0d1p0b2ct",
  "p0d1p0b3ct",
  "p0d1p1b0ct",
  "p0d1p1b1ct",
  "p0d1p1b2ct",
  "p0d1p1b3ct",
  "p1d0p0b0ct",
  "p1d0p0b1ct",
  "p1d0p0b2ct",
  "p1d0p0b3ct",
  "p1d0p1b0ct",
  "p1d0p1b1ct",
  "p1d0p1b2ct",
  "p1d0p1b3ct",
  "p1d1p0b0ct",
  "p1d1p0b1ct",
  "p1d1p0b2ct",
  "p1d1p0b3ct",
  "p1d1p1b0ct",
  "p1d1p1b1ct",
  "p1d1p1b2ct",
  "p1d1p1b3ct",
];

// for tracing uploaded file and get later to update, remove or add
class FileMapping {
  constructor() {
    this.mappingEntries = [];
  }

  updateSelectionAdd(fileName) {
    var selectElement = document.getElementById("update_file");
    // Create a new option element
    var newOption = document.createElement("option");
    newOption.value = fileName;
    newOption.textContent = fileName;
    // Append the new option to the select element
    selectElement.appendChild(newOption);

    // add the file name to the delete select element
    // Get the select element
    var selectElement = document.getElementById("delete_file");
    // Create a new option element
    var newOption = document.createElement("option");
    newOption.value = fileName;
    newOption.textContent = fileName;
    // Append the new option to the select element
    selectElement.appendChild(newOption);

    // add the file name to the read select element
    // Get the select element
    var selectElement = document.getElementById("read_file");
    // Create a new option element
    var newOption = document.createElement("option");
    newOption.value = fileName;
    newOption.textContent = fileName;
    // Append the new option to the select element
    selectElement.appendChild(newOption);
  }

  updateSelectionRemove(fileName) {
    var selectElement = document.getElementById("update_file");
    var optionToRemove = fileName;

    for (let i = 0; i < selectElement.options.length; i++) {
      if (selectElement.options[i].text === optionToRemove) {
        selectElement.remove(i);
        break;
      }
    }

    // remove the file name from the delete select element
    // Get the select element
    var selectElement = document.getElementById("delete_file");
    // Create a new option element
    var optionToRemove = fileName;
    for (let i = 0; i < selectElement.options.length; i++) {
      if (selectElement.options[i].text === optionToRemove) {
        selectElement.remove(i);
        break;
      }
    }

    // remove the file name from the read select element
    // Get the select element
    var selectElement = document.getElementById("read_file");
    // Create a new option element
    var optionToRemove = fileName;
    for (let i = 0; i < selectElement.options.length; i++) {
      if (selectElement.options[i].text === optionToRemove) {
        selectElement.remove(i);
        break;
      }
    }
  }

  addMapping(fileName, firstRowOfMappingFile, lastRowOfMappingFile) {
    const entry = { fileName, firstRowOfMappingFile, lastRowOfMappingFile };
    this.mappingEntries.push(entry);
    // add the file name to the update select element
    // Get the select element
    this.updateSelectionAdd(fileName);
  }

  removeMapping(fileName) {
    this.mappingEntries = this.mappingEntries.filter(
      (entry) => entry.fileName !== fileName
    );
    // remove the file name from the update select element
    // Get the select element
    this.updateSelectionRemove(fileName);
  }

  updateMapping(fileName, firstRowOfMappingFile, lastRowOfMappingFile) {
    const entry = this.mappingEntries.find(
      (entry) => entry.fileName === fileName
    );
    if (entry) {
      entry.firstRowOfMappingFile = firstRowOfMappingFile;
      entry.lastRowOfMappingFile = lastRowOfMappingFile;
    }
  }

  getMapping(fileName) {
    return this.mappingEntries.find((entry) => entry.fileName === fileName);
  }
}
const fileMapping = new FileMapping();

// Scroll the table to the selected row so that user don't have to scroll manually
function scrollToSelectedRow(table) {
  parentElement = table.parentElement;
  while (parentElement.tagName != "DIV") {
    parentElement = parentElement.parentElement;
    // console.log(parentElement.tagName);
  }
  parentElementTop = parentElement.getBoundingClientRect().top;
  tableTop = table.getBoundingClientRect().top;
  // Scroll the table to the selected row so that user don't have to scroll manually
  parentElement.scrollTop = tableTop - parentElementTop;

  // console.log(table.getBoundingClientRect());
}

// reading the table row
function readTableRow(tableName, rowNumber, fileSizeInKB) {
  console.log(tableName);
  var table = document.getElementById(tableName);
  var rows = table.getElementsByTagName("tr");
  scrollToSelectedRow(table);
  if (rowNumber >= 0 && rowNumber < rows.length) {
    var row = rows[rowNumber];
    row.style.backgroundColor = "green";
    row.cells[1].innerHTML = fileSizeInKB + "kb";
  } else {
    console.log("Invalid row number.");
  }
}

// Selecting page table and store LA and PA
var mapping_table_row = 1;
function selectRowMappingTable(rowNumber, logicalAddress, physicalAddress) {
  var table = document.getElementById("mapping_table");
  var rows = table.getElementsByTagName("tr");

  if (rowNumber >= 0 && rowNumber < rows.length) {
    var row = rows[rowNumber];
    row.style.backgroundColor = "green";
    row.cells[0].innerHTML = logicalAddress;
    row.cells[1].innerHTML = physicalAddress;
  } else {
    console.log("Invalid row number.");
  }
  mapping_table_row++;
}
// File tracer from logical address
var file_tracer = 0;
async function FileUpload(file) {
  // Get the size of the file in bytes
  var fileSize = file.size;

  // Display the file size
  console.log("File Size: " + fileSize + " bytes");
  // Bytes to kb 2 decimal places
  var fileSizeInKB = (fileSize / 1024).toFixed(2);
  if (fileSizeInKB >= 512) {
    alert("File size is too large, please select a file less than 512kb");
    return;
  } else {
    fileMapping.addMapping(file.name, mapping_table_row, 0);
    var logicalAddressTracer = 0;
    // divide the file size by 16kb (block size) to get the number of blocks
    while (fileSizeInKB > 0) {
      // taking a random number
      var random = Math.floor(Math.random() * sequence.length);
      // Get the block number from the sequence
      var block = sequence[random];
      console.log(block);
      // divide the file size by 4kb (page size) to get the number of pages
      blockPageTracer = 1;
      while (fileSizeInKB > 0 && blockPageTracer <= 4) {
        if (fileSizeInKB < 4) {
          readTableRow(block, blockPageTracer, fileSizeInKB);
        } else {
          readTableRow(block, blockPageTracer, 4);
        }

        selectRowMappingTable(
          mapping_table_row,
          "f" + file_tracer + logicalAddressTracer,
          block + blockPageTracer
        );
        // Save the filename, logical address and mapping_table_row in the java class
        // decrease the file size by 4kb
        fileSizeInKB = (fileSizeInKB - 4).toFixed(2);
        logicalAddressTracer++;
        blockPageTracer++;
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      // Remove the block from the sequence
      sequence.splice(random, 1);
    }
    file_tracer++;
    var getFileInformation = fileMapping.getMapping(file.name);
    fileMapping.updateMapping(
      getFileInformation.fileName,
      getFileInformation.firstRowOfMappingFile,
      mapping_table_row
    );
    console.log(fileMapping.getMapping(file.name));
  }

  // divide the file size by 4kb (page size) to get the number of pages
}
// Read the uploaded file from input onchange
function handleFileInputChange() {
  var fileInput = document.getElementById("fileUpload");
  var file = fileInput.files[0];
  if (file) {
    FileUpload(file);
  }
}

// ----------------------------------------- Update File -------------------------------------------//

async function handleSelection(fileName) {
  // const fileMapping = new FileMapping();
  var getFileInformation = fileMapping.getMapping(fileName);

  console.log(getFileInformation);
  var table = document.getElementById("mapping_table");
  var rows = table.getElementsByTagName("tr");
  console.log(getFileInformation.firstRowOfMappingFile);
  console.log(getFileInformation.lastRowOfMappingFile);
  for (
    firstRow = getFileInformation.firstRowOfMappingFile;
    firstRow < getFileInformation.lastRowOfMappingFile;
    firstRow++
  ) {
    var row = rows[firstRow];
    logicalAddress = row.cells[0].innerHTML;
    physicalAddressWithRow = row.cells[1].innerHTML;
    physicalAddressBlockRow = physicalAddressWithRow.charAt(
      physicalAddressWithRow.length - 1
    );
    physicalAddress = physicalAddressWithRow.slice(0, -1);
    console.log(logicalAddress);
    console.log(physicalAddress);
    console.log(physicalAddressBlockRow);
    // Update the table row
    row.style.backgroundColor = "yellow";
    blockTable = document.getElementById(physicalAddress);
    blockTable.rows[physicalAddressBlockRow].style.backgroundColor = "yellow";
    await new Promise((resolve) => setTimeout(resolve, 1000));
    row.cells[0].innerHTML = "";
    row.cells[1].innerHTML = "";
    row.style.backgroundColor = "white";
  }
  fileMapping.removeMapping(fileName);
}

// Update change handler
function handleFileUpdate() {
  var fileInput = document.getElementById("fileUpdate");
  var file = fileInput.files[0];
  var selectedFileName = document.getElementById("update_file");
  var fileName = selectedFileName.value;
  handleSelection(fileName);
  if (file) {
    FileUpload(file);
  }
}

// ----------------------------------------- Read File -------------------------------------------//

async function readSelectedFile(fileName) {
  var getFileInformation = fileMapping.getMapping(fileName);
  console.log(getFileInformation);
  var table = document.getElementById("mapping_table");
  var rows = table.getElementsByTagName("tr");
  console.log(getFileInformation.firstRowOfMappingFile);
  console.log(getFileInformation.lastRowOfMappingFile);
  for (
    firstRow = getFileInformation.firstRowOfMappingFile;
    firstRow < getFileInformation.lastRowOfMappingFile;
    firstRow++
  ) {
    var row = rows[firstRow];
    logicalAddress = row.cells[0].innerHTML;
    physicalAddressWithRow = row.cells[1].innerHTML;
    physicalAddressBlockRow = physicalAddressWithRow.charAt(
      physicalAddressWithRow.length - 1
    );
    physicalAddress = physicalAddressWithRow.slice(0, -1);
    console.log(logicalAddress);
    console.log(physicalAddress);
    console.log(physicalAddressBlockRow);
    // Update the table row
    row.style.backgroundColor = "blue";
    blockTable = document.getElementById(physicalAddress);
    blockTable.rows[physicalAddressBlockRow].style.backgroundColor = "blue";
    await new Promise((resolve) => setTimeout(resolve, 1000));
    // make it green again
    row.style.backgroundColor = "green";
    blockTable.rows[physicalAddressBlockRow].style.backgroundColor = "green";
  }
}

var selectedFileName = document.getElementById("read_file");
// Add event listener for the "change" event
selectedFileName.addEventListener("change", function () {
  // Get the selected value
  var fileName = selectedFileName.value;
  // Display the selected value
  console.log("Selected file name: " + fileName);
  readSelectedFile(fileName);
});
