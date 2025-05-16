import os
from utils import get_args, save_lines, update_args_by_toml

def main():
    args = get_args()
    args = update_args_by_toml(args, args.config_filename)

    png_list = []
    for dirpath, _dirnames, filenames in os.walk(args.png_list_target_dir):
        for filename in filenames:
            if filename.endswith(".png"):
                png_list.append(os.path.join(dirpath, filename))

    save_lines(args.png_list_filename, png_list)

if __name__ == "__main__":
    main()
