def nop(*args, **kwargs):
    pass


def tick(interpreter):
    import dots.exceptions

    if not interpreter.needs_shutdown:
      try:
        interpreter.parallel_tick()
      except Exception as e:
        print(e)
        interpreter.needs_shutdown = True
      except:
        interpreter.needs_shutdown = True


    if all(dot.state.isWaiting for dot in interpreter.env.dots):
        interpreter.needs_shutdown = True
        

    positions = [[d.pos.x, d.pos.y, d.value, d.id]
                 for d in interpreter.env.dots if not d.state.is_dead()]
    return [positions, interpreter.needs_shutdown]


def get_dots_at(interpreter, x, y):
    out = ', '.join(
        f'#{d.value}' + (f'@{d.id}' if d.id != 0 else '')
        for d in interpreter.env.dots
        if not d.state.is_dead() and (d.pos.x, d.pos.y) == (int(x), int(y))
    )
    return out


def get_interpreter(program, output_callback, input_callback):
    from dots.environment import Env
    from dots.interpreter import AsciiDotsInterpreter
    from dots.callbacks import IOCallbacksStorageConstructor

    print("STARTING PROG:", program)

    io_callbacks = IOCallbacksStorageConstructor(
        get_input=input_callback, on_output=output_callback,
        on_finish=nop, on_error=nop, on_microtick=nop)

    env = Env()
    env.io = io_callbacks
    return AsciiDotsInterpreter(
        env, program, './asciidots', run_in_parallel=True)
