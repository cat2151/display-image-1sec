from datetime import datetime, timedelta
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

    server_thread = Thread(target=run_ipc_listener, args=(args.pipe_name, root, args.disp_msec, args.interval_minutes), daemon=True)
    server_thread.start()

    root.mainloop()

def run_ipc_listener(pipe_name, root, disp_msec, interval_minutes):
    last_action_time = datetime.min
    while True:
        pipe = create_named_pipe(pipe_name)
        try:
            print("Waiting for client connection...")
            win32pipe.ConnectNamedPipe(pipe, None)
            print("Client connected.")
            last_action_time = handle_client_communication(pipe, root, disp_msec, interval_minutes, last_action_time)
        finally:
            win32file.CloseHandle(pipe)

def handle_client_communication(pipe, root, disp_msec, interval_minutes, last_action_time):
    while True:
        try:
            last_action_time = handle_received_message(pipe, root, disp_msec, last_action_time, interval_minutes)
        except pywintypes.error as e:
            if e.args[0] == 109:  # ERROR_BROKEN_PIPE
                print("Client disconnected.")
                break
            else:
                raise
    return last_action_time

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

def handle_received_message(pipe, root, disp_msec, last_action_time, interval_minutes):
    resp = win32file.ReadFile(pipe, 64*1024)
    message = resp[1].decode()
    print(f"Received: {message}")

    last_action_time = check_and_perform_action(root, disp_msec, last_action_time, interval_minutes)

    win32file.WriteFile(pipe, b"Message received")
    return last_action_time

def check_and_perform_action(root, disp_msec, last_action_time, interval_minutes):
    # 過去interval_minutes分以内にアクションが実行されている場合は、アクションを実行しない
    now = datetime.now()

    interval_start = now - timedelta(minutes=interval_minutes)
    print(f"Now: {now}, Interval Start: {interval_start}, Last Action Time: {last_action_time}")

    if last_action_time > interval_start:
        print("Action skipped due to interval restriction.")
        return last_action_time

    last_action_time = do_action(root, disp_msec)
    return last_action_time

def do_action(root, disp_msec):
    # TODO messageに応じた画像の表示をする。そのため、引数に actions を追加する。tomlに [[actions]] を書き、args.actions で受け渡す。action_name = 'disp_png' などを想定。

    do_topmost(root)
    root.after(disp_msec, do_backmost, root)

    last_action_time = datetime.now()
    return last_action_time

if __name__ == "__main__":
    main()
