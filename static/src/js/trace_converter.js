// Call function to upload trace file
function upload_trace_file() {
  const fileInput = document.getElementById("upload_trace_file");
  var file = fileInput.files[0];
  // call flask api to upload trace file
  var formData = new FormData();
  formData.append("file", file);
  fetch("/trace_file_converter", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      // get converted format selected
      var converted_format = document.getElementById("conversionFormat").value;
      console.log(converted_format);
      if (converted_format == "json") {
        // download this data as a json file
        var a = document.createElement("a");
        var file = new Blob([JSON.stringify(data.traces)], {
          type: "application/json",
        });
        a.href = URL.createObjectURL(file);
        a.download = "converted_trace.json";
        a.click();
      }else if (converted_format == "csv") {

        var a = document.createElement("a");
        var csv = "CPU_Core_ID,Device_Major_Number,Device_Minor_Number,IO_Size,OperationType,ProcessID,ProcessName,Record_ID,SectorNumber,Timestamp_nanoseconds,Trace_Action\n";
        data.traces.forEach(function(row) {
          csv += row.CPU_Core_ID + "," + row.Device_Major_Number + "," + row.Device_Minor_Number + "," + row.IO_Size + "," + row.OperationType + "," + row.ProcessID + "," + row.ProcessName + "," + row.Record_ID + "," + row.SectorNumber + "," + row.Timestamp_nanoseconds + "," + row.Trace_Action + "\n";
        });
        var file = new Blob([csv], { type: "text/csv" });
        a.href = URL.createObjectURL(file);
        a.download = "converted_trace.csv";
        a.click();

      }
    });
}
