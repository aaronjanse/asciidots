---
layout: post
permalink: /libs/bool_not/
title: bool_not.dots
---


### Purpose
Since there is no unary operators in asciidots, this librairy operate a NOT oparation on a dots value. 

### Usage
    
     T
    L+R
     B

##### Parameters
- `L`, `R`, `T` or `B`: The dot where do do the NOT 
- `R`, `L`, `B` or `T`: The output will come strait in the same direction

##### Example

    %!bool_not.dots n

    .-#1--n--$_#-#0--n--$_#-#3--n--$_#-&

##### Output

    010

### Notes
- This is not the bitwise not
- Any other value than 0 will be changed to 0.

### Source 
The source code is availaible [here](https://github.com/aaronjanse/asciidots/blob/master/dots/libs/bool_not.dots)
. If something doesn't work, do not hesitate to [open an issue](https://github.com/aaronjanse/asciidots/issues/new?title=Bug%20in%20bool_not%20library:%20).
