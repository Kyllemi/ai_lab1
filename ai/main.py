import tkinter as tk
from tkinter import filedialog, simpledialog, ttk
from PIL import Image, ImageTk

from logic import (
    calculate_distance,
    draw_grid_on_image,
    extract_feature_vector,
)


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Розпізнавання Образів")
        self.root.geometry("1000x700")

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True)

        self.t1 = ttk.Frame(self.nb)
        self.t2 = ttk.Frame(self.nb)
        self.t3 = ttk.Frame(self.nb)

        self.nb.add(self.t1, text="1. Вектор ознак")
        self.nb.add(self.t2, text="2. Еталони")
        self.nb.add(self.t3, text="3. Кластери")

        self._init_t1()
        self._init_t2()
        self._init_t3()

    def _init_t1(self):
        ctrl = ttk.Frame(self.t1, padding=10)
        ctrl.pack(side="left", fill="y")
        img_p = ttk.Frame(self.t1, padding=10)
        img_p.pack(side="right", fill="both", expand=True)

        ttk.Button(ctrl, text="Завантажити BMP", command=self._t1_load).pack(
            fill="x", pady=2
        )
        ttk.Button(ctrl, text="Розрахувати", command=self._t1_calc).pack(
            fill="x", pady=2
        )

        f_grid = ttk.LabelFrame(ctrl, text="Сітка", padding=5)
        f_grid.pack(fill="x", pady=5)
        ttk.Label(f_grid, text="Рядки:").grid(row=0, column=0)
        self.t1_r = ttk.Entry(f_grid, width=5)
        self.t1_r.insert(0, "5")
        self.t1_r.grid(row=0, column=1)
        ttk.Label(f_grid, text="Стовпці:").grid(row=1, column=0)
        self.t1_c = ttk.Entry(f_grid, width=5)
        self.t1_c.insert(0, "5")
        self.t1_c.grid(row=1, column=1)

        self.t1_txt = tk.Text(ctrl, width=30, font=("Courier", 8))
        self.t1_txt.pack(fill="both", expand=True)

        self.t1_img_lbl = tk.Label(img_p, bg="black", relief="sunken")
        self.t1_img_lbl.pack(fill="both", expand=True)
        self.t1_img = None

    def _t1_load(self):
        p = filedialog.askopenfilename(filetypes=[("BMP", "*.bmp")])
        if p:
            self.t1_img = Image.open(p).convert("RGB")
            self._t1_calc()

    def _t1_calc(self):
        if not self.t1_img:
            return
        r, c = int(self.t1_r.get()), int(self.t1_c.get())
        abs_v, norm_v = extract_feature_vector(self.t1_img, r, c)

        self.t1_txt.delete("1.0", tk.END)
        self.t1_txt.insert(tk.END, f"Абсолютний:\n{abs_v}\n\nНормований:\n{norm_v}")

        grid_img = draw_grid_on_image(self.t1_img, r, c)
        grid_img.thumbnail((450, 450))
        self.t1_photo = ImageTk.PhotoImage(grid_img)
        self.t1_img_lbl.config(image=self.t1_photo)

    def _init_t2(self):
        top = ttk.Frame(self.t2, padding=5)
        top.pack(fill="x")
        ttk.Label(top, text="Метрика:").pack(side="left")
        self.t2_m = ttk.Combobox(
            top,
            values=["Евклідова", "Мангеттенська", "Чебишова"],
            state="readonly",
        )
        self.t2_m.current(0)
        self.t2_m.pack(side="left", padx=5)

        p_left = ttk.LabelFrame(self.t2, text="Еталони", padding=5)
        p_left.pack(side="left", fill="both", expand=True)
        p_right = ttk.LabelFrame(self.t2, text="Тест", padding=5)
        p_right.pack(side="right", fill="both", expand=True)

        self.t2_tree = ttk.Treeview(
            p_left, columns=("C", "V"), show="headings", height=8
        )
        self.t2_tree.heading("C", text="Клас")
        self.t2_tree.heading("V", text="Вектор")
        self.t2_tree.pack(fill="both", expand=True)

        btn_f = ttk.Frame(p_left)
        btn_f.pack(fill="x")
        ttk.Button(btn_f, text="+ Додати", command=self._t2_add).pack(
            side="left", expand=True, fill="x"
        )
        ttk.Button(btn_f, text="Очистити", command=self._t2_clear).pack(
            side="left", expand=True, fill="x"
        )

        ttk.Button(p_right, text="Класифікувати", command=self._t2_classify).pack(
            fill="x"
        )
        self.t2_lbl = tk.Label(p_right, bg="black", height=8)
        self.t2_lbl.pack(fill="x", pady=5)
        self.t2_txt = tk.Text(p_right, font=("Courier", 8))
        self.t2_txt.pack(fill="both", expand=True)

        self.t2_etalons = {}

    def _t2_add(self):
        p = filedialog.askopenfilename(filetypes=[("BMP", "*.bmp")])
        if not p:
            return
        cls = simpledialog.askstring("Клас", "Назва класу:")
        if cls:
            _, nv = extract_feature_vector(Image.open(p), 5, 5)
            self.t2_etalons[cls] = nv
            self.t2_tree.insert("", "end", values=(cls, str(nv)))

    def _t2_clear(self):
        self.t2_etalons.clear()
        self.t2_tree.delete(*self.t2_tree.get_children())

    def _t2_classify(self):
        if not self.t2_etalons:
            return
        p = filedialog.askopenfilename(filetypes=[("BMP", "*.bmp")])
        if not p:
            return
        img = Image.open(p).convert("RGB")
        _, nv = extract_feature_vector(img, 5, 5)

        g_img = draw_grid_on_image(img, 5, 5)
        g_img.thumbnail((150, 150))
        self.t2_ph = ImageTk.PhotoImage(g_img)
        self.t2_lbl.config(image=self.t2_ph)

        m_map = {
            "Евклідова": "euclidean",
            "Мангеттенська": "manhattan",
            "Чебишова": "chebyshev",
        }
        metric = m_map[self.t2_m.get()]

        self.t2_txt.delete("1.0", tk.END)
        best, min_d = None, float("inf")
        for cls, env in self.t2_etalons.items():
            d = calculate_distance(nv, env, metric)
            self.t2_txt.insert(tk.END, f"До '{cls}': d = {round(d, 4)}\n")
            if d < min_d:
                min_d, best = d, cls
        self.t2_txt.insert(
            tk.END, f"\nРезультат: Клас '{best}' (d = {round(min_d, 4)})"
        )

    def _init_t3(self):
        p_left = ttk.LabelFrame(self.t3, text="Навчання", padding=5)
        p_left.pack(side="left", fill="both", expand=True)
        p_right = ttk.LabelFrame(self.t3, text="Тест", padding=5)
        p_right.pack(side="right", fill="both", expand=True)

        self.t3_m = ttk.Combobox(
            p_left,
            values=["Геометричні центри", "Ортогональні області"],
            state="readonly",
        )
        self.t3_m.current(0)
        self.t3_m.pack(fill="x", pady=2)

        ttk.Button(p_left, text="+ Додати вибірку", command=self._t3_add).pack(fill="x")

        self.t3_tree = ttk.Treeview(
            p_left, columns=("C", "N"), show="headings", height=8
        )
        self.t3_tree.heading("C", text="Клас")
        self.t3_tree.heading("N", text="К-сть")
        self.t3_tree.pack(fill="both", expand=True, pady=5)

        ttk.Button(p_right, text="Класифікувати", command=self._t3_classify).pack(
            fill="x"
        )
        self.t3_txt = tk.Text(p_right, font=("Courier", 8))
        self.t3_txt.pack(fill="both", expand=True, pady=5)

        self.t3_data = {}

    def _t3_add(self):
        paths = filedialog.askopenfilenames(filetypes=[("BMP", "*.bmp")])
        if not paths:
            return
        cls = simpledialog.askstring("Клас", "Назва класу:")
        if cls:
            self.t3_data[cls] = [
                extract_feature_vector(Image.open(p), 5, 5)[1] for p in paths
            ]
            self.t3_tree.delete(*self.t3_tree.get_children())
            for c, vec in self.t3_data.items():
                self.t3_tree.insert("", "end", values=(c, len(vec)))

    def _t3_classify(self):
        if not self.t3_data:
            return
        p = filedialog.askopenfilename(filetypes=[("BMP", "*.bmp")])
        if not p:
            return
        _, nv = extract_feature_vector(Image.open(p), 5, 5)
        method = self.t3_m.get()
        self.t3_txt.delete("1.0", tk.END)

        if method == "Геометричні центри":
            best, min_d = None, float("inf")
            for cls, vecs in self.t3_data.items():
                center = [
                    sum(v[i] for v in vecs) / len(vecs) for i in range(len(vecs[0]))
                ]
                d = calculate_distance(nv, center, "euclidean")
                self.t3_txt.insert(tk.END, f"Центр '{cls}': d = {round(d, 4)}\n")
                if d < min_d:
                    min_d, best = d, cls
            self.t3_txt.insert(tk.END, f"\nРезультат: Кластер '{best}'")
        else:
            hits = []
            for cls, vecs in self.t3_data.items():
                dim = len(vecs[0])
                min_v = [min(v[i] for v in vecs) for i in range(dim)]
                max_v = [max(v[i] for v in vecs) for i in range(dim)]
                if all(min_v[i] - 0.05 <= nv[i] <= max_v[i] + 0.05 for i in range(dim)):
                    hits.append(cls)
            res = (
                f"Клас: {hits[0]}"
                if len(hits) == 1
                else f"Потрапив у: {hits}" if hits else "Не розпізнано"
            )
            self.t3_txt.insert(tk.END, f"Результат: {res}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
