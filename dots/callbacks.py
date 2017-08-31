class IOCallbacksStorage(object):
    """ This class stores user-defined callbacks. Feel free to inherit this! """
    def __init__(self, env):
        """
        The base interface for inputs and outputs for a asciidots program.

        :type env: dots.environement.Env
        """
        self.env = env
        self.env.io = self

    def get_input(self):
        """ This function should return an integer from stdin, the user, etc """
        raise Exception('get_input: not implemented')

    def on_output(self, value):
        """
        This function is called whenever the AsciiDots program returns a value
        Note that the value may be a string
        """
        raise Exception('on_output: not implemented')

    def on_finish(self):
        """ This function is called when the AsciiDots program finished executing """
        raise Exception('on_finish: not implemented')

    def on_error(self, error_text):
        """ This function is pretty self explanatory; it catches errors with the AsciiDot program that occur during interpretetion """
        raise Exception('on_error: not implemented')

    def on_microtick(self, dot):
        pass


class IOCallbacksStorageConstructor(object):
    """ This is just a way to build an IOCallbacksStorage equivalent object """
    def __init__(self, get_input, on_output, on_finish, on_error, on_microtick):
        self.get_input = get_input
        self.on_output = on_output
        self.on_finish = on_finish
        self.on_error = on_error
        self.on_microtick = on_microtick
