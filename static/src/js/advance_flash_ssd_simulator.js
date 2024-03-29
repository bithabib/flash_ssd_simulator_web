// Function to create block for each plane
function create_block_for_each_plane() {
  // read table by id and create block for each plane
  var ssd_container = document.getElementById("ssd_container");
  var ssd_container_trh = document.createElement("tr");
  var ssd_container_trtd = document.createElement("tr");
  for (var i = 0; i < 2; i++) {
    var ssd_container_trhv = document.createElement("th");
    ssd_container_trhv.innerHTML = "Package " + i;
    ssd_container_trhv.setAttribute("style", "font-size: 10px;");
    ssd_container_trh.appendChild(ssd_container_trhv);
    var ssd_container_trtdv = document.createElement("td");
    var chip_table = document.createElement("table");
    var chip_table_trh = document.createElement("tr");
    var chip_table_trtd = document.createElement("tr");
    for (var j = 0; j < 1; j++) {
      var chip_table_trhv = document.createElement("th");
      chip_table_trhv.innerHTML = "Chip " + j;
      chip_table_trhv.setAttribute("style", "font-size: 10px;");
      chip_table_trh.appendChild(chip_table_trhv);
      var chip_table_trtdv = document.createElement("td");
      var die_table = document.createElement("table");
      var die_table_trh = document.createElement("tr");
      var die_table_trtd = document.createElement("tr");
      for (var k = 0; k < 2; k++) {
        var die_table_trhv = document.createElement("th");
        die_table_trhv.innerHTML = "Die " + k;
        die_table_trhv.setAttribute("style", "font-size: 10px;");
        die_table_trh.appendChild(die_table_trhv);
        var die_table_trtdv = document.createElement("td");
        var plane_table = document.createElement("table");
        var plane_table_trh = document.createElement("tr");
        var plane_table_trtd = document.createElement("tr");
        for (var l = 0; l < 4; l++) {
          var plane_table_trhv = document.createElement("th");
          plane_table_trhv.innerHTML = "P" + l;
          plane_table_trhv.setAttribute("style", "font-size: 10px;");
          plane_table_trh.appendChild(plane_table_trhv);
          var plane_table_trtdv = document.createElement("td");
          var block_table = document.createElement("table");
          for (var m = 0; m < 60; m++) {
            var block_table_trtd = document.createElement("tr");
            for (var n = 0; n < 5; n++) {
              var block_table_trtdv = document.createElement("td");
              // create block with id for each td
              block_table_trtdv.setAttribute(
                "id",
                "block_" + i + "_" + j + "_" + k + "_" + l + "_" + m + "_" + n
              );
              block_table_trtd.appendChild(block_table_trtdv);
            }
            block_table.appendChild(block_table_trtd);
          }
          plane_table_trtdv.appendChild(block_table);
          plane_table_trtd.appendChild(plane_table_trtdv);
        }
        plane_table.appendChild(plane_table_trh);
        plane_table.appendChild(plane_table_trtd);
        die_table_trtdv.appendChild(plane_table);
        die_table_trtd.appendChild(die_table_trtdv);
      }
      die_table.appendChild(die_table_trh);
      die_table.appendChild(die_table_trtd);
      chip_table_trtdv.appendChild(die_table);
      chip_table_trtd.appendChild(chip_table_trtdv);
    }
    chip_table.appendChild(chip_table_trh);
    chip_table.appendChild(chip_table_trtd);
    ssd_container_trtdv.appendChild(chip_table);
    ssd_container_trtd.appendChild(ssd_container_trtdv);
  }
  ssd_container.appendChild(ssd_container_trh);
  ssd_container.appendChild(ssd_container_trtd);
}

function color_brighness(part, whole) {
  var percentage = (part / whole) * 100;
  var brightness = Math.floor(255 * (percentage / 100));
  if (brightness < 0) brightness = 0;
  if (brightness > 255) brightness = 255;
  // Construct the CSS color string
  var color = "rgb(0," + brightness + ",0)";
  return color;
}

// Call function to upload trace file
async function upload_trace_file(event) {
  var file = event.target.files[0];
  var allocation_scheme = document.getElementById(
    "ssd_allocation_scheme"
  ).value;
  // call flask api to upload trace file
  var formData = new FormData();
  formData.append("file", file);
  formData.append("allocation_scheme", allocation_scheme);
  fetch("/upload_trace_file", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then(async (data) => {
      console.log(data);
      // loop through each trace and change color of block
      for (var i = 0; i < data.traces.length; i++) {
        var block = document.getElementById(data.traces[i].block_id);
        block.style.backgroundColor = color_brighness(data.traces[i].number_of_hit_in_block, 7);
        // block.setAttribute("style", "background-color: green;" );
        // block.setAttribute("style", "margin: 0; padding: 0;");
        // var background = document.createElement("div");
        // background.setAttribute("style", "background-color: green; height:100%; width:100%; margin: 0; padding: 0;" );
        // block.appendChild(background);
        // // block.setAttribute("style", "background-color: green; background-size:50% 100%;" );

        await new Promise((resolve) => setTimeout(resolve, 10));
        // add wait sleep time for each trace

        // change color of block based on trace type
        // if (trace.type == "READ") {
        //   block.style.backgroundColor = "green";
        // } else {
        //   block.style.backgroundColor = "red";
        // }
      }
    });
}
const fileInput = document.getElementById("upload_trace_file");
fileInput.addEventListener("change", upload_trace_file);

// Overprovisioning ratio setup
function handleOverprovisioning(event) {
  var overprovisioningRatio = event.target.value;
  // find the total ss size after overprovision ratio removed from total size
  var totalSize = 1.2288;
  // four decimal points
  var totalSizeAfterOverprovision = (
    totalSize -
    (totalSize * overprovisioningRatio) / 100
  ).toFixed(4);
  ssd_size_holder = document.getElementById("totalSize");
  ssd_size_holder.innerHTML = totalSizeAfterOverprovision + "gb";
}

document.onload = create_block_for_each_plane();
