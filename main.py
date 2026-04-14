import tkinter as tk

from viewer_app import ViewerApp


def main():
    root = tk.Tk()
    app = ViewerApp(root)
    root.minsize(900, 650)
    root.mainloop()


if __name__ == "__main__":
    main()
