// CodeMirror, copyright (c) by Marijn Haverbeke and others
// Distributed under an MIT license: https://codemirror.net/LICENSE

// Brainfuck mode created by Michael Kaminsky https://github.com/mkaminsky11

(function(mod) {
  if (typeof exports == "object" && typeof module == "object")
    mod(require("../../lib/codemirror"))
  else if (typeof define == "function" && define.amd)
    define(["../../lib/codemirror"], mod)
  else
    mod(CodeMirror)
})(function(CodeMirror) {
  "use strict"
  CodeMirror.defineMode("asciidots", function() {
    return {
      startState: function() {
        return {
          lineComment: false,
          inlineComment: false,
          prevBacktick: false,

          line: 0,
          col: 0,
        }
      },
      token: function(stream, state) {
        // if (stream.eatSpace()) return null
        if(stream.sol()){
          state.comment = false;
        }
        var ch = stream.next().toString();

        let pos = `pos-${state.line}:${state.col}`;

        if(ch == '`'){
          if (state.prevBacktick) {
            state.lineComment = true;
          }

          state.prevBacktick = true;
          
          if (!state.lineComment) {
            state.inlineComment = !state.inlineComment;
          }

          if(stream.eol()){
            state.lineComment = false;
            state.inlineComment = false;
          }
          return `comment ${pos}`;
        } else {
          if (stream.eol()) {
            state.line += 1
            state.col = 0
          } else {
            state.col += 1
          }

          state.prevBacktick = false;

          if(state.lineComment || state.inlineComment){
            if(stream.eol()){
              state.lineComment = false;
              state.inlineComment = false;
            }
            return `comment ${pos}`;
          }
          // if('[]{}'.includes(ch)){
          //   return "bracket";
          // }
          else if(ch === "#" || ch === "@"){
            return `keyword ${pos}`;
          }
          else if('[]{}'.includes(ch)){
            return `atom ${pos}`;
          }
          else if(ch === "."){
            return `builtin ${pos}`;
          }
          return pos
        }
      }
    };
  });
CodeMirror.defineMIME("text/x-asciidots","asciidots")
});