function getScrollPosition() {
  const verticalScroll =
    window.pageYOffset || document.documentElement.scrollTop;
  const horizontalScroll =
    window.pageXOffset || document.documentElement.scrollLeft;
  return { verticalScroll, horizontalScroll };
}
window.addEventListener("scroll", getScrollPosition);

function getCurrentScrollPositions() {
  return getScrollPosition();
}

class ElectronList {
  constructor() {
    this.electrons = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
    this.removedElectrons = [];
  }

  addElectron(electron) {
    this.electrons.push(electron);
  }

  removeElectron() {
    if (this.electrons.length > 0) {
      const removedElectron = this.electrons.pop();
      this.removedElectrons.push(removedElectron);
      return removedElectron;
    } else {
      return null;
    }
  }

  getRemovedElectrons() {
    return this.removedElectrons;
  }

  selectRandomElectrons() {
    var cell_type_id = document.getElementById("cell_type");
    var cell_type = cell_type_id.value;
    if (cell_type === "single_level_cell") {
      const selectedElectrons = [];
      for (let i = 0; i < 7; i++) {
        const randomIndex = Math.floor(Math.random() * this.electrons.length);
        const selectedElectron = this.electrons.splice(randomIndex, 1)[0];
        this.removedElectrons.push(selectedElectron);
        selectedElectrons.push(selectedElectron);
      }
      return selectedElectrons;
    } else {
      const selectedElectrons = [];
      for (let i = 0; i < 3; i++) {
        const randomIndex = Math.floor(Math.random() * this.electrons.length);
        const selectedElectron = this.electrons.splice(randomIndex, 1)[0];
        this.removedElectrons.push(selectedElectron);
        selectedElectrons.push(selectedElectron);
      }
      return selectedElectrons;
    }
  }
}
const electronList = new ElectronList();
var floatingGate = document.getElementById("floating_gate");
var controlGate = document.getElementById("control_gate");
var electrons = document.getElementsByClassName("rounded-circle");

var floatingGateX = floatingGate.getBoundingClientRect().left;
var floatingGateY = floatingGate.getBoundingClientRect().top;

async function moveVoltage(voltageCircle, animation, diffY) {
  animation += 1;
  voltageCircle.style.top = animation + "px";
  if (diffY > Math.abs(animation)) {
    requestAnimationFrame(() => moveVoltage(voltageCircle, animation, diffY));
  } else {
    voltageCircle.style.display = "none";
    voltageCircle.style.top = "50px";
  }
}

function moveNegativeVoltage(voltageCircle, animation, diffY) {
  animation -= 1;
  voltageCircle.style.top = animation + "px";
  if (diffY < Math.abs(animation)) {
    requestAnimationFrame(() =>
      moveNegativeVoltage(voltageCircle, animation, diffY)
    );
  } else {
    voltageCircle.style.display = "none";
    voltageCircle.style.top = diffY + "px";
  }
}

function applyingVoltageMessage(isApplying) {
  var voltageWriteMessage = document.getElementById("applying_write_voltage");
  var voltageEraseMessage = document.getElementById("applying_erase_voltage");
  var voltageReadMessage = document.getElementById("applying_read_voltage");
  if (isApplying) {
    voltageWriteMessage.style.display = "block";
    voltageEraseMessage.style.display = "none";
    voltageReadMessage.style.display = "none";
  } else {
    voltageWriteMessage.style.display = "none";
    voltageEraseMessage.style.display = "block";
  }
}

async function moveElectron(electron, animation, diffY) {
  animation -= 1;
  electron.style.top = animation + "px";
  if (diffY > Math.abs(animation)) {
    requestAnimationFrame(
      async () => await moveElectron(electron, animation, diffY)
    );
  }
}

async function moveElectronButton() {
  var selectRandomElectrons = electronList.selectRandomElectrons();
  // var voltageCircle = document.getElementById("voltage_circle");
  var voltageCircles = document.getElementsByClassName("voltage_circle");
  for (const voltageCircle of voltageCircles) {
    voltageCircle.style.display = "block";
    var voltageCircleY = voltageCircle.getBoundingClientRect().top;
    var controlGateY = controlGate.getBoundingClientRect().top;
    var diffYVoltage = Math.abs(voltageCircleY - controlGateY);
    applyingVoltageMessage(true);
    await moveVoltage(voltageCircle, 50, diffYVoltage + 60);
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  await new Promise((resolve) => setTimeout(resolve, 1000));
  for (const randomElectron of selectRandomElectrons) {
    // electrons[randomElectron].style.display = "none";
    var electron = electrons[randomElectron];
    var electronY = electron.getBoundingClientRect().top;
    const scrollPositions = getCurrentScrollPositions();
    var diffY =
      Math.abs(electronY - floatingGateY) + scrollPositions.verticalScroll + 40;
    await moveElectron(electron, 0, diffY);
  }
}

const writeButton = document.getElementById("write_button");
writeButton.addEventListener("click", moveElectronButton);

// make a div full screen
// var fullscreenBtn = document.getElementById("fullscreen");
// fullscreenBtn.addEventListener("click", function () {
//   var myDiv = document.getElementById("fullscreen_div");
//   myDiv.classList.toggle("fullscreen");
// });

async function moveElectronRead(moveCurrent, animation, diffX) {
  animation += 1;
  moveCurrent.style.left = animation + "px";
  if (diffX > Math.abs(animation)) {
    requestAnimationFrame(
      async () => await moveElectronRead(moveCurrent, animation, diffX)
    );
  } else {
    moveCurrent.style.left = "0px";
    moveCurrent.style.display = "none";
  }
}

var readButton = document.getElementById("read_button");
readButton.addEventListener("click", async function () {
  var cell_type_id = document.getElementById("cell_type");
  var cell_type = cell_type_id.value;
  var cell_type_value = 0;
  if (cell_type === "single_level_cell") {
    cell_type_value = 4;
  } else {
    cell_type_value = 0;
  }
  var removed_electrons_length =
    electronList.getRemovedElectrons().length + 3 + cell_type_value;

  var circle_tracer = 1 + cell_type_value;
  for (
    var applying_voltage = 2.5 + cell_type_value;
    applying_voltage <= removed_electrons_length;
    applying_voltage += 2.5 + cell_type_value
  ) {
    var applying_read_voltage = document.getElementById(
      "applying_read_voltage"
    );
    applying_read_voltage.textContent = "Applying " + applying_voltage + "V";
    applying_read_voltage.style.display = "block";

    document.getElementById("applying_write_voltage").style.display = "none";
    var voltageCircles = document.getElementsByClassName("voltage_circle");
    for (const voltageCircle of voltageCircles) {
      voltageCircle.style.display = "block";
      var voltageCircleY = voltageCircle.getBoundingClientRect().top;
      var controlGateY = controlGate.getBoundingClientRect().top;
      var diffYVoltage = Math.abs(voltageCircleY - controlGateY);
      // applyingVoltageMessage(true);
      await moveVoltage(voltageCircle, 50, diffYVoltage + 60);
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
    var moveCurrents = document.getElementsByClassName("arrow");
    var drain = document.getElementById("drain_id");
    var drainX = drain.getBoundingClientRect().left;
    for (const moveCurrent of moveCurrents) {
      if (applying_voltage + 2.5 > removed_electrons_length) {
        moveCurrent.style.display = "block";
        var moveCurrentX = moveCurrent.getBoundingClientRect().left;
        var diffX = Math.abs(moveCurrentX - drainX) - 60;
        await moveElectronRead(moveCurrent, 0, diffX + 70);
        await new Promise((resolve) => setTimeout(resolve, 500));
      } else {
        moveCurrent.style.display = "block";
        var moveCurrentX = moveCurrent.getBoundingClientRect().left;
        var diffX = Math.abs(moveCurrentX - drainX) - 60;
        await moveElectronRead(moveCurrent, 0, (diffX + 70) / 2);
        await new Promise((resolve) => setTimeout(resolve, 500));
        var circle_element = document.getElementsByClassName(
          "circle" + circle_tracer
        )[0];
        circle_element.style.backgroundColor = "lightblue";
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 3000));
    if (applying_voltage + 2.5 > removed_electrons_length) {
      var circle_element = document.getElementsByClassName(
        "circle" + circle_tracer
      )[0];
      circle_element.style.backgroundColor = "red";
    }
    circle_tracer += 1;
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
});

// Erase button
async function moveElectronErase(moveCurrent, animation, diffX) {}

// erase button click event
var eraseButton = document.getElementById("erase_button");
eraseButton.addEventListener("click", async function () {
  applying_erase_voltage = document.getElementById("applying_erase_voltage");
  applying_erase_voltage.style.display = "block";
  document.getElementById("applying_write_voltage").style.display = "none";
  var voltageCircles = document.getElementsByClassName("neg_voltage_circle");
  for (const voltageCircle of voltageCircles) {
    voltageCircle.style.display = "block";
    var voltageCircleY = voltageCircle.getBoundingClientRect().top;
    var controlGateY = controlGate.getBoundingClientRect().top;
    var diffYVoltage = Math.abs(voltageCircleY - controlGateY);
    // applyingVoltageMessage(true);
    moveNegativeVoltage(voltageCircle, diffYVoltage + 150, diffYVoltage + 70);
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  // get removed electrons
  var removedElectrons = electronList.getRemovedElectrons();
  for (const randomElectron of removedElectrons) {
    // electrons[randomElectron].style.display = "none";
    var electron = electrons[randomElectron];
    var electronY = electron.getBoundingClientRect().top;
    const scrollPositions = getCurrentScrollPositions();
    var diffY =
      Math.abs(electronY - floatingGateY) + scrollPositions.verticalScroll - 60;
    moveElectron(electron, 0, diffY);
  }
});

// selection of single level cell and multi level cell from dropdown menu

document.addEventListener("DOMContentLoaded", function () {
  var cell_type = document.getElementById("cell_type");
  cell_type.addEventListener("change", function () {
    var cell_type_value = cell_type.value;
    if (cell_type_value === "single_level_cell") {
      document.getElementById("single_level_cell").style.display = "block";
      document.getElementById("multi_level_cell").style.display = "none";
    } else {
      document.getElementById("single_level_cell").style.display = "none";
      document.getElementById("multi_level_cell").style.display = "block";
    }
  });
});
