"""IPC Client for Windows using Named Pipes
すぐdisconnectする
処理負荷と処理速度の検証用
"""
import time
import msvcrt
import win32file
import win32pipe
import pywintypes

pipe_name = r'\\.\pipe\mypipe_test'

def main():
    try:
        print("Type characters to send to the server. Press 'q' to quit.")
        while True:
            if msvcrt.kbhit():  # キーボード入力があるか確認
                user_input = msvcrt.getch().decode()  # 1文字取得
                if user_input.lower() == "q":  # 'q'で終了
                    print("Exiting...")
                    break
                handle = create_pipe_handle()
                send_user_input(handle, user_input)
                win32file.CloseHandle(handle)
            time.sleep(1 / 60)
    except pywintypes.error as e:
        print(f"Failed to connect to pipe: {e}")

def create_pipe_handle():
    timeout_msec = 5000
    win32pipe.WaitNamedPipe(pipe_name, timeout_msec)
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
