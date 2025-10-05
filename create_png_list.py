import os
from utils import get_args, save_lines, update_args_by_toml

def create_png_list_from_dir(target_dir):
    """指定されたディレクトリから.pngファイルのリストを作成する"""
    png_list = []
    for dirpath, _dirnames, filenames in os.walk(target_dir):
        for filename in filenames:
            if filename.endswith(".png"):
                png_list.append(os.path.join(dirpath, filename))
    return png_list

def main():
    args = get_args()
    args = update_args_by_toml(args, args.config_filename)

    for action in args.actions:
        png_list = create_png_list_from_dir(action.png_list_target_dir)
        save_lines(action.png_list_filename, png_list)

if __name__ == "__main__":
    main()
