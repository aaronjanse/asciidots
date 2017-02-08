# Dots - Esoteric Language Specs
##### Language By Aaron Janse

---

## Samples

Hello world:

```
 .-$"Hello, World!"
```

Counter:

```

     /1#-.
     |
   /-+-$#\
   | |   |
  [+]<1#-*
   |     |
   \--<--/
      |
      0
      #
      |
      .
```

Semi-compact factorial calculator:

```
'' Compact Factorial Calculator

 /---------*--~-$#-&
 | /--;---\| [!]-\
 | *------++--*#1/
 | | /1#\ ||
[*]*{-}-*~<+*?#-.
 *-------+-</
 \-#0----/

```

Code-golfed counter (19 bytes):

```
.>$#\
[+]>1#)
 \-*/
```

## Program Syntax

### Basics
`.`, or `•`, signifies a dot, the core of the language. This carries information. Each dot is initialized with both an [address and value](#addresses-and-values) of `0`

Everything after ``` '' ``` (two apostrophes) is a comment and is ignored

### Paths
`|` is a vertical path<br>
`-` is a horizontal path

Think as these two paths as mirrors:<br>
`/`<br>
`\`

#### Special Paths
`+` is the crossing of paths (they do not interact)

`>` acts like a regular, 2-way, horizontal, path, except dots can be inserted into the path from the bottom or the top. Those dots will go to the right<br>
`<` does likewise except new dots go to the left

`(` reflects a dot backwards along its original path. It accepts dot coming from the left.<br>
`)` does likewise but for the opposite direction

`*` duplicates a dot and distributes copies including the original dot to all attached paths except the origin of dot

### Addresses and Values
`@` sets the address to the value after it following the direction of the line<br>
`#` does the same except it sets the value

### Interactive Console
`$` is the output console. If there are quotation marks (`"`), it outputs the text after it until there are closing quotation marks. `#` and `@` are substituted with the dot's value and address, respectively<br>
`?` is input from the console. It prompts the user for a value, and pauses until a value is entered in. It only runs after a `#` or `@` symbol<br>

```

  . '' This dot is the data carrier
  | '' Travel along these vertical paths
  # '' Set the value...
  3 ''   ... to 3
  | '' Continue down the path
  $ '' Output to the console...
  # ''   ... the dot's value


```


```

  .
  |
  # '' Get ready to set the value
  ? '' Prompt the user
  |
  $
  # '' Print that value to the console

```

### Control Flow
` ~` (tilde) redirects dots going through it horizontally to the upward path if a dot waiting at the bottom has a value greater than 0. Otherwise, the dot continues horizontally. If an exclamation point (`!`) is under it, then it redirects only if the value of the dot waiting is *not* greater than zero.<br>
&nbsp;&nbsp;&nbsp;&nbsp;`!` acts like a pipe. Special function described above

### Operations
`[*]` multiplies the value that passes through vertically by the value that runs into it horizontally. When a dot arrive here, it waits for another dot to arrive from a perpendicular direction. When that dot arrives, the dot that arrived from the top or bottom has its value updated and it continues through the opposite side. The dot that passed through horizontally is deleted.<br>
`{*}` does likewise except it multiplies the value that enters horizontally by the value that enters vertically. The resulting dot exits horizontally<br>

Other operations work similarly but with a different symbol in the middle. This is the key to these symbols:<br>
`*`: multiplication<br>
`/`: division<br>
`÷`: also division<br>
`+`: addition<br>
`-`: subtraction<br>
`%`: modulus<br>
`^`: exponent<br>
`&`: boolean AND<br>
`!`: boolean NOT<br>
`v`: boolean OR (the 'v' is from the symbol for Logical Disjunction)<br>
`>`: greater than<br>
`≥`: greater than or equal to<br>
`<`: less than<br>
`≤`: less than or equal to<br>
`=`: equal to<br>
`≠`: not equal to<br>

Boolean operations return a dot with a value of `1` if true and `0` if false.

These are only operators when located within brackets. When outside of brackets,
symbols like `*` perform their regular functions as described earlier.

Example:

```
'' Simple subtraction:
''   (3 - 2 = 1)

   #
   $
   |
  [-]-2#-.
   |
   3
   #
   |
   .
```

### Warps
A warp is a character that teleports, or 'warps', a dot to the other occurrence of
the same letter in the program.

Define warps at the beginning of the file by listing them after a `%$`.
The `%$` must be at the beginning of the line.

Example:

```
%$A

.-#9-A '' Create a dot, set its value to 9, then warp it

A-$#   '' Print the dot's value (9)

```

## Libraries
Dots supports libraries!
A library is a program that defines a character (usually a letter).

#### Using Libraries
A library can be imported by starting a line with `%!`, followed with the file name, followed with a single space and then the character that the library defines.

Here's an example of importing the standard `for_in_range` library (located in the `libs` folder) as the character `f`:

```
%!for_in_range.fry f
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
%!for_in_range.fry f

         #
         $
         |
.-*-#1---f-\
  \-#100-+-/
         |
         &

```

#### Creating Libraries
The inputs/outputs for a library with the inputs/outputs like this (A is from the left, B from the top, etc):

```
   B
 A + C
   D
```

... Would be defined in the library's code like this:

```
%+ABCD
```

Unused inputs are replaced with an underscore(`_`). So, if the upper input/output is unused, the definition would look like this (note the underscore):

```
%+A_CD
```

The letters defined then work like warps in the rest of the code. Remember that direction is preserved!

Here's the code for a library that accepts a dot coming from the left, sets its value to its address, and then outputs it to the right:
```
%+A_B_

'' Set address to zero, then add the value to the address (which is 0)
A-*-@0-@{+}-B
  |      |
  \------/

```


## Interpretation
Each tick, the dots will travel along the lines until they hit a charter that acts as a function of multiple dots (i.e. an operation character or a `~` character). The dot will stop if it
goes on a path that it has already traversed in the same tick

Due to the fact that dots may be moving backwards down a line, if a number or system value (e.g. `?`) is seen without a preceding `@` or `#`, it will be ignored, along with any `@` or `#` immediately thereafter

### Ending the program
Interpretation of a dots program ends when a dot passes over an `&`

### Defining custom dots and prompts (***Obsolete***)
At the beginning of the program, the priority of the dots at the beginning of runtime can be
defined at the beginning of the program by writing `%.` followed by the list of letters that represent dots with the letter with the highest priority first.<br>

```
'' Print to the console if the input equals 0
'' Note that the 'A' dot moves before the 'B' dot


        #
        $
        |
B-#?-*--~
     |  |
     \-[=]
        |
        0
        #
        |
        A
```

## Examples

Hello, World!<br>

```
.-$"Hello, World!"
```

---
<br>
Test if 2 input values are equal:<br>

```

       /-$"Equal"
       |
.-#?-*-~-$"Not equal"
     | |
     \[=]
       |
       ?
       #
       |
       .
       
```

---
<br>
Counter:

```

     /1#-.
     |
   /-+-$#\
   | |   |
  [+]<1#-*
   |     |
   \--<--/
      |
      0
      #
      |
      .
      
```

---
<br>
Fibonacci Sequence Calculator:<br>

```

/--#$--\
|      |
>-*>{+}/
| \+-/
1  |
#  #
|  1
|  |
|  .
.

```
