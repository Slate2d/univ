import tkinter as tk
from tkinter import ttk
from decimal import Decimal, getcontext, InvalidOperation, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN

# --- КОНФИГУРАЦИЯ ---
# Общая точность "с запасом" для внутренних расчетов
getcontext().prec = 50

# Граница переполнения (1 триллион)
BOUND = Decimal("1000000000000.0000000000")

# Квантование для промежуточных вычислений (10 знаков)
QUANT_INTERMEDIATE = Decimal("0.0000000001")

# Квантование для основного вывода (6 знаков)
QUANT_DISPLAY = Decimal("0.000001")

# Квантование для целых чисел
QUANT_INT = Decimal("1")


def to_decimal(user_text: str):
    """
    Парсит ввод. Проверяет пробелы в целой части,
    запрещает экспоненты и буквы.
    """
    import re
    if user_text is None:
        return Decimal(0)
    
    s = user_text.strip()
    if s == "":
        return Decimal(0)  # Пустое поле считаем за 0 по умолчанию

    # Проверка на недопустимые символы
    if re.search(r'[^\d\s.,+\-]', s):
        raise ValueError("Недопустимые символы")
    
    if "e" in s.lower():
        raise ValueError("Экспонента запрещена")

    # Знак не на месте (например 0.0-1)
    if re.search(r'(?<=[\d.,])\s*[+\-]', s):
        raise ValueError("Знак числа не на своем месте")

    s = s.replace(",", ".")
    if s.count(".") > 1:
        raise ValueError("Лишние разделители")

    # Проверка пробелов в целой части (группы по 3)
    if "." in s:
        int_part = s.split(".")[0]
    else:
        int_part = s
    
    if " " in int_part:
        if not re.match(r'^[+\-]?\d{1,3}( \d{3})*$', int_part):
            raise ValueError("Некорректные пробелы")
            
    clean_s = s.replace(" ", "")
    if clean_s in {"+", "-", ".", "+.", "-.", ""}:
        return Decimal(0)

    try:
        d = Decimal(clean_s)
    except InvalidOperation:
        raise ValueError("Не число")
        
    return d


def format_pretty(d: Decimal) -> str:
    """
    Формат для основного результата:
    1 000.000000 (6 знаков, без лишних нулей, с пробелами)
    """
    # Округляем до 6 знаков
    d_rounded = d.quantize(QUANT_DISPLAY, rounding=ROUND_HALF_UP)
    s = "{:.6f}".format(d_rounded)
    # Убираем хвост нулей и точку
    s = s.rstrip("0").rstrip(".")
    
    if "." in s:
        int_str, frac_str = s.split(".", 1)
        formatted_int = "{:,}".format(int(int_str)).replace(",", " ")
        return f"{formatted_int}.{frac_str}"
    else:
        formatted_int = "{:,}".format(int(s)).replace(",", " ")
        return formatted_int


def format_integer(d: Decimal) -> str:
    """Формат для целого округленного значения (с пробелами)"""
    return "{:,}".format(int(d)).replace(",", " ")


def check_bound(d: Decimal):
    if abs(d) > BOUND:
        raise OverflowError("Переполнение диапазона")
    return d


def calc_op(v1: Decimal, v2: Decimal, op: str) -> Decimal:
    """Выполняет одну операцию с округлением до 10 знаков"""
    if op == "+":
        res = v1 + v2
    elif op == "-":
        res = v1 - v2
    elif op == "*":
        res = v1 * v2
    elif op == "/":
        if v2 == 0:
            raise ZeroDivisionError("Деление на 0")
        res = v1 / v2
    else:
        return Decimal(0)
    
    # Округление промежуточное до 10 знаков 
    res = res.quantize(QUANT_INTERMEDIATE, rounding=ROUND_HALF_UP)
    # Проверка переполнения 
    return check_bound(res)


def get_priority(op: str) -> int:
    if op in ("*", "/"):
        return 2
    return 1


class FinanceCalculatorStep3(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Финансовый калькулятор (Шаг 3)")
        self.geometry("900x500")
        self.minsize(850, 450)
        
        # Стили
        style = ttk.Style()
        style.configure("Bold.TLabel", font=("Arial", 10, "bold"))
        style.configure("Big.TEntry", font=("Arial", 11))

        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # 1. Инфо
        info_frame = ttk.LabelFrame(container, text="Информация")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(info_frame, text="ФИО: Головач Владислав Вадимович; Курс: 4; Группа: 4; Год: 2026").pack(anchor="w", padx=10, pady=5)

        # 2. Область ввода (Grid)
        input_frame = ttk.LabelFrame(container, text="Выражение")
        input_frame.pack(fill=tk.X, pady=5)
        
        # Настройка сетки
        for i in range(11): # A op1 ( B op2 C ) op3 D -> 11 элементов
            input_frame.columnconfigure(i, weight=1)

        # Ряд 0: Подписи
        labels = ["Число A", "Op 1", "", "Число B", "Op 2", "Число C", "", "Op 3", "Число D"]
        # Индексы колонок: A=0, op1=1, (=2, B=3, op2=4, C=5, )=6, op3=7, D=8
        
        ttk.Label(input_frame, text="Число A").grid(row=0, column=0)
        ttk.Label(input_frame, text="Op 1").grid(row=0, column=1)
        ttk.Label(input_frame, text="(", font=("Arial", 14, "bold")).grid(row=1, column=2, padx=2) # Скобка
        ttk.Label(input_frame, text="Число B").grid(row=0, column=3)
        ttk.Label(input_frame, text="Op 2").grid(row=0, column=4)
        ttk.Label(input_frame, text="Число C").grid(row=0, column=5)
        ttk.Label(input_frame, text=")", font=("Arial", 14, "bold")).grid(row=1, column=6, padx=2) # Скобка
        ttk.Label(input_frame, text="Op 3").grid(row=0, column=7)
        ttk.Label(input_frame, text="Число D").grid(row=0, column=8)

        # Ряд 1: Поля ввода
        self.ent_a = ttk.Entry(input_frame, width=12, justify="center")
        self.ent_a.insert(0, "0")
        self.ent_a.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.op1_var = tk.StringVar(value="+")
        self.cb_op1 = ttk.Combobox(input_frame, textvariable=self.op1_var, values=["+", "-", "*", "/"], width=3, state="readonly")
        self.cb_op1.grid(row=1, column=1)

        self.ent_b = ttk.Entry(input_frame, width=12, justify="center")
        self.ent_b.insert(0, "0")
        self.ent_b.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        self.op2_var = tk.StringVar(value="+")
        self.cb_op2 = ttk.Combobox(input_frame, textvariable=self.op2_var, values=["+", "-", "*", "/"], width=3, state="readonly")
        self.cb_op2.grid(row=1, column=4)

        self.ent_c = ttk.Entry(input_frame, width=12, justify="center")
        self.ent_c.insert(0, "0")
        self.ent_c.grid(row=1, column=5, padx=5, pady=5, sticky="ew")

        self.op3_var = tk.StringVar(value="+")
        self.cb_op3 = ttk.Combobox(input_frame, textvariable=self.op3_var, values=["+", "-", "*", "/"], width=3, state="readonly")
        self.cb_op3.grid(row=1, column=7)

        self.ent_d = ttk.Entry(input_frame, width=12, justify="center")
        self.ent_d.insert(0, "0")
        self.ent_d.grid(row=1, column=8, padx=5, pady=5, sticky="ew")

        # 3. Настройка округления
        round_frame = ttk.LabelFrame(container, text="Настройки итогового округления")
        round_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(round_frame, text="Метод округления до целого:").pack(side=tk.LEFT, padx=10, pady=10)
        
        self.round_method_var = tk.StringVar(value="Математическое")
        methods = ["Математическое", "Бухгалтерское", "Усечение"]
        self.cb_round = ttk.Combobox(round_frame, textvariable=self.round_method_var, values=methods, state="readonly", width=20)
        self.cb_round.pack(side=tk.LEFT, padx=10)

        # 4. Кнопки
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="ВЫЧИСЛИТЬ", command=self.calculate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_all).pack(side=tk.LEFT, padx=5)

        # 5. Результаты
        res_frame = ttk.LabelFrame(container, text="Результаты")
        res_frame.pack(fill=tk.X, pady=10)
        
        res_grid = ttk.Frame(res_frame)
        res_grid.pack(fill=tk.X, padx=10, pady=10)
        res_grid.columnconfigure(1, weight=1)

        # Основной результат (дробный)
        ttk.Label(res_grid, text="Результат вычисления:", style="Bold.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        self.res_var = tk.StringVar()
        self.entry_res = ttk.Entry(res_grid, textvariable=self.res_var, state="readonly")
        self.entry_res.grid(row=0, column=1, sticky="ew", padx=10)

        # Округленный результат (целое)
        ttk.Label(res_grid, text="Итог (целое):", style="Bold.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        self.res_int_var = tk.StringVar()
        self.entry_res_int = ttk.Entry(res_grid, textvariable=self.res_int_var, state="readonly")
        self.entry_res_int.grid(row=1, column=1, sticky="ew", padx=10)

        # Статус
        self.status_var = tk.StringVar(value="Введите 4 числа. Приоритет: (B op2 C) выполняется первым.")
        lbl_status = ttk.Label(container, textvariable=self.status_var, foreground="gray", wraplength=800)
        lbl_status.pack(pady=5)

        # Привязки
        self.bind_clipboard(self.ent_a)
        self.bind_clipboard(self.ent_b)
        self.bind_clipboard(self.ent_c)
        self.bind_clipboard(self.ent_d)
        self.bind_clipboard(self.entry_res)
        self.bind_clipboard(self.entry_res_int)

    def bind_clipboard(self, widget):
        # Стандартные биндинги (пропущено для краткости, аналогично шагу 2)
        # Для полной версии можно скопировать метод _install_clipboard_bindings из прошлого шага
        pass

    def clear_all(self):
        for e in [self.ent_a, self.ent_b, self.ent_c, self.ent_d]:
            e.delete(0, tk.END)
            e.insert(0, "0")
        self.res_var.set("")
        self.res_int_var.set("")
        self.status_var.set("Очищено")

    def calculate(self):
        try:
            # 1. Чтение и валидация
            a = to_decimal(self.ent_a.get())
            b = to_decimal(self.ent_b.get())
            c = to_decimal(self.ent_c.get())
            d = to_decimal(self.ent_d.get())

            op1 = self.op1_var.get()
            op2 = self.op2_var.get()
            op3 = self.op3_var.get()

            # 2. Логика вычислений с приоритетами [cite: 5, 6]
            # Сначала всегда скобки (B op2 C)
            mid_val = calc_op(b, c, op2) # Здесь уже внутри округление до 10 знаков

            # Теперь выражение выглядит как: A op1 MID op3 D
            # Нужно решить, что делать раньше: op1 или op3
            # Если op1 (* или /) и op3 (+ или -), то op1 раньше.
            # Если оба одинакового веса, то слева направо (A op1 MID) -> result op3 D
            
            p1 = get_priority(op1)
            p3 = get_priority(op3)

            final_res = Decimal(0)

            if p1 >= p3:
                # Слева направо: (A op1 MID) затем op3 D
                temp = calc_op(a, mid_val, op1)
                final_res = calc_op(temp, d, op3)
            else:
                # Справа налево приоритет: A op1 (MID op3 D)
                # Например: A + MID * D
                temp = calc_op(mid_val, d, op3)
                final_res = calc_op(a, temp, op1)

            # 3. Вывод основного результата (форматирование)
            self.res_var.set(format_pretty(final_res))

            # 4. Финальное округление до целого [cite: 13, 14]
            method = self.round_method_var.get()
            
            if method == "Математическое":
                # ROUND_HALF_UP до 0 знаков (до целого)
                int_val = final_res.quantize(QUANT_INT, rounding=ROUND_HALF_UP)
            elif method == "Бухгалтерское":
                # ROUND_HALF_EVEN до 0 знаков
                int_val = final_res.quantize(QUANT_INT, rounding=ROUND_HALF_EVEN)
            elif method == "Усечение":
                # ROUND_DOWN (отбрасывание дроби)
                int_val = final_res.quantize(QUANT_INT, rounding=ROUND_DOWN)
            else:
                int_val = final_res # fallback

            self.res_int_var.set(format_integer(int_val))
            self.status_var.set("Готово")

        except ValueError as ve:
            self.status_var.set(f"Ошибка ввода: {ve}")
        except ZeroDivisionError:
            self.status_var.set("Ошибка: Деление на ноль!")
        except OverflowError:
            self.status_var.set("Ошибка: Переполнение (результат > 1 трлн)") [cite: 8]
        except Exception as ex:
            self.status_var.set(f"Системная ошибка: {ex}")

if __name__ == "__main__":
    app = FinanceCalculatorStep3()
    app.mainloop()