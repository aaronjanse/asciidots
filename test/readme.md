# Tests

### Running tests

Asciidots tests are written with pytest, you can install it with 
    
    pip install pytest

To run the test suite, just run `pytest` in the top directory (namely, asciidots) and hoppefully, you should see a green message
saying that all tests are succesful.

However, that might also mean that we don't have enough tests. Currently, our tests are just a bunch of asciidots programs that we run and check their output. Therefore there is no precise tests on the interpreter, but you can help write them.

### Writing tests

#### Asciidots programs

If you have some asciidots programs that illustrate corner cases of the language or untested features,
you can add the program in the test/ folder and add a test at the end of `test/test_programs.py` like this:

```python
def test_dots_WHAT_YOU_TEST():
    out = check_output('name of the test without the extention', 'input'):
    assert out == ['first line of output\n', 'second line...']
```

Three things to note though:
 - pytest uses `assert` to do tests
 - input is a single string, with newlines if requiered
 - `check_output` returns a list of what the program outputed, each output at a different index.
   example: `.-$#-#1-$_#-&` would output `['0\n', '1']`

#### Core Tests

If you want to write specific test for the core of the interpreter, write them in a file named `test_[name].py` where `[name]` is the file you are testing.

