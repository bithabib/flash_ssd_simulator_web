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

