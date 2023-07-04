class TopicStorage {
  constructor() {
    this.definitions = {
      definition_ssd: {
        title: "SSD Simulator",
        description: `<p>Eyana: The SSD Simulator offers an immersive experience to understand the intricate workings of Solid-State Drives (SSDs). Through realistic simulations, users can delve into the complexities of flash memory technology, data management algorithms, wear leveling techniques, and performance optimizations employed by SSDs. Eyana provides a hands-on platform for learning and experimentation, enabling users to gain insights into the inner workings of SSDs and their impact on storage performance and reliability.</p>`,
      },

      page: {
        title: "Page",
        description: `<p>Page: A page refers to the smallest unit of data that can be read from or written to in a NAND-flash memory. It is typically a fixed-size portion of memory, such as 2 KB, 4 KB, 8 KB, or 16 KB. Pages are organized within blocks.</p>`,
      },
      block: {
        title: "Block",
        description: `<p>Block: A block is a collection of pages. It is the smallest unit of data that can be erased from a NAND-flash memory. A block is typically 128 KB or 256 KB in size. Blocks are organized within planes.</p>`,
      },
      plane: {
        title: "Plane",
        description: `<p>Plane: A plane is a collection of blocks. It is the smallest unit of data that can be erased from a NAND-flash memory. A plane is typically 1 MB in size. Planes are organized within dies.</p>`,
      },
      die: {
        title: "Die",
        description: `<p>Die: A die is a collection of planes. It is the smallest unit of data that can be erased from a NAND-flash memory. A die is typically 4 MB in size. Dies are organized within chips.</p>`,
      },
      package: {
        title: "Package",
        description: `<p>Package: A package is a collection of dies. It is the smallest unit of data that can be erased from a NAND-flash memory. A package is typically 16 MB in size. Packages are organized within SSDs.</p>`,
      },
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
// const infoButtons = document.querySelector(".definition_ssd");
const infoButtons = document.getElementsByClassName("definition_ssd");
const closePopupButton = document.getElementById("closePopupButton");

for (const infoButton of infoButtons) {
  infoButton.addEventListener("click", function () {
    const buttonRect = infoButton.getBoundingClientRect();
    const buttonX = buttonRect.left + buttonRect.width / 2;
    const buttonY = buttonRect.top + buttonRect.height / 2;
    const popupDescription = document.getElementById("popup_description");
    const popupDescriptionTitle = document.getElementById("defination_title");
    const popupDescriptionContent = document.getElementById(
      "defination_description"
    );
    // get the id of the clicked span
    const defination_id = infoButton.id;
    popupDescriptionTitle.innerHTML = storage.getDefinition(defination_id).title;
    popupDescriptionContent.innerHTML = storage.getDefinition(defination_id).description;

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
}

closePopupButton.addEventListener("click", function () {
  const popupDescription = document.getElementById("popup_description");
  popupDescription.style.display = "none";
});
