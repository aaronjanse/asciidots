---
layout: post
permalink: /libs/negate_id/
title: negate_id.dots
---

### Purpose
Since there is no way to set a dot's id to a negative number directly, this librairy is a shortcut to changes the id of a dot to its opposite.

### Usage
    
     T
    L+R
     B

##### Parameters
- `L`, `R`, `T` or `B`: The entry for the dot can be any of the 4 directions.
- `R`, `L`, `B` or `T`: And the dot will go out to the opposite direction, continuing its way.

##### Example

    %!negate_id.dots n

    .---@7--n--$@--\
                   |
                   n
         /--$@-&   |
         n         $
         |         @
         \-@$--n---/

##### Output 

    -7
    7
    -7
    7

### Source 
The source code is availaible [here](https://github.com/aaronjanse/asciidots/blob/master/dots/libs/negate_id.dots)
. If something doesn't work, do not hesitate to [open an issue](https://github.com/aaronjanse/asciidots/issues/new?title=Bug%20in%20negate_id%20library:%20).
