from threading import Thread
import tkinter
import toml
import win32pipe
import win32file
import pywintypes

def main():
    args = get_args()
    args = update_args_by_toml(args, args.config_filename)
    display_image(args)

def get_args():
    import argparse
    parser = argparse.ArgumentParser(description="Display an image for 1 second.")
    parser.add_argument("--config-filename", type=str, help="Path to the config file")
    args = parser.parse_args()
    return args

def update_args_by_toml(args, config_filename=None):
    if not config_filename:
        config_filename = args.config_filename
    print(f'args : before: {args}')
    toml_data = read_toml(config_filename)
    print(f'TOML : {toml_data}')
    for key, value in toml_data.items():
        setattr(args, key, value)
    print(f'args : after : {args}')
    return args

def read_toml(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        toml_data = toml.load(f)
    return toml_data

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

def create_gui(x, y, pos_x, pos_y, title):
    root = tkinter.Tk()
    root.title(title)
    root.geometry(f"{x}x{y}")
    root.configure(bg="black")
    canvas = tkinter.Canvas(root, width=x, height=y, bg="black", highlightthickness=0)
    canvas.pack()

    root.geometry(f"+{pos_x}+{pos_y}")
    root.update()

    return root,canvas

def load_image_to_canvas(x, y, png_filename, root, canvas):
    image = tkinter.PhotoImage(file=png_filename)
    canvas.create_image(x / 2, y / 2, image=image)
    if not hasattr(root, 'images'):
        root.images = []
    root.images.append(image)  # Keep a reference to avoid garbage collection
    root.update()

def print_string_to_canvas(x, y, disp_string, font, font_size, root, canvas):
    # 縁取り
    canvas.create_text(x / 2 + 1, y / 2 + 1, text=disp_string, font=(font, font_size), fill="black")
    canvas.create_text(x / 2 - 1, y / 2 - 1, text=disp_string, font=(font, font_size), fill="black")
    canvas.create_text(x / 2 + 1, y / 2 - 1, text=disp_string, font=(font, font_size), fill="black")
    canvas.create_text(x / 2 - 1, y / 2 + 1, text=disp_string, font=(font, font_size), fill="black")
    # 本文
    canvas.create_text(x / 2, y / 2, text=disp_string, font=(font, font_size), fill="white")
    root.update()

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

def do_topmost(root):
    root.attributes("-topmost", True)
    root.update()

def do_backmost(root):
    root.attributes("-topmost", False)
    root.lower()
    root.update()

if __name__ == "__main__":
    main()
