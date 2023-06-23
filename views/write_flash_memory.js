// reading the table row
function readTableRow(tableName, rowNumber, fileSizeInKB) {
  var table = document.getElementById(tableName);
  var rows = table.getElementsByTagName("tr");

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
    if (fileSizeInKB >= 512) {
      alert("File size is too large, please select a file less than 512kb");
      return;
    } else {
      var logicalAddressTracer = 0;
      // divide the file size by 16kb (block size) to get the number of blocks
      while (fileSizeInKB > 0) {
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
          // decrease the file size by 4kb
          fileSizeInKB = (fileSizeInKB - 4).toFixed(2);
          logicalAddressTracer++;
          blockPageTracer++;
        }
      }
      file_tracer++;
    }

    // divide the file size by 4kb (page size) to get the number of pages
  }
}
