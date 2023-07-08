const moveButton = document.getElementById("write_button");
const circleDiv = document.getElementById("circle1");

let intervalId = null; // Store the interval ID

moveButton.addEventListener("click", () => {
  clearInterval(intervalId); // Clear the previous interval if any

  const targetTop = 0; // Target top position (adjust as needed)
  const duration = 1000; // Animation duration in milliseconds (adjust as needed)
  const fps = 60; // Frames per second (adjust as needed)
  const increment = (targetTop - circleDiv.offsetTop) / (duration / 1000 * fps);

  intervalId = setInterval(() => {
    const currentTop = circleDiv.offsetTop;
    const newTop = currentTop + increment;

    if (newTop <= targetTop) {
      circleDiv.style.top = `${targetTop}px`;
      clearInterval(intervalId); // Stop the interval once the div reaches the desired position
    } else {
      circleDiv.style.top = `${newTop}px`;
    }
  }, 1000 / fps);
});
