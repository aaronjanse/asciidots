def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = None
        try:
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
        except termios.error:
            pass
        try:
            ch = sys.stdin.read(1)
        finally:
            if old_settings is not None:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

getch = _find_getch()