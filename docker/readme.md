# Asciidots on docker

Run [asciidots][] in a docker container.

Run a program `test.dots` in the current directory:

    docker run -ti --rm -v $PWD:/data aaronduino/asciidots /data/test.dots

Run the samples from the original asciidots repository:

    docker run -ti --rm aaronduino/asciidots samples/hello_world.dots

[asciidots]: https://github.com/aaronjanse/asciidots
