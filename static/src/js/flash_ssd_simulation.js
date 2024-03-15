// -----------------------------  Flash SSD Simulation  -----------------------------//
// -----------------------------  Flash SSD Simulation  -----------------------------//
class BlockList {
  constructor() {
    this.block_list = [
      {
        block: "p0d0p0b0ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d0p0b1ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d0p0b2ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d0p0b3ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d0p1b0ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d0p1b1ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d0p1b2ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d0p1b3ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d1p0b0ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d1p0b1ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d1p0b2ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d1p0b3ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d1p1b0ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d1p1b1ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d1p1b2ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p0d1p1b3ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d0p0b0ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d0p0b1ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d0p0b2ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d0p0b3ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d0p1b0ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d0p1b1ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d0p1b2ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d0p1b3ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d1p0b0ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d1p0b1ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d1p0b2ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d1p0b3ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d1p1b0ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d1p1b1ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d1p1b2ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
      {
        block: "p1d1p1b3ct",
        write_count: 0,
        erase_count: 0,
        written_page: [
          { page: 0, data: 0, state: "free" },
          { page: 1, data: 0, state: "free" },
          { page: 2, data: 0, state: "free" },
          { page: 3, data: 0, state: "free" },
        ],
      },
    ];
    this.removed_block_list = [];
  }

  // Add a block object to the block_list
  addBlock(blockObj) {
    this.block_list.push(blockObj);
  }

  // Get a block object from the block_list based on blockName
  getBlockRemoveBlockList(blockName) {
    // console.log(blockName);
    // console.log(blockName);
    return this.removed_block_list.find((block) => block.block === blockName);
  }

  // Get a block object from the block_list based on blockName
  getBlock(blockName) {
    // console.log(blockName);
    // console.log(blockName);
    return this.block_list.find((block) => block.block === blockName);
  }

  // Remove a block from the block_list based on blockName
  removeBlock(blockName) {
    const removedBlock = this.block_list.find(
      (block) => block.block === blockName
    );
    if (removedBlock) {
      this.block_list = this.block_list.filter(
        (block) => block.block !== blockName
      );
      this.removed_block_list.push(removedBlock);
    }
  }

  // Remove a block from the removed_block_list based on blockName
  removeBlockFromRemovedBlockList(blockName) {
    const removedBlock = this.removed_block_list.find(
      (block) => block.block === blockName
    );
    if (removedBlock) {
      this.removed_block_list = this.removed_block_list.filter(
        (block) => block.block !== blockName
      );
      this.block_list.push(removedBlock);
    }
  }

  // Update an existing block in the block_list with an updatedBlockObj
  updateBlock(blockName, updatedBlockObj) {
    this.block_list = this.block_list.map((block) =>
      block.block === blockName ? updatedBlockObj : block
    );
  }

  // Delete all blocks from the block_list
  deleteAllBlocks() {
    this.block_list = [];
    this.removed_block_list = [];
  }
}
// for tracing uploaded file and get later to update, remove or add
const blockList = new BlockList();

// Block information tracer function --------------------------------------------------//
function TraceBlockInformation() {
  dataset = blockList.block_list.concat(blockList.removed_block_list);
  // console.log(dataset);
  var table = document.getElementById("block_information_tracer");
  var tbody = table.getElementsByTagName("tbody")[0];
  while (tbody.firstChild) {
    tbody.removeChild(tbody.firstChild);
  }
  // Iterate through the dataset and dynamically create table rows
  dataset.forEach(function (entry) {
    var block = entry.block;
    var writeCount = entry.write_count;
    var eraseCount = entry.erase_count;
    // console.log(entry);

    entry.written_page.forEach(function (pageData) {
      var row = document.createElement("tr");

      var blockCell = document.createElement("td");
      blockCell.textContent = block;
      row.appendChild(blockCell);

      var writeCountCell = document.createElement("td");
      writeCountCell.textContent = writeCount;
      row.appendChild(writeCountCell);

      var eraseCountCell = document.createElement("td");
      eraseCountCell.textContent = eraseCount;
      row.appendChild(eraseCountCell);

      var pageCell = document.createElement("td");
      pageCell.textContent = pageData.page;
      row.appendChild(pageCell);

      var dataCell = document.createElement("td");
      dataCell.textContent = pageData.data;
      row.appendChild(dataCell);

      var dataCell = document.createElement("td");
      dataCell.textContent = pageData.state;
      row.appendChild(dataCell);

      tbody.appendChild(row);
    });
  });
}

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
var globalFileSize = 512;
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
  // console.log(tableName);
  var table = document.getElementById(tableName);
  var rows = table.getElementsByTagName("tr");
  scrollToSelectedRow(table);
  if (rowNumber >= 0 && rowNumber < rows.length) {
    var row = rows[rowNumber];
    row.style.backgroundColor = "green";
    row.cells[0].innerHTML = fileSizeInKB + "kb";
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
// garbage collection update mapping table
async function garbageUpdateMappingTable(
  garbageFileName,
  logicalAddressTracer,
  block,
  blockPageTracer
) {
  var table = document.getElementById("mapping_table");
  var rows = table.getElementsByTagName("tr");
  // remove "garbage" from string
  logical_address_with_page_info = garbageFileName.replace("garbage", "");
  // remove pageinfo from string
  logical_address = logical_address_with_page_info.substring(0, 10);
  page_info = logical_address_with_page_info.substring(10);
  page_number = page_info[logicalAddressTracer];

  for (i = 0; i < rows.length; i++) {
    // if logical address is found in the mapping table
    if (rows[i].cells[1].innerHTML == logical_address + page_number) {
      rows[i].style.backgroundColor = "yellow";
      rows[i].cells[1].innerHTML = block + blockPageTracer;
      // sleep for 1 second
      await new Promise((resolve) => setTimeout(resolve, 1000));
      break;
    }
  }
}

// Selected ssd type normal/ parallel
var ssdType = document.getElementById("ssd_type");
function getRandomBlockParallel(blocks, prefix) {
  console.log(blocks);
  const filteredBlocks = blocks.filter((block) =>
    block.block.startsWith(prefix)
  );
  const randomIndex = Math.floor(Math.random() * filteredBlocks.length);
  return filteredBlocks[randomIndex];
}
// File tracer from logical address
var file_tracer = 0;
async function FileUpload(fileSize, fileName, fileIndex) {
  // Bytes to kb 2 decimal places
  var fileSizeInKB = (fileSize / 1024).toFixed(2);
  if (fileSizeInKB >= globalFileSize) {
    alert("File size is too large, please select a file less than 512kb");
    return;
  } else {
    garbage_file_cheker = fileName.includes("garbage");
    if (!garbage_file_cheker) {
      fileMapping.addMapping(fileName, mapping_table_row, 0);
    }

    var logicalAddressTracer = 0;
    // divide the file size by 16kb (block size) to get the number of blocks
    var while_loop_tracer = 0;
    while (fileSizeInKB > 0) {
      if (fileIndex == 2) {
        // taking a random number from the block list
        var random = Math.floor(Math.random() * blockList.block_list.length);
        // var random = Math.floor(Math.random() * blockList.length);
        // Get the block number from the sequence
        var block = blockList.block_list[random];
      } else if (fileIndex == "s1") {
        // take down value of the division
        var n_channel = 2;
        var n_chip = 1;
        var n_die = 2;
        var n_plane = 2;

        var channel =
          Math.floor(while_loop_tracer / (n_plane * n_die * n_chip)) %
          n_channel;
        var chip = while_loop_tracer % n_chip;
        var die = Math.floor(while_loop_tracer / n_chip) % n_die;
        var plane = Math.floor(while_loop_tracer / (n_die * n_chip)) % n_plane;
        var block_ =
          Math.floor(
            while_loop_tracer / (n_plane * n_die * n_chip * n_channel)
          ) % 4;
        // var channel = (logicalAddressTracer/(1*2*2))%2;
        console.log(
          "channel: " +
            channel +
            " chip: " +
            chip +
            " die: " +
            die +
            " plane: " +
            plane +
            " block: " +
            block_
        );
        // var random = Math.floor(Math.random() * blockList.block_list.length);
        // var random = Math.floor(Math.random() * blockList.length);
        // Get the block number from the sequence
        var block = getRandomBlockParallel(
          blockList.block_list,
          "p" + channel + "d" + die + "p" + plane + "b" + block_
        );
      } else if (fileIndex == "s2") {
        // take down value of the division
        var n_channel = 2;
        var n_chip = 1;
        var n_die = 2;
        var n_plane = 2;

        var channel = while_loop_tracer % n_channel;
        var chip = Math.floor(while_loop_tracer / n_channel) % n_chip;
        var die = Math.floor(while_loop_tracer / (n_chip * n_channel)) % n_die;
        var plane =
          Math.floor(while_loop_tracer / (n_die * n_chip * n_channel)) %
          n_plane;
        var block_ =
          Math.floor(
            while_loop_tracer / (n_plane * n_die * n_chip * n_channel)
          ) % 4;
        // var channel = (logicalAddressTracer/(1*2*2))%2;
        console.log(
          "channel: " +
            channel +
            " chip: " +
            chip +
            " die: " +
            die +
            " plane: " +
            plane +
            " block: " +
            block_
        );
        // var random = Math.floor(Math.random() * blockList.block_list.length);
        // var random = Math.floor(Math.random() * blockList.length);
        // Get the block number from the sequence
        var block = getRandomBlockParallel(
          blockList.block_list,
          "p" + channel + "d" + die + "p" + plane + "b" + block_
        );
      } else if (fileIndex == "s3") {
        // take down value of the division
        var n_channel = 2;
        var n_chip = 1;
        var n_die = 2;
        var n_plane = 2;

        var channel = while_loop_tracer % n_channel;
        var chip =
          Math.floor(while_loop_tracer / (n_plane * n_channel)) % n_chip;
        var die =
          Math.floor(while_loop_tracer / (n_plane * n_chip * n_channel)) %
          n_die;
        var plane = Math.floor(while_loop_tracer / n_channel) % n_plane;
        var block_ =
          Math.floor(
            while_loop_tracer / (n_plane * n_die * n_chip * n_channel)
          ) % 4;
        // var channel = (logicalAddressTracer/(1*2*2))%2;
        console.log(
          "channel: " +
            channel +
            " chip: " +
            chip +
            " die: " +
            die +
            " plane: " +
            plane +
            " block: " +
            block_
        );
        // var random = Math.floor(Math.random() * blockList.block_list.length);
        // var random = Math.floor(Math.random() * blockList.length);
        // Get the block number from the sequence
        var block = getRandomBlockParallel(
          blockList.block_list,
          "p" + channel + "d" + die + "p" + plane + "b" + block_
        );
      } else if (fileIndex == "s4") {
        // take down value of the division
        var n_channel = 2;
        var n_chip = 1;
        var n_die = 2;
        var n_plane = 2;

        var channel = while_loop_tracer % n_channel;
        var chip = Math.floor(while_loop_tracer / (n_die * n_channel)) % n_chip;
        var die = Math.floor(while_loop_tracer / n_channel) % n_die;
        var plane =
          Math.floor(while_loop_tracer / (n_die * n_chip * n_channel)) %
          n_plane;
        var block_ =
          Math.floor(
            while_loop_tracer / (n_plane * n_die * n_chip * n_channel)
          ) % 4;
        // var channel = (logicalAddressTracer/(1*2*2))%2;
        console.log(
          "channel: " +
            channel +
            " chip: " +
            chip +
            " die: " +
            die +
            " plane: " +
            plane +
            " block: " +
            block_
        );
        // var random = Math.floor(Math.random() * blockList.block_list.length);
        // var random = Math.floor(Math.random() * blockList.length);
        // Get the block number from the sequence
        var block = getRandomBlockParallel(
          blockList.block_list,
          "p" + channel + "d" + die + "p" + plane + "b" + block_
        );
      } else if (fileIndex == "s5") {
        // take down value of the division
        var n_channel = 2;
        var n_chip = 1;
        var n_die = 2;
        var n_plane = 2;

        var channel = while_loop_tracer % n_channel;
        var chip =
          Math.floor(while_loop_tracer / (n_plane * n_die * n_channel)) %
          n_chip;
        var die = Math.floor(while_loop_tracer / (n_plane * n_channel)) % n_die;
        var plane = Math.floor(while_loop_tracer / n_channel) % n_plane;
        var block_ =
          Math.floor(
            while_loop_tracer / (n_plane * n_die * n_chip * n_channel)
          ) % 4;
        // var channel = (logicalAddressTracer/(1*2*2))%2;
        console.log(
          "channel: " +
            channel +
            " chip: " +
            chip +
            " die: " +
            die +
            " plane: " +
            plane +
            " block: " +
            block_
        );
        // var random = Math.floor(Math.random() * blockList.block_list.length);
        // var random = Math.floor(Math.random() * blockList.length);
        // Get the block number from the sequence
        var block = getRandomBlockParallel(
          blockList.block_list,
          "p" + channel + "d" + die + "p" + plane + "b" + block_
        );
      } else if (fileIndex == "s6") {
        // take down value of the division
        var n_channel = 2;
        var n_chip = 1;
        var n_die = 2;
        var n_plane = 2;

        var channel = while_loop_tracer % n_channel;
        var chip =
          Math.floor(while_loop_tracer / (n_plane * n_die * n_channel)) %
          n_chip;
        var die = Math.floor(while_loop_tracer / n_channel) % n_die;
        var plane =
          Math.floor(while_loop_tracer / (n_die * n_channel)) % n_plane;
        var block_ =
          Math.floor(
            while_loop_tracer / (n_plane * n_die * n_chip * n_channel)
          ) % 4;
        // var channel = (logicalAddressTracer/(1*2*2))%2;
        console.log(
          "channel: " +
            channel +
            " chip: " +
            chip +
            " die: " +
            die +
            " plane: " +
            plane +
            " block: " +
            block_
        );
        // var random = Math.floor(Math.random() * blockList.block_list.length);
        // var random = Math.floor(Math.random() * blockList.length);
        // Get the block number from the sequence
        var block = getRandomBlockParallel(
          blockList.block_list,
          "p" + channel + "d" + die + "p" + plane + "b" + block_
        );
      } else {
        var block = getRandomBlockParallel(blockList.block_list, fileIndex);
      }

      // console.log(block);
      // Get the block page tracer from the correct page
      var blockPageTracer = 0;
      console.log(block);
      for (i = 0; i < block.written_page.length; i++) {
        if (block.written_page[i].data == 0) {
          blockPageTracer = i + 1;
          break;
        }
      }
      // divide the file size by 4kb (page size) to get the number of pages
      while (fileSizeInKB > 0 && blockPageTracer <= 4) {
        if (fileSizeInKB < 4) {
          readTableRow(block["block"], blockPageTracer, fileSizeInKB);
          // update the block page
          block["written_page"][blockPageTracer - 1]["data"] = fileSizeInKB;
          block["written_page"][blockPageTracer - 1]["state"] = "valid";
          globalFileSize = globalFileSize - 4;
        } else {
          readTableRow(block["block"], blockPageTracer, 4);
          // update the block page
          block["written_page"][blockPageTracer - 1]["data"] = 4;
          block["written_page"][blockPageTracer - 1]["state"] = "valid";
          // console.log(block);
          globalFileSize = globalFileSize - 4;
        }

        if (garbage_file_cheker) {
          garbageUpdateMappingTable(
            fileName,
            logicalAddressTracer,
            block["block"],
            blockPageTracer
          );
        } else {
          // Select the row in the mapping table
          selectRowMappingTable(
            mapping_table_row,
            "f" + file_tracer + logicalAddressTracer,
            block["block"] + blockPageTracer
          );
        }

        // Save the filename, logical address and mapping_table_row in the java class
        // decrease the file size by 4kb
        fileSizeInKB = (fileSizeInKB - 4).toFixed(2);
        logicalAddressTracer++;
        blockPageTracer++;
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      // Remove the block from the sequence
      if (blockPageTracer === 5) {
        // remove the block from the block list
        // blockList.block_list.splice(random, 1);

        // add the removed block to the removed_block list by updating the write count and erase count
        block["write_count"]++;
        blockList.removed_block_list.push(block);
      } else {
        // blockList.block_list.splice(random, 1);
        // add the removed block to the removed_block list by updating the write count and erase count
        block["write_count"]++;
        // blockList.removed_block_list.push(block);
      }
      while_loop_tracer++;
    }
    if (!garbage_file_cheker) {
      file_tracer++;
      var getFileInformation = fileMapping.getMapping(fileName);
      fileMapping.updateMapping(
        getFileInformation.fileName,
        getFileInformation.firstRowOfMappingFile,
        mapping_table_row
      );
    }
    // console.log(fileMapping.getMapping(file.name));
    TraceBlockInformation();
  }

  // divide the file size by 4kb (page size) to get the number of pages
}

class cacheStorage {
  constructor() {
    this.cacheStorage = [
      {
        cacheRegisterId: "progress_p0d0p0",
        cacheRegisterValue: 0, // max value 4kb = 4096
      },
      {
        cacheRegisterId: "progress_p0d0p1",
        cacheRegisterValue: 0, // max value 4kb = 4096
      },
      {
        cacheRegisterId: "progress_p0d1p0",
        cacheRegisterValue: 0, // max value 4kb = 4096
      },
      {
        cacheRegisterId: "progress_p0d1p1",
        cacheRegisterValue: 0, // max value 4kb = 4096
      },
      {
        cacheRegisterId: "progress_p1d0p0",
        cacheRegisterValue: 0, // max value 4kb = 4096
      },
      {
        cacheRegisterId: "progress_p1d0p1",
        cacheRegisterValue: 0, // max value 4kb = 4096
      },
      {
        cacheRegisterId: "progress_p1d1p0",
        cacheRegisterValue: 0, // max value 4kb = 4096
      },
      {
        cacheRegisterId: "progress_p1d1p1",
        cacheRegisterValue: 0, // max value 4kb = 4096
      },
    ];
  }
  updateCacheRegister(cacheRegisterId, cacheRegisterValue) {
    this.cacheStorage.forEach((element) => {
      if (element.cacheRegisterId === cacheRegisterId) {
        cacheStorager.cacheStorage[i].cacheRegisterValue = cacheRegisterValue;
      }
    });
  }
  getCacheRegisterValue(cacheRegisterId) {
    var cacheRegisterValue = 0;
    this.cacheStorage.forEach((element) => {
      if (element.cacheRegisterId === cacheRegisterId) {
        cacheRegisterValue = cacheStorager.cacheStorage[i].cacheRegisterValue;
      }
    });
    return cacheRegisterValue;
  }
  // clear cacheStorage
  clearCacheStorage() {
    this.cacheStorage.forEach((element) => {
      element.cacheRegisterValue = 0;
      document.getElementById(element.cacheRegisterId).style.width = "0%";
    });
  }
}
const cacheStorager = new cacheStorage();
// Read the uploaded file from input onchange
async function handleFileInputChangeChache() {
  var fileInput = document.getElementById("fileUpload");
  var file = fileInput.files[0];
  if (file) {
    var fileSize = file.size;
    if (fileSize > 1) {
      handleFileInputChange(file);
    } else if (fileSize % 4096 == 0) {
      handleFileInputChange(file);
    } else {
      var totalFileSizeTracer = 0;
      for (let i = 0; i < 8; i++) {
        if (cacheStorager.cacheStorage[i].cacheRegisterValue < 4096) {
          while (fileSize > 0) {
            fileSize = fileSize - 4;
            // console.log(fileSize);
            cacheStorager.cacheStorage[i].cacheRegisterValue =
              cacheStorager.cacheStorage[i].cacheRegisterValue + 4;
            // console.log(cacheStorager.cacheStorage[i].cacheRegisterValue);
            document.getElementById(
              cacheStorager.cacheStorage[i].cacheRegisterId
            ).style.width =
              cacheStorager.cacheStorage[i].cacheRegisterValue / 40.96 + "%";

            if (cacheStorager.cacheStorage[i].cacheRegisterValue == 4096) {
              break;
            }
            await new Promise((resolve) => setTimeout(resolve, 1));
          }
          totalFileSizeTracer =
            totalFileSizeTracer +
            cacheStorager.cacheStorage[i].cacheRegisterValue;
          console.log(totalFileSizeTracer);
          if (fileSize == 0) {
            break;
          }
        } else {
          totalFileSizeTracer = totalFileSizeTracer + 4096;
        }
      }
      if (fileSize > 0) {
        handleFileInputChange({
          size: totalFileSizeTracer + fileSize,
          name: "combiner_file_buffer",
        });
        cacheStorager.clearCacheStorage();
      }

      if (totalFileSizeTracer % 4096 > 3000) {
        handleFileInputChange({
          size: totalFileSizeTracer,
          name: "combiner_file_buffer",
        });
        cacheStorager.clearCacheStorage();
      }
    }
  }
}
async function handleFileInputChange(file) {
  // var fileInput = document.getElementById("fileUpload");
  // var file = fileInput.files[0];
  if (file) {
    var fileSize = file.size;

    if (ssdType.value == "single") {
      FileUpload(fileSize, file.name, 2);
    }
    // ssdType.value contain multi then it is multi plane
    else if (ssdType.value.includes("multi")) {
      const promises = [];
      // Number of planes selection get the uppoer value
      var numberOfPlanes = Math.ceil(fileSize / (4096 * 4));
      // select the plane
      var packag_selector = 0;
      var die_selector = 0;
      var plane_selector = 0;

      for (let i = 0; i < numberOfPlanes; i++) {
        // if i dived by 4 is integer then change the package
        if (i % 4 == 0) {
          packag_selector = (i / 4) % 2;
        }
        if (i % 2 == 0) {
          die_selector = (i / 2) % 2;
        }
        plane_selector = i % 2;
        if (ssdType.value == "pdpmulti") {
          promises.push(
            FileUpload(
              fileSize / numberOfPlanes,
              file.name,
              "p" + packag_selector + "d" + die_selector + "p" + plane_selector
            )
          );
        } else if (ssdType.value == "pdmulti") {
          promises.push(
            FileUpload(
              fileSize / numberOfPlanes,
              file.name,
              "p" + packag_selector + "d" + die_selector
            )
          );
        } else if (ssdType.value == "pmulti") {
          promises.push(
            FileUpload(fileSize / numberOfPlanes, file.name, "p" + (i % 2))
          );
        }
      }

      await Promise.all(promises);

      // if the file name is similar in update delete and read remove duplicate slection name
      var selectElement = document.getElementById("update_file");
      var optionToRemove = file.name;
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
      var optionToRemove = file.name;
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
      var optionToRemove = file.name;
      for (let i = 0; i < selectElement.options.length; i++) {
        if (selectElement.options[i].text === optionToRemove) {
          selectElement.remove(i);
          break;
        }
      }
    } else {
      FileUpload(fileSize, file.name, ssdType.value);
    }
  }
}

// ----------------------------------------- Update File -------------------------------------------//

async function handleSelection(fileName) {
  // const fileMapping = new FileMapping();
  var getFileInformation = fileMapping.getMapping(fileName);

  // console.log(getFileInformation);
  var table = document.getElementById("mapping_table");
  var rows = table.getElementsByTagName("tr");
  // console.log(getFileInformation.firstRowOfMappingFile);
  // console.log(getFileInformation.lastRowOfMappingFile);
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
    // Update the table row
    row.style.backgroundColor = "yellow";
    blockTable = document.getElementById(physicalAddress);
    blockTable.rows[physicalAddressBlockRow].style.backgroundColor = "yellow";
    // Get the block mapping table to update the page state
    var block = blockList.getBlockRemoveBlockList(physicalAddress);
    // If the block is not in the removed block list then get it from the block list
    if (block == undefined) {
      block = blockList.getBlock(physicalAddress);
    }
    block["written_page"][physicalAddressBlockRow - 1]["state"] = "invalid";
    // update the block page tracer
    TraceBlockInformation();
    await new Promise((resolve) => setTimeout(resolve, 1000));
    row.cells[0].innerHTML = "";
    row.cells[1].innerHTML = "";
    row.style.backgroundColor = "white";
  }
  fileMapping.removeMapping(fileName);
}

// Update change handler
async function handleFileUpdate() {
  var fileInput = document.getElementById("fileUpdate");
  var file = fileInput.files[0];
  var selectedFileName = document.getElementById("update_file");
  var fileName = selectedFileName.value;
  handleSelection(fileName);
  if (file) {
    var fileSize = file.size;
    if (ssdType.value == "single") {
      // check the file is devideable by 4kb
      // alert("File size should be devided by 4kb");
      console.log(fileSize % 4096);
      console.log(fileSize % 4096);
      console.log(fileSize % 4096);
      console.log(fileSize % 4096);
      console.log(fileSize % 4096);
      console.log(fileSize % 4096);
      if (fileSize % 4096 != 0) {
        // alert("File size should be devided by 4kb");
        return;
      }
      FileUpload(fileSize, file.name, 2);
    } else {
      const promises = [
        FileUpload(fileSize / 2, file.name, 0),
        FileUpload(fileSize / 2, file.name, 1),
      ];
      await Promise.all(promises);
    }
  }
}

// ----------------------------------------- Read File -------------------------------------------//

async function readSelectedFile(fileName) {
  var getFileInformation = fileMapping.getMapping(fileName);
  // console.log(getFileInformation);
  var table = document.getElementById("mapping_table");
  var rows = table.getElementsByTagName("tr");
  // console.log(getFileInformation.firstRowOfMappingFile);
  // console.log(getFileInformation.lastRowOfMappingFile);
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
    // console.log(logicalAddress);
    // console.log(physicalAddress);
    // console.log(physicalAddressBlockRow);
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

var readSelectedFileName = document.getElementById("read_file");
// Add event listener for the "change" event
readSelectedFileName.addEventListener("change", function () {
  // Get the selected value
  var fileName = readSelectedFileName.value;
  // Display the selected value
  // console.log("Selected file name: " + fileName);
  readSelectedFile(fileName);
});

// ----------------------------------------- Delete File -------------------------------------------//
var selectedFileName = document.getElementById("delete_file");
// Add event listener for the "change" event
selectedFileName.addEventListener("change", function () {
  // Get the selected value
  var fileName = selectedFileName.value;
  // Display the selected value
  // console.log("Selected file name: " + fileName);
  handleSelection(fileName);
});

// ----------------------------------------- Garbage Collection -----------------------------------------//

async function garbageCollection() {
  // console.log("Garbage Collection");
  // get removed block elements from the garbage collection
  var removedBlockElements = blockList.removed_block_list;
  // console.log(removedBlockElements);
  // get the removed block elements
  for (var i = 0; i < removedBlockElements.length; i++) {
    var removedBlock = removedBlockElements[i];
    // console.log(removedBlock);
    // get the block table id and page number from block address
    var blockAddress = removedBlock["block"];
    // console.log(blockAddress);
    // console.log(blockAddress);
    // get the table using the block address
    var blockTable = document.getElementById(blockAddress);

    if (
      removedBlock.written_page[0].state == "invalid" &&
      removedBlock.written_page[1].state == "invalid" &&
      removedBlock.written_page[2].state == "invalid" &&
      removedBlock.written_page[3].state == "invalid"
    ) {
      var row1 = blockTable.rows[removedBlock.written_page[0].page + 1];
      row1.style.backgroundColor = "red";
      row1.cells[0].innerHTML = "";
      removedBlock.written_page[0].data = 0;
      await new Promise((resolve) => setTimeout(resolve, 1000));
      row1.style.backgroundColor = "white";
      var row2 = blockTable.rows[removedBlock.written_page[1].page + 1];
      row2.style.backgroundColor = "red";
      row2.cells[0].innerHTML = "";
      removedBlock.written_page[1].data = 0;
      await new Promise((resolve) => setTimeout(resolve, 1000));
      row2.style.backgroundColor = "white";
      var row3 = blockTable.rows[removedBlock.written_page[2].page + 1];
      row3.style.backgroundColor = "red";
      row3.cells[0].innerHTML = "";
      removedBlock.written_page[2].data = 0;
      await new Promise((resolve) => setTimeout(resolve, 1000));
      row3.style.backgroundColor = "white";
      var row4 = blockTable.rows[removedBlock.written_page[3].page + 1];
      row4.style.backgroundColor = "red";
      row4.cells[0].innerHTML = "";
      removedBlock.written_page[3].data = 0;
      await new Promise((resolve) => setTimeout(resolve, 1000));
      row4.style.backgroundColor = "white";
      removedBlock.erase_count++;
      // remove the block from the removed block list and add it to the block list
      blockList.removeBlockFromRemovedBlockList(blockAddress);
    } else if (
      removedBlock.written_page[0].state == "invalid" &&
      removedBlock.written_page[1].state == "invalid" &&
      removedBlock.written_page[2].state == "invalid"
    ) {
      var row1 = blockTable.rows[removedBlock.written_page[0].page + 1];
      row1.style.backgroundColor = "red";
      row1.cells[0].innerHTML = "";
      removedBlock.written_page[0].data = 0;
      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row1.style.backgroundColor = "white";
      var row2 = blockTable.rows[removedBlock.written_page[1].page + 1];
      row2.style.backgroundColor = "red";
      row2.cells[0].innerHTML = "";
      removedBlock.written_page[1].data = 0;
      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row2.style.backgroundColor = "white";
      var row3 = blockTable.rows[removedBlock.written_page[2].page + 1];
      row3.style.backgroundColor = "red";
      row3.cells[0].innerHTML = "";
      removedBlock.written_page[2].data = 0;
      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row3.style.backgroundColor = "white";
      var row4 = blockTable.rows[removedBlock.written_page[3].page + 1];
      row4.style.backgroundColor = "red";
      row4.cells[0].innerHTML = "";
      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row4.style.backgroundColor = "white";
      removedBlock.erase_count++;
      var garbage_collection_tracer = "garbage" + removedBlock["block"] + "4";
      FileUpload(
        removedBlock.written_page[3].data * 1024,
        garbage_collection_tracer,
        2
      );
      removedBlock.written_page[3].data = 0;
      blockList.removeBlockFromRemovedBlockList(blockAddress);
    } else if (
      removedBlock.written_page[0].state == "invalid" &&
      removedBlock.written_page[1].state == "invalid"
    ) {
      var row1 = blockTable.rows[removedBlock.written_page[0].page + 1];
      row1.style.backgroundColor = "red";
      row1.cells[0].innerHTML = "";
      removedBlock.written_page[0].data = 0;
      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row1.style.backgroundColor = "white";
      var row2 = blockTable.rows[removedBlock.written_page[1].page + 1];
      row2.style.backgroundColor = "red";
      row2.cells[0].innerHTML = "";
      removedBlock.written_page[1].data = 0;
      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row2.style.backgroundColor = "white";
      var row3 = blockTable.rows[removedBlock.written_page[2].page + 1];
      row3.style.backgroundColor = "red";
      row3.cells[0].innerHTML = "";

      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row3.style.backgroundColor = "white";
      var row4 = blockTable.rows[removedBlock.written_page[3].page + 1];
      row4.style.backgroundColor = "red";
      row4.cells[0].innerHTML = "";

      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row4.style.backgroundColor = "white";
      removedBlock.erase_count++;
      var garbage_collection_tracer = "garbage" + removedBlock["block"] + "34";
      FileUpload(
        (removedBlock.written_page[2].data +
          removedBlock.written_page[3].data) *
          1024,
        garbage_collection_tracer,
        2
      );
      removedBlock.written_page[2].data = 0;
      removedBlock.written_page[3].data = 0;
      blockList.removeBlockFromRemovedBlockList(blockAddress);
    } else if (removedBlock.written_page[0].state == "invalid") {
      var row1 = blockTable.rows[removedBlock.written_page[0].page + 1];
      row1.style.backgroundColor = "red";
      row1.cells[0].innerHTML = "";
      removedBlock.written_page[0].data = 0;
      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row1.style.backgroundColor = "white";
      var row2 = blockTable.rows[removedBlock.written_page[1].page + 1];
      row2.style.backgroundColor = "red";
      row2.cells[0].innerHTML = "";
      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row2.style.backgroundColor = "white";
      var row3 = blockTable.rows[removedBlock.written_page[2].page + 1];
      row3.style.backgroundColor = "red";
      row3.cells[0].innerHTML = "";
      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row3.style.backgroundColor = "white";
      var row4 = blockTable.rows[removedBlock.written_page[3].page + 1];
      row4.style.backgroundColor = "red";
      row4.cells[0].innerHTML = "";
      // await new Promise((resolve) => setTimeout(resolve, 1000));
      row4.style.backgroundColor = "white";
      removedBlock.erase_count++;
      var garbage_collection_tracer = "garbage" + removedBlock["block"] + "234";
      FileUpload(
        (removedBlock.written_page[1].data +
          removedBlock.written_page[2].data +
          removedBlock.written_page[3].data) *
          1024,
        garbage_collection_tracer,
        2
      );
      removedBlock.written_page[1].data = 0;
      removedBlock.written_page[2].data = 0;
      removedBlock.written_page[3].data = 0;
      blockList.removeBlockFromRemovedBlockList(blockAddress);
    }
  }
}

//-------------------------------------  Flash Memory Design ------------------------------------//
//-------------------------------------  Flash Memory Design ------------------------------------//
window.onload = function () {
  calculateFlashMemorySize();
};

// Objective: Flash memory page
// Get the select element
var select = document.getElementById("pageCount");
// Add event listener for the "change" event
select.addEventListener("change", function () {
  // Get the selected value
  var selectedValue = select.value;

  // Perform actions based on the selected value
  if (selectedValue === "2") {
    // Code to execute when the value "16" is selected
    // console.log("Selected value is 16");
  } else if (selectedValue === "4") {
    // Code to execute when the value "32" is selected
    // console.log("Selected value is 32");
  }
});

// --------------------------------------Flash memory Block----------------------------------------------------------//
var blockSelect = document.getElementById("blockCount");
// Add event listener for the "change" event
blockSelect.addEventListener("change", function () {
  // Get the selected value
  var blockValue = blockSelect.value;
  // Perform actions based on the selected value
  blockList.block_list = blockList.block_list.concat(
    blockList.removed_block_list
  );
  if (blockValue === "1") {
    // get the block from blockList where block contain b1, b2, b3 through loop
    var removed_list = [];
    // Add two list

    var length_of_the_list = blockList.block_list.length;
    for (var i = 0; i < length_of_the_list; i++) {
      // select block contain b1, b2, b3
      if (
        blockList.block_list[i].block.includes("b1") ||
        blockList.block_list[i].block.includes("b2") ||
        blockList.block_list[i].block.includes("b3")
      ) {
        // hide the block
        document.getElementById(blockList.block_list[i].block).style.display =
          "none";
        // remove the block
        removed_list.push(blockList.block_list[i].block);
      }
    }
    // remove the block from blockList
    for (var i = 0; i < removed_list.length; i++) {
      blockList.removeBlock(removed_list[i]);
      console.log(blockList);
      // console.log(blockList.block_list.length);
      // console.log(blockList.removed_block_list.length);
    }
  } else if (blockValue === "2") {
    // Code to execute when the value "32" is selected
    var removed_list = [];
    var length_of_the_list = blockList.block_list.length;
    for (var i = 0; i < length_of_the_list; i++) {
      if (
        blockList.block_list[i].block.includes("b2") ||
        blockList.block_list[i].block.includes("b3")
      ) {
        document.getElementById(blockList.block_list[i].block).style.display =
          "none";
        removed_list.push(blockList.block_list[i].block);
      } else {
        document.getElementById(blockList.block_list[i].block).style.display =
          "table";
      }
    }
    // remove the block from blockList
    for (var i = 0; i < removed_list.length; i++) {
      blockList.removeBlock(removed_list[i]);
      // console.log(blockList.block_list.length);
      // console.log(blockList.removed_block_list.length);
    }
  } else if (blockValue === "4") {
    // Code to execute when the value "32" is selected
    for (var i = 0; i < blockList.block_list.length; i++) {
      document.getElementById(blockList.block_list[i].block).style.display =
        "table";
    }
  }
  calculateFlashMemorySize();
});

// --------------------------------------Flash memory Plane----------------------------------------------------------//
var planeSelect = document.getElementById("planeCount");
// Add event listener for the "change" event
planeSelect.addEventListener("change", function () {
  // Get the selected value
  var planeValue = planeSelect.value;
  // console.log(planeValue);
  var planeTable1 = document.getElementById("p0d0p1ct");
  var planeTable2 = document.getElementById("p0d1p1ct");
  var planeTable3 = document.getElementById("p1d0p1ct");
  var planeTable4 = document.getElementById("p1d1p1ct");
  // Perform actions based on the selected value
  if (planeValue === "1") {
    // Code to execute when the value "16" is selected
    planeTable1.style.display = "none";
    planeTable2.style.display = "none";
    planeTable3.style.display = "none";
    planeTable4.style.display = "none";
  } else if (planeValue === "2") {
    // Code to execute when the value "32" is selected
    planeTable1.style.display = "table";
    planeTable2.style.display = "table";
    planeTable3.style.display = "table";
    planeTable4.style.display = "table";
  }
  calculateFlashMemorySize();
});

// ---------------------------------------Flash memory Die---------------------------------------------------------//
var dieSelect = document.getElementById("dieCount");
// Add event listener for the "change" event
dieSelect.addEventListener("change", function () {
  // Get the selected value
  var dieValue = dieSelect.value;
  var table1 = document.getElementById("p0d1ct");
  var table2 = document.getElementById("p1d1ct");
  if (dieValue === "1") {
    // Code to execute when the value "16" is selected
    table1.style.display = "none";
    table2.style.display = "none";
  }
  // Perform actions based on the selected value
  else if (dieValue === "2") {
    // Code to execute when the value "32" is selected
    table1.style.display = "table";
    table2.style.display = "table";
  }
  calculateFlashMemorySize();
});

// ------------------------------------------Flash memory Package------------------------------------------------------//
var packageSelect = document.getElementById("packageCount");
// Add event listener for the "change" event
packageSelect.addEventListener("change", function () {
  // Get the selected value
  var packageValue = packageSelect.value;
  var packageTable = document.getElementById("p0ct");
  // Perform actions based on the selected value
  if (packageValue === "1") {
    // Code to execute when the value "16" is selected
    packageTable.style.display = "none";
  } else if (packageValue === "2") {
    // Code to execute when the value "32" is selected
    packageTable.style.display = "table";
  }
  calculateFlashMemorySize();
});

// create a function to calculate the size of the flash memory
function calculateFlashMemorySize() {
  var pageSize = 4;
  var pageCount = document.getElementById("pageCount").value;
  var blockCount = document.getElementById("blockCount").value;
  var planeCount = document.getElementById("planeCount").value;
  var dieCount = document.getElementById("dieCount").value;
  var packageCount = document.getElementById("packageCount").value;

  var block = document.getElementById("blockSize");
  block.textContent = pageSize * pageCount + "kb";
  var plane = document.getElementById("planeSize");
  plane.textContent = pageSize * pageCount * blockCount + "kb";
  var die = document.getElementById("dieSize");
  die.textContent = pageSize * pageCount * blockCount * planeCount + "kb";
  var package = document.getElementById("packageSize");
  package.textContent =
    pageSize * pageCount * blockCount * planeCount * dieCount + "kb";
  var flashSSDSize = document.getElementById("flashSSDSize");
  flashSSDSize.textContent =
    pageSize * pageCount * blockCount * planeCount * dieCount * packageCount +
    "kb";

  globalFileSize =
    pageSize * pageCount * blockCount * planeCount * dieCount * packageCount;
  // create mapping table based on the number of block
  var mapping_table = document.getElementById("mapping_table");
  var rows = mapping_table.getElementsByTagName("tr");

  // Start from the second row (index 1) to avoid removing the header row
  for (var i = rows.length - 1; i > 0; i--) {
    var row = rows[i];
    row.parentNode.removeChild(row);
  }
  var n = pageCount * blockCount * planeCount * dieCount * packageCount; // Number of rows to create

  for (var i = 1; i <= n; i++) {
    var row = document.createElement("tr");
    var cell1 = document.createElement("td");
    var cell2 = document.createElement("td");

    cell1.textContent = "";
    cell2.textContent = "";

    cell1.setAttribute("class", "la");
    cell2.setAttribute("class", "pa");

    cell1.setAttribute("id", "la" + i);
    cell2.setAttribute("id", "pa" + i);

    cell1.setAttribute("style", "font-size: 10px");
    cell2.setAttribute("style", "font-size: 10px");

    row.appendChild(cell1);
    row.appendChild(cell2);
    mapping_table.appendChild(row);
  }
  document.getElementById("mapping_table_entries").textContent = n;
}

// make a div full screen
var fullscreenBtn = document.getElementById("fullscreen");
fullscreenBtn.addEventListener("click", function () {
  var myDiv = document.getElementById("fullscreen_div");
  myDiv.classList.toggle("fullscreen");
});

// Trim function
function checkActiveTrim() {
  const activeTrimCheckbox = document.getElementById("active_trim");

  if (activeTrimCheckbox.checked) {
    garbageCollection();
  } else {
    console.log("Active Trim is OFF");
  }
}

// Call the checkActiveTrim function initially
checkActiveTrim();

// Set up an interval to check the state every 10 seconds (10000 milliseconds)
setInterval(checkActiveTrim, 10000);

// ------------------------------------------Write Amplification Factor------------------------------------------------------//
var xyValues = [
  { x: 50, y: 2 },
  { x: 60, y: 2.5 },
  { x: 70, y: 2.6 },
  { x: 80, y: 2.8 },
  { x: 90, y: 3 },
  { x: 100, y: 3.2 },
  { x: 110, y: 3.5 },
  { x: 120, y: 3.7 },
  { x: 130, y: 3.4 },
  { x: 140, y: 3.2 },
  { x: 150, y: 3.1 },
  { x: 160, y: 3.0 },
  { x: 170, y: 3.2 },
  { x: 180, y: 3.1 },
  { x: 190, y: 3.0 },
  { x: 200, y: 3.1 },
  { x: 210, y: 3.2 },
  { x: 220, y: 3.0 },
];

new Chart("waf_graph", {
  type: "scatter",
  data: {
    datasets: [
      {
        pointRadius: 4,
        pointBackgroundColor: "rgb(0,0,255)",
        data: xyValues,
      },
    ],
  },
  options: {
    legend: { display: false },
    scales: {
      xAxes: [
        {
          ticks: { min: 50, max: 250, stepSize: 25 },
          scaleLabel: {
            display: true,
            labelString: "Write Amplification", // Add your X axis title here
            fontSize: 8,
          },
        },
      ],
      yAxes: [
        {
          scaleLabel: {
            display: true,
            labelString: "Block Writes Over Time", // Add your Y axis title here
            fontSize: 8,
          },
        },
      ],
    },
    title: {
      display: true,
      text: "WAF Graph", // Add your graph title here
      fontSize: 20,
    },
  },
});
