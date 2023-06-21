class FlashMemory {
    constructor(packageCount, dieCount, blockCount, pageCount) {
      this.packageCount = packageCount;
      this.dieCount = dieCount;
      this.blockCount = blockCount;
      this.pageCount = pageCount;
  
      this.flashMemoryArray = this.createFlashMemoryArray();
    }
  
    createFlashMemoryArray() {
      const flashMemoryArray = [];
  
      for (let packageIndex = 0; packageIndex < this.packageCount; packageIndex++) {
        const packageData = [];
  
        for (let dieIndex = 0; dieIndex < this.dieCount; dieIndex++) {
          const dieData = [];
  
          for (let blockIndex = 0; blockIndex < this.blockCount; blockIndex++) {
            const blockData = [];
  
            for (let pageIndex = 0; pageIndex < this.pageCount; pageIndex++) {
              // Initializing with empty data
              blockData.push(null);
            }
  
            dieData.push(blockData);
          }
  
          packageData.push(dieData);
        }
  
        flashMemoryArray.push(packageData);
      }
  
      return flashMemoryArray;
    }
  
    readData(packageIndex, dieIndex, blockIndex, pageIndex) {
      if (
        packageIndex < 0 ||
        packageIndex >= this.packageCount ||
        dieIndex < 0 ||
        dieIndex >= this.dieCount ||
        blockIndex < 0 ||
        blockIndex >= this.blockCount ||
        pageIndex < 0 ||
        pageIndex >= this.pageCount
      ) {
        throw new Error("Invalid memory address.");
      }
  
      return this.flashMemoryArray[packageIndex][dieIndex][blockIndex][pageIndex];
    }
  
    writeData(packageIndex, dieIndex, blockIndex, pageIndex, data) {
      if (
        packageIndex < 0 ||
        packageIndex >= this.packageCount ||
        dieIndex < 0 ||
        dieIndex >= this.dieCount ||
        blockIndex < 0 ||
        blockIndex >= this.blockCount ||
        pageIndex < 0 ||
        pageIndex >= this.pageCount
      ) {
        throw new Error("Invalid memory address.");
      }
  
      this.flashMemoryArray[packageIndex][dieIndex][blockIndex][pageIndex] = data;
    }
  }
  
  // Example usage
  const flashMemory = new FlashMemory(2, 4, 16, 64);
  
  // Write data
  flashMemory.writeData(0, 0, 0, 0, "Data1");
  
  // Read data
  const data = flashMemory.readData(0, 0, 0, 0);
  console.log(data); // Output: "Data1"