---
layout: post
permalink: /libs/list/
title: list.dots
---

### Purpose
This librairy simulate a list to store an arbitrary number of values. Note that the ids are not preserved.

### Usage
    
     S
    A+O
     F

##### Parameters
- `A`: Append a dot to the list
- `S`: Set the dot at index `@` with the value `#` 
- `O`: The output of all function goes out to the east. If you use this as input, it [inserts](#insert) the dot. 
- `F`: Different function are performed depending on the id of the the dot. See [functions](#functions).

##### Functions

| Function | Id |        Value        |                      Description                      |
|---------:|:--:|:-------------------:|:------------------------------------------------------|
|   Append | 0  | The value to append | Adds a dot at the end of the list                     |
|      Get | 1  |   The index to get  | Return the value at the index                         |
|   Delete | 2  | The index to remove | Removes a dot from the list at the `#` index          |
|   Remove | 3  | The value to remove | Removes the first dot in the list with the same value |
|   Length | 4  |          -          | Return the current size of the list                   |
|     Copy | 5  |          -          | Return all the dots in the list                       |
|    Clear | 6  |          -          | Empty the list                                        |
|     Sort | 7  |          -          | Sort the list                                         |

###### Set
A dot comming from the top sets the dot at the index of its id to its value.

###### Insert
If a dot comes from the right, it will be inserted at the index of its id and all other dots from its id will be shifted by one to the end of the list (the last one won't be deleted).

##### Output
Every function (except append from  the left) outputs a dot, even if there is no value to return (like `Set` or `Delete`) so you know when the function has finished its execution. 

##### Example

    %!list.dots l

##### Output

    42
   



### Notes

##### Complexity
It's not a good idea to ask, but the complexity of each function is `O(n)` with `n` the number of elements in the list, except `Length` which is `O(1)` and of course `Sort` which is... too much

##### Other notes
- Everything is not already implemented, for now only `Set`, `Get`, `Append` and `Length` will work. 
- Using a list is very slow, thus if you find a way to do without, it is a good idea.
- To use more than one list, you need to import the librairy more than once.
- You can ask an other function while one is still running, but they'll be executed only after the first finishes. Alternatively, you can use the [wait](wait.md) librairy.


### Source 
The source code is availaible [here](https://github.com/aaronjanse/asciidots/blob/master/dots/libs/list.dots)
. If something doesn't work, do not hesitate to [open an issue](https://github.com/aaronjanse/asciidots/issues/new?title=Bug%20in%20list%20library:%20).
