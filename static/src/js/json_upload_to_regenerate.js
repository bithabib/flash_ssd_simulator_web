const sector_size = 1024 * 4 * 6;
const page_size = 4 * 1024;
const gc_free_space_percentage = 0.02;
const gc_threshold = 0.99;
var global_block_tracer = 0;
var full_ssd_storage = {};
// var lba_contain_block_address = {};
var forceStop = false;
var waf_trace = [
  {
    y: 0,
  },
];
var ssd_write = 0;
var host_write = 0;
var max_erase_count = 0;
var max_write_count = 0;
var number_of_page_per_block = 256;
gc_tracer = false;

// Waf Graph update
function updateWAFGraph() {
  var writeCountGraphData = [];
  var averageWriteCount = 0;
  var averageWriteCountGraphData = [];
  var eraseCountGraphData = [];
  var averageEraseCount = 0;
  var averageEraseCountGraphData = [];

  var counter = 1;
  for (var block in full_ssd_storage) {
    writeCountGraphData.push({
      y: full_ssd_storage[block]["wc"],
    });
    eraseCountGraphData.push({
      y: full_ssd_storage[block]["ec"],
    });
    averageWriteCount += full_ssd_storage[block]["wc"];
    averageEraseCount += full_ssd_storage[block]["ec"];
    averageEraseCountGraphData.push({
      y: averageEraseCount / counter,
    });
    averageWriteCountGraphData.push({
      y: averageWriteCount / counter,
    });
    counter += 1;
  }
  var wafChart = new CanvasJS.Chart("wafChartContainer", {
    animationEnabled: true,
    theme: "light2",
    title: {
      text: "Write Amplification Factor Over Time",
    },
    data: [
      {
        type: "line",
        indexLabelFontSize: 16,
        dataPoints: waf_trace,
        name: "WAF",
      },
    ],
  });

  var writeCountChart = new CanvasJS.Chart("writeCountChartContainer", {
    animationEnabled: true,
    theme: "light2",
    title: {
      text: "Write Count Over Time",
    },
    data: [
      {
        type: "column",
        indexLabelFontSize: 16,
        dataPoints: writeCountGraphData,
        name: "Write Count",
      },
      {
        type: "line",
        indexLabelFontSize: 16,
        dataPoints: averageWriteCountGraphData,
        name: "Average Write Count",
      },
    ],
  });

  var eraseCountChart = new CanvasJS.Chart("eraseCountChartContainer", {
    animationEnabled: true,
    theme: "light2",
    title: {
      text: "Erase Count Over Time",
    },
    data: [
      {
        type: "column",
        indexLabelFontSize: 16,
        dataPoints: eraseCountGraphData,
        name: "Erase Count",
      },
      {
        type: "line",
        indexLabelFontSize: 16,
        dataPoints: averageEraseCountGraphData,
        name: "Erase Count",
      },
    ],
  });
  wafChart.render();
  writeCountChart.render();
  eraseCountChart.render();
}

// Function to create block for each plane
// All global variables
const ssd_structure = {
  channel: 2,
  chip: 1,
  die: 2,
  plane: 4,
  block_container: 60,
  block: 5,
};

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

async function color_brighness() {
  for (var block in full_ssd_storage) {
    // get the block by get element by id
    var valid_page = 0;
    var invalid_page = 0;
    full_ssd_storage[block]["vlba"].forEach((vlba) => {
      if (vlba["status"] == "valid") {
        valid_page += 1;
      } else {
        invalid_page += 1;
      }
    });
    var percentage = (invalid_page / (valid_page + invalid_page)) * 100;
    var brightness = Math.floor(255 * (percentage / 100));
    if (brightness < 0) brightness = 0;
    if (brightness > 255) brightness = 255;
    var color = "rgb(0," + brightness + ",0)";
    var block = document.getElementById(block);
    if (valid_page == 0 && invalid_page == 0) {
      color = "rgb(255,255,255)";
    } else if (valid_page == 0 && invalid_page > 0) {
      block.style.backgroundImage = 'url("static/src/logo/x.webp")';
    }

    block.style.backgroundColor = color;
    await new Promise((resolve) => setTimeout(resolve, 3));
  }
}

// Function to select allocation scheme
// Function to select allocation scheme
// Function to select allocation scheme
function allocation_scheme_algorithm(block_tracer) {
  var allocation_scheme = document.getElementById(
    "ssd_allocation_scheme"
  ).value;
  var channel = 0;
  var chip = 0;
  var die = 0;
  var plane = 0;
  var block_container = 0;
  var block = 0;
  if (allocation_scheme == "s1") {
    channel =
      Math.floor(
        block_tracer /
          (ssd_structure["plane"] *
            ssd_structure["die"] *
            ssd_structure["chip"])
      ) % ssd_structure["channel"];
    chip = block_tracer % ssd_structure["chip"];
    die =
      Math.floor(block_tracer / ssd_structure["chip"]) % ssd_structure["die"];
    plane =
      Math.floor(
        block_tracer / (ssd_structure["die"] * ssd_structure["chip"])
      ) % ssd_structure["plane"];
    block_container =
      Math.floor(
        block_tracer /
          (ssd_structure["plane"] *
            ssd_structure["die"] *
            ssd_structure["chip"] *
            ssd_structure["channel"])
      ) % ssd_structure["block_container"];
    block =
      Math.floor(
        block_tracer /
          (ssd_structure["plane"] *
            ssd_structure["die"] *
            ssd_structure["chip"] *
            ssd_structure["channel"] *
            ssd_structure["block_container"])
      ) % ssd_structure["block"];
  } else if (allocation_scheme == "s2") {
    channel = block_tracer % ssd_structure["channel"];
    chip =
      Math.floor(block_tracer / ssd_structure["channel"]) %
      ssd_structure["chip"];
    die =
      Math.floor(
        block_tracer / (ssd_structure["chip"] * ssd_structure["channel"])
      ) % ssd_structure["die"];
    plane =
      Math.floor(
        block_tracer /
          (ssd_structure["die"] *
            ssd_structure["chip"] *
            ssd_structure["channel"])
      ) % ssd_structure["plane"];
    block_container =
      Math.floor(
        block_tracer /
          (ssd_structure["plane"] *
            ssd_structure["die"] *
            ssd_structure["chip"] *
            ssd_structure["channel"])
      ) % ssd_structure["block_container"];
    block =
      Math.floor(
        block_tracer /
          (ssd_structure["plane"] *
            ssd_structure["die"] *
            ssd_structure["chip"] *
            ssd_structure["channel"] *
            ssd_structure["block_container"])
      ) % ssd_structure["block"];
  } else {
    return None;
  }
  var block_id =
    "block" +
    "_" +
    channel +
    "_" +
    chip +
    "_" +
    die +
    "_" +
    plane +
    "_" +
    block_container +
    "_" +
    block;
  return block_id;
}



// Call function to upload trace file
async function upload_trace_file(event) {
  var file = event.target.files[0];
  console.log("this is test",file);
  if (!file) {
    console.error("No file selected");
    return;
  }
  console.log("this is test",file);
  const reader = new FileReader();
  reader.onload = async function (e) {
    console.log("test");
    try {
      // read the file name 
      var file_name = file.name;
      // if file name contain waf then update the waf graph
      if (file_name.includes("waf")) {
        var waf_data = JSON.parse(e.target.result);
        waf_trace = waf_data;
        updateWAFGraph();
        return;
      }
      full_ssd_storage = JSON.parse(e.target.result);
      color_brighness();
      updateWAFGraph();
    } catch (e) {
      console.error("Invalid file format");
      return;
    }
  };
  reader.readAsText(file);
}
const fileInput = document.getElementById("upload_trace_file");
fileInput.addEventListener("change", upload_trace_file);


// ----------------------------- Processing Status -----------------------------//
// ----------------------------- Processing Status -----------------------------//
function stopProcessingGif(message) {
  var div = document.getElementById("processing_status_container");
  div.style.backgroundImage = "none";
  var processingStatus = document.getElementById("processing_status");
  processingStatus.innerHTML = message;
}
function startProcessingGif(message) {
  var div = document.getElementById("processing_status_container");
  div.style.backgroundImage = 'url("static/src/logo/1amw.gif")';
  var processingStatus = document.getElementById("processing_status");
  processingStatus.innerHTML = message;
}

window.onload = function () {
  create_block_for_each_plane();
  stopProcessingGif("Please start writing");
  handleOverprovisioning();
};

async function stopWritingForce() {
  forceStop = true;
  stopProcessingGif("Write Stopped");
}