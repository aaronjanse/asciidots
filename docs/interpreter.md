---
layout: page
permalink: /interpreter/
title: Interpreter Documentation
---

This page documents usage of the official asciidots interpreter.

---

The first argument of the interpreter script is the `dots` file that you wish to run.

Here's an example of running the counter sample program (the working directory is the dots repo folder):

```bash
$ asciidots samples/counter.dots
```

Here is the list of available flags:

```
-t [ticks]        Run the program for a specified number of ticks (Default to 0: no limit)

-o [output-limit] Run the program for a specified number of outputs (Default to 0: no limit)

-s                Run without printing ANYTHING to the console. Useful for benchmarking

-d                Run the program in debug mode. It shows the program and highlights the dots with red. Press enter to step the program once.

Some extra flags when debugging:
-a [delay]        Step the program automatically, using the specified delay in seconds. Decimal numbers are permitted, and so is 0.

-w                Run the program without using ncurses. This can fix problems related to Windows.

-l [line-count]   When not in compatibility mode, reserve the specified number of the lines for displaying the program
```

This is how one might debug a program for 300 ticks while running it automatically with a delay of 0.05 seconds:

```bash
$ asciidots samples/counter.dots -t 300 -d -a 0.05
```
