---
layout: post
permalink: /libs/for_in_range/
title: for_in_range.dots
---

### Purpose
This librairy generates a range of one-spaced values between two integers. It is similar to the range function of python, the first value is included but the last one is not.

### Usage

     O
    A+B
     E

##### Parameters
- `A`: The beginning value, included in the range
- `B`: The end value, not included
- `O`: The output, the dots generated will be emitted from the top
- `E`: When the loop is finished a dot goes from the bottom.

##### Example

This is a count to 10 example

    %!for_in_range.dots f

         /-$_#
         |
    .-#1-f-11#-.
         |
         |
         \-&

##### Output

    12345678910

### Notes
- Once the end dot is emmited, you can send other dots in the lib to use it again

### Source
The source code is availaible [here](https://github.com/aaronjanse/asciidots/blob/master/dots/libs/for_in_range.dots)
. If something doesn't work, do not hesitate to [open an issue](https://github.com/aaronjanse/asciidots/issues/new?title=Bug%20in%20for_in_range%20library:%20).

