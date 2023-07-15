# Abstract 
Understanding the intricacies of Flash SSD technology can be challenging for students without a solid foundation. To address this issue, we developed Eyana: The SSD Simulator, a web-based tool aimed at simplifying the comprehension of Flash SSD operations. Eyana provides a visual representation of Write, Read, Update, Delete, garbage collection, and flash translation layer processes, along with supporting documentation on concepts like Write Amplification, Wear Leveling, Parallelism, and Multi-Channel. By allowing users to upload files and observe real-time operations, Eyana enables students to understand the complete procedure within a short timeframe. In a survey conducted to evaluate its effectiveness, 99 percent of users regarded Eyana as an exceptionally valuable and one of the best simulators available. In this paper, we present an in-depth overview of Eyana, highlighting its features, functionalities, and its impact on enhancing the understanding of Flash SSD technology. Additionally, we discuss the results of the survey, affirming the simulator's efficacy in facilitating the comprehension of Flash SSDs.


# Eyana: The SSD Simulator
Welcome to the Flash SSD Simulator! This simulator allows you to experience the inner workings of a flash-based Solid-State Drive (SSD) right from your web browser. Whether you're a student studying computer architecture or a curious tech enthusiast, this simulator provides a hands-on understanding of the key operations and concepts related to flash SSDs.

## Enjoy the Simulation
Click [here](https://schoolofthought.tech/templates/flash_memory.html) to dive into the Flash SSD Simulation and explore its interactive features. Gain insights into the intricate processes and components involved in the operation of a Flash SSD.


## Read:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Upload a file to the simulator and observe the read operation in action. Gain insights into how the SSD retrieves data from the flash memory cells and transfers it to the system.

## Write:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Experience the write operation by uploading a file to the simulator. Understand how the SSD stores data in its flash memory cells and organizes it efficiently for quick retrieval.

## Garbage Collection:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Witness the intelligent garbage collection process in action. Learn how the SSD manages free space by reclaiming invalid or deleted data, ensuring optimal utilization of the flash memory.
1. Mark-and-Sweep: This is one of the simplest and most basic garbage collection algorithms. It works by traversing the object graph, starting from a set of root objects, and marking all reachable objects. Then, it sweeps through the memory, deallocating any objects that were not marked.

2. Stop-and-Copy: This algorithm divides the memory into two halves: the "from" space and the "to" space. It starts by marking all reachable objects, and then it copies the live objects from the "from" space to the "to" space, updating all references accordingly. After the copying is complete, the roles of the two spaces are swapped, and the process repeats.

3. Mark-and-Compact: This algorithm is similar to the mark-and-sweep algorithm, but it includes an additional step of compacting the memory after marking. It moves the live objects closer together to eliminate fragmentation and improve memory locality.

4. Generational: This algorithm takes advantage of the observation that most objects become garbage relatively quickly after being allocated. It divides the heap into multiple generations based on the age of the objects. Younger objects are allocated in one generation, while older objects are allocated in other generations. Garbage collection is performed more frequently on the younger generations, while the older generations are collected less often.

5. Reference Counting: Unlike the previous algorithms, reference counting keeps track of the number of references to an object. Each object has a reference count associated with it, and when the count reaches zero, the object is considered garbage and can be deallocated. However, reference counting has the drawback of not being able to detect and collect cyclic references, where objects refer to each other in a cycle.

6. Concurrent and Parallel: These algorithms aim to minimize pauses or reduce the impact of garbage collection on the overall application performance. Concurrent garbage collectors perform garbage collection concurrently with the application, allowing it to continue executing while garbage collection is in progress. Parallel garbage collectors use multiple threads or processors to perform garbage collection in parallel, reducing the overall time spent on garbage collection.

These are some of the commonly used garbage collection algorithms, but there are variations and combinations of these algorithms as well. The choice of garbage collection algorithm depends on various factors, such as the programming language, runtime environment, and specific requirements of the application.

## Mapping (Logical Address to Physical Address):
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Explore the mapping process that converts virtual addresses (VAs) to physical addresses (PAs) within the SSD. Understand how the controller maps logical blocks to specific physical locations, enabling efficient read and write operations.

## Wear Leveling:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Discover the crucial wear leveling mechanism employed by flash SSDs. Observe how the simulator distributes write operations evenly across the memory cells, extending the lifespan and endurance of the SSD.
1. Static Wear Leveling: This algorithm evenly distributes writes across all blocks in the SSD. It ensures that each block receives an equal number of write operations, preventing certain blocks from wearing out faster than others. However, static wear leveling does not take into account the varying usage patterns of different blocks.

2. Dynamic Wear Leveling: This algorithm takes into consideration the usage patterns of blocks. It monitors the number of erase and program cycles for each block and dynamically redistributes data to less-used blocks. This helps to achieve a more balanced wear across the entire SSD, improving longevity.

3. Hybrid Wear Leveling: This algorithm combines the benefits of both static and dynamic wear leveling. It initially uses static wear leveling to evenly distribute writes. Over time, it switches to dynamic wear leveling to adapt to changing usage patterns and maintain wear balance.

4. Block-based Wear Leveling: This algorithm operates at the block level rather than the page level. It redistributes data among entire blocks rather than individual pages. This approach reduces write amplification and ensures that all cells within a block wear out uniformly.

5. Over-Provisioning: This technique reserves a certain percentage of the SSD's capacity as spare area that is not accessible to the user. The over-provisioned space is used by the wear-leveling algorithms to perform data relocation and wear balancing operations. It helps to mitigate the impact of uneven wear on the usable capacity of the SSD.

## Write Amplification:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Delve into the concept of write amplification, a critical metric for flash SSD performance. Gain insights into how the simulator minimizes write amplification by optimizing the write operations and reducing unnecessary data movements.

## Trim Command:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Learn about the Trim command, an essential feature for maintaining SSD performance. Explore how the simulator handles Trim commands to improve the efficiency of garbage collection and reduce write amplification.

## Over-provisioning:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Understand the significance of over-provisioning in flash SSDs. Experience how the simulator reserves a portion of the flash memory for background operations, enhancing performance, and extending the SSD's lifespan.

By providing this comprehensive range of functionalities, the Flash SSD Simulator offers an interactive and educational environment for users to explore the inner workings of flash-based SSDs. It enables users to develop a deeper understanding of the technology behind SSDs and the factors that influence their performance and longevity. So go ahead, dive in, and experience the fascinating world of flash SSDs firsthand!

## Table 01: Specifications of a NAND Flash Device
| Parameter | Value |
|----------|----------|
Page Size | 4 KB
Block Size | 256 KB (64 pages)
Page Read | 25 μs
Page Program (Write) | 200 μs
Block Erase | 1.5 ms


## Figure 01: Internal Architecture of a Typical NAND Flash Device
![Example Image](readme_documentation_src/figure/flash_ssd_simulator.png)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Figure 01 above shows the internals of a NAND-flash package, which is organized as a hierarchical structure. The levels are channel, package, chip, plane, block, and page. Those different levels offer parallelism as follows:

1. Channel-level parallelism:  The flash controller communicates with the flash packages through multiple channels. Those channels can be accessed independently and simultaneously. Each individual channel is shared by multiple packages.

2. Package-level parallelism: The packages on a channel can be accessed independently. Interleaving can be used to run commands simultaneously on the packages shared by the same channel.

3. Chip-level parallelism: A package contains two or more chips, which can be accessed independently in parallel. Note: chips are also called “dies”.

4. Plane-level parallelism: A chip contains two or more planes. The same operation (read, write or erase) can be run simultaneously on multiple planes inside a chip. Planes contain blocks, which themselves contains pages. The plane also contains registers (small RAM buffers), which are used for plane-level operations.

## Cache 
1. Least Recently Used (LRU): LRU is one of the most widely used cache replacement algorithms. It evicts the cache line that has not been accessed for the longest period of time. It assumes that the cache line that has been accessed least recently is the least likely to be accessed again in the near future.

2. First-In, First-Out (FIFO): FIFO is a simple cache replacement algorithm that evicts the cache line that was inserted first when the cache is full. It maintains a queue structure, and the cache line at the front of the queue is evicted. This algorithm does not consider the recency or frequency of cache line accesses.

3. Random Replacement: In this algorithm, a cache line is selected randomly for eviction when the cache is full. It does not consider any access patterns or history of cache line usage. Random replacement can be simple to implement, but it may not always result in optimal cache performance.

4. Least Frequently Used (LFU): LFU replaces the cache line that has been accessed the fewest number of times. It keeps track of the access frequency for each cache line and evicts the one with the lowest count. This algorithm assumes that cache lines with lower access frequency are less likely to be accessed in the future.

5. Most Recently Used (MRU): MRU evicts the cache line that has been accessed most recently. It assumes that recently accessed cache lines are more likely to be accessed again in the near future. MRU is useful in situations where temporal locality is important, but it can be less effective in handling certain access patterns.

6. Not Recently Used (NRU): NRU is a variation of the MRU algorithm that distinguishes between recently used and not recently used cache lines. It divides the cache lines into two categories: "recently used" and "not recently used." When eviction is required, it chooses a cache line from the "not recently used" category. This algorithm provides a simple approximation of LRU and is often used in hardware implementations due to its lower complexity.

## References
- [1] Coding for SSDs – Part 1: Introduction and Table of Contents https://codecapsule.com/2014/02/12/coding-for-ssds-part-1-introduction-and-table-of-contents/
- [2] NEW MULTI-TIERED SOLID STATE DISK USING SLC/MLC COMBINED FLASH MEMORY https://arxiv.org/pdf/1405.2157.pdf
- [3] Experimental demonstration of Single-Level and Multi-Level-Cell RRAM-based In-Memory Computing with up to 16 parallel operationshttps://arxiv.org/pdf/2203.01680.pdf
- [4] 3D Flash Memories. (2016). Netherlands: Springer Netherlands.
- [5] Mcnulty, P.J. & Rajaram, Navin & Poole, Kelvin & Freeman, Kurt & Dyar, J.P. & Scheick, Leif & Alkhafazi, Mazin & Randall, Mitchell. (2006). Simplified Readout of UVPROM Dosimeters for Spacecraft Applications. Nuclear Science, IEEE Transactions on. 53. 1859 - 1862. 10.1109/TNS.2006.877564.
- [6] https://www.cactus-tech.com/resources/blog/details/solid-state-drive-primer-1-the-basic-nand-flash-cell/
- [7] https://www.embedded.com/flash-101-types-of-nand-flash/

## License
This simulation is provided under the [MIT License](LICENSE). You are free to use, modify, and distribute the simulation in accordance with the terms of the license.


## Journal List
https://olj.onlinelearningconsortium.org/index.php/olj/about/submissions

