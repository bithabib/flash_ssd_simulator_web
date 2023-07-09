var floatingGate = document.getElementById("floating_gate");
var electron = document.getElementById("electron1");

var floatingGateX = floatingGate.getBoundingClientRect().left;
var floatingGateY = floatingGate.getBoundingClientRect().top;

var electronX = electron.getBoundingClientRect().left;
var electronY = electron.getBoundingClientRect().top;
// get the difference between the floating gate and electron
// var diffX = (electronX - floatingGateX) * 0.05; // Adjust the speed of motion by changing the multiplier

// click write button to move electron to floating gate
var animation = 0;
var diffY = electronY - floatingGateY;
function moveElectron() {
  animation -= 1;
  electron.style.top = animation + "px";
  if (Math.abs(diffY) > Math.abs(animation)) {
    requestAnimationFrame(moveElectron);
  }
}

const writeButton = document.getElementById("write_button");
writeButton.addEventListener("click", moveElectron);

