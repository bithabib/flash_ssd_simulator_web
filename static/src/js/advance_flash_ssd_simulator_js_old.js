// All global variables
const ssd_structure = {
  channel: 2,
  chip: 1,
  die: 2,
  plane: 4,
  block_container: 60,
  block: 5,
};
const sector_size = 520192;
const page_size = 4 * 1024;
const gc_free_space_percentage = 0.15;
const gc_threshold = 0.95;
var global_block_tracer = 0;
var full_ssd_storage = {};
var forceStop = false;
var ssd_block_trace_list = [];
var ssd_block_trace_dict = {};
var ssd_write = 0;
var host_write = 0;
var waf_trace = [
  {
    y: 1,
  },
];
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
      x: block,
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
  waf_trace.push({
    y: ssd_write / host_write,
  });

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

function color_brighness() {
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

// Function to check if lba is available in full_ssd_storage
// Function to check if lba is available in full_ssd_storage
// Function to check if lba is available in full_ssd_storage
function invalid_lba(lba) {
  if (full_ssd_storage) {
    for (var block in full_ssd_storage) {
      full_ssd_storage[block]["vlba"].forEach((vlba) => {
        if (lba == vlba["lba"]) {
          vlba["status"] = "invalid";
        }
      });
    }
  }
}

// Function is_block_full to check if block is full
// Function is_block_full to check if block is full
// Function is_block_full to check if block is full
function is_block_full(block_id) {
  var total_written_pages = 0;
  if (block_id in full_ssd_storage) {
    full_ssd_storage[block_id]["vlba"].forEach((vlba) => {
      if (vlba["status"] == "valid" || vlba["status"] == "invalid") {
        total_written_pages += 1;
      }
    });
  }

  if (total_written_pages >= number_of_page_per_block) {
    return true;
  } else {
    return false;
  }
}
// get total ssd after overprovisioning
// get total ssd after overprovisioning
// get total ssd after overprovisioning
function get_total_ssd_after_overprovisioning() {
  var overprovisioningRatio = getOverprovisioningRatio();
  var total_ssd_size =
    ssd_structure["channel"] *
    ssd_structure["chip"] *
    ssd_structure["die"] *
    ssd_structure["plane"] *
    ssd_structure["block_container"] *
    ssd_structure["block"] *
    number_of_page_per_block *
    1024 *
    4;
  var total_ssd_size_after_overprovision =
    total_ssd_size * (1 - overprovisioningRatio / 100);
  return total_ssd_size_after_overprovision;
}

// get number of logical block address
// get number of logical block address
// get number of logical block address
function get_number_of_logical_block_address() {
  var total_ssd_size = get_total_ssd_after_overprovisioning();
  var number_of_logical_block_address = total_ssd_size / sector_size - 1;
  return parseInt(number_of_logical_block_address);
}
// Function is_ssd_full to check if ssd is full
// Function is_ssd_full to check if ssd is full
// Function is_ssd_full to check if ssd is full
function will_run_gc(io_size, gc_free_space = 0) {
  // read overprovisioning ratio
  var gc_free_plus_threshold = gc_threshold - gc_free_space;
  var total_ssd_size_after_overprovision =
    get_total_ssd_after_overprovisioning() * gc_free_plus_threshold;
  // count valid and invalid pages together
  var total_written_pages = 0;
  for (var block in full_ssd_storage) {
    full_ssd_storage[block]["vlba"].forEach((vlba) => {
      if (vlba["status"] == "valid" || vlba["status"] == "invalid") {
        total_written_pages += 1;
      }
    });
  }
  if (
    total_written_pages * 4 * 1024 + io_size >=
    total_ssd_size_after_overprovision
  ) {
    return true;
  } else {
    return false;
  }
}
function gc_stop_condition_met(io_size) {
  return will_run_gc(io_size, gc_free_space_percentage);
}

// Function to setup progress bar
// Function to setup progress bar
// Function to setup progress bar
function progress_setup(trace_length, i, global_block_tracer) {
  var trace_progress = document.getElementById("trace_progress");
  trace_progress.value = (i / trace_length) * 100;
  var ssd_progress = document.getElementById("ssd_progress");
  ssd_progress.value = (global_block_tracer / 4000) * 100;
}

// Function to write data to block
// Function to write data to block
// Function to write data to block
function write_page(block_id, lba, io_size, is_gc_running = false) {
  if (is_gc_running) {
    ssd_write += 4000;
  } else {
    host_write += io_size;
    ssd_write += 4000;
  }
  if (block_id in full_ssd_storage) {
    full_ssd_storage[block_id]["aw"] += io_size;
    full_ssd_storage[block_id]["wc"] += 1;
    full_ssd_storage[block_id]["vlba"].push({
      lba: lba,
      size: io_size,
      status: "valid",
    });
  } else {
    full_ssd_storage[block_id] = {
      aw: io_size,
      wc: 1,
      vlba: [
        {
          lba: lba,
          size: io_size,
          status: "valid",
        },
      ],
      ec: 0,
    };
  }
}
// Function to write data to ssd
// Function to write data to ssd
// Function to write data to ssd
async function write_ssd(lba, io_size, gc_block = "", is_gc_running = false) {
  while (io_size > 0) {
    block_id = allocation_scheme_algorithm(global_block_tracer);
    var is_full = is_block_full(block_id);
    if (is_full || gc_block == block_id) {
      global_block_tracer += 1;
      if (!gc_tracer) {
        await new Promise((resolve) => setTimeout(resolve, 30));
      }
    } else {
      if (io_size >= 4000) {
        write_page(block_id, lba, 4000, is_gc_running);
        io_size = io_size - 4000;
      } else {
        write_page(block_id, lba, io_size, is_gc_running);
        io_size = 0;
      }
    }
  }
}
// Greedy Garbage Collection
// Greedy Garbage Collection
// Greedy Garbage Collection
function greedyGarbageCollection() {
  var max_invalid_page = 0;
  var max_invalid_block = "";
  for (var block in full_ssd_storage) {
    var invalid_page = 0;
    full_ssd_storage[block]["vlba"].forEach((vlba) => {
      if (vlba["status"] == "invalid") {
        invalid_page += 1;
      }
    });
    if (invalid_page >= max_invalid_page) {
      max_invalid_page = invalid_page;
      max_invalid_block = block;
    }
  }

  return max_invalid_block;
}
// Function to lrw Garbage Collection
// Function to lrw Garbage Collection
// Function to lrw Garbage Collection
function lrwGarbageCollection() {}
// Function to garbage collection
// Function to garbage collection
// Function to garbage collection
async function garbageCollection() {
  var gc_block = greedyGarbageCollection();
  for (var lba in full_ssd_storage[gc_block]["vlba"]) {
    if (full_ssd_storage[gc_block]["vlba"][lba]["status"] == "valid") {
      global_block_tracer = 0;
      await write_ssd(
        full_ssd_storage[gc_block]["vlba"][lba]["lba"],
        full_ssd_storage[gc_block]["vlba"][lba]["size"],
        gc_block,
        true
      );
    }
  }

  var write_count = full_ssd_storage[gc_block]["wc"];
  var erase_count = full_ssd_storage[gc_block]["ec"] + 1;
  full_ssd_storage[gc_block] = {
    wc: write_count,
    aw: 0,
    vlba: [],
    ec: erase_count,
  };
  color_brighness();
  global_block_tracer = 0;
  await new Promise((resolve) => setTimeout(resolve, 100));
}

// Call function to upload trace file
async function upload_trace_file(event) {
  var file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = async function (e) {
      const lines = e.target.result.split("\n");
      var trace_length = lines.length;
      for (var i = 0; i < trace_length; i++) {
        startProcessingGif("start writing trace to ssd");
        if (lines[i] != "") {
          var data = lines[i].split(" ");
          var lba = parseInt(data[0]) % get_number_of_logical_block_address();
          var io_size = parseInt(data[1]);
          invalid_lba(lba);
          var run_gc = will_run_gc(io_size);
          if (run_gc) {
            startProcessingGif("Garbage Collection");
            while (gc_stop_condition_met(io_size)) {
              // set message to garbage collection

              await garbageCollection();
            }
            stopProcessingGif("Garbage Collection Completed");
          }
          await write_ssd(lba, io_size);
          color_brighness();
          progress_setup(trace_length, i, global_block_tracer);
          if (gc_tracer) {
            await new Promise((resolve) => setTimeout(resolve, 30));
          }
        }
        //
        if (i % 1000 == 0) {
          updateWAFGraph();
        }
      }
      stopProcessingGif("Write Completed");
      color_brighness();
    };
    reader.readAsText(file);
  }
}
const fileInput = document.getElementById("upload_trace_file");
fileInput.addEventListener("change", upload_trace_file);

// ----------------------------- Overprovisioning Ratio -----------------------------//
// ----------------------------- Overprovisioning Ratio -----------------------------//

// Overprovisioning ratio setup
function getOverprovisioningRatio() {
  var overprovisioningRatio = document.getElementById(
    "overprovisioning_ratio"
  ).value;
  // parseFloat to convert string to float
  overprovisioningRatio = parseFloat(overprovisioningRatio);
  return overprovisioningRatio;
}
function handleOverprovisioning() {
  var overprovisioningRatio = getOverprovisioningRatio();
  var totalSize =
    ssd_structure["channel"] *
    ssd_structure["chip"] *
    ssd_structure["die"] *
    ssd_structure["plane"] *
    ssd_structure["block_container"] *
    ssd_structure["block"] *
    number_of_page_per_block *
    1024 *
    4;
  var totalSizeAfterOverprovision =
    totalSize * (1 - overprovisioningRatio / 100);
  // convert byte to gb
  totalSizeAfterOverprovision =
    totalSizeAfterOverprovision / 1024 / 1024 / 1024;
  // two decimal places
  totalSizeAfterOverprovision = totalSizeAfterOverprovision.toFixed(2);
  ssd_size_holder = document.getElementById("totalSize");
  ssd_size_holder.innerHTML = totalSizeAfterOverprovision + "gb";
}

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

var select_hitmap_type = document.getElementById("select_hitmap_type");
// Add event listener for the "change" event
select_hitmap_type.addEventListener("change", async function () {
  // Get the selected value
  var hitmap_type = select_hitmap_type.value;
  let ssd_block_trace_list_length = ssd_block_trace_list.length;
  if (hitmap_type == "wc") {
    var max_value = max_write_count;
  } else if (hitmap_type == "ec") {
    var max_value = max_erase_count;
  }
  for (var i = 0; i < ssd_block_trace_list_length; i++) {
    var block = document.getElementById(ssd_block_trace_list[i]);

    block.style.backgroundColor = color_brighness(
      ssd_block_trace_dict[ssd_block_trace_list[i]][hitmap_type],
      max_value,
      ssd_block_trace_dict[ssd_block_trace_list[i]].aw
    );
    await new Promise((resolve) => setTimeout(resolve, 5));
  }
});

async function reset() {
  // Call api /write/complete
  await fetch("/write/complete", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then(async (data) => {
      // reload the page
      location.reload();
    });
}
