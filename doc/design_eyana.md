# Design the SSD simulator

## SSD Simulator
 - 

## Advanced SSD Simulator
 - Heatmap
   - Number of erase, write and read
 - Statistics
   - WAF
   - Numer of erase, write and read 
 - Performance (figure our how to?)
   - Throughput
   - Latency
 - Garbage collection policy
   - Greedy
   - FTL
   

## Idea regarding ssd simulator 
  - We will trace how many times a block is erased, based on number of erase and invalid pages this block will be erased next time.
     - Equation: 
       - Erase = (invalid_page/total_page)*100 - (this_block_erase_count/max_erase_count)*100


## 03-09-2024 Meeting Preparation 
  - Study FDP and ZNS SSD
    - ZNS : 
        - 1. How they separate the data in each zone
        - 2. How they manage the data in each zone
        - 3. If one zoned is ful then how they manage the data
    - FDP:
        - 1. How they 
  - Idea 2: Wear leveling withour wear leveling algorithm We will keep another information to trace which block will be erase next. Block will be choosen based on number of invalid page and max erase count. We will find a law to get it.
  - Finding the limitation of other paper and how we can improve it.