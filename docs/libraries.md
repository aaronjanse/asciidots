---
layout: post
permalink: /libraries/
title: Library documentation
---

[Go Back](../)

AsciiDots supports libraries!
A library is a program that defines a character (usually a letter).

## Using Libraries
A library can be imported by starting a line with `%!`, followed with the file name, followed with a single space and then the character that the library defines.

By default, all copies of the character to lead to the same ([singleton](https://en.wikipedia.org/wiki/Singleton_pattern)) library code. This can cause some unexpected behavior if the library returns an old dot, since that old dot will come out of the char that _it_ came from.

Here's an example of importing the standard `for_in_range` library (located in the `libs` folder) as the character `f`:

```
%!for_in_range.dots f
```

The way to use a library varies. Inputs and outputs of the library are through the alias character.

For the `for_in_range` library, the inputs are defined as follows:
- The dot coming from the **left** side sets the starting value of the counter
- The dot coming from the **right** sets the end value of the Counter

And the outputs are as follows:
- A dot for each number within the range defined by the inputs is output from the **top**
- When the loop is complete (the end value has been reached), a dot is output from the **bottom**

Here is an example of outputting all the numbers between `1` and `100` to the console, then stopping the program:

```
%!for_in_range.dots f

         #
         $
         |
.-*-#1---f-\
  \-#100-+-/
         |
         &
```

## Creating Libraries
Each library defined a character that will act as a warp to & from the library.

That can be done like so:

```
%$X `` X could be replaced with a different character, if so desired
```

It is recommended that you create warps for different sides of the char. Just look at the example code for the `val_to_addr.dots` library:

```
%^X
%$AB

B-X-A


A-*----@{+}-#0-B
  |      |
  \------/
```

## Location of Library Source Files
The source files for libraries are searched for in the following directories (in order):
1. The directory of the asciidots file being interpreted
2. The implementation's `dots/libs/` directory
3. The implementation's `libs/` directory (for backwards compatibility)

## Built-in library docs

#### Simple operations on dots
- **[neg.dots](../libs/neg)** - Change the value of a dot to the opposite
- **[negate_id.dots](../libs/negate_id)** - Change the id of a dot to the opposite
- **[val_to_id.dots](../libs/val_to_id)** - Set the id to the value
- **[bool_not.dots](../libs/bool_not)**	- Operation NOT on booleans


#### Loops
- **[for_in_range.dots](../libs/for_in_range)** - Generate a range of numbers between to values
- **[clone.dots](../libs/clone)** - Generate the same dot *x* times

#### Data structures
- **[list.dots](../libs/list)** - Simulate a list with get, set, append, etc methods
- **[storage.dots](../libs/storage)** - Simulates a queue that can be used to store a single value

#### Time
- **[wait.dots](../libs/wait)** - Make a dot wait

#### (De)compression
- **[compress.dots](../libs/compress)** - Compress dots so they go in the same path
- **[decompress.dots](../libs/decompress)** - Separate dots that go in the same path
