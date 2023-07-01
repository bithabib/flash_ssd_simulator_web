class TopicStorage {
  constructor() {
    this.definitions = {
        "eyana_ssd_simulator":"Eyana: The SSD Simulator offers an immersive experience to understand the intricate workings of Solid-State Drives (SSDs). Through realistic simulations, users can delve into the complexities of flash memory technology, data management algorithms, wear leveling techniques, and performance optimizations employed by SSDs. Eyana provides a hands-on platform for learning and experimentation, enabling users to gain insights into the inner workings of SSDs and their impact on storage performance and reliability.",
        "page_block_plane_die_package": "Page: A page refers to the smallest unit of data that can be read from or written to in a NAND-flash memory. It is typically a fixed-size portion of memory, such as 2 KB, 4 KB, 8 KB, or 16 KB. Pages are organized within blocks. \n Block: A block is a group of pages in NAND-flash memory that can be erased as a single unit. The block size can vary depending on the SSD, typically ranging from 256 KB to 4 MB. All pages within a block need to be erased together before new data can be written to them. \n Plane: A plane is a higher-level grouping of blocks within NAND-flash memory. It consists of multiple blocks that are organized together. The purpose of having planes is to allow parallel operations, such as simultaneous reading or writing, to improve overall performance and efficiency. \nDie: A die is a physical unit within a NAND-flash memory chip. It contains multiple planes and is responsible for storing and accessing data. A die is typically a square or rectangular piece of semiconductor material that contains the necessary circuitry to operate the memory cells.\nPackage: A package refers to the overall physical enclosure that houses one or more NAND-flash memory dies. It includes the necessary components for the memory chip to function, such as the controller, interface, and other supporting circuitry. The package is what is typically visible and connects to a computer or device when using an SSD or other NAND-flash-based storage device."
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