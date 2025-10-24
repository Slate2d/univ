import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, getcontext, InvalidOperation, ROUND_HALF_UP



getcontext().prec = 40


BOUND = Decimal("1000000000000.000000")
QUANT = Decimal("0.000000")


def to_decimal(user_text: str):
    """
    Parse user input into Decimal with:
    - accepts comma or dot as decimal separator
    - rejects exponential notation
    - trims spaces, allows leading +/-, and empty fractional part after sep
    Returns Decimal quantized to 6 fractional digits (ROUND_HALF_UP).
    Raises ValueError on invalid input.
    """
    if user_text is None:
        raise ValueError("Пустое значение")
    s = user_text.strip()
    if s == "":
        raise ValueError("Введите число")
    
    if "e" in s.lower():
        raise ValueError("Экспоненциальная нотация не допускается")
    
    s = s.replace(" ", "")
    s = s.replace(",", ".")
    
    if s.count(".") > 1:
        raise ValueError("Слишком много десятичных разделителей")
    if s in {"+", "-", ".", "+.", "-."}:
        raise ValueError("Неполное число")

    
    if s.endswith("."):
        s += "0"

    try:
        d = Decimal(s)
    except InvalidOperation:
        raise ValueError("Некорректное число")

    
    try:
        d = d.quantize(QUANT, rounding=ROUND_HALF_UP)
    except InvalidOperation:
        
        raise ValueError("Ошибка округления")
    return d


def in_range(d: Decimal) -> bool:
    return -BOUND <= d <= BOUND


def format_fixed(d: Decimal) -> str:
    """Format Decimal as fixed-point with up to 6 decimals, no exponent."""
    
    s = format(d, 'f')  
    
    if "." not in s:
        s += ".000000"
    else:
        int_part, frac = s.split(".", 1)
        if len(frac) < 6:
            frac = frac + ("0" * (6 - len(frac)))
        elif len(frac) > 6:
            
            frac = frac[:6]
        s = int_part + "." + frac
    return s


class BigCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Калькулятор (сложение/вычитание)")
        self.geometry("560x360")
        self.minsize(520, 340)

        
        container = ttk.Frame(self, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        
        info = ttk.LabelFrame(container, text="Информация о студенте")
        info.pack(fill=tk.X, pady=(0, 10))

        
        student_lines = [
            "ФИО: Головач Владислав Вадимович",
            "Курс: 4",
            "Группа: 4",
            "Год: 2026",
        ]
        ttk.Label(info, text="; ".join(student_lines)).pack(anchor="w", padx=8, pady=6)

        
        io_frame = ttk.LabelFrame(container, text="Данные")
        io_frame.pack(fill=tk.X)

        ttk.Label(io_frame, text="Число A:").grid(row=0, column=0, sticky="w", padx=(8, 6), pady=6)
        self.entry_a = ttk.Entry(io_frame)
        self.entry_a.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=6)

        ttk.Label(io_frame, text="Операция:").grid(row=1, column=0, sticky="w", padx=(8, 6), pady=6)
        self.op_var = tk.StringVar(value="+")
        ops = ttk.Frame(io_frame)
        ops.grid(row=1, column=1, sticky="w", padx=(0, 8), pady=6)
        ttk.Radiobutton(ops, text="Сложение", value="+", variable=self.op_var).pack(side=tk.LEFT)
        ttk.Radiobutton(ops, text="Вычитание", value="-", variable=self.op_var).pack(side=tk.LEFT, padx=(12, 0))

        ttk.Label(io_frame, text="Число B:").grid(row=2, column=0, sticky="w", padx=(8, 6), pady=6)
        self.entry_b = ttk.Entry(io_frame)
        self.entry_b.grid(row=2, column=1, sticky="ew", padx=(0, 8), pady=6)

        io_frame.columnconfigure(1, weight=1)

        
        btns = ttk.Frame(container)
        btns.pack(fill=tk.X, pady=10)
        ttk.Button(btns, text="Вычислить", command=self.calculate).pack(side=tk.LEFT)
        ttk.Button(btns, text="Очистить", command=self.clear_all).pack(side=tk.LEFT, padx=(8, 0))

        
        out = ttk.LabelFrame(container, text="Результат")
        out.pack(fill=tk.X)
        self.result_var = tk.StringVar(value="")
        self.result_entry = ttk.Entry(out, textvariable=self.result_var, state="readonly")
        self.result_entry.pack(fill=tk.X, padx=8, pady=8)

        
        self.status_var = tk.StringVar(value="Поддерживаются точка и запятая. Диапазон: ±1 000 000 000 000.000000")
        status = ttk.Label(container, textvariable=self.status_var, foreground="#444")
        status.pack(fill=tk.X, pady=(8, 0))

        
        self._install_clipboard_bindings(self.entry_a)
        self._install_clipboard_bindings(self.entry_b)
        self._install_clipboard_bindings(self.result_entry)

        
        self.entry_a.focus_set()

    def _install_clipboard_bindings(self, widget: tk.Widget):
        
        
        def on_key(event):
            ctrl = (event.state & 0x4) != 0  
            if not ctrl:
                return
            
            if event.keycode == 67:  
                widget.event_generate('<<Copy>>')
                return "break"
            if event.keycode == 86:  
                widget.event_generate('<<Paste>>')
                return "break"
            if event.keycode == 88:  
                widget.event_generate('<<Cut>>')
                return "break"
            
            if event.keycode == 45 and (event.state & 0x1) != 0:  
                widget.event_generate('<<Paste>>')
                return "break"
            if event.keycode == 45 and (event.state & 0x8) != 0:  
                widget.event_generate('<<Copy>>')
                return "break"

        widget.bind('<KeyPress>', on_key, add=True)

        
        menu = tk.Menu(widget, tearoff=False)
        menu.add_command(label="Копировать", command=lambda: widget.event_generate('<<Copy>>'))
        menu.add_command(label="Вставить", command=lambda: widget.event_generate('<<Paste>>'))
        menu.add_command(label="Вырезать", command=lambda: widget.event_generate('<<Cut>>'))

        def show_menu(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        widget.bind("<Button-3>", show_menu)

    def clear_all(self):
        self.entry_a.delete(0, tk.END)
        self.entry_b.delete(0, tk.END)
        self.result_var.set("")
        self.status_var.set("Поддерживаются точка и запятая. Диапазон: ±1 000 000 000 000.000000")
        self.entry_a.focus_set()

    def calculate(self):
        
        a_text = self.entry_a.get()
        b_text = self.entry_b.get()
        try:
            a = to_decimal(a_text)
        except ValueError as ex:
            self.status_var.set(f"Ошибка в первом числе: {ex}")
            self.result_var.set("")
            return
        try:
            b = to_decimal(b_text)
        except ValueError as ex:
            self.status_var.set(f"Ошибка во втором числе: {ex}")
            self.result_var.set("")
            return

        
        if not in_range(a):
            self.status_var.set("Первое число вне диапазона ±1 000 000 000 000.000000")
            self.result_var.set("")
            return
        if not in_range(b):
            self.status_var.set("Второе число вне диапазона ±1 000 000 000 000.000000")
            self.result_var.set("")
            return

        op = self.op_var.get()
        res = a + b if op == "+" else a - b
        
        res = res.quantize(QUANT, rounding=ROUND_HALF_UP)

        if not in_range(res):
            self.status_var.set("Переполнение диапазона результата")
            self.result_var.set("")
            return

        self.result_var.set(format_fixed(res))
        self.status_var.set("Готово")


def main():
    app = BigCalculator()
    app.mainloop()


if __name__ == "__main__":
    main()

