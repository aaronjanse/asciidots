class Env(object):
    """
    A container for all the importants parts of an Asciidots program.
    """

    def __init__(self, world=None, dots=None, io=None, interpreter=None):
        """
        Structure for the for important parts of a dots environement.

        If you don't pass one of the 4 parameters, you need to set them quickly.

        :type world: dots.world.World
        :type dots: list[dots.dot.Dot]
        :type io: dots.callbacks.IOCallbacksStorage
        :type interpreter: dots.interpreter.AsciiDotsInterpreter
        """

        self.world = world
        self.dots = dots
        self.io = io
        self.interpreter = interpreter



