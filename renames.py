import curses
import os


def do_stuff(stdscr):
    current_line = 0
    for entry in sorted([f for f in os.listdir(os.getcwd()) if not f.startswith('.')]):
        stdscr.addstr(current_line, 0, entry)
        current_line += 1
        # c = stdscr.getch()
        # if c == ord('q'):
        #     break
    stdscr.refresh()
            
    while True:
        c = stdscr.getch()
        if c == ord('q'):
            break
    

curses.wrapper(do_stuff)
