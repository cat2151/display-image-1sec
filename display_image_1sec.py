from datetime import datetime, timedelta
from threading import Thread
import random
import win32pipe
import win32file
import pywintypes
from gui import create_gui, do_backmost, do_topmost, get_image, load_image_to_canvas, print_string_to_canvas
from ipc import create_named_pipe
from utils import get_args, load_image_list, update_args_by_toml

def main():
    args = get_args()
    args = update_args_by_toml(args, args.config_filename)
    action = args.actions[0]

    action.image_list = load_image_list(action.png_list_filename)
    random.shuffle(action.image_list)
    action.current_image_index = 0
    # TODO あとで index は、history.json に保存する。そして history.json のファイル名はtomlで指定する

    display_image(args.pipe_name, action)

def display_image(pipe_name, action):
    x = action.canvas_size_x
    y = action.canvas_size_y

    (root, canvas) = create_gui(x, y, action.pos_x, action.pos_y, f"display-image-1sec : {action.png_filename}")
    load_image_to_canvas(x, y, action.png_filename, root, canvas)
    print_string_to_canvas(x, y, action.disp_string, action.font, action.font_size, root, canvas)
    do_backmost(root)

    server_thread = Thread(target=run_ipc_listener, args=(pipe_name, action, root, canvas), daemon=True)
    server_thread.start()

    root.mainloop()

def run_ipc_listener(pipe_name, action, root, canvas):
    last_action_time = datetime.min
    while True:
        pipe = create_named_pipe(pipe_name)
        try:
            print("Waiting for client connection...")
            win32pipe.ConnectNamedPipe(pipe, None)
            print("Client connected.")
            last_action_time = handle_client_communication(pipe, action, root, canvas, last_action_time)
        finally:
            win32file.CloseHandle(pipe)

def handle_client_communication(pipe, action, root, canvas, last_action_time):
    while True:
        try:
            last_action_time = handle_received_message(pipe, action, root, canvas, last_action_time)
        except pywintypes.error as e:
            if e.args[0] == 109:  # ERROR_BROKEN_PIPE
                print("Client disconnected.")
                break
            else:
                raise
    return last_action_time

def handle_received_message(pipe, action, root, canvas, last_action_time):
    resp = win32file.ReadFile(pipe, 64*1024)
    message = resp[1].decode()
    print(f"Received: {message}")

    last_action_time = check_and_perform_action(action, root, canvas, last_action_time)

    win32file.WriteFile(pipe, b"Message received")
    return last_action_time

def check_and_perform_action(action, root, canvas, last_action_time):
    now = datetime.now()
    interval_start = now - timedelta(minutes=action.interval_minutes)
    print(f"Now: {now}, Interval Start: {interval_start}, Last Action Time: {last_action_time}")

    if last_action_time > interval_start:
        print("Action skipped due to interval restriction.")
        return last_action_time

    last_action_time = do_action(action, root, canvas)
    return last_action_time

def do_action(action, root, canvas):
    load_image_to_canvas(action.canvas_size_x, action.canvas_size_y, get_image(action), root, canvas)
    print_string_to_canvas(action.canvas_size_x, action.canvas_size_y, action.disp_string, action.font, action.font_size, root, canvas)

    do_topmost(root)
    root.after(action.disp_msec, do_backmost, root)

    last_action_time = datetime.now()
    return last_action_time

if __name__ == "__main__":
    main()
