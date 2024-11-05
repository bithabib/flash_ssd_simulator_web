// Function to create block for each plane
// All global variables

const ssd_structure = {
  channel: 2,
  chip: 1,
  die: 2,
  plane: 4,
  block_container: 64,
  block: 8,
  page: 512,
  sector: 8,
  sector_size: 512,
  page_size: 4096,
};
// const gc_free_space_percentage = 0.0005;
const gc_free_space_percentage = 0.001;
const gc_threshold = 0.9995;
var overprovisioningRatio = 0;
var max_write = 255;
var max_erase = 255;
var max_d_time = 1;

// # Time in us for flash operations us means microsecond
const flash_operation_time = {
  read_msb: 25,
  read_lsb: 80,
  write_msb: 200,
  write_lsb: 1500,
  read: 25,
  write: 0.5, // millisecond per page
  erase_block: 2, // millisecond per block
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
var cummalative_time_per_packet = 0;
var cummalative_time_per_packet_log = [];
// var run_till = 157;
// var run_till = 1598512;
var run_till = 2576129;

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
              ssd_storage[p_block] = {
                block_id: p_block,
                status: "free", // free, inused, used
                offset: 0,
                valid_pages: 0,
                invalid_pages: 0,
                write_count: 0,
                erase_count: 0,
                d_time: 0,
              };
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
  IntialSSDSetup();
}

function IntialSSDSetup() {
  var total_block =
    ssd_structure.channel *
    ssd_structure.chip *
    ssd_structure.die *
    ssd_structure.plane *
    ssd_structure.block_container *
    ssd_structure.block;
  var initially_filled_percentage = document.getElementById(
    "initially_filled_percentage"
  ).value;
  var initially_filled_block = Math.floor(
    (initially_filled_percentage / 100) * total_block
  );
  for (var i = 0; i < total_block; i++) {
    var block = allocation_scheme_algorithm(i);
    if (i < initially_filled_block) {
      ssd_storage[block]["status"] = "used";
      ssd_storage[block]["valid_pages"] = ssd_structure.page;
      ssd_storage[block]["invalid_pages"] = 0;
      ssd_storage[block]["offset"] = ssd_structure.page;
      ssd_storage[block]["write_count"] = ssd_structure.page;
      ssd_storage[block]["erase_count"] = 0;
      for (
        var j = i * ssd_structure.page;
        j < (i + 1) * ssd_structure.page;
        j++
      ) {
        address_mapping_table[j] = {
          lpn: j,
          ppn: block,
          offset: j - i * ssd_structure.page + 1,
        };
      }
    } else {
      ssd_storage[block]["status"] = "free";
      ssd_storage[block]["valid_pages"] = 0;
      ssd_storage[block]["invalid_pages"] = 0;
      ssd_storage[block]["offset"] = 0;
      ssd_storage[block]["write_count"] = 0;
      ssd_storage[block]["erase_count"] = 0;
      for (
        var j = i * ssd_structure.page;
        j < (i + 1) * ssd_structure.page;
        j++
      ) {
        address_mapping_table[j] = null;
      }
    }
  }
  color_brighness();
}

function progress_setup(trace_length, i) {
  var trace_progress = document.getElementById("trace_progress");
  trace_progress.value = (i / trace_length) * 100;
  // var ssd_progress = document.getElementById("ssd_progress");
  // ssd_progress.value = (global_block_tracer / 4000) * 100;
}

function number_of_logical_block() {
  return (
    ssd_structure.channel *
    ssd_structure.chip *
    ssd_structure.die *
    ssd_structure.plane *
    ssd_structure.block_container *
    ssd_structure.block *
    ssd_structure.page
  );
}

function handleOverprovisioning() {
  overprovisioningRatio = document.getElementById(
    "overprovisioning_ratio"
  ).value;
  var totalSize =
    number_of_logical_block() *
    ssd_structure.sector_size *
    ssd_structure.sector;
  var totalSizeAfterOverprovision =
    totalSize * (1 - overprovisioningRatio / 100);

  // number of block reserved for overprovisioning
  // var total_block =
  //   ssd_structure.channel *
  //   ssd_structure.chip *
  //   ssd_structure.die *
  //   ssd_structure.plane *
  //   ssd_structure.block_container *
  //   ssd_structure.block;
  // var overprovisioning_block = total_block * (overprovisioningRatio / 100);

  // for (var i = total_block - 1; i >= 0; i--) {
  //   var block = allocation_scheme_algorithm(i);
  //   if (overprovisioning_block > 0) {
  //     ssd_storage[block]["ov"] = true;
  //     overprovisioning_block -= 1;
  //   } else {
  //     ssd_storage[block]["ov"] = false;
  //   }
  // }
  // convert byte to gb
  totalSizeAfterOverprovision =
    totalSizeAfterOverprovision / 1024 / 1024 / 1024;
  // two decimal places
  totalSizeAfterOverprovision = totalSizeAfterOverprovision.toFixed(2);
  ssd_size_holder = document.getElementById("totalSize");
  ssd_size_holder.innerHTML = totalSizeAfterOverprovision + "gb";
}
// Overprovisioning ratio setup
function get_number_of_overprovisioning_block() {
  var total_block =
    ssd_structure.channel *
    ssd_structure.chip *
    ssd_structure.die *
    ssd_structure.plane *
    ssd_structure.block_container *
    ssd_structure.block;
  var overprovisioning_block = total_block * (overprovisioningRatio / 100);
  return overprovisioning_block;
}

function get_total_ssd() {
  var total_ssd_size =
    number_of_logical_block() *
    ssd_structure.sector_size *
    ssd_structure.sector;
  return total_ssd_size;
}

// color brightness function to change color of block
async function color_brighness() {
  for (var block in ssd_storage) {
    // get the block by get element by id
    var valid_page = ssd_storage[block]["valid_pages"];
    var invalid_page = ssd_storage[block]["invalid_pages"];
    // get the write count and erase count
    var write_count = ssd_storage[block]["write_count"];
    var erase_count = ssd_storage[block]["erase_count"];
    var d_time = ssd_storage[block]["d_time"];
    if (write_count > max_write) {
      max_write = write_count;
    }
    if (erase_count > max_erase) {
      max_erase = erase_count;
    }

    // var hot_write_ratio = write_count / max_write;
    // var hot_erase_ratio = erase_count / max_erase;
    // var percentage = invalid_page / (valid_page + invalid_page);
    var percentage = 0;
    var heat_map_value = document.getElementById("heat_map").value;
    //     valid_invalid
    // write_count
    // erase_count
    // read_count
    if (heat_map_value == "valid_invalid") {
      percentage = invalid_page / (valid_page + invalid_page);
    }
    if (heat_map_value == "write_count") {
      percentage = (write_count === 0) ? 0 || 1 : write_count / max_write;
    }
    if (heat_map_value == "erase_count") {
      percentage = (erase_count === 0) ? 0 : erase_count / max_erase;
    }
    if (heat_map_value == "read_count") {
      percentage = 0;
    }
    if (heat_map_value == "death_time") {
      percentage = d_time / max_d_time;
    }
    // stop for 10 second 
    // var r_write = Math.floor(255 * hot_write_ratio);
    // var g_erase = Math.floor(255 * hot_erase_ratio);
    var color_code = Math.floor(255 * percentage);
    if (color_code < 0) color_code = 0;
    if (color_code > 255) color_code = 255;
    var color = "rgb(" + color_code + ",0,0)";
    // var color = "rgb(" + r_write + "," + b_invalid_page + "," + g_erase + ")";
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

function allocate_block(gc) {
  for (
    var i = 0;
    i <
    ssd_structure.block_container *
      ssd_structure.block *
      ssd_structure.channel *
      ssd_structure.chip *
      ssd_structure.die *
      ssd_structure.plane;
    i++
  ) {
    p_block = allocation_scheme_algorithm(i);
    if (update_block != null) {
      break;
    } else {
      if (
        ssd_storage[p_block]["status"] == "inused" ||
        ssd_storage[p_block]["status"] == "free"
      ) {
        update_block = ssd_storage[p_block];
        break;
      }
    }
  }
  //   if (gc) {
  //     if (
  //       ssd_storage[p_block]["ov"] &&
  //       ssd_storage[p_block]["status"] == "free"
  //     ) {
  //       update_block = ssd_storage[p_block];
  //       break;
  //     }
  //   } else {
  //     if (ssd_storage[p_block]["status"] == "free") {
  //       update_block = ssd_storage[p_block];
  //       break;
  //     }
  //   }
  // }
  // if (update_block == null) {
  //   for (
  //     var i = 0;
  //     i <
  //     ssd_structure.block_container *
  //       ssd_structure.block *
  //       ssd_structure.channel *
  //       ssd_structure.chip *
  //       ssd_structure.die *
  //       ssd_structure.plane;
  //     i++
  //   ) {
  //     p_block = allocation_scheme_algorithm(i);
  //     if (
  //       ssd_storage[p_block]["status"] == "inused" ||
  //       ssd_storage[p_block]["status"] == "free"
  //     ) {
  //       update_block = ssd_storage[p_block];
  //       break;
  //     }
  //   }
  // }
  return update_block;
}

// Function to get update ppn for each block
async function get_update_ppn(gc = false) {
  if (update_block == null) {
    await new Promise((resolve) => setTimeout(resolve, 1));
    var update_ppn = allocate_block(gc);
  } else {
    var update_ppn = update_block;
  }
  return update_ppn;
}

// Function to update mapping table
function update_mapping_table(page_start, update_ppn) {
  address_mapping_table[page_start] = {
    lpn: page_start,
    ppn: update_ppn["block_id"],
    offset: update_ppn["offset"],
  };
}

// Function to backup lsb page
function write_page(page_start, update_ppn, is_gc = false) {
  update_ppn["offset"] += 1;
  update_ppn["valid_pages"] += 1;
  update_ppn["write_count"] += 1;
  max_d_time += 1;
  update_ppn["d_time"] = max_d_time;
  ssd_storage[update_ppn["block_id"]] = update_ppn;
  if (update_ppn["offset"] == ssd_structure.page - 1) {
    update_ppn["status"] = "used";
    update_block = null;
  } else {
    update_ppn["status"] = "inused";
    update_block = update_ppn;
  }

  if (is_gc) {
    internal_write += 8;
    startProcessingGif("Garbage Collection");
  } else {
    host_write += 8;
    internal_write += 8;
    startProcessingGif("Writing Page");
  }
  cummalative_time_per_packet += flash_operation_time.write;
  update_mapping_table(page_start, update_ppn);
}

// Function to check invalid page
function isInvalid(page_start) {
  if (address_mapping_table[page_start] != null) {
    var ppn = address_mapping_table[page_start]["ppn"];
    var block = ssd_storage[ppn];
    block["valid_pages"] -= 1;
    block["invalid_pages"] += 1;
    ssd_storage[ppn] = block;
  }
}

// Function is_ssd_full to check if ssd is full
// Function is_ssd_full to check if ssd is full
// Function is_ssd_full to check if ssd is full
function will_run_gc(gc_free_space = 0) {
  // read overprovisioning ratio
  var gc_free_plus_threshold = gc_threshold - gc_free_space;
  var total_ssd_size_after_overprovision =
    get_total_ssd() * gc_free_plus_threshold;
  // count valid and invalid pages together
  var total_written_pages = 0;
  for (var block in ssd_storage) {
    // if (!ssd_storage[block]["ov"]) {
    total_written_pages += ssd_storage[block]["valid_pages"];
    total_written_pages += ssd_storage[block]["invalid_pages"];
    // }
  }
  if (
    total_written_pages * ssd_structure.sector_size * ssd_structure.sector >=
    total_ssd_size_after_overprovision
  ) {
    return true;
  } else {
    return false;
  }
}

// Greedy Garbage Collection
// Greedy Garbage Collection
// Greedy Garbage Collection
function greedyGarbageCollection() {
  var max_invalid_page = 0;
  var max_invalid_block = "";
  var min_valid_page = ssd_structure.page;
  var min_valid_block = "";
  var i = 0;
  var tracer = true;
  while (
    i <
    ssd_structure.block_container *
      ssd_structure.block *
      ssd_structure.channel *
      ssd_structure.chip *
      ssd_structure.die *
      ssd_structure.plane
  ) {
    var block = allocation_scheme_algorithm(i);

    if (block in ssd_storage) {
      if (ssd_storage[block]["invalid_pages"] > max_invalid_page) {
        max_invalid_page = ssd_storage[block]["invalid_pages"];
        max_invalid_block = block;
      }
      if (
        ssd_storage[block]["valid_pages"] <= min_valid_page &&
        ssd_storage[block]["valid_pages"] > 0
      ) {
        if (ssd_storage[block]["valid_pages"] == min_valid_page && tracer) {
          tracer = false;
          min_valid_block = block;
        } else {
          if (ssd_storage[block]["valid_pages"] < min_valid_page) {
            min_valid_block = block;
            min_valid_page = ssd_storage[block]["valid_pages"];
          }
        }
      }
    }
    i += 1;
  }
  if (max_invalid_page == 0) {
    return min_valid_block;
  } else {
    return max_invalid_block;
  }
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
  if (ssd_storage[gc_block].invalid_pages == ssd_structure.page) {
    ssd_storage[gc_block]["invalid_pages"] = 0;
    ssd_storage[gc_block]["valid_pages"] = 0;
    ssd_storage[gc_block]["offset"] = 0;
    ssd_storage[gc_block]["erase_count"] += 1;
    ssd_storage[gc_block]["status"] = "free";
    color_brighness();
    await new Promise((resolve) => setTimeout(resolve, 10));
    return true;
  } else {
    // loop in array of address mapping table don't use forEach
    for (var i = 0; i < address_mapping_table.length; i++) {
      if (address_mapping_table[i] != null) {
        if (address_mapping_table[i]["ppn"] == gc_block) {
          var update_ppn = await get_update_ppn(true);
          write_page(address_mapping_table[i]["lpn"], update_ppn, true);
        }
      }
    }
    ssd_storage[gc_block]["invalid_pages"] = 0;
    ssd_storage[gc_block]["valid_pages"] = 0;
    ssd_storage[gc_block]["offset"] = 0;
    ssd_storage[gc_block]["erase_count"] += 1;
    ssd_storage[gc_block]["status"] = "free";
    cummalative_time_per_packet += flash_operation_time.erase_block;

    color_brighness();
    await new Promise((resolve) => setTimeout(resolve, 10));
    return true;
  }
}
// Call function to upload trace file
async function upload_trace_file(event) {
  var file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    var file_name = file.name;
    reader.onload = async function (e) {
      const lines = e.target.result.split("\n");
      var trace_length = lines.length;
      for (var i = 0; i < run_till; i++) {
        var i_2 = i % trace_length;
        if (lines[i_2] != "") {
          var data = lines[i_2].split(" ");
          var lba =
            parseInt(data[0]) %
            parseInt(
              number_of_logical_block() *
                ssd_structure.sector *
                (1 - overprovisioningRatio / 100)
            );
          // var lba = parseInt(data[0]);
          // var io_size = parseInt(data[1]); // add * ssd_structure.sector_size if sector is given in replace of i/o size
          var io_size = parseInt(data[1]) * ssd_structure.sector_size; // remove ssd_structure.sector_size if i/o size is given in replace of sector
          var sector_count = Math.ceil(io_size / ssd_structure.sector_size);
          var page_start = Math.floor(lba / ssd_structure.sector);
          var page_end = Math.floor(
            (lba + sector_count + (ssd_structure.sector - 1)) /
              ssd_structure.sector
          );
          var run_gc = will_run_gc();
          if (run_gc) {
            var number_times_gc = 0;
            while (run_gc) {
              is_gc_complete = await garbageCollection();
              if (!is_gc_complete) {
                break;
              }
              run_gc = will_run_gc(gc_free_space_percentage);
              number_times_gc += 1;
            }
          }
          while (page_start < page_end) {
            isInvalid(page_start);
            var update_ppn = await get_update_ppn();
            write_page(page_start, update_ppn);
            page_start += 1;
          }
          color_brighness();
        }
        progress_setup(run_till, i);
        if (i_2 % ssd_structure.page == 0) {
          waf_log.push({
            waf: internal_write / host_write,
          });
          cummalative_time_per_packet_log.push({
            time: cummalative_time_per_packet,
          });
          await new Promise((resolve) => setTimeout(resolve, 2));
        }
      }
      waf_log.push({
        iw: internal_write,
        hw: host_write,
      });
      cummalative_time_per_packet_log.push({
        time: cummalative_time_per_packet,
      });
      progress_setup(run_till, run_till);
      // save ssd_storage as a json file
      var ssd_storage_json = JSON.stringify(ssd_storage);
      var blob = new Blob([ssd_storage_json], { type: "application/json" });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = file_name + ".json";
      a.click();

      // save waf_trace as a json file
      var waf_storage = JSON.stringify(waf_log);
      var blob = new Blob([waf_storage], { type: "application/json" });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = file_name + "_waf.json";
      a.click();

      // save cummalative_time_per_packet_log as a json file
      var cummalative_time_per_packet_storage = JSON.stringify(
        cummalative_time_per_packet_log
      );
      var blob = new Blob([cummalative_time_per_packet_storage], {
        type: "application/json",
      });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = file_name + "_cummalative_time_per_packet.json";
      a.click();

      stopProcessingGif("Write Completed");
      color_brighness();
    };
    reader.readAsText(file);
  }
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
  stopProcessingGif("Please upload trace");
  handleOverprovisioning();
};
