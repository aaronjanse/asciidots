let sampleCode = `.-$'Hello world'`;

let urlParams = new URLSearchParams(window.location.search);
let urlParamCode = urlParams.get('code');
if (urlParamCode) {
  sampleCode = atob(urlParamCode.replace(/_/g, '/').replace(/-/g, '+'));
}
const hash = window.location.hash;
if (hash.startsWith('#code:')) {
  try {
    sampleCode = atob(hash.substring('#code:'.length))
  } catch (_) { }
}


function pauseGraphic() {
  document.querySelectorAll('.graphic-obj').forEach(g => {
    let doc = g.contentDocument;
    if (!doc) {
      return
    }
    doc.querySelectorAll('.highlight').forEach(t => {
      t.style.animationPlayState = 'paused';
      t.style.display = 'none'
    })
  })
}

let pythonWorker = new Worker("worker.js");

class IDE {
  constructor(root) {
    this.root = root;
    this.codemirror = CodeMirror(root.querySelector(".codemirror"), {
      lineNumbers: false,
      tabSize: 1,
      value: sampleCode,
      mode: "asciidots",
      theme: "one-dark",
      styleActiveLine: { nonEmpty: false },
    });

    this.dotPositions = [];

    this.codemirror.on("change", (_) => {
      this.root.querySelectorAll(".input").forEach((e) => {
        e.style.display = this.codemirror.getValue().includes("?")
          ? "block"
          : "none";
      });
      document.querySelectorAll('.examples .selected').forEach(e => {
        e.classList.remove('selected')
      })
    });

    this.speed = parseFloat(root.querySelector(".speed input").value);

    this.state = "STOPPED";

    this.inputTextarea = this.root.querySelector(".console textarea.input");
    this.inputCursor = 0;
    this.wasRunning = false; // was running before asked for input;

    this.pyodide = null;

    root.querySelector("button.run").addEventListener("click", (_) => {
      pauseGraphic();
      this.run();
    });

    root.querySelector("button.reset").addEventListener("click", (_) => {
      this.reset();
      this.wasRunning = false;
    });

    root.querySelector("button.step").addEventListener("click", (_) => {
      pauseGraphic();
      if (this.pyodide == null) {
        return;
      }

      this.wasRunning = false;

      let is_new = this.state == "STOPPED";

      this.pause();
      if (!is_new) {
        this.tick();
      }
    });

    root.querySelector("button.pause").addEventListener("click", (_) => {
      this.pause();
      this.wasRunning = false;
    });

    root.querySelector(".speed input").addEventListener("change", (e) => {
      this.speed = parseFloat(e.target.value);
      if (this.state == "RUNNING") {
        clearInterval(this.autotick_interval);
        this.autotick_interval = setInterval(
          () => this.tick(),
          this.speed * 1000
        );
      }
    });

    root
      .querySelector(".additional-input button")
      .addEventListener("click", (_) => {
        // TODO: validate input!
        let input = this.root.querySelector(".additional-input input");
        pythonWorker.postMessage({ type: "extra-input", data: input.value });
        if (this.wasRunning) {
          this.run();
        }
      });


    const share_button = root.querySelector('.share');
    share_button.addEventListener('click', (_) => {
      let code = this.codemirror.getValue();
      let encoded = btoa(code).replace(/\//g, '_').replace(/\+/g, '-')

      const url = new URL(window.location.href);
      url.searchParams.set('code', encoded);
      window.history.pushState(null, '', url.toString());

      navigator.clipboard.writeText(url.toString())
      share_button.innerText = "Copied"
      setTimeout(() => {
        share_button.innerText = "Share"
      }, 1000)
    })


    pythonWorker.onmessage = (event) => {
      if (event.data.type == "ready") {
        this.enable(true);
      }

      if (event.data.type == "tick") {
        this.clearDots();

        let positions = event.data.state;
        this.dotPositions = positions;

        if (positions.length == 0 || event.data.needs_shutdown) {
          this.reset();
          return;
        }

        let lines = this.root.querySelector('.CodeMirror-lines').querySelectorAll('.CodeMirror-line');

        if (this.speed > 0 || this.state != 'RUNNING') {
          for (let index = 0; index < positions.length; index++) {
            const element = positions[index];
            let x = element[0];
            let y = element[1];
            if (y >= lines.length) {
              console.log('y not found.', x, y)
              continue
            }
            let chars = lines[y].querySelectorAll('span[role=presentation] span');
            if (x >= chars.length) {
              console.log('x not found.', x, y, chars)
              continue
            }
            chars[x].classList.add("dot");
          }
        }

        console.log("STATE:", this.state)

        if (this.state == "PAUSED") {
          this.annotateDots();
        }
      }

      if (event.data.type == "output") {
        let output = this.root.querySelector(".output pre");
        output.innerText += event.data.data;
        output.scrollTop = output.scrollHeight;
        this.root.querySelector(".output").classList.remove("empty");
      }

      if (event.data.type == "extra-input") {
        this.pause();
        this.root.classList.add("needs-extra-input");
        // TODO!!
      }
    };
  }

  run() {
    if (this.pyodide == null) {
      return;
    }

    this.wasRunning = true;

    this.codemirror.options.readOnly = true;
    this.root.querySelector('.input textarea').readOnly = true;
    this.root.classList.add("running");

    if (this.state == "STOPPED") {
      this.load_code();
      this.root.classList.remove("stopped");
    }
    if (this.state == "PAUSED") {
      this.root.classList.remove("paused");
    }

    this.state = "RUNNING";

    this.autotick_interval = setInterval(() => this.tick(), this.speed * 1000);
  }

  reset() {
    this.root.classList.add("stopped");
    if (this.state == "RUNNING") {
      this.root.classList.remove("running");
      clearInterval(this.autotick_interval);
    }
    if (this.state == "PAUSED") {
      this.root.classList.remove("paused");
    }
    this.root.classList.remove("needs-extra-input");
    this.clearDots();
    this.stop();
  }

  load_code() {
    let init_input = this.root.querySelector(".input textarea");
    this.clearOutput();
    pythonWorker.postMessage({
      type: "load",
      input: init_input.value,
      code: this.codemirror.getValue(),
    });
    // this.interpreter = this.pyodide.globals.get("get_interpreter")(
    //   this.codemirror.getValue(),
    //   (a, b) => this.outputCallback(a, b),
    //   (a) => this.inputCallback(a)
    // );
  }

  setContent(text) {
    this.reset();
    this.clearOutput();
    this.codemirror.setValue(text);
    this.root.querySelectorAll(".input").forEach((e) => {
      e.style.display = text.includes("?") ? "block" : "none";
    });
  }

  clearOutput() {
    this.root.querySelector(".output pre").innerText = "";
    this.root.querySelector(".output").classList.add("empty");
  }

  outputCallback(text, _newline) {
    this.root.querySelector(".output pre").innerText += text;
    this.root.querySelector(".output").classList.remove("empty");
  }

  inputCallback(params) {
    if (params.ascii_char) {
      let ch = this.inputTextarea.value.charAt(this.inputCursor);
      this.inputCursor += 1;
      return ch;
    } else {
      let remaining = this.inputTextarea.value.substr(this.inputCursor);
      let newline = remaining.indexOf("\n");
      if (newline == -1) {
        newline = remaining.length;
      }
      let out = remaining.substr(0, newline);
      this.inputCursor += newline + 1;
      return out;
    }
  }

  pause() {
    if (this.state != "PAUSED") {
      this.root.classList.add("paused");
      this.root.querySelector('.input textarea').readOnly = true;
      this.codemirror.options.readOnly = true;
    }

    if (this.state == "STOPPED") {
      this.load_code();
      this.root.classList.remove("stopped");
    }
    if (this.state == "RUNNING") {
      this.root.classList.remove("running");
      clearInterval(this.autotick_interval);
      this.annotateDots();
    }

    this.state = "PAUSED";
  }

  /// Add tooltips to show value upon hover
  annotateDots() {
    let tooltips = {}; // x -> y -> {element, data: [](value, id)}

    let lines = this.root.querySelector('.CodeMirror-lines').querySelectorAll('.CodeMirror-line');

    for (let i = 0; i < this.dotPositions.length; i++) {
      let [x, y, value, id] = this.dotPositions[i];

      if (!(x in tooltips)) {
        tooltips[x] = {};
      }
      let tooltips_given_x = tooltips[x];
      if (!(y in tooltips_given_x)) {
        if (y >= lines.length) {
          continue
        }
        let chars = lines[y].querySelectorAll('span[role=presentation] span');
        if (x >= chars.length) {
          continue
        }
        tooltips_given_x[y] = {'char': chars[x], 'data': []};
      }
      let tooltip = tooltips_given_x[y];
      tooltip['data'].push([value, id]);
    }

    Object.values(tooltips).forEach(row =>
      Object.values(row).forEach(tooltip => {
        let char = tooltip['char'];
        let data = tooltip['data'];

        let text = data.map(([value, id]) => `#${value}`+(id == 0 ? "" : `@${id}`)).join(", ");

        const node = document.createElement("span");
        const textnode = document.createTextNode(text);
        node.appendChild(textnode);
        node.classList.add('tooltip');
        char.insertAdjacentElement('afterend', node);
        // char.appendChild(node);
      })
    )
  }

tick() {
    pythonWorker.postMessage({ type: "tick" });
    // let positions = this.pyodide.globals.get("tick")(this.interpreter);
    // this.clearDots();
    // if (this.speed > 0) {
    //   for (let index = 0; index < positions.length; index++) {
    //     const element = positions.get(index);
    //     let x = element.get(0);
    //     let y = element.get(1);
    //     let tag = `cm-pos-${y}:${x}`;
    //     let matches = this.root.getElementsByClassName(tag);
    //     if (matches.length > 0) {
    //       matches[0].classList.add("dot");
    //     }
    //   }
    // }
  }

  clearDots() {
    this.root
      .querySelectorAll(".editor .dot")
      .forEach((e) => e.classList.remove("dot"));
    
    this.root
      .querySelectorAll(".editor .tooltip")
      .forEach((e) => e.remove());
    this.dotPositions = [];
  }

  stop() {
    this.state = "STOPPED";
    this.root.classList.add("stopped");
    this.root.classList.remove("running");
    this.codemirror.options.readOnly = false;
    this.root.querySelector('.input textarea').readOnly = false;
  }

  enable(pyodide) {
    this.pyodide = pyodide;
    this.root.classList.remove("loading");


    // this.root.addEventListener("mousemove", (e) => {
    //   if (!e.target.classList.contains("dot")) {
    //     return;
    //   }
    //   let tag = Array.from(e.target.classList).filter((c) =>
    //     c.startsWith("cm-pos-")
    //   )[0];
    //   let [y, x] = tag.split("-")[2].split(":");
    //   console.log(pyodide)
    //   let debug = pyodide.globals.get("get_dots_at")(
    //     this.interpreter,
    //     x,
    //     y
    //   );
    //   console.log(debug);
    // });
  }
}

// function onDots(data) {
//   let on = data.get(0);
//   for (let index = 0; index < on.length; index++) {
//     const element = on.get(index);
//     let x = element.get(0);
//     let y = element.get(1);
//     let tag = `cm-pos-${y}:${x}`;
//     document.getElementsByClassName(tag)[0].classList.add("dot");
//   }

//   let off = data.get(1);
//   for (let index = 0; index < off.length; index++) {
//     const element = off.get(index);
//     let x = element.get(0);
//     let y = element.get(1);
//     let tag = `cm-pos-${y}:${x}`;
//     document.getElementsByClassName(tag)[0].classList.remove("dot");
//   }
//   // list.forEach(pos => {
//   //   tag = `cm-pos-${pos[1]}:${pos[0]}`
//   //   document.getElementsByClassName(tag)[0].classList.add('dot')
//   // });
// }

// let positions = [[[8, 5], [7, 6]], [[9, 5], [8, 6]], [[10, 5], [9, 6]], [[10, 5], [10, 6]], [[10, 5], [11, 6]], [[10, 5], [12, 6]], [[10, 5], [13, 6]], [[10, 5], [14, 6]], [[10, 5], [15, 6]], [[10, 5], [16, 6]], [[10, 5], [17, 6]], [[10, 5], [18, 6]], [[10, 5], [18, 5], [18, 7]], [[10, 5], [18, 5], [17, 7]], [[10, 5], [18, 5], [16, 7]], [[10, 5], [18, 5], [15, 7]], [[10, 5], [18, 5], [14, 7]], [[10, 5], [18, 5], [13, 7]], [[10, 5], [18, 5], [12, 7]], [[10, 5], [18, 5], [11, 7]], [[10, 5], [18, 5], [10, 7]], [[10, 5], [18, 5], [10, 6]], [[10, 5], [18, 5], [10, 5]], [[11, 5], [18, 5]], [[12, 5], [18, 5], [11, 4], [11, 6]], [[13, 5], [18, 5], [12, 4]], [[14, 5], [18, 5], [13, 4]], [[14, 5], [18, 5], [14, 4]], [[14, 5], [18, 5], [14, 5]], [[15, 5], [18, 5]], [[16, 5], [18, 5]], [[17, 5], [18, 5], [16, 4], [16, 6]], [[18, 5], [18, 5], [16, 3]], [[18, 4], [16, 2], [15, 3]], [[18, 3], [15, 2], [14, 3]], [[18, 2], [14, 2], [13, 3]], [[18, 1], [13, 2], [12, 3]], [[17, 1], [12, 2], [11, 3]], [[16, 1], [11, 2], [10, 3]], [[15, 1], [10, 2], [9, 3]], [[14, 1], [9, 2], [8, 3]], [[13, 1], [9, 3], [7, 3]], [[12, 1], [9, 4], [6, 3]], [[11, 1], [9, 5], [5, 3]], [[10, 1], [10, 5], [4, 3], [5, 2]], [[9, 1], [10, 5], [3, 3], [5, 2]], [[8, 1], [10, 5], [2, 3], [5, 2]], [[7, 1], [10, 5], [2, 2], [5, 2]], [[6, 1], [10, 5], [3, 2], [5, 2], [7, 2]], [[5, 1], [10, 5], [4, 2], [5, 2], [7, 3]], [[5, 1], [10, 5], [5, 2], [5, 2], [7, 4]], [[5, 1], [10, 5], [5, 1], [7, 5]], [[10, 5], [7, 6]], [[10, 5], [8, 6]], [[10, 5], [9, 6]], [[10, 5], [10, 6]], [[10, 5], [11, 6]], [[10, 5], [12, 6]], [[10, 5], [13, 6]], [[10, 5], [14, 6]], [[10, 5], [15, 6]], [[10, 5], [16, 6]], [[10, 5], [17, 6]], [[10, 5], [18, 6]], [[10, 5], [18, 5], [18, 7]], [[10, 5], [18, 5], [17, 7]], [[10, 5], [18, 5], [16, 7]], [[10, 5], [18, 5], [15, 7]], [[10, 5], [18, 5], [14, 7]], [[10, 5], [18, 5], [13, 7]], [[10, 5], [18, 5], [12, 7]], [[10, 5], [18, 5], [11, 7]], [[10, 5], [18, 5], [10, 7]], [[10, 5], [18, 5], [10, 6]], [[10, 5], [18, 5], [10, 5]]];
// let positions_idx = 0;

// setInterval(_ => {
//   document.querySelectorAll('svg .active').forEach(e => {
//     e.classList.remove('active')
//   })
//   positions[positions_idx].forEach(([x, y]) => {
//     // console.log(`text.graphic-${x}-${y}`)
//     document.querySelectorAll(`svg #graphic-${x}-${y}`).forEach(e => {
//       // console.log(e)
//       e.classList.add('active')
//     })
//   })
//   positions_idx = (positions_idx + 1) % positions.length;
// }, 50)

let ide = new IDE(document.getElementsByClassName('ide')[0]);

let examples = {
  "ex-hello-world": `.-$'Hello world'`,

  "ex-counter": `.->$#-*-#1\\
  \\--{+}--/`,

  "ex-fibonacci": `/-#$--<-1#-.
*-{+}-/
\\--^-#$-1#-.`,

  "ex-fizz-buzz": `  /$#
/-~$"Buzz"
|[%]-5#--\\
\\-*      |
/-~$"Fizz"
|[%]-3#--*
\\-*      |
/-~$"FizzBuzz"
|[%]51#--*
\\-*-~----*\\
  |[>]001#*
.->-*-{+}-/
    \\#1/`,

  "ex-factorial": `  /-1#-*---{*}-\\
/{-}-:-* #$-~--<-1#-.
>------*----/
\\-?#-.`,

  "ex-prime-sieve": `/--*--*-<--<-1@-3#-.
|  |  |   /+----\\
|  #  |   v+-0@-~-\\
|  2  | /->~*{%}/ |
|  |  | 1  |\\-+---/
|  |  | @  ^\\ |
\\-{+}-+-*  01 |
      | |  ## |
    /-* v--*+-/
 /--+-+\\|  *+--\\
 ~--+-*||  ||  |
[=]@+*/||  ||  |
 \\1#+///|  ||  |
    # $ # /~/  |
    0 # 1 */   |
    \\->-+-~----<-#$-2#-.
        \\-/
  `,
};

document.querySelectorAll(".examples button").forEach((e) => {
  e.addEventListener("click", (_) => {
    ide.setContent(examples[e.id]);
    document.querySelectorAll(".examples button").forEach((f) => {
      f.classList.remove("selected");
    });
    e.classList.add("selected");
  });
});


let anchorCursor = 0;
let goBack = document.getElementById('go-back');

document.querySelectorAll("#learn pre").forEach((e) => {
  let code = e.children[0].innerText;

  let tryIt = document.createElement('a');
  tryIt.className = "try-it"
  tryIt.innerText = "Run"
  tryIt.href = "#demo"
  e.insertBefore(tryIt, e.children[0]);

  let anchor = "ex"+anchorCursor
  anchorCursor++

  e.id = anchor

  e.addEventListener("click", (_) => {
    ide.setContent(code);
    ide.run();

    goBack.href = '#'+anchor
    goBack.style.display = "block"
  });

});
