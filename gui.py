import tkinter
from PIL import Image, ImageTk

def create_gui(x, y, pos_x, pos_y, title):
    root = tkinter.Tk()
    root.title(title)
    root.geometry(f"{x}x{y}")
    root.configure(bg="black")
    canvas = tkinter.Canvas(root, width=x, height=y, bg="black", highlightthickness=0)
    canvas.pack()

    root.geometry(f"+{pos_x}+{pos_y}")
    root.update()

    return root,canvas

def get_image(args):
    image = args.image_list[args.current_image_index]
    args.current_image_index = (args.current_image_index + 1) % len(args.image_list)  # 循環
    return image

def load_image_to_canvas(canvas_width, canvas_height, image_path, root, canvas):
    img = Image.open(image_path)
    img = img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
    tk_img = ImageTk.PhotoImage(img)

    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img  # 参照を保持して画像が破棄されないようにする
    root.update()

def print_string_to_canvas(x, y, disp_string, font, font_size, root, canvas):
    # 縁取り
    canvas.create_text(x / 2 + 1, y / 2 + 1, text=disp_string, font=(font, font_size), fill="black")
    canvas.create_text(x / 2 - 1, y / 2 - 1, text=disp_string, font=(font, font_size), fill="black")
    canvas.create_text(x / 2 + 1, y / 2 - 1, text=disp_string, font=(font, font_size), fill="black")
    canvas.create_text(x / 2 - 1, y / 2 + 1, text=disp_string, font=(font, font_size), fill="black")
    # 本文
    canvas.create_text(x / 2, y / 2, text=disp_string, font=(font, font_size), fill="white")
    root.update()

def do_topmost(root):
    root.attributes("-topmost", True)
    root.update()

def do_backmost(root):
    root.attributes("-topmost", False)
    root.lower()
    root.update()
