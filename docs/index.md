---
layout: post
---


<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/codemirror.min.css">
<link rel="stylesheet" href="codemirror-onedark.css">
<link rel="stylesheet" href="index.css">

<div id="header">
    <div id="graphic">
      <object class="graphic-obj" id="graphic-left" data="graphic2.svg" type="image/svg+xml" title="example factorial calculator in asciidots">
      </object>
      <object class="graphic-obj" id="graphic-right" data="graphic.svg" type="image/svg+xml" title="example factorial calculator in asciidots">
      </object>
    </div>
    <div id="text">
      <h1>asciidots</h1>
      <p id="tagline">An esolang based on ascii art</p>
      <p id="links">
        <a href="https://github.com/aaronjanse/asciidots">github</a>&nbsp;
        <!-- <a href="https://discord.gg/8XAxAEnkBz">discord</a> -->
        <a href="https://ajanse.me">ajanse.me</a>&nbsp;
      </p>
    </div>
  </div>

  <div id="demo"></div>

  <a id="go-back" href="#ex1" style="display: none">← Go back</a>

  <div class="examples">
    <button id="ex-hello-world" class="selected">Hello World</button>
    <button id="ex-counter">Counter</button>
    <button id="ex-fibonacci">Fibonacci</button>
    <button id="ex-fizz-buzz">Fizz Buzz</button>
    <button id="ex-factorial">Factorial</button>
    <button id="ex-prime-sieve">Prime Sieve</button>
  </div>

  <div class="ide loading stopped">
    <div class="editor">
    <div class="controls ide-col-header">
        <span id="loading-text">Loading Pyodide...</span>
        <button class="run">Run</button>
        <button class="pause">Pause</button>
        <button class="step">Step</button>
        <button class="share">Share</button>
        <button class="reset">Reset</button>
        <span class="speed">(<input name="" id="" value="0.05"> seconds/tick)</span>
      </div>
    <noscript style="font-size: 14px;">The online IDE requires JavaScript, but you can try asciidots locally by following installation instructions <a href="https://github.com/aaronjanse/asciidots">on GitHub</a>.</noscript>
    <div class="codemirror"></div>
    <div id="hover-hint">Hover over a dot while paused to see its value</div>
    </div>
    <div class="console">
      <div class="additional-input">
        <div id="additional-input-text" style="color: red">Additional input needed</div>
        <div class="additional-input-form">
          <input type="text">
          <button>Submit</button>
        </div>
      </div>
      <div class="input">
        <div>Input</div>
        <textarea></textarea>
      </div>
      <div class="output empty">
        <div>Output</div>
        <pre></pre>
      </div>
    </div>
</div>

<div id="learn" markdown="1">

AsciiDots is an esoteric programming language based on ascii art. In this language, _dots_, represented by periods (`.`), travel down ascii art paths and undergo operations.

Feel free to learn AsciiDots below or watch [Truttle1's video on YouTube](https://youtu.be/2BvBk-WHHZQ).

## Movement

Let's start by looking at a simple asciidots program, where a dot winds through an ascii-art path:

```
/-&        `` ... and ends here
| 
\-\ /-\ 
  | | |
/-/ | \-\  `` ... turns left then up
\---/   |
        |  `` ... goes up
        .  `` The dot starts here
```

Here's what all those characters mean:

* `.` represents the starting point of a dot
* `-` and `|` move the dot horizontally and vertically
* `/` and `\` act like mirrors to change the direction of a dot
* `&` immediately stops the program when a dot passes over it

This syntax for comments is the following:
* <code>``</code> starts a comment for the rest of the line
* Inline comments look <code>`like this`</code>

<br/>

Let's see a more complicated example:


```
  /-\ /-& `` End
  | | |
  \-+-v
    | | /-\
(-<-/ | | |
  |   \-<-/
  \-\
    |
    .     `` Start
```

Here are the new characters introduced:

* `+` allows paths to cross without interacting
* `(` and `)` set the direction of a dot to right or left (respectively)
* `<` `>` `^` `)` are arrows that set the direction of a dot that pass through it perpendicularly. If a dot passes through parallel to the arrow, its direction is unchanged.

<br/>

There can be multiple dots in an asciidots program. This example sends two dots through the same path:

```
.-->---
   |
.--/
```

## Data

Each dot stores a _value_ and an _id_. The _id_ can simply be thought as a second value that a dot can hold, and it can be used in any way.

You can set a dot's value by having it pass over a `#` followed by a number:

```
.-#7
```

A dot's value can be overwritten. In this example, the dot ends up with a value of 3:

```
.-#18-#0-#6-#148-#13-#3
```

The same applies to a dot's id, except we use the `@` symbol. The following example sets a dot's value to 5 and its id to 6:

```
.-#5-@6
```

We can set a dot's id and value in any direction. The following sets a dot's value to 18 and its id to 100:

```
001@-\
     |
     8
     1
     #
     |
     .
```

## Input

To read an integer from stdin, use `#?` (similar to the syntax for setting a dot to an integer literal). To read a byte from stdin as a number, use `#a?`, which sets the value to -1 at the end of the file. Similarly, use `@` instead of `#` to set a dot's id.

This program reads a single number from the program's input then prints it back out:

```
.-#?-$#
```

## Output

The `$` character is used to output data to stdout. There are a few ways it can be used:

* `$#` and `$@` print the dot's value/id in decimal
* `$a#` and `$a@` print the dot's value/id as a raw byte
* `$"hello"` prints _hello_ with buffering (all at once)
* `$'hello'` prints _hello_ one character at a time

Using double quotes `"` is helpful to avoid race conditions when multiple dots print at once.

The characacter `_` prints without adding a newline. It can go anywhere except the end newline from being added the the output.


This example prints a `%` without a newline, using its ASCII code 37:

```
.-#37-$_a#
```

Now we can read a number from the program's input then print it back:

```
.-#?-$#
```

## Operations

`[*]` multiplies the value that passes through vertically by the value that runs into it horizontally. When a dot arrive here, it waits for another dot to arrive from a perpendicular direction. When that dot arrives, the dot that arrived from the top or bottom has its value updated and it continues through the opposite side. The dot that passed through horizontally is deleted.

`{*}` does the same except it multiplies the value that enters horizontally by the value that enters vertically. The resulting dot exits horizontally.

Other operations work similarly:

|     |          |     |
|:---:|----------|:---:|
| `+` | add      | `=` | equal
| `-` | subtract | `!` | not equal
| `*` | multiply | `>` | greater
| `/` | divide   | `<` | less
| `%` | modulo   | `G` | greater or equal
| `^` | exponent | `L` | less or equal
|     |
| `&` | bitwise AND
| `o` | bitwise OR
| `x` | bitwise XOR

These characters are only considered operators when located within brackets. Outside of brackets, symbols like `+` perform their regular functions as described earlier.

Example of subtraction (3 - 2 = 1):

```
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

Calculating the sum of two input values:

```
.-#?-{+}-$#
      |
.-#?--/
```

## Duplication

`*` duplicates a dot and distributes copies to all attached paths except the path where the original dot came from. These copies have the same id and value as the original dot.

This example creates three dots, each with a value of 7:

```
     /---$#
     |
.-#7-*---$#
     |
     \---$#
```

These three dots are entirely unrelated, and changing the value of one will not affect any others.


## Control Flow

`~` takes two dots, one from the side (the "input") and one from the bottom (the "condition"). The input dot is directed upwards if the condition dot's value is equal to zero. Otherwise, it's directed horizontally:

```
     /-$"Equal to zero"
     |
.----~-$"Not equal to zero"
     !
.-#?-/
```

If an `!` is placed under the `~`, then the behavior is reversed: the input dot is now directed _horizontally_ if the condition dot is equal to zero:

```
     /-$"Not equal to zero"
     |
.----~-$"Equal to zero"
     !
.-#?-/
```

## Filters

A "filter" delete dots traveling over it that have a specific value:

* `:` deletes dots with a value of 0 traveling over it
* `;` deletes dots with a value of 1 traveling over it

## Advanced Features

A warp is a character that teleports, or 'warps', a dot to the other occurrence of the same letter in the program.

Define warps at the beginning of the file by listing them after a `%$`. The `%$` must be at the beginning of the line.

This example outputs the number 9:

```
%$A

.-#9-A

A-$#
```

AsciiDots also supports libraries, which are documented [here](libraries).

</div>

<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/selection/active-line.min.js"
integrity="sha512-0sDhEPgX5DsfNcL5ty4kP6tR8H2vPkn40GwA0RYTshkbksURAlsRVnG4ECPPBQh7ZYU6S3rGvp5uhlGQUNrcmA=="
crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script src="codemirror-asciidots.js"></script>

<script src="index.js"></script>