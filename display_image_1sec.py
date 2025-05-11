from threading import Thread
import win32pipe
import win32file
import pywintypes
from gui import create_gui, do_backmost, do_topmost, load_image_to_canvas, print_string_to_canvas
from utils import get_args, update_args_by_toml

def main():
    args = get_args()
    args = update_args_by_toml(args, args.config_filename)
    display_image(args)

def display_image(args):
    x = args.canvas_size_x
    y = args.canvas_size_y

    (root, canvas) = create_gui(x, y, args.pos_x, args.pos_y, f"display-image-1sec : {args.png_filename}")
    load_image_to_canvas(x, y, args.png_filename, root, canvas)
    print_string_to_canvas(x, y, args.disp_string, args.font, args.font_size, root, canvas)
    do_backmost(root)

    server_thread = Thread(target=run_ipc_listener, args=(args.pipe_name, root, args.disp_msec), daemon=True)
    server_thread.start()

    root.mainloop()

def run_ipc_listener(pipe_name, root, disp_msec):
    while True:
        pipe = create_named_pipe(pipe_name)
        try:
            print("Waiting for client connection...")
            win32pipe.ConnectNamedPipe(pipe, None)
            print("Client connected.")
            while True:
                try:
                    handle_received_message(pipe, root, disp_msec)
                except pywintypes.error as e:
                    if e.args[0] == 109:  # ERROR_BROKEN_PIPE
                        print("Client disconnected.")
                        break
                    else:
                        raise
        finally:
            win32file.CloseHandle(pipe)

def create_named_pipe(pipe_name):
    pipe = win32pipe.CreateNamedPipe(
        pipe_name,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None
    )
    return pipe

def handle_received_message(pipe, root, disp_msec):
    resp = win32file.ReadFile(pipe, 64*1024)
    message = resp[1].decode()
    print(f"Received: {message}")
    # ↑ TODO messageに応じた画像の表示をする。そのため、引数に actions を追加する。tomlに [[actions]] を書き、args.actions で受け渡す。action_name = 'disp_png' などを想定。

    do_topmost(root)
    root.after(disp_msec, do_backmost, root)

    win32file.WriteFile(pipe, b"Message received")

if __name__ == "__main__":
    main()
