# ...existing code...
import sys, tty, termios

def main():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        sys.stdout.write("w=up s=down a=left d=right space=stop q=quit\n")
        sys.stdout.flush()
        while True:
            ch = sys.stdin.read(1)
            if ch in ("w", "W"):
                print("up")
            elif ch in ("s", "S"):
                print("down")
            elif ch in ("a", "A"):
                print("left")
            elif ch in ("d", "D"):
                print("right")
            elif ch == " ":
                print("stop")
            elif ch in ("q", "Q", "\x03"):  # q or Ctrl-C to quit
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

if __name__ == "__main__":
    main()
