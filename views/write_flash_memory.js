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

  addMapping(fileName, firstRowOfMappingFile, lastRowOfMappingFile) {
    const entry = { fileName, firstRowOfMappingFile, lastRowOfMappingFile };
    this.mappingEntries.push(entry);
    // add the file name to the update select element
    // Get the select element
    var selectElement = document.getElementById("update_file");
    // Create a new option element
    var newOption = document.createElement("option");
    newOption.value = lastRowOfMappingFile;
    newOption.textContent = fileName;
    // Append the new option to the select element
    selectElement.appendChild(newOption);

    // add the file name to the delete select element
    // Get the select element
    var selectElement = document.getElementById("delete_file");
    // Create a new option element
    var newOption = document.createElement("option");
    newOption.value = lastRowOfMappingFile;
    newOption.textContent = fileName;
    // Append the new option to the select element
    selectElement.appendChild(newOption);

    // add the file name to the read select element
    // Get the select element
    var selectElement = document.getElementById("read_file");
    // Create a new option element
    var newOption = document.createElement("option");
    newOption.value = lastRowOfMappingFile;
    newOption.textContent = fileName;
    // Append the new option to the select element
    selectElement.appendChild(newOption);


  }

  removeMapping(fileName) {
    this.mappingEntries = this.mappingEntries.filter(
      (entry) => entry.fileName !== fileName
    );
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
// Read the uploaded file from input onchange
async function handleFileInputChange(e) {
  var fileInput = document.getElementById("fileUpload");
  var file = fileInput.files[0];
  // make delay based on user choice in seconds

  // Check if a file is selected
  if (file) {
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
      const fileMapping = new FileMapping();
      fileMapping.addMapping(file.name, mapping_table_row, 0);
      var logicalAddressTracer = 0;
      // divide the file size by 16kb (block size) to get the number of blocks
      while (fileSizeInKB > 0) {
        // taking a random number
        var random = Math.floor(Math.random() * 32);
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
            block
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
      var getFileInformation =  fileMapping.getMapping(file.name);
      fileMapping.updateMapping(getFileInformation.fileName, getFileInformation.firstRowOfMappingFile, mapping_table_row);
      console.log(fileMapping.getMapping(file.name));
    }

    // divide the file size by 4kb (page size) to get the number of pages
  }
}
