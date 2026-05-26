
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime
import os


class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Список всех тренировок
        self.trainings = []
        
        # Типы тренировок для выпадающего списка
        self.workout_types = [
            "Бег",
            "Велосипед",
            "Плавание",
            "Силовая тренировка",
            "Йога",
            "Кроссфит",
            "Растяжка",
            "Другое"
        ]
        
        self.setup_ui()
        self.load_default_data()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        
        # === Фрейм ввода данных ===
        input_frame = ttk.LabelFrame(self.root, text="Добавить тренировку", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Дата
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        # Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.type_combobox = ttk.Combobox(input_frame, values=self.workout_types, width=20, state="readonly")
        self.type_combobox.grid(row=0, column=3, padx=5, pady=5)
        self.type_combobox.set(self.workout_types[0])
        
        # Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.duration_entry = ttk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="➕ Добавить тренировку", command=self.add_training)
        self.add_button.grid(row=0, column=6, padx=10, pady=5)
        
        # === Фрейм фильтрации ===
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Фильтр по типу
        ttk.Label(filter_frame, text="Тип:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.filter_type = ttk.Combobox(filter_frame, values=["Все"] + self.workout_types, width=20, state="readonly")
        self.filter_type.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type.set("Все")
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.filter_date = ttk.Entry(filter_frame, width=15)
        self.filter_date.grid(row=0, column=3, padx=5, pady=5)
        
        # Кнопки фильтрации
        ttk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(filter_frame, text="❌ Сбросить фильтр", command=self.reset_filter).grid(row=0, column=5, padx=5, pady=5)
        
        # === Таблица с тренировками ===
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Скроллбары
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Заголовки колонок
        self.tree.heading("date", text="📅 Дата")
        self.tree.heading("type", text="🏃 Тип тренировки")
        self.tree.heading("duration", text="⏱ Длительность (мин)")
        
        # Ширина колонок
        self.tree.column("date", width=150, anchor=tk.CENTER)
        self.tree.column("type", width=200, anchor=tk.CENTER)
        self.tree.column("duration", width=150, anchor=tk.CENTER)
        
        # Размещение
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # === Фрейм статистики ===
        stats_frame = ttk.LabelFrame(self.root, text="Статистика", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="Всего тренировок: 0 | Общая длительность: 0 мин")
        self.stats_label.pack(anchor=tk.W)
        
        # === Фрейм кнопок управления ===
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="💾 Сохранить в JSON", command=self.save_to_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="📂 Загрузить из JSON", command=self.load_from_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🗑 Удалить выбранную", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="✏️ Редактировать", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        
        # Привязка двойного клика для редактирования
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())
    
    def validate_date(self, date_str):
        """Проверка корректности даты в формате ДД.ММ.ГГГГ"""
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_str):
        """Проверка корректности длительности (положительное число)"""
        try:
            duration = int(duration_str)
            return duration > 0
        except ValueError:
            return False
    
    def add_training(self):
        """Добавление новой тренировки"""
        date = self.date_entry.get().strip()
        workout_type = self.type_combobox.get()
        duration = self.duration_entry.get().strip()
        
        # Валидация даты
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ\nПример: 25.12.2024")
            return
        
        # Валидация длительности
        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным целым числом!")
            return
        
        # Добавление в список
        training = {
            "date": date,
            "type": workout_type,
            "duration": int(duration)
        }
        self.trainings.append(training)
        
        # Очистка полей
        self.duration_entry.delete(0, tk.END)
        
        # Обновление таблицы
        self.refresh_table()
        self.update_stats()
        
        messagebox.showinfo("Успех", "Тренировка добавлена!")
    
    def refresh_table(self, data=None):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Используем переданные данные или все тренировки
        display_data = data if data is not None else self.trainings
        
        # Заполнение таблицы
        for training in display_data:
            self.tree.insert("", tk.END, values=(
                training["date"],
                training["type"],
                training["duration"]
            ))
    
    def apply_filter(self):
        """Применение фильтров"""
        filter_type = self.filter_type.get()
        filter_date = self.filter_date.get().strip()
        
        filtered = self.trainings.copy()
        
        # Фильтр по типу
        if filter_type != "Все":
            filtered = [t for t in filtered if t["type"] == filter_type]
        
        # Фильтр по дате
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты для фильтра! Используйте ДД.ММ.ГГГГ")
                return
            filtered = [t for t in filtered if t["date"] == filter_date]
        
        self.refresh_table(filtered)
        self.update_stats(filtered)
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_type.set("Все")
        self.filter_date.delete(0, tk.END)
        self.refresh_table()
        self.update_stats()
    
    def delete_selected(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите тренировку для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную тренировку?"):
            # Получаем значения выбранной строки
            item = self.tree.item(selected[0])
            values = item["values"]
            
            # Удаляем из списка
            self.trainings = [
                t for t in self.trainings 
                if not (t["date"] == values[0] and t["type"] == values[1] and t["duration"] == values[2])
            ]
            
            self.refresh_table()
            self.update_stats()
    
    def edit_selected(self):
        """Редактирование выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите тренировку для редактирования!")
            return
        
        item = self.tree.item(selected[0])
        values = item["values"]
        
        # Находим индекс в списке
        for i, t in enumerate(self.trainings):
            if t["date"] == values[0] and t["type"] == values[1] and t["duration"] == values[2]:
                # Заполняем поля для редактирования
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, t["date"])
                self.type_combobox.set(t["type"])
                self.duration_entry.delete(0, tk.END)
                self.duration_entry.insert(0, str(t["duration"]))
                
                # Удаляем старую запись
                self.trainings.pop(i)
                self.refresh_table()
                self.update_stats()
                break
    
    def update_stats(self, data=None):
        """Обновление статистики"""
        display_data = data if data is not None else self.trainings
        total = len(display_data)
        total_duration = sum(t["duration"] for t in display_data)
        
        self.stats_label.config(
            text=f"Всего тренировок: {total} | Общая длительность: {total_duration} мин"
        )
    
    def save_to_json(self):
        """Сохранение данных в JSON файл"""
        if not self.trainings:
            messagebox.showwarning("Внимание", "Нет данных для сохранения!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")],
            title="Сохранить тренировки"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.trainings, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", f"Данные сохранены в:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def load_from_json(self):
        """Загрузка данных из JSON файла"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")],
            title="Загрузить тренировки"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                
                # Валидация загруженных данных
                valid = True
                for t in loaded:
                    if not all(k in t for k in ("date", "type", "duration")):
                        valid = False
                        break
                    if not self.validate_date(t["date"]):
                        valid = False
                        break
                    if not isinstance(t["duration"], int) or t["duration"] <= 0:
                        valid = False
                        break
                
                if not valid:
                    messagebox.showerror("Ошибка", "Файл содержит некорректные данные!")
                    return
                
                self.trainings = loaded
                self.refresh_table()
                self.update_stats()
                messagebox.showinfo("Успех", f"Загружено {len(loaded)} тренировок!")
                
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", "Неверный формат JSON файла!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def load_default_data(self):
        """Загрузка демо-данных при первом запуске"""
        # Можно раскомментировать для тестовых данных:
        """
        self.trainings = [
            {"date": "20.05.2024", "type": "Бег", "duration": 30},
            {"date": "21.05.2024", "type": "Силовая тренировка", "duration": 45},
            {"date": "22.05.2024", "type": "Йога", "duration": 60},
            {"date": "23.05.2024", "type": "Бег", "duration": 25},
        ]
        self.refresh_table()
        self.update_stats()
        """


def main():
    root = tk.Tk()
    
    # Установка стиля
    style = ttk.Style()
    style.theme_use('clam')  # или 'alt', 'default', 'classic'
    
    app = TrainingPlanner(root)
    root.mainloop()


if __name__ == "__main__":
    main()