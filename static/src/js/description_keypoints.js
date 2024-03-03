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
      mapping: {
        title: "Logical Block Mapping",
        description: `
        <p>The logical block mapping translates logical block addresses (LBAs) from the host space into physical block addresses (PBAs) in the physical NAND-flash memory space. This mapping takes the form of a table, which for any LBA gives the corresponding PBA. This mapping table is stored in the RAM of the SSD for speed of access, and is persisted in flash memory in case of power failure. When the SSD powers up, the table is read from the persisted version and reconstructed into the RAM of the SSD.</p>
        <p>The naive approach is to use a page-level mapping to map any logical page from the host to a physical page. This mapping policy offers a lot of flexibility, but the major drawback is that the mapping table requires a lot of RAM, which can significantly increase the manufacturing costs. A solution to that would be to map blocks instead of pages, using a block-level mapping. Let’s assume that an SSD drive has 256 pages per block. This means that block-level mapping requires 256 times less memory than page-level mapping, which is a huge improvement for space utilization. However, the mapping still needs to be persisted on disk in case of power failure, and in case of workloads with a lot of small updates, full blocks of flash memory will be written whereas pages would have been enough. This increases the write amplification and makes block-level mapping widely inefficient</p>
        <p>The tradeoff between page-level mapping and block-level mapping is the one of performance versus space. Some researcher have tried to get the best of both worlds, giving birth to the so-called “hybrid” approaches [10]. The most common is the log-block mapping, which uses an approach similar to log-structured file systems. Incoming write operations are written sequentially to log blocks. When a log block is full, it is merged with the data block associated to the same logical block number (LBN) into a free block. Only a few log blocks need to be maintained, which allows to maintain them with a page granularity. Data blocks on the contrary are maintained with a block granularity [9, 10].</p>
        `,
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
    popupDescriptionTitle.innerHTML =
      storage.getDefinition(defination_id).title;
    popupDescriptionContent.innerHTML =
      storage.getDefinition(defination_id).description;

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
