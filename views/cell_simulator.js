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
const electronList = new ElectronList();
var floatingGate = document.getElementById("floating_gate");
var controlGate = document.getElementById("control_gate");
var electrons = document.getElementsByClassName("rounded-circle");

var floatingGateX = floatingGate.getBoundingClientRect().left;
var floatingGateY = floatingGate.getBoundingClientRect().top;

function moveVoltage(voltageCircle, animation, diffY) {
  console.log("moveVoltage");
  console.log("animation: " + animation);
  console.log("diffY: " + diffY);
  animation += 1;
  voltageCircle.style.top = animation + "px";
  if (diffY > Math.abs(animation)) {
    requestAnimationFrame(() => moveVoltage(voltageCircle, animation, diffY));
  } else {
    voltageCircle.style.display = "none";
    voltageCircle.style.top = "50px";
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

function moveElectron(electron, animation, diffY) {
  animation -= 1;
  electron.style.top = animation + "px";
  if (diffY > Math.abs(animation)) {
    requestAnimationFrame(() => moveElectron(electron, animation, diffY));
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
    // console.log("voltageCircleY: " + voltageCircleY);
    var diffYVoltage = Math.abs(voltageCircleY - controlGateY);
    applyingVoltageMessage(true);
    moveVoltage(voltageCircle, 50, diffYVoltage + 60);
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  await new Promise((resolve) => setTimeout(resolve, 1000));
  for (const randomElectron of selectRandomElectrons) {
    // electrons[randomElectron].style.display = "none";
    var electron = electrons[randomElectron];
    var electronY = electron.getBoundingClientRect().top;
    var diffY = Math.abs(electronY - floatingGateY) - 60;
    moveElectron(electron, 0, diffY);
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
  console.log("animation: " + animation);
  moveCurrent.style.left = animation + "px";
  if (diffX > Math.abs(animation)) {
    requestAnimationFrame(() =>
      moveElectronRead(moveCurrent, animation, diffX)
    );
  } else {
    moveCurrent.style.left = "0px";
    moveCurrent.style.display = "none";
  }
}

var readButton = document.getElementById("read_button");
readButton.addEventListener("click", async function () {
  document.getElementById("applying_read_voltage").style.display = "block";
  document.getElementById("applying_write_voltage").style.display = "none";
  var voltageCircles = document.getElementsByClassName("voltage_circle");
  for (const voltageCircle of voltageCircles) {
    voltageCircle.style.display = "block";
    var voltageCircleY = voltageCircle.getBoundingClientRect().top;
    var controlGateY = controlGate.getBoundingClientRect().top;
    // console.log("voltageCircleY: " + voltageCircleY);
    var diffYVoltage = Math.abs(voltageCircleY - controlGateY);
    // applyingVoltageMessage(true);
    moveVoltage(voltageCircle, 50, diffYVoltage + 60);
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  var moveCurrents = document.getElementsByClassName("arrow");
  var drain = document.getElementById("drain_id");
  var drainX = drain.getBoundingClientRect().left;
  var removed_electrons = electronList.getRemovedElectrons();
  for (const moveCurrent of moveCurrents) {
    if (removed_electrons.length === 0) {
      moveCurrent.style.display = "block";
      var moveCurrentX = moveCurrent.getBoundingClientRect().left;
      var diffX = Math.abs(moveCurrentX - drainX) - 60;
      moveElectronRead(moveCurrent, 0, (diffX + 70) / 2);
      await new Promise((resolve) => setTimeout(resolve, 1000));
    } else {
      moveCurrent.style.display = "block";
      var moveCurrentX = moveCurrent.getBoundingClientRect().left;
      var diffX = Math.abs(moveCurrentX - drainX) - 60;
      moveElectronRead(moveCurrent, 0, diffX + 70);
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }
});
