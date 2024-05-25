const ssd_structure = {
  channel: 2,
  chip: 1,
  die: 2,
  plane: 4,
  block_container: 60,
  block: 5,
  page: 256,
  sector: 8,
  sector_size: 512,
  page_size: 8192,
};
const gc_free_space_percentage = 0.02;
const gc_threshold = 0.99;
var overprovisioningRatio = 0;

// # Time in us for flash operations us means microsecond
const flash_operation_time = {
  read_msb: 80,
  read_lsb: 25,
  write_msb: 200,
  write_lsb: 1500,
  erase_block: 1500,
};
// declare address mapping table with size of total page number
var address_mapping_table = new Array(
  ssd_structure.channel *
    ssd_structure.chip *
    ssd_structure.die *
    ssd_structure.plane *
    ssd_structure.block_container *
    ssd_structure.block *
    ssd_structure.page
);
var update_block = null;
var ssd_storage = {};
var host_write = 0;
var internal_write = 0;
var waf_log = [];
function create_block_for_each_plane() {
  // read table by id and create block for each plane
  var ssd_container = document.getElementById("ssd_container");
  var ssd_container_trh = document.createElement("tr");
  var ssd_container_trtd = document.createElement("tr");

  for (var i = 0; i < ssd_structure.channel; i++) {
    var ssd_container_trhv = document.createElement("th");
    ssd_container_trhv.innerHTML = "Package " + i;
    ssd_container_trhv.setAttribute("style", "font-size: 10px;");
    ssd_container_trh.appendChild(ssd_container_trhv);
    var ssd_container_trtdv = document.createElement("td");
    var chip_table = document.createElement("table");
    var chip_table_trh = document.createElement("tr");
    var chip_table_trtd = document.createElement("tr");
    for (var j = 0; j < ssd_structure.chip; j++) {
      var chip_table_trhv = document.createElement("th");
      chip_table_trhv.innerHTML = "Chip " + j;
      chip_table_trhv.setAttribute("style", "font-size: 10px;");
      chip_table_trh.appendChild(chip_table_trhv);
      var chip_table_trtdv = document.createElement("td");
      var die_table = document.createElement("table");
      var die_table_trh = document.createElement("tr");
      var die_table_trtd = document.createElement("tr");
      for (var k = 0; k < ssd_structure.die; k++) {
        var die_table_trhv = document.createElement("th");
        die_table_trhv.innerHTML = "Die " + k;
        die_table_trhv.setAttribute("style", "font-size: 10px;");
        die_table_trh.appendChild(die_table_trhv);
        var die_table_trtdv = document.createElement("td");
        var plane_table = document.createElement("table");
        var plane_table_trh = document.createElement("tr");
        var plane_table_trtd = document.createElement("tr");
        for (var l = 0; l < ssd_structure.plane; l++) {
          var plane_table_trhv = document.createElement("th");
          plane_table_trhv.innerHTML = "P" + l;
          plane_table_trhv.setAttribute("style", "font-size: 10px;");
          plane_table_trh.appendChild(plane_table_trhv);
          var plane_table_trtdv = document.createElement("td");
          var block_table = document.createElement("table");
          for (var m = 0; m < ssd_structure.block_container; m++) {
            var block_table_trtd = document.createElement("tr");
            for (var n = 0; n < ssd_structure.block; n++) {
              var block_table_trtdv = document.createElement("td");
              // create block with id for each td
              var p_block =
                "block_" + i + "_" + j + "_" + k + "_" + l + "_" + m + "_" + n;
              block_table_trtdv.setAttribute("id", p_block);
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

var waf_trace = [];
function updateWAFGraph() {
  console.log(ssd_storage);
  var writeCountGraphData = [];
  var averageWriteCount = 0;
  var averageWriteCountGraphData = [];
  var eraseCountGraphData = [];
  var averageEraseCount = 0;
  var averageEraseCountGraphData = [];

  var counter = 1;
  for (var block in ssd_storage) {
    writeCountGraphData.push({
      y: ssd_storage[block]["write_count"],
    });
    eraseCountGraphData.push({
      y: ssd_storage[block]["erase_count"],
    });
    averageWriteCount += ssd_storage[block]["write_count"];
    averageEraseCount += ssd_storage[block]["erase_count"];
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



// color brightness function to change color of block
function color_brighness() {
  for (var block in ssd_storage) {
    // get the block by get element by id
    var valid_page = ssd_storage[block]["valid_pages"];
    var invalid_page = ssd_storage[block]["invalid_pages"];

    var percentage = (invalid_page / (valid_page + invalid_page)) * 100;
    var brightness = Math.floor(255 * (percentage / 100));
    if (brightness < 0) brightness = 0;
    if (brightness > 255) brightness = 255;
    var color = "rgb(0," + brightness + ",0)";
    var block = document.getElementById(block);
    // remove background image
    block.style.backgroundImage = "none";
    if (valid_page == 0 && invalid_page == 0) {
      color = "rgb(255,255,255)";
    } else if (valid_page == 0 && invalid_page > 0) {
      block.style.backgroundImage = 'url("static/src/logo/x.webp")';
      block.style.backgroundSize = "cover";
    } else if (valid_page > 0 && invalid_page == 0) {
      block.style.backgroundImage = 'url("static/src/logo/r.webp")';
      block.style.backgroundSize = "cover";
    }

    block.style.backgroundColor = color;
  }
}


// // Call function to upload trace file
async function upload_trace_file(event) {
  var file = event.target.files[0];
  if (!file) {
    console.error("No file selected");
    return;
  }
  const reader = new FileReader();
  reader.onload = async function (e) {
    console.log("test");
    try {
      // read the file name
      var file_name = file.name;
      // if file name contain waf then update the waf graph
      if (file_name.includes("waf")) {
        var waf_data = JSON.parse(e.target.result);
        console.log(waf_data);
        for (var i = 0; i < waf_data.length; i++) {
          waf_trace.push({
            y: waf_data[i]["waf"],
          });
        }
        // waf_trace = waf_data;
        updateWAFGraph();
        return;
      }
      ssd_storage = JSON.parse(e.target.result);
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



window.onload = function () {
  create_block_for_each_plane();
};
