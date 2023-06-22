// reading the table row
function readTableRow(tableName, rowNumber, fileSizeInKB) {
  var table = document.getElementById(tableName);
  var rows = table.getElementsByTagName("tr");

  if (rowNumber >= 0 && rowNumber < rows.length) {
    var row = rows[rowNumber];
    row.style.backgroundColor = "red";
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
        row.style.backgroundColor = "red";
        row.cells[0].innerHTML = logicalAddress;
        row.cells[1].innerHTML = physicalAddress;
    } else {
        console.log("Invalid row number.");
    }
    mapping_table_row++;
}
// Read the uploaded file from input onchange
function handleFileInputChange(e) {
  var fileInput = document.getElementById("fileUpload");
  var file = fileInput.files[0];
  // Check if a file is selected
  if (file) {
    // Get the size of the file in bytes
    var fileSize = file.size;

    // Display the file size
    console.log("File Size: " + fileSize + " bytes");
    // Bytes to kb 2 decimal places
    var fileSizeInKB = (fileSize / 1024).toFixed(2);

    // List of block in flash memory (32 blocks)
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

    // taking a random number
    var random = Math.floor(Math.random() * 32);
    // Get the block number from the sequence
    var block = sequence[random];
    // taking a random number for selecting page from 1 to 4
    var randomPage = Math.floor(Math.random() * 3) + 1;
    console.log("Block: " + block);
    console.log("Page: " + randomPage);

    readTableRow(block, randomPage, fileSizeInKB);
    selectRowMappingTable(mapping_table_row, "f"+mapping_table_row, block+randomPage);
  }
}
