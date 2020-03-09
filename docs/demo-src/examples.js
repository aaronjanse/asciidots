const examples = {
  'Hello World': `.-$'Hello, World!'`,
  'Hello World 2': `.-($'Hello, World!'$)`,
  'Counter': String.raw`
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
`,
  'Fibonacci': String.raw`
/--#$--\
|      |
>-*>{+}/
| \+-/
1  |
#  1
|  #
|  |
.  .
`,
  'Factorial': String.raw`
 /---------*--~-$#-&
 | /--;---\| [!]-\
 | *------++--*#1/
 | | /1#\ ||
[*]*{-}-*~<+*?#-.
 *-------+-</
 \-#0----/
`,
  'Factor': `
%!for_in_range.dots f

/.
# /{/}$#
?/* \\#$~\\
*~*{%}-//
|\\1#*-*//1#-.
| .-#1f-+-\\
*--{^}+{+}/
*-#2\\-\\#0*~~&
\\#1{/}/  \\*/
`
}

for (const exampleName in examples) {
  if (examples.hasOwnProperty(exampleName)) {
    document.getElementById('demolist').innerHTML += `<li><a>${exampleName}</a></li>`
  }
}
