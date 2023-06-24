// Update button handler
async function handleSelection(fileName) {
    const fileMapping = new FileMapping();
    var getFileInformation =  fileMapping.getMapping(fileName);
    console.log(getFileInformation);
}

var selectedFileName = document.getElementById("update_file");
// Add event listener for the "change" event
selectedFileName.addEventListener("change", function () {
  // Get the selected value
  var fileName = selectedFileName.value;
  // Display the selected value
  console.log("Selected file name: " + fileName);
  handleSelection(fileName);
});


// Update change handler
async function handleFileUpdate() {
  // read the file
  const file = document.getElementById("fileUpdate").value;
  
}
