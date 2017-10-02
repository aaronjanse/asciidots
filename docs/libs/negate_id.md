[Back to docs home](../index.md) - [Back to libs](index.md#Simple%20operations%20on%20dots)
# negate_id.dots

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
         /--@#-&   |
         n         $
         |         @
         \-@$--n---/

This will output: 

    -7
    7
    -7
    7


[Back to docs home](../index.md) - [Back to libs](index.md#Simple%20operations%20on%20dots)
