import argparse
import toml

def get_args():
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
    def set_attrs(obj, data):
        for key, value in data.items():
            if isinstance(value, list):
                # tomlに [[action]] のようにlistが定義されている場合
                new_list = []
                for item in value:
                    if isinstance(item, dict):
                        ns = argparse.Namespace()
                        set_attrs(ns, item)
                        new_list.append(ns)
                    else:
                        new_list.append(item)
                setattr(obj, key, new_list)
            else:
                setattr(obj, key, value)
    set_attrs(args, toml_data)
    print(f'args : after : {args}')
    return args

def read_toml(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        toml_data = toml.load(f)
    return toml_data

def load_image_list(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def save_lines(filename, lines):
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
