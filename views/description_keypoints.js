class TopicStorage {
  constructor() {
    this.definitions = {
        "eyana_ssd_simulator":"Eyana: The SSD Simulator offers an immersive experience to understand the intricate workings of Solid-State Drives (SSDs). Through realistic simulations, users can delve into the complexities of flash memory technology, data management algorithms, wear leveling techniques, and performance optimizations employed by SSDs. Eyana provides a hands-on platform for learning and experimentation, enabling users to gain insights into the inner workings of SSDs and their impact on storage performance and reliability."
    };
  }

  addDefinition(topic, definition) {
    this.definitions[topic] = definition;
  }

  getDefinition(topic) {
    return this.definitions[topic];
  }

  getAllTopics() {
    return Object.keys(this.definitions);
  }

  removeDefinition(topic) {
    delete this.definitions[topic];
  }

  removeAllDefinitions() {
    this.definitions = {};
  }
}
const storage = new TopicStorage();
var hoverArea = document.getElementById("ssd_defination_hover");
var popup = document.getElementById("popup_description");
var hoverTimeout;

function showPopup(x, y) {
  popup.style.display = "block";
  popup.style.left = x + "px";
  popup.style.top = y + "px";
}

function hidePopup() {
  popup.style.display = "none";
}

function startTimer(x, y) {
  hoverTimeout = setTimeout(function () {
    showPopup(x, y);
  }, 2000);
}

function resetTimer() {
  clearTimeout(hoverTimeout);
  var rect = hoverArea.getBoundingClientRect();
  startTimer(rect.left, rect.top);
}

function handleMouseOver(event) {
  resetTimer();
}

function handleMouseOut() {
  clearTimeout(hoverTimeout);
}

function handleOkButtonClick() {
  hidePopup();
  clearTimeout(hoverTimeout);
}

hoverArea.addEventListener("mouseover", handleMouseOver);
hoverArea.addEventListener("mouseout", handleMouseOut);

// Generate dynamic content and OK button for the popup
var popupContent = document.createElement("p");
popupContent.textContent = storage.getDefinition("eyana_ssd_simulator");
popup.appendChild(popupContent);

var okButton = document.createElement("button");
okButton.textContent = "OK";
okButton.addEventListener("click", handleOkButtonClick);
popup.appendChild(okButton);
