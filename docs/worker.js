importScripts("https://cdn.jsdelivr.net/pyodide/v0.22.0/full/pyodide.js");

// let initialized = false;

// async function loadPyodideAndPackages() {
//   let pyodide = await loadPyodide();
//   await pyodide.loadPackage("https://files.pythonhosted.org/packages/dd/be/72bccad813d72a50779c4f539660add0bfc0ee47c14ab05a243b80bcc033/asciidots-1.4.0-py3-none-any.whl");

//   await pyodide.loadPackage("micropip");
//   const micropip = pyodide.pyimport("micropip");
//   await micropip.install("asciidots");

//   if (!initialized) {
//     pyodide.runPython(pythonSrc);
//     initialized = true;
//   }
// }

let pending_input = "";

let pyodide = null;

// let pyodideReadyPromise = loadPyodideAndPackages();
(async () => {
  let pythonSrc = await (await fetch("./asciidots.py")).text();
  pyodide = await loadPyodide();
  await pyodide.loadPackage(
    "https://files.pythonhosted.org/packages/dd/be/72bccad813d72a50779c4f539660add0bfc0ee47c14ab05a243b80bcc033/asciidots-1.4.0-py3-none-any.whl"
  );

  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");
  await micropip.install("asciidots");
  pyodide.runPython(pythonSrc);

  self.postMessage({ type: "ready" });
})();

function outputCallback(text, _newline) {
  self.postMessage({ type: "output", data: text });
}

function inputCallback(params) {
  if (pending_input.length == 0) {
    self.postMessage({ type: "extra-input", char_mode: params.ascii_char });
    return null;
  }
  if (params.ascii_char) {
    let ch = pending_input.charAt(0);
    pending_input = pending_input.substring(1)
    return ch;
  } else {
    let newline = pending_input.indexOf("\n");
    if (newline == -1) {
      newline = pending_input.length;
    }
    let out = pending_input.substring(0, newline);
    pending_input = pending_input.substring(newline + 1)
    return out;
  }

  // // TODO: input queue!
  // self.postMessage({ type: "extra-input", char_mode });

}

let interpreter = null;

self.onmessage = async (event) => {
  if (event.data.type == "load") {
    pending_input = event.data.input;
    interpreter = pyodide.globals.get("get_interpreter")(
      event.data.code,
      (a, b) => outputCallback(a, b),
      (a) => inputCallback(a),
    );
  }

  if (event.data.type == "load" || event.data.type == 'tick') {
    let out = pyodide.globals.get("tick")(interpreter);
    let positions = out.get(0);
    let needs_shutdown = out.get(1);

    let state = [];
    for (let index = 0; index < positions.length; index++) {
      const element = positions.get(index);
      // console.log("DOT:", element.get(0), element.get(1));
      state.push([element.get(0), element.get(1), element.get(2), element.get(3)])
    }
    // console.log("---")

    self.postMessage({type: 'tick', state, needs_shutdown})
  }

  if (event.data.type == 'extra-input') {
    pending_input += event.data.data;
  }
};
