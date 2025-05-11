"""IPC Server for Windows using Named Pipes
検証用
使い方
    client側 ipc_send.py を参照のこと
"""
import tkinter as tk
from threading import Thread
import win32pipe
import win32file
import pywintypes

pipe_name = r'\\.\pipe\mypipe_test'

def main():
    (root, message_label) = gui_setup()
    server_thread = Thread(target=run_ipc_listener, args=(root, message_label), daemon=True)
    server_thread.start()
    root.mainloop()

def gui_setup():
    root = tk.Tk()
    root.title("Message Viewer")
    message_label = tk.Label(root, text="Waiting for messages...", font=("Arial", 14), wraplength=400)
    message_label.pack(padx=20, pady=20)
    return root, message_label

def gui_set_label_text(root, message_label, message):
    root.after(0, message_label.config, {"text": message})

def run_ipc_listener(root, message_label):
    while True:
        pipe = create_named_pipe()
        try:
            print("Waiting for client connection...")
            win32pipe.ConnectNamedPipe(pipe, None)
            print("Client connected.")
            while True:
                try:
                    handle_received_message(pipe, root, message_label)
                except pywintypes.error as e:
                    if e.args[0] == 109:  # ERROR_BROKEN_PIPE
                        print("Client disconnected.")
                        break
                    else:
                        raise
        finally:
            win32file.CloseHandle(pipe)

def create_named_pipe():
    pipe = win32pipe.CreateNamedPipe(
        pipe_name,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None
    )
    return pipe

def handle_received_message(pipe, root, message_label):
    resp = win32file.ReadFile(pipe, 64*1024)
    message = resp[1].decode()
    print(f"Received: {message}")
    gui_set_label_text(root, message_label, message)
    win32file.WriteFile(pipe, b"Message received")

if __name__ == "__main__":
    main()
