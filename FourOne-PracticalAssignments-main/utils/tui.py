import sys

def interactive_select(options: list[str], title: str = "Select an option:", default_idx: int = 0) -> int:
    """
    Renders an interactive selection menu in the terminal using arrow keys.
    Returns the index of the selected option, or -1 if the terminal doesn't support TUI.
    """
    # Check if stdout/stdin is interactive TTY
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return -1
        
    try:
        import tty
        import termios
    except ImportError:
        # Fallback for Windows or environments without termios
        return -1
        
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    current_idx = default_idx
    lines_written = 3 + len(options)  # Title + Instruction + Blank line + options
    
    try:
        # Set terminal to raw mode to read characters instantly
        tty.setcbreak(fd)
        
        # Hide cursor
        sys.stdout.write("\033[?25l")
        
        # Draw Title and instructions
        sys.stdout.write(f"\033[1;33m{title}\033[0m\n")
        sys.stdout.write("  [Use Up/Down Arrow keys to navigate, Enter to confirm]\n\n")
        sys.stdout.flush()
        
        while True:
            # Render choices
            for i, opt in enumerate(options):
                if i == current_idx:
                    sys.stdout.write(f"\r\033[K\033[1;36m ➔  {opt}\033[0m\n")
                else:
                    sys.stdout.write(f"\r\033[K    {opt}\n")
            sys.stdout.flush()
            
            # Read raw character
            char = sys.stdin.read(1)
            
            # Move cursor back up to redraw options
            sys.stdout.write(f"\033[{len(options)}A")
            sys.stdout.flush()
            
            if char in ('\r', '\n'):
                # Selected
                break
            elif char == '\x1b':
                # Check for escape sequences (arrow keys)
                seq = sys.stdin.read(2)
                if seq == '[A':  # Up Arrow
                    current_idx = (current_idx - 1) % len(options)
                elif seq == '[B':  # Down Arrow
                    current_idx = (current_idx + 1) % len(options)
            elif char.lower() == 'q':
                # Abort
                current_idx = -1
                break
                
        # Clear the entire menu from terminal to leave a clean screen
        sys.stdout.write("\033[3A")  # Move up to title line
        for _ in range(lines_written):
            sys.stdout.write("\r\033[K\n")
        sys.stdout.write(f"\033[{lines_written}A")
        
        # Show cursor again
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        
    except Exception:
        # Restore cursor on error
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        return -1
    finally:
        # Restore terminal attributes
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
    return current_idx
