import random
import subprocess
from datetime import datetime, timedelta
from threading import Thread

import pywintypes
import win32file
import win32pipe

from gui import (ImageLoadError, create_gui, do_backmost, do_topmost,
                 get_image, load_image_to_canvas, print_string_to_canvas)
from ipc import create_named_pipe
from utils import get_args, load_image_list, update_args_by_toml


def main():
    args = get_args()
    args = update_args_by_toml(args, args.config_filename)
    args.actions = inherit_base_action_properties(args.actions)
    for action in args.actions:
        action.image_list = load_image_list(action.png_list_filename)
        random.shuffle(action.image_list)
        action.current_image_index = 0
    # TODO あとで index は、history.json に保存する。そして history.json のファイル名はtomlで指定する

    setup_image_viewer_and_start_mainloop(args.pipe_name, args.actions)

def inherit_base_action_properties(actions):
    for action in actions:
        if hasattr(action, 'base_action_name'):
            base_action = next((a for a in actions if a.action_name == action.base_action_name), None)
            if base_action:
                for key, value in base_action.__dict__.items():
                    if not hasattr(action, key):
                        setattr(action, key, value)
            else:
                raise ValueError(f"Base action '{action.base_action_name}' not found for action '{action.action_name}'")
    print(f"Inherited action properties: {[action.__dict__ for action in actions]}")
    return actions

def setup_image_viewer_and_start_mainloop(pipe_name, actions):
    # 先頭の action を使って GUI を作る（ウィンドウサイズや位置のため）
    action = actions[0]
    x = action.canvas_size_x
    y = action.canvas_size_y

    (root, canvas) = create_gui(x, y, action.pos_x, action.pos_y, "display-image-1sec")
    load_image_to_canvas(x, y, get_image(action), root, canvas)
    print_string_to_canvas(x, y, action.disp_string, action.font, action.font_size, root, canvas)
    do_backmost(root)

    server_thread = Thread(target=run_ipc_listener, args=(pipe_name, actions, root, canvas), daemon=True)
    server_thread.start()

    root.mainloop()

def run_ipc_listener(pipe_name, actions, root, canvas):
    last_action_times = {action.action_name: datetime.min for action in actions}
    while True:
        pipe = create_named_pipe(pipe_name)
        try:
            print("Waiting for client connection...")
            win32pipe.ConnectNamedPipe(pipe, None)
            print("Client connected.")
            last_action_times = handle_client_communication(pipe, actions, root, canvas, last_action_times)
        finally:
            win32file.CloseHandle(pipe)

def handle_client_communication(pipe, actions, root, canvas, last_action_times):
    while True:
        try:
            last_action_times = handle_received_message(pipe, actions, root, canvas, last_action_times)
        except pywintypes.error as e: # pylint: disable=no-member
            # ERROR_BROKEN_PIPE (109) をチェック
            if e.args[0] == 109:  # ERROR_BROKEN_PIPE
                print("Client disconnected.")
                break
            else:
                print(f"Unexpected pipe error: {e}")
                raise
    return last_action_times

def handle_received_message(pipe, actions, root, canvas, last_action_times):
    resp = win32file.ReadFile(pipe, 64*1024)
    message = resp[1].decode()
    print(f"Received: {message}")
    action_name = message.strip()
    print(f"Action name: {action_name}")

    action = next((a for a in actions if a.action_name == action_name), None)
    if action is None:
        print(f"actionがありません : {action_name}")
        win32file.WriteFile(pipe, b"Action not found")
        return last_action_times

    last_action_time = last_action_times.get(action_name, datetime.min)
    new_last_action_time = check_and_perform_action(action, root, canvas, last_action_time)
    last_action_times[action_name] = new_last_action_time

    win32file.WriteFile(pipe, b"Message received")
    return last_action_times

def check_and_perform_action(action, root, canvas, last_action_time):
    now = datetime.now()
    interval_start = now - timedelta(minutes=action.interval_minutes)
    print(f"Now: {now}, Interval Start: {interval_start}, Last Action Time: {last_action_time}")

    if last_action_time > interval_start:
        print("skipします : interval中です")
        return last_action_time

    try:
        last_action_time = do_action(action, root, canvas)
        return last_action_time
    except RuntimeError as e:
        # 画像読み込みエラーによる再生成処理後のエラー
        print(f"FATAL ERROR: {e}")
        # システム終了前にGUIを閉じる
        if root:
            root.quit()
        raise SystemExit(str(e)) from e

def do_action(action, root, canvas):
    try:
        load_image_to_canvas(action.canvas_size_x, action.canvas_size_y, get_image(action), root, canvas)
        print_string_to_canvas(action.canvas_size_x, action.canvas_size_y, action.disp_string, action.font, action.font_size, root, canvas)

        do_topmost(root)
        root.after(action.disp_msec, do_backmost, root)

        last_action_time = datetime.now()
        return last_action_time
    except ImageLoadError as e:
        print(f"画像読み込みエラーが発生しました: {e}")
        print(f"影響を受けたファイル: {e.image_path}")

        # 再生成コマンドを実行
        if hasattr(action, 'regeneration_command') and action.regeneration_command:
            try:
                regenerate_image_list(action)
                print("画像リストの再生成が完了しました。")
                raise RuntimeError("画像ファイルが見つかりませんでした。画像リストを再生成しました。アプリケーションを再起動してください。") from e
            except subprocess.SubprocessError as regen_error:
                print(f"再生成に失敗しました: {regen_error}")
                raise RuntimeError(f"画像ファイルが見つからず、再生成にも失敗しました。手動で対応してください。詳細: {e}") from e
        else:
            raise RuntimeError(f"画像ファイルが見つかりません。設定を確認して再生成してください。詳細: {e}") from e

def regenerate_image_list(action):
    """画像リストを再生成する"""
    command = action.regeneration_command
    print(f"再生成コマンドを実行します: {command}")

    # subprocessを使ってコマンドを実行
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60, check=False)

    if result.returncode != 0:
        raise subprocess.SubprocessError(f"再生成コマンドが失敗しました。終了コード: {result.returncode}, エラー: {result.stderr}")

    print(f"再生成コマンド実行結果: {result.stdout}")
    return result

if __name__ == "__main__":
    main()
