---
layout: post
permalink: /libs/wait/
title: wait.dots
---

### Purpose
This librairy keeps a dot inside the lib for a certain amount of time. Since every dot moves at the same time, it can be usefull to have one dot that waits untill an other completes an operation.

### Usage
    
     _
    L+R
     B

##### Parameters
- `L`: Entry for the waiting dot
- `R`: output the L dot after wait
- `B`: Number of ticks to wait.

##### Example

    %!wait.dots W

         .--W--$'The dot has waited 121 ticks'--&
    .-#100--/

### Notes
- The waiting time is changed to the following number of the form `22 + 33k` (with k positive integer), thus A dot will always wait at least `B` ticks, but it can be not exactly `B`
- This doesn't work at all in async mode

### Source 
The source code is availaible [here](https://github.com/aaronjanse/asciidots/blob/master/dots/libs/wait.dots)
. If something doesn't work, do not hesitate to [open an issue](https://github.com/aaronjanse/asciidots/issues/new?title=Bug%20in%20wait%20library:%20).
