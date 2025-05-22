import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import win32clipboard
from io import BytesIO

class ImageSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('表情包助手_搜索框选不中可以多次拖动窗口锁定注意力 - 关键词搜图并复制到剪贴板 ')
        self.folder = ''
        self.photo_refs = []  # 防止图片被垃圾回收
        self.create_widgets()
        self.choose_folder()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(side='top', fill='x', padx=10, pady=10)
        tk.Label(top_frame, text='关键词:').pack(side='left')
        self.keyword_var = tk.StringVar()
        self.entry = tk.Entry(top_frame, textvariable=self.keyword_var, width=20)
        self.entry.pack(side='left')
        self.entry.bind('<Return>', lambda event: self.search_images())
        # 强制激活输入框
        self.entry.focus_set()
        search_btn = tk.Button(top_frame, text='搜索', command=self.search_images)
        search_btn.pack(side='left', padx=5)
        folder_btn = tk.Button(top_frame, text='更换文件夹', command=self.choose_folder)
        folder_btn.pack(side='left', padx=5)

        self.canvas = tk.Canvas(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas)
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def choose_folder(self):
        folder = filedialog.askdirectory(title="选择表情包文件夹")
        if folder:
            self.folder = folder
            self.root.title(f'表情包助手_搜索框选不中可以最小化以后再打开 - {os.path.basename(folder)}')
            self.keyword_var.set('')
            self.clear_images()
            self.entry.focus_set()
        else:
            if not self.folder:
                self.root.quit()

    def search_images(self):
        keyword = self.keyword_var.get().strip()
        if not self.folder:
            messagebox.showinfo("提示", "请先选择文件夹")
            return
        self.clear_images()
        imgs = []
        for fname in os.listdir(self.folder):
            if keyword in fname:
                if fname.lower().endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp')):
                    imgs.append(os.path.join(self.folder, fname))
        if not imgs:
            tk.Label(self.frame, text=f'没有找到包含“{keyword}”的图片').grid(row=0, column=0, padx=5, pady=5)
        else:
            self.show_images(imgs)

    def show_images(self, img_paths):
        self.photo_refs.clear()
        max_per_row = 8
        for idx, img_path in enumerate(img_paths):
            try:
                img = Image.open(img_path)
                img.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(img)
                btn = tk.Button(self.frame, image=photo, command=lambda p=img_path: self.copy_image_to_clipboard(p))
                btn.image = photo
                r, c = divmod(idx, max_per_row)
                btn.grid(row=r*2, column=c, padx=5, pady=2)
                # 文件名标签
                fn = os.path.basename(img_path)
                label = tk.Label(self.frame, text=fn, wraplength=100, font=("Microsoft YaHei", 8))
                label.grid(row=r*2+1, column=c, padx=5, pady=(0,8))
                self.photo_refs.append(photo)
            except Exception:
                continue

    def clear_images(self):
        for w in self.frame.winfo_children():
            w.destroy()
        self.photo_refs.clear()

    def copy_image_to_clipboard(self, img_path):
        try:
            image = Image.open(img_path).convert("RGB")
            output = BytesIO()
            image.save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
        except Exception as e:
            messagebox.showerror("错误", f"复制图片失败：{e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = ImageSearchGUI(root)
    root.mainloop()