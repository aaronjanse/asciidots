---
layout: post
permalink: /libs/neg/
title: neg.dots
---

### Purpose
Since there is no way to set a dot's value to a negative number directly, this librairy is a shortcut to changes the value of a dot to its opposite.

### Usage
    
     T
    L+R
     B

##### Parameters
- `L`, `R`, `T` or `B`: The entry for the dot can be any of the 4 directions.
- `R`, `L`, `B` or `T`: And the dot will go out to the opposite direction, continuing its way.

##### Example

    %!neg.dots n

    .--#42--n--$#--\
                   |
                   n
         /--$#-&   |
         n         $
         |         #
         \-#$--n---/

##### Output

    -42
    42
    -42
    42

### Source 
The source code is availaible [here](https://github.com/aaronjanse/asciidots/blob/master/dots/libs/neg.dots)
. If something doesn't work, do not hesitate to [open an issue](https://github.com/aaronjanse/asciidots/issues/new?title=Bug%20in%20neg%20library:%20).

