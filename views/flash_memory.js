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
    console.log("Selected value is 16");
  } else if (selectedValue === "4") {
    // Code to execute when the value "32" is selected
    console.log("Selected value is 32");
  }
});

// --------------------------------------Flash memory Block----------------------------------------------------------//
var blockSelect = document.getElementById("blockCount");
// Add event listener for the "change" event
blockSelect.addEventListener("change", function () {
  // Get the selected value
  var blockValue = blockSelect.value;
  console.log(blockValue);
  var p0d0p0b0ct = document.getElementById("p0d0p0b0ct");
  var p0d0p0b1ct = document.getElementById("p0d0p0b1ct");
  var p0d0p0b2ct = document.getElementById("p0d0p0b2ct");
  var p0d0p0b3ct = document.getElementById("p0d0p0b3ct");
  var p0d0p1b0ct = document.getElementById("p0d0p1b0ct");
  var p0d0p1b1ct = document.getElementById("p0d0p1b1ct");
  var p0d0p1b2ct = document.getElementById("p0d0p1b2ct");
  var p0d0p1b3ct = document.getElementById("p0d0p1b3ct");
  var p0d1p0b0ct = document.getElementById("p0d1p0b0ct");
  var p0d1p0b1ct = document.getElementById("p0d1p0b1ct");
  var p0d1p0b2ct = document.getElementById("p0d1p0b2ct");
  var p0d1p0b3ct = document.getElementById("p0d1p0b3ct");
  var p0d1p1b0ct = document.getElementById("p0d1p1b0ct");
  var p0d1p1b1ct = document.getElementById("p0d1p1b1ct");
  var p0d1p1b2ct = document.getElementById("p0d1p1b2ct");
  var p0d1p1b3ct = document.getElementById("p0d1p1b3ct");
  var p1d0p0b0ct = document.getElementById("p1d0p0b0ct");
  var p1d0p0b1ct = document.getElementById("p1d0p0b1ct");
  var p1d0p0b2ct = document.getElementById("p1d0p0b2ct");
  var p1d0p0b3ct = document.getElementById("p1d0p0b3ct");
  var p1d0p1b0ct = document.getElementById("p1d0p1b0ct");
  var p1d0p1b1ct = document.getElementById("p1d0p1b1ct");
  var p1d0p1b2ct = document.getElementById("p1d0p1b2ct");
  var p1d0p1b3ct = document.getElementById("p1d0p1b3ct");
  var p1d1p0b0ct = document.getElementById("p1d1p0b0ct");
  var p1d1p0b1ct = document.getElementById("p1d1p0b1ct");
  var p1d1p0b2ct = document.getElementById("p1d1p0b2ct");
  var p1d1p0b3ct = document.getElementById("p1d1p0b3ct");
  var p1d1p1b0ct = document.getElementById("p1d1p1b0ct");
  var p1d1p1b1ct = document.getElementById("p1d1p1b1ct");
  var p1d1p1b2ct = document.getElementById("p1d1p1b2ct");
  var p1d1p1b3ct = document.getElementById("p1d1p1b3ct");

  // Perform actions based on the selected value
  if (blockValue === "1") {
    // Code to execute when the value "16" is selected
    p0d0p0b1ct.style.display = "none";
    p0d0p0b2ct.style.display = "none";
    p0d0p0b3ct.style.display = "none";
    p0d0p1b1ct.style.display = "none";
    p0d0p1b2ct.style.display = "none";
    p0d0p1b3ct.style.display = "none";
    p0d1p0b1ct.style.display = "none";
    p0d1p0b2ct.style.display = "none";
    p0d1p0b3ct.style.display = "none";
    p0d1p1b1ct.style.display = "none";
    p0d1p1b2ct.style.display = "none";
    p0d1p1b3ct.style.display = "none";
    p1d0p0b1ct.style.display = "none";
    p1d0p0b2ct.style.display = "none";
    p1d0p0b3ct.style.display = "none";
    p1d0p1b1ct.style.display = "none";
    p1d0p1b2ct.style.display = "none";
    p1d0p1b3ct.style.display = "none";
    p1d1p0b1ct.style.display = "none";
    p1d1p0b2ct.style.display = "none";
    p1d1p0b3ct.style.display = "none";
    p1d1p1b1ct.style.display = "none";
    p1d1p1b2ct.style.display = "none";
    p1d1p1b3ct.style.display = "none";
  } else if (blockValue === "2") {
    // Code to execute when the value "32" is selected
    p0d0p0b1ct.style.display = "table";
    p0d0p0b2ct.style.display = "none";
    p0d0p0b3ct.style.display = "none";
    p0d0p1b1ct.style.display = "table";
    p0d0p1b2ct.style.display = "none";
    p0d0p1b3ct.style.display = "none";
    p0d1p0b1ct.style.display = "table";
    p0d1p0b2ct.style.display = "none";
    p0d1p0b3ct.style.display = "none";
    p0d1p1b1ct.style.display = "table";
    p0d1p1b2ct.style.display = "none";
    p0d1p1b3ct.style.display = "none";
    p1d0p0b1ct.style.display = "table";
    p1d0p0b2ct.style.display = "none";
    p1d0p0b3ct.style.display = "none";
    p1d0p1b1ct.style.display = "table";
    p1d0p1b2ct.style.display = "none";
    p1d0p1b3ct.style.display = "none";
    p1d1p0b1ct.style.display = "table";
    p1d1p0b2ct.style.display = "none";
    p1d1p0b3ct.style.display = "none";
    p1d1p1b1ct.style.display = "table";
    p1d1p1b2ct.style.display = "none";
    p1d1p1b3ct.style.display = "none";
  }else if (blockValue === "4") {
    // Code to execute when the value "32" is selected
    p0d0p0b1ct.style.display = "table";
    p0d0p0b2ct.style.display = "table";
    p0d0p0b3ct.style.display = "table";
    p0d0p1b1ct.style.display = "table";
    p0d0p1b2ct.style.display = "table";
    p0d0p1b3ct.style.display = "table";
    p0d1p0b1ct.style.display = "table";
    p0d1p0b2ct.style.display = "table";
    p0d1p0b3ct.style.display = "table";
    p0d1p1b1ct.style.display = "table";
    p0d1p1b2ct.style.display = "table";
    p0d1p1b3ct.style.display = "table";
    p1d0p0b1ct.style.display = "table";
    p1d0p0b2ct.style.display = "table";
    p1d0p0b3ct.style.display = "table";
    p1d0p1b1ct.style.display = "table";
    p1d0p1b2ct.style.display = "table";
    p1d0p1b3ct.style.display = "table";
    p1d1p0b1ct.style.display = "table";
    p1d1p0b2ct.style.display = "table";
    p1d1p0b3ct.style.display = "table";
    p1d1p1b1ct.style.display = "table";
    p1d1p1b2ct.style.display = "table";
    p1d1p1b3ct.style.display = "table";
  }
  calculateFlashMemorySize();
});

// --------------------------------------Flash memory Plane----------------------------------------------------------//
var planeSelect = document.getElementById("planeCount");
// Add event listener for the "change" event
planeSelect.addEventListener("change", function () {
  // Get the selected value
  var planeValue = planeSelect.value;
  console.log(planeValue);
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
  package.textContent = pageSize * pageCount * blockCount * planeCount * dieCount + "kb";
  var flashSSDSize = document.getElementById("flashSSDSize");
  flashSSDSize.textContent = pageSize * pageCount * blockCount * planeCount * dieCount * packageCount + "kb";

  // package.textContent = pageSize * pageCount * blockCount * planeCount * dieCount;
  var flashMemorySize = pageSize * pageCount * blockCount * planeCount * dieCount * packageCount;
  console.log(flashMemorySize);
  // document.getElementById("flashMemorySize").value = flashMemorySize;
}