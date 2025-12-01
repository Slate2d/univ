import tkinter as tk
from tkinter import ttk
from decimal import Decimal, getcontext, InvalidOperation, ROUND_HALF_UP, DivisionByZero
import re

# Устанавливаем точность вычислений с запасом
getcontext().prec = 40

BOUND = Decimal("1000000000000.000000")
QUANT = Decimal("0.000001")  # Базовое квантование для округления


def to_decimal(user_text: str):
    """
    Парсит ввод пользователя:
    1. Проверяет корректность пробелов (разделителей групп).
    2. Принимает точку или запятую.
    3. Отвергает экспоненту, буквы и некорректные знаки.
    """
    if user_text is None:
        raise ValueError("Пустое значение")
    
    s = user_text.strip()
    if s == "":
        raise ValueError("Введите число")

    # Проверка на недопустимые символы (буквы, экспоненты)
    if re.search(r'[^\d\s.,+\-]', s):
        raise ValueError("Введены недопустимые символы (буквы или спецзнаки)")
    
    if "e" in s.lower():
        raise ValueError("Экспоненциальная нотация не допускается")

    # Проверка: знак минуса/плюса не может быть в середине (например, 0.0-1)
    # Ищем знак + или -, перед которым есть цифра или точка
    if re.search(r'(?<=[\d.,])\s*[+\-]', s):
        raise ValueError("Знак числа не на своем месте")

    # Нормализация разделителя дроби
    s = s.replace(",", ".")

    if s.count(".") > 1:
        raise ValueError("Слишком много десятичных разделителей")
    
    # Разделяем на целую и дробную части для проверки пробелов
    if "." in s:
        parts = s.split(".")
        int_part = parts[0]
        frac_part = parts[1]
    else:
        int_part = s
        frac_part = ""

    # ПРОВЕРКА ПРОБЕЛОВ В ЦЕЛОЙ ЧАСТИ
    # Если пробелы есть, они должны стоять корректно: 1 000 000 (группы по 3)
    # Регулярка:
    # ^[+\-]?       - начало строки, опционально знак
    # \d{1,3}       - от 1 до 3 цифр (первая группа)
    # ( \d{3})* - далее ноль или более групп: "пробел + 3 цифры"
    # $             - конец строки
    if " " in int_part:
        if not re.match(r'^[+\-]?\d{1,3}( \d{3})*$', int_part):
            raise ValueError("Некорректная расстановка пробелов в числе")
    
    # Удаляем пробелы для создания Decimal
    clean_s = s.replace(" ", "")

    if clean_s in {"+", "-", ".", "+.", "-.", ""}:
        raise ValueError("Неполное число")

    try:
        d = Decimal(clean_s)
    except InvalidOperation:
        raise ValueError("Некорректный формат числа")

    return d


def in_range(d: Decimal) -> bool:
    return -BOUND <= d <= BOUND


def format_pretty(d: Decimal) -> str:
    """
    Форматирует число по требованиям Шага 2:
    1. Округляем до 6 знаков.
    2. Убираем незначащие нули в конце.
    3. Целая часть с пробелами-разделителями.
    4. Разделитель дробной части - точка.
    """
    # Сначала округляем математически до 6 знаков
    d_rounded = d.quantize(QUANT, rounding=ROUND_HALF_UP)
    
    # Превращаем в строку с фиксированной точкой (чтобы не было E-нотации)
    s = "{:.6f}".format(d_rounded)
    
    # Удаляем лишние нули справа (и точку, если она стала последней)
    # Например: "123.450000" -> "123.45", "100.000000" -> "100"
    s = s.rstrip("0").rstrip(".")
    
    # Форматируем целую часть с пробелами
    if "." in s:
        int_str, frac_str = s.split(".", 1)
        # int(int_str) нужен, чтобы f-string понял, что это число, 
        # но надо быть осторожным с "-" (int обрабатывает минус нормально)
        # Используем запятую как временный разделитель, потом меняем на пробел
        formatted_int = "{:,}".format(int(int_str)).replace(",", " ")
        return f"{formatted_int}.{frac_str}"
    else:
        # Число целое
        formatted_int = "{:,}".format(int(s)).replace(",", " ")
        return formatted_int


class BigCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Калькулятор (Финансовый)")
        self.geometry("580x400")
        self.minsize(560, 380)

        container = ttk.Frame(self, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        # --- Блок информации ---
        info = ttk.LabelFrame(container, text="Информация о студенте")
        info.pack(fill=tk.X, pady=(0, 10))

        student_lines = [
            "ФИО: Головач Владислав Вадимович",
            "Курс: 4",
            "Группа: 4",
            "Год: 2026",
        ]
        ttk.Label(info, text="; ".join(student_lines)).pack(anchor="w", padx=8, pady=6)

        # --- Блок ввода данных ---
        io_frame = ttk.LabelFrame(container, text="Данные")
        io_frame.pack(fill=tk.X)

        # Число А
        ttk.Label(io_frame, text="Число A:").grid(row=0, column=0, sticky="w", padx=(8, 6), pady=6)
        self.entry_a = ttk.Entry(io_frame)
        self.entry_a.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=6)

        # Операции (Radiobuttons)
        ttk.Label(io_frame, text="Операция:").grid(row=1, column=0, sticky="w", padx=(8, 6), pady=6)
        self.op_var = tk.StringVar(value="+")
        
        ops_frame = ttk.Frame(io_frame)
        ops_frame.grid(row=1, column=1, sticky="w", padx=(0, 8), pady=6)
        
        # Grid для кнопок операций (2x2 или в ряд, сделаем в ряд для компактности или 2x2)
        ttk.Radiobutton(ops_frame, text="+", value="+", variable=self.op_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(ops_frame, text="−", value="-", variable=self.op_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(ops_frame, text="×", value="*", variable=self.op_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(ops_frame, text="÷", value="/", variable=self.op_var).pack(side=tk.LEFT)

        # Число B
        ttk.Label(io_frame, text="Число B:").grid(row=2, column=0, sticky="w", padx=(8, 6), pady=6)
        self.entry_b = ttk.Entry(io_frame)
        self.entry_b.grid(row=2, column=1, sticky="ew", padx=(0, 8), pady=6)

        io_frame.columnconfigure(1, weight=1)

        # --- Кнопки управления ---
        btns = ttk.Frame(container)
        btns.pack(fill=tk.X, pady=10)
        ttk.Button(btns, text="Вычислить", command=self.calculate).pack(side=tk.LEFT)
        ttk.Button(btns, text="Очистить", command=self.clear_all).pack(side=tk.LEFT, padx=(8, 0))

        # --- Результат ---
        out = ttk.LabelFrame(container, text="Результат")
        out.pack(fill=tk.X)
        self.result_var = tk.StringVar(value="")
        self.result_entry = ttk.Entry(out, textvariable=self.result_var, state="readonly")
        self.result_entry.pack(fill=tk.X, padx=8, pady=8)

        # --- Статус бар / Ошибки ---
        # Многострочный Label для длинных сообщений об ошибках
        self.status_var = tk.StringVar(value="Введите числа. Разделитель дробной части: точка или запятая.")
        status = ttk.Label(container, textvariable=self.status_var, foreground="#444", wraplength=540)
        status.pack(fill=tk.X, pady=(8, 0))

        # --- Привязки клавиш (Clipboard) ---
        self._install_clipboard_bindings(self.entry_a)
        self._install_clipboard_bindings(self.entry_b)
        self._install_clipboard_bindings(self.result_entry)

        self.entry_a.focus_set()

    def _install_clipboard_bindings(self, widget: tk.Widget):
        def on_key(event):
            ctrl = (event.state & 0x4) != 0
            if not ctrl:
                return
            if event.keycode == 67: # Ctrl+C
                widget.event_generate('<<Copy>>')
                return "break"
            if event.keycode == 86: # Ctrl+V
                widget.event_generate('<<Paste>>')
                return "break"
            if event.keycode == 88: # Ctrl+X
                widget.event_generate('<<Cut>>')
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
        self.status_var.set("Готово к вычислениям")
        self.entry_a.focus_set()

    def calculate(self):
        a_text = self.entry_a.get()
        b_text = self.entry_b.get()
        
        # 1. Парсинг
        try:
            a = to_decimal(a_text)
        except ValueError as ex:
            self.status_var.set(f"Ошибка в числе A: {ex}")
            self.result_var.set("")
            return
        
        try:
            b = to_decimal(b_text)
        except ValueError as ex:
            self.status_var.set(f"Ошибка в числе B: {ex}")
            self.result_var.set("")
            return

        # 2. Проверка диапазона входных данных (до операции)
        if not in_range(a):
            self.status_var.set("Число A вне диапазона ±1 000 000 000 000")
            self.result_var.set("")
            return
        if not in_range(b):
            self.status_var.set("Число B вне диапазона ±1 000 000 000 000")
            self.result_var.set("")
            return

        op = self.op_var.get()
        res = Decimal(0)

        # 3. Вычисления
        try:
            if op == "+":
                res = a + b
            elif op == "-":
                res = a - b
            elif op == "*":
                res = a * b
            elif op == "/":
                if b == 0:
                    self.status_var.set("Ошибка: Деление на ноль невозможно")
                    self.result_var.set("")
                    return
                res = a / b
        except Exception as e:
            self.status_var.set(f"Ошибка вычисления: {e}")
            return

        # 4. Проверка результата на диапазон
        # Важно: сначала проверяем переполнение, потом форматируем
        if not in_range(res):
            self.status_var.set("Результат превышает допустимый диапазон")
            self.result_var.set("")
            return

        # 5. Форматирование результата
        try:
            res_str = format_pretty(res)
            self.result_var.set(res_str)
            self.status_var.set("Вычисление успешно завершено")
        except Exception as e:
            self.status_var.set(f"Ошибка форматирования: {e}")


def main():
    app = BigCalculator()
    app.mainloop()


if __name__ == "__main__":
    main()