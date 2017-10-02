[Back to docs home](../../index.md) - [Back to libs](index.md#Simple%20operations%20on%20dots)
# neg.dots

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


[Back to docs home](../../index.md) - [Back to libs](index.md#Simple%20operations%20on%20dots)
