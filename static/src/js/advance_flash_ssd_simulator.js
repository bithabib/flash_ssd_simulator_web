// Waf Graph update
function updateWAFGraph(
  wafGraphData,
  writeCountGraphData,
  averageWriteCountGraphData,
  eraseCountGraphData,
  averageEraseCountGraphData
) {
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
        dataPoints: wafGraphData,
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
        type: "line",
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
  document.getElementById("waf_value").innerHTML =
    wafGraphData[wafGraphData.length - 1].y.toFixed(2);
  wafChart.render();
  writeCountChart.render();
  eraseCountChart.render();
}

// Function to create block for each plane
var forceStop = false;
var ssd_block_trace_list = [];
var ssd_block_trace_dict = {};
var max_erase_count = 0;
var max_write_count = 0;
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

function color_brighness(part, whole, aw, garbage = false) {
  var percentage = (part / whole) * 100;
  var brightness = Math.floor(255 * (percentage / 100));
  if (brightness < 0) brightness = 0;
  if (brightness > 255) brightness = 255;
  // Construct the CSS color string
  var color = "rgb(0," + brightness + ",0)";
  if (garbage && aw == 0) {
    // set color as white
    color = "rgb(255,255,255)";
  }
  if (part == 0 && whole == 0) {
    // set color as white
    color = "rgb(255,255,255)";
  }
  // console.log(color);
  return color;
}

// Call function to upload trace file
async function upload_trace_file(event) {
  var file = event.target.files[0];
  const fields_name = ["lba", "io_s", "iot"];
  var allocation_scheme = document.getElementById(
    "ssd_allocation_scheme"
  ).value;
  console.log(allocation_scheme);
  if (file) {
    const reader = new FileReader();
    reader.onload = async function (e) {
      const lines = e.target.result.split("\n");
      var file_lenght = lines.length;
      var count_written_block = 0;
      for (let i = 0; i < file_lenght; i += 10000) {
        let traceList = [];
        for (let j = i; j < i + 10000 && j < file_lenght; j++) {
          const trace = {};
          const values = lines[j].split(",");
          for (let k = 0; k < fields_name.length; k++) {
            trace[fields_name[k]] = values[k + 1];
          }
          if (trace["iot"] == "W" || trace["iot"] == "w") {
            traceList.push(trace);
          }
        }
        // console.log("traceList");
        // console.log(traceList);
        var body = {
          traceList: traceList,
          allocation_scheme: allocation_scheme,
        };
        startProcessingGif("processing trace file");
        await fetch("/upload_trace_file", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
        })
          .then((response) => response.json())
          .then(async (data) => {
            // console.log(data);
            startProcessingGif("start writing trace to ssd");
            ssd_block_trace_list = data.traces.ssd_block_trace_list;
            ssd_block_trace_dict = data.traces.ssd_block_trace_dict;
            max_erase_count = data.traces.max_erase_count;
            max_write_count = data.traces.max_write_count;
            let ssd_block_trace_list_length = ssd_block_trace_list.length;

            // all graph variable
            var wafGraphData = [];
            var hostWrite = 0;
            var nandWrite = 0;
            var writeCountGraphData = [];
            var averageWriteCountGraphData = [];
            var totalWriteCount = 0;
            var eraseCountGraphData = [];
            var totalEraseCount = 0;
            var averageEraseCountGraphData = [];
            for (var i = 0; i < ssd_block_trace_list_length; i++) {
              var block = document.getElementById(ssd_block_trace_list[i]);
              hostWrite += ssd_block_trace_dict[ssd_block_trace_list[i]].aw;
              if (ssd_block_trace_dict[ssd_block_trace_list[i]].wpc > 128) {
                console.log(ssd_block_trace_dict[ssd_block_trace_list[i]].wpc);
              }
              nandWrite +=
                ssd_block_trace_dict[ssd_block_trace_list[i]].wpc +
                ssd_block_trace_dict[ssd_block_trace_list[i]].gcs;
              totalWriteCount +=
                ssd_block_trace_dict[ssd_block_trace_list[i]].wc;
              totalEraseCount +=
                ssd_block_trace_dict[ssd_block_trace_list[i]].ec;
              wafGraphData.push({
                y: (nandWrite * 4) / hostWrite,
              });

              writeCountGraphData.push({
                y: ssd_block_trace_dict[ssd_block_trace_list[i]].wc,
              });
              averageWriteCountGraphData.push({
                y: totalWriteCount / (i + 1),
              });
              eraseCountGraphData.push({
                y: ssd_block_trace_dict[ssd_block_trace_list[i]].ec,
              });
              averageEraseCountGraphData.push({
                y: totalEraseCount / (i + 1),
              });
              // Call waf graph update function

              // call function to update block color
              block.style.backgroundColor = color_brighness(
                ssd_block_trace_dict[ssd_block_trace_list[i]].wc,
                max_write_count
              );
              await new Promise((resolve) => setTimeout(resolve, 5));
            }
            updateWAFGraph(
              wafGraphData,
              writeCountGraphData,
              averageWriteCountGraphData,
              eraseCountGraphData,
              averageEraseCountGraphData
            );
            var writeableSSDSizePercent = 100 - getOverprovisioningRatio();
            count_written_block += ssd_block_trace_list_length;
            var nandWritePercentage = (nandWrite / 614400) * 100;
            console.log(nandWritePercentage);
            console.log(writeableSSDSizePercent);
            stopProcessingGif("Trace written to ssd");

            await new Promise((resolve) => setTimeout(resolve, 1000));

            if (nandWritePercentage >= writeableSSDSizePercent) {
              if (nandWritePercentage > 100) {
                // notify user that ssd is full
                alert("SSD is full");
              }

              startProcessingGif("Garbage Collection");
              await fetch("/garbage_collection", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({}),
              })
                .then((response) => response.json())
                .then(async (data) => {
                  // console.log(data);
                  ssd_block_trace_list = data.traces.ssd_block_trace_list;
                  ssd_block_trace_dict = data.traces.ssd_block_trace_dict;
                  let ssd_block_trace_list_length = ssd_block_trace_list.length;
                  for (var i = 0; i < ssd_block_trace_list_length; i++) {
                    var block = document.getElementById(
                      ssd_block_trace_list[i]
                    );
                    block.style.backgroundColor = color_brighness(
                      ssd_block_trace_dict[ssd_block_trace_list[i]].wc,
                      max_write_count,
                      ssd_block_trace_dict[ssd_block_trace_list[i]].aw,
                      true
                    );
                    await new Promise((resolve) => setTimeout(resolve, 5));
                  }
                  stopProcessingGif("Garbage Collection Done");
                });
            }
          });

        if (forceStop) {
          await fetch("/write/complete", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({}),
          })
            .then((response) => response.json())
            .then(async (data) => {
              // console.log(data);
              stopProcessingGif("Write Complete");
            });
          break;
        }
        // break;
      }
      // await fetch("/write/complete", {
      //   method: "POST",
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      //   body: JSON.stringify({}),
      // })
      //   .then((response) => response.json())
      //   .then(async (data) => {
      //     // console.log(data);
      //     stopProcessingGif("Write Complete");
      //   });
    };
    reader.readAsText(file);
  }

  // var allocation_scheme = document.getElementById(
  //   "ssd_allocation_scheme"
  // ).value;
  // // call flask api to upload trace file
  // var formData = new FormData();
  // formData.append("file", file);
  // formData.append("allocation_scheme", allocation_scheme);
  // startProcessingGif("processing trace file");
  // await new Promise((resolve) => setTimeout(resolve, 1000));
  // fetch("/upload_trace_file", {
  //   method: "POST",
  //   body: formData,
  // })
  //   .then((response) => response.json())
  //   .then(async (data) => {
  //     console.log(data);
  //     // loop through each trace and change color of block
  //     startProcessingGif("start writing trace to ssd");
  //     for (var i = 0; i < data.traces.length; i++) {
  //       var block = document.getElementById(data.traces[i].block_id);
  //       block.style.backgroundColor = color_brighness(
  //         data.traces[i].number_of_hit_in_block,
  //         7
  //       );
  //       await new Promise((resolve) => setTimeout(resolve, 5));
  //     }
  //     stopProcessingGif("Trace written to ssd");
  //   });
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
  // parseInt to convert string to integer
  overprovisioningRatio = parseInt(overprovisioningRatio);
  return overprovisioningRatio;
}
function handleOverprovisioning() {
  var overprovisioningRatio = getOverprovisioningRatio();
  // find the total ss size after overprovision ratio removed from total size
  var totalSize = 2.34375;
  // four decimal points
  var totalSizeAfterOverprovision = (
    totalSize -
    (totalSize * overprovisioningRatio) / 100
  ).toFixed(4);
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
};

async function stopWritingForce() {
  forceStop = true;
  stopProcessingGif("Write Stopped");
  // await fetch("/write/complete", {
  //   method: "POST",
  //   headers: {
  //     "Content-Type": "application/json",
  //   },
  //   body: JSON.stringify({}),
  // })
  //   .then((response) => response.json())
  //   .then(async (data) => {
  //     console.log(data);
  //     stopProcessingGif("Write Complete");
  //   });
}

var select_hitmap_type = document.getElementById("select_hitmap_type");
// Add event listener for the "change" event
select_hitmap_type.addEventListener("change", async function () {
  // Get the selected value
  var hitmap_type = select_hitmap_type.value;
  // console.log(hitmap_type);
  let ssd_block_trace_list_length = ssd_block_trace_list.length;
  if (hitmap_type == "wc") {
    var max_value = max_write_count;
  } else if (hitmap_type == "ec") {
    var max_value = max_erase_count;
  }
  // console.log(ssd_block_trace_list_length);
  // console.log(max_erase_count);
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
      console.log(data);
      // reload the page
      location.reload();
    });
}
