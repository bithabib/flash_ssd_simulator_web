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
  }else{
    voltageCircle.style.display = "none";
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
    moveVoltage(voltageCircle, 50, diffYVoltage+60);
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  await new Promise((resolve) => setTimeout(resolve, 1000));
  for (const randomElectron of selectRandomElectrons) {
    // electrons[randomElectron].style.display = "none";
    var electron = electrons[randomElectron];
    var electronY = electron.getBoundingClientRect().top;
    var diffY = Math.abs(electronY - floatingGateY) - 10;
    moveElectron(electron, 0, diffY);
  }
}

const writeButton = document.getElementById("write_button");
writeButton.addEventListener("click", moveElectronButton);
