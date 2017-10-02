[Back to docs home](../../index.md) - [Back to libs](index.md)
# clone.dots

### Purpose
This librairy replicates a dot at identical a certain number of times. You can see this as an arbitrary number of `*`.

### Usage
    
     O
    D+N
     E

##### Parameters
- `D`: The dot to clone
- `N`: The number of times to clone the dot
- `O`: The output for the copies of the dot
- `E`: A dot is emmited from here once all clones are created

##### Example

    %!clone.dots c

             /-$_@-$#
             |
    .-#2-@4--c--5#-.
             |
             &

##### Output

    42
    42
    42
    42
    42

### Notes
- Once the end dot is emmited, you can send other dots in the lib and use it again
- If the `N` dot is not an integer or is negative, this will generate continuously clones of the dot.

[Back to docs home](../../index.md) - [Back to libs](index.md)