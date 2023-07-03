class TopicStorage {
  constructor() {
    this.definitions = {
      definition_ssd: `
        <p>Eyana: The SSD Simulator offers an immersive experience to understand the intricate workings of Solid-State Drives (SSDs). Through realistic simulations, users can delve into the complexities of flash memory technology, data management algorithms, wear leveling techniques, and performance optimizations employed by SSDs. Eyana provides a hands-on platform for learning and experimentation, enabling users to gain insights into the inner workings of SSDs and their impact on storage performance and reliability.</p>
      `,
      popup_description2: `
        <p>Page: A page refers to the smallest unit of data that can be read from or written to in a NAND-flash memory. It is typically a fixed-size portion of memory, such as 2 KB, 4 KB, 8 KB, or 16 KB. Pages are organized within blocks.</p>
        <p>Block: A block is a group of pages in NAND-flash memory that can be erased as a single unit. The block size can vary depending on the SSD, typically ranging from 256 KB to 4 MB. All pages within a block need to be erased together before new data can be written to them.</p>
        <p>Plane: A plane is a higher-level grouping of blocks within NAND-flash memory. It consists of multiple blocks that are organized together. The purpose of having planes is to allow parallel operations, such as simultaneous reading or writing, to improve overall performance and efficiency.</p>
        <p>Die: A die is a physical unit within a NAND-flash memory chip. It contains multiple planes and is responsible for storing and accessing data. A die is typically a square or rectangular piece of semiconductor material that contains the necessary circuitry to operate the memory cells.</p>
        <p>Package: A package refers to the overall physical enclosure that houses one or more NAND-flash memory dies. It includes the necessary components for the memory chip to function, such as the controller, interface, and other supporting circuitry. The package is what is typically visible and connects to a computer or device when using an SSD or other NAND-flash-based storage device.</p>
      `,
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
const infoButton = document.querySelector(".definition_ssd");
const closePopupButton = document.getElementById("closePopupButton");
infoButton.addEventListener("click", function() {
  const buttonRect = infoButton.getBoundingClientRect();
  const buttonX = buttonRect.left + buttonRect.width / 2;
  const buttonY = buttonRect.top + buttonRect.height / 2;
  const popupDescription = document.getElementById("popup_description");
  const popupDescriptionTitle = document.getElementById("defination_title");
  const popupDescriptionContent = document.getElementById("defination_description");
  popupDescriptionTitle.innerHTML = "SSD Simulator";
  popupDescriptionContent.innerHTML = storage.getDefinition("definition_ssd");

  // Get the dimensions of the popup
  const popupWidth = popupDescription.offsetWidth;
  const popupHeight = popupDescription.offsetHeight;

  // Calculate the desired position of the popup
  let popupX = window.innerWidth / 2 - popupWidth / 2;
  let popupY = Math.max(10, buttonY - popupHeight - 10);

  // Check if the popup would go off the screen
  if (popupX < 0) {
    popupX = 0;
  } else if (popupX + popupWidth > window.innerWidth) {
    popupX = window.innerWidth - popupWidth;
  }

  if (popupY < 0) {
    popupY = 0;
  } else if (popupY + popupHeight > window.innerHeight) {
    popupY = window.innerHeight - popupHeight;
  }

  // Set the position of the popup
  popupDescription.style.display = "block";
  popupDescription.style.top = `${popupY}px`;
  popupDescription.style.left = `${popupX}px`;
});



closePopupButton.addEventListener("click", function () {
  const popupDescription = document.getElementById("popup_description");
  popupDescription.style.display = "none";
  // Remove p tag child from popupDescription
  

});
