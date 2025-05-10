"""IPC Client for Windows using Named Pipes
検証用
使い方
    1. サーバーを起動する : `start python ipc_server.py`
    2. このスクリプトを実行する
    3. キーボードから文字を入力する
    4. サーバー側で受信したメッセージが表示されることを確認する
    5. 終了するときは、'q'を入力する
"""
import msvcrt
import win32file
import pywintypes

pipe_name = r'\\.\pipe\mypipe'

def main():
    try:
        handle = create_pipe_handle()
        print("Type characters to send to the server. Press 'q' to quit.")
        while True:
            if msvcrt.kbhit():  # キーボード入力があるか確認
                user_input = msvcrt.getch().decode()  # 1文字取得
                if user_input.lower() == "q":  # 'q'で終了
                    print("Exiting...")
                    break
                send_user_input(handle, user_input)
        win32file.CloseHandle(handle)
    except pywintypes.error as e:
        print(f"Failed to connect to pipe: {e}")

def create_pipe_handle():
    handle = win32file.CreateFile(
            pipe_name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None
        )
    return handle

def send_user_input(handle, user_input):
    win32file.WriteFile(handle, user_input.encode())
    resp = win32file.ReadFile(handle, 64*1024)
    print(f"Server response: {resp[1].decode()}")

if __name__ == "__main__":
    main()
