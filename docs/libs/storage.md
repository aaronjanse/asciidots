---
layout: post
permalink: /libs/storage/
title: storage.dots
---

### Purpose
This librairy is a queue. You can use it to store a single dot or more than one. If you want to store a single dot, don't forget to put the dot back once you you it. This stores both values and ids.

### Usage
    
     T
    L+R
     B

##### Parameters
- `L` or `R`: A dot that comes horizontally will go through and have the value and id of the first dot that was stored. This first dot is then removed from the queue.
- `T` or `B`: A dot coming vertically will be added at the end of the queue.

##### Example

    %!storage.dots s

    .--#6--*-#9-*---q--$#--*--q--$#--q--$#--&
           q    q          q

##### Output

    6
    9
    6

### Notes
- If you send two dots at the same time (to store or retrieve dots) there's no way to know which one will be first in the queue.

### Source 
The source code is availaible [here](https://github.com/aaronjanse/asciidots/blob/master/dots/libs/storage.dots)
. If something doesn't work, do not hesitate to [open an issue](https://github.com/aaronjanse/asciidots/issues/new?title=Bug%20in%20storage%20library:%20).
