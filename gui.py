import tkinter

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

def load_image_to_canvas(x, y, png_filename, root, canvas):
    image = tkinter.PhotoImage(file=png_filename)
    canvas.create_image(x / 2, y / 2, image=image)
    if not hasattr(root, 'images'):
        root.images = []
    root.images.append(image)  # Keep a reference to avoid garbage collection
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
