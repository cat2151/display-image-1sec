import tkinter
import toml

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

def read_toml(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        toml_data = toml.load(f)
    return toml_data

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

def display_image(args):
    x = args.canvas_size_x
    y = args.canvas_size_y
    png_filename = args.png_filename

    (root, canvas) = create_gui(x, y, f"display-image-1sec : {png_filename}")
    load_image_to_canvas(x, y, png_filename, root, canvas)

    # 1秒待機
    root.after(args.disp_msec)
    root.destroy()
    root.mainloop()

def load_image_to_canvas(x, y, png_filename, root, canvas):
    image = tkinter.PhotoImage(file=png_filename)
    canvas.create_image(x / 2, y / 2, image=image)
    root.update()

def create_gui(x, y, title):
    root = tkinter.Tk()
    root.title(title)
    root.geometry(f"{x}x{y}")
    root.configure(bg="black")
    canvas = tkinter.Canvas(root, width=x, height=y, bg="black", highlightthickness=0)
    canvas.pack()
    return root,canvas

if __name__ == "__main__":
    main()
