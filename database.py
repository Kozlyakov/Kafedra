import tkinter as tk
from tkinter import messagebox
import sqlite3
import re
from openpyxl import Workbook
import io
from tkinter import filedialog
from tkinter.simpledialog import askstring

# Создание базы данных и таблиц
def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Таблица администраторов (логины, пароли, роли)
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
           username TEXT NOT NULL,
           password TEXT NOT NULL,
           role TEXT,
           id INTEGER PRIMARY KEY AUTOINCREMENT)''')

    # Таблица преподавателей (логины, пароли, ID и информация)
    cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            subject TEXT,
            education TEXT,
            education_level TEXT,
            retraining TEXT,
            qualification_improvement TEXT,
            labor_start_date TEXT,
            teaching_start_date TEXT,
            institution_start_date TEXT,
            phone_number TEXT,
            birth_date TEXT,
            address TEXT,
            qualification_category TEXT,
            attestation_date TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS schedule (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               teacher_id INTEGER,
               day_of_week TEXT,
               time_slot TEXT,
               subject TEXT,
               cabinet TEXT,
               FOREIGN KEY (teacher_id) REFERENCES teachers (id))''')

    # Добавим несколько тестовых данных
    #cursor.execute("INSERT INTO admins (username, password, role) VALUES ('1', '1', 'developer')")
    #cursor.execute("INSERT INTO admins (username, password, role) VALUES ('2', '2', 'rector')")

    #cursor.execute('''
    #INSERT OR IGNORE INTO teachers (username, password, teacher_id, fio, phone, birth_date, education, subject, retraining, qualification, start_work_date, start_teaching_date, work_start_date)
    #VALUES
    #('3', '3', 'T001', 'Иванов Иван Иванович', '1234567890', '01.01.1980', 'Высшее образование', 'Математика', 'Нет', 'Повышение квалификации', '01.09.2005', '01.09.2010', '01.09.2005')
    #''')

    conn.commit()
    conn.close()

# Основной класс приложения
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.teacher_combobox = None
        self.root = self
        self.root.config(bg="#ADD8E6")
        self.connection = sqlite3.connect('users.db')  # Установите соединение
        self.cursor = self.connection.cursor()
        self.title("Система 'Кафедра'")
        self.geometry("420x400")
        self.role = None
        self.username = None
        self.current_user_id = None

        create_db()  # Создаем базу данных

        self.create_auth_window()

    # Окно авторизации
    def create_auth_window(self):
        self.clear_window()

        role_label = tk.Label(self, text="Выберите роль:", bg="#ADD8E6")
        role_label.pack()
        tk.Button(self, text="Администратор", command=self.start_auth, bg="#4682B4",
                  fg="black").pack(pady=20)
        tk.Button(self, text="Преподаватель", command=self.start_pol, bg="#4682B4",
                  fg="black").pack(pady=20)
        tk.Button(self, text="Выйти", command=self.quit, bg="red",
                  fg="black").pack(pady=20)


    def start_auth(self):
        self.clear_window()

        self.username_label = tk.Label(self, text="Логин:", bg="#ADD8E6")
        self.username_label.pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        self.password_label = tk.Label(self, text="Пароль:", bg="#ADD8E6")
        self.password_label.pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Войти", command=self.check_login, bg="#4682B4",
                  fg="black").pack(pady=20)
        tk.Button(self, text="Выйти", command=self.create_auth_window, bg="red",
                  fg="black").pack(pady=20)

    def start_pol(self):
        self.clear_window()

        self.username_label = tk.Label(self, text="Логин:", bg="#ADD8E6")
        self.username_label.pack()

        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        self.password_label = tk.Label(self, text="Пароль:", bg="#ADD8E6")
        self.password_label.pack()

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Войти", command=self.check_logins, bg="#4682B4",
                  fg="black").pack(pady=20)
        tk.Button(self, text="Выйти", command=self.create_auth_window, bg="red",
                  fg="black").pack(pady=20)

    # Проверка логина и пароля
    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            # Проверка логина и пароля в базе данных
            self.check_user_login(username, password)
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, "
                                           "введите логин и пароль.")

    def check_logins(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            # Проверка логина и пароля в базе данных
            self.check_user_logins(username, password)
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, "
                                           "введите логин и пароль.")

    def check_user_login(self, username, password):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE username = ? '
                       'AND password = ?', (username, password))
        admin = cursor.fetchone()
        conn.close()
        if admin:
            self.username = username
            self.role = admin[2]  # Роль (developer или rector)
            if self.role == 'developer':
                self.developer_dashboard()
            elif self.role == 'rector':
                self.rector_dashboard()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")
            
    def check_user_logins(self, username, password):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        # Проверка для преподавателей
        cursor.execute('SELECT * FROM teachers WHERE username = ? '
                       'AND password = ?', (username, password))
        teacher = cursor.fetchone()
        if teacher:
            self.username = username
            self.role = 'teacher'
            self.teacher_dashboard()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")

    def teacher_dashboard(self):
        self.clear_window()

        title = tk.Label(self, text="Панель преподавателя", bg="#ADD8E6",
                         font=("Arial", 14,))
        title.pack(pady=20)

        tk.Button(self, text="Смотреть информацию о себе",
                  command=self.teacher_information, bg="light green", fg="black").pack(pady=10)
        tk.Button(self, text="Смотреть расписание",
                  command=lambda: self.view_schedule(), bg="light green",fg="black").pack(pady=10)
        tk.Button(self, text="Выйти",
                  command=self.create_auth_window, bg="red", fg="black").pack(pady=10)

    # Панель разработчика
    def developer_dashboard(self):
        self.clear_window()

        title = tk.Label(self, text="Панель разработчика", bg="#ADD8E6", font=("Arial", 14, ))
        title.pack(pady=20)
        tk.Button(self, text="Добавить пользователя", command=self.add_user, bg="light green",fg="black").pack(pady=10)
        tk.Button(self, text="Обновить информацию о преподавателе", command=self.update_teacher,bg="light green", fg="black").pack(pady=10)
        tk.Button(self, text="Посмотреть всех преподавателей", command=self.view_teachers,bg="light green", fg="black").pack(pady=10)
        tk.Button(self, text="Расписание", command=self.add_schedule, bg="light green", fg="black").pack(pady=10)
        tk.Button(self, text="Удалить администратора", command=self.delete_user, bg="light green", fg="black").pack(pady=10)
        tk.Button(self, text="Удалить преподавателя", command=self.delete_users, bg="light green", fg="black").pack(pady=10)
        tk.Button(self, text="Выйти", command=self.create_auth_window, bg="red", fg="black").pack(pady=10)
    # Панель ректора
    def rector_dashboard(self):
        self.clear_window()

        title = tk.Label(self, text="Панель ректора", bg="#ADD8E6", font=("Arial", 14))
        title.pack(pady=20)

        tk.Button(self, text="Посмотреть всех преподавателей", command=self.view_teacher, bg="light green", fg="black").pack(pady=10)
        tk.Button(self, text="Выгрузка расписания", command=self.export_schedule, bg="light green", fg="black").pack(pady=10)
        search_teacher_label = tk.Label(self, text="Поиск преподавателя по имени", bg="#ADD8E6", font=("Arial", 12))
        search_teacher_label.pack(pady=5)

        self.search_teacher_entry = tk.Entry(self, width=30)
        self.search_teacher_entry.pack(pady=5)

        search_btn = tk.Button(self, text="Поиск", width=20, command=self.search_teacher_by_name, bg="light green", fg="black")
        search_btn.pack(pady=10)
        logout_btn = tk.Button(self, text="Выйти", command=self.create_auth_window, bg="red", fg="black")
        logout_btn.pack(pady=20)

    def teacher_information(self):
        self.clear_window()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teachers WHERE username = ?', (self.username,))
        teacher = cursor.fetchone()
        conn.close()

        info_label = tk.Label(self, text=f"ФИО: {teacher[3]}\nПредмет: {teacher[4]}\n"
                                         f"Образование: {teacher[5]}\nУровень образования: {teacher[6]}\n"
                                         f"Переподготовка: {teacher[7]}\nПовышение квалификации: {teacher[8]}\n"
                                         f"Дата начала трудовой деятельности: {teacher[9]}\nДата начала преподавания: {teacher[10]}\n"
                                         f"Дата начала работы в учебном заведении: {teacher[11]}\nНомер телефона: {teacher[12]}\n"
                                         f"Дата рождения: {teacher[13]}\nАдрес: {teacher[14]}\nКвалификационная категория: {teacher[15]}\n"
                                         f"Дата аттестации: {teacher[16]}\n", bg="#ADD8E6", font=("Arial", 12))
        info_label.pack(pady=20)

        tk.Button(self, text="Выйти", command=self.teacher_dashboard, bg="red", fg="black").pack(pady=10)

    def view_schedule(self):
        self.clear_window()
        # Получение ID преподавателя по имени
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM teachers WHERE username = ?", (self.username,))
        teacher_id = cursor.fetchone()[0]
        
        # Получаем расписание для выбранного преподавателя
        cursor.execute("SELECT day_of_week, time_slot, subject FROM schedule WHERE teacher_id = ?", (teacher_id,))
        schedule = cursor.fetchall()
        conn.close()

        schedule_label = tk.Label(self, text=f"Расписание:", bg="#ADD8E6", font=("Arial", 14))
        schedule_label.pack(pady=10)

        if schedule:
            for item in schedule:
                day_label = tk.Label(self, text=f"{item[0]} - {item[1]}: {item[2]}", bg="#ADD8E6")
                day_label.pack(fill="x", padx=10, pady=5)
        else:
            no_schedule_label = tk.Label(self, text="Расписание не задано.", bg="#ADD8E6")
            no_schedule_label.pack(pady=10)

        tk.Button(self, text="Выйти", command=self.teacher_dashboard, bg="red", fg="black").pack(pady=10)


    def add_user(self):
        self.clear_window()

        add_user_label = tk.Label(self, text="Выберите роль пользователя, которого хотите добавить:", bg="#ADD8E6")
        add_user_label.pack()

        teacher_button = tk.Button(self, text="Преподаватель", bg="light green", fg="black", command=lambda: self.add_teacher())
        teacher_button.pack()

        admin_button = tk.Button(self, text="Администратор", bg="light green", fg="black", command=lambda: self.add_admin())
        admin_button.pack()

        back_button = tk.Button(self, text="Назад", bg="red", fg="black", command=lambda: self.developer_dashboard())
        back_button.pack()

    def add_admin(self):
        for widget in self.winfo_children():
            widget.pack_forget()

        username_label = tk.Label(self, text="Логин администратора:", bg="#ADD8E6")
        username_label.pack()
        username_entry = tk.Entry(self)
        username_entry.pack()

        password_label = tk.Label(self, text="Пароль:", bg="#ADD8E6")
        password_label.pack()
        password_entry = tk.Entry(self, show="*")
        password_entry.pack()

        role_label = tk.Label(self, text="Выберите роль администратора:", bg="#ADD8E6")
        role_label.pack()

        # Выпадающий список для выбора роли
        roles = ["developer", "rector"]
        role_var = tk.StringVar()
        role_var.set(roles[0])  # Устанавливаем значение по умолчанию

        role_menu = tk.OptionMenu(self, role_var, *roles)
        role_menu.pack()

        def save_admin():
            username = username_entry.get()
            password = password_entry.get()

            # Проверка на пустые поля
            if not username or not password:
                messagebox.showerror("Ошибка", "Логин и пароль не могут быть пустыми!")
                return

            role = role_var.get()
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            cursor.execute('''
                    INSERT INTO admins (username, password, role)
                    VALUES (?, ?, ?)
                ''', (username_entry.get(), password_entry.get(), role))

            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", f"Администратор с ролью {role} добавлен")
            self.developer_dashboard()

        save_button = tk.Button(self, text="Сохранить", command=save_admin, bg="light green", fg="black")
        save_button.pack()

        back_button = tk.Button(self, text="Назад", bg="red", fg="black", command=lambda: self.add_user())
        back_button.pack()

    def add_teacher(self):
        self.clear_window()
        
        # Создаем Canvas с полосой прокрутки
        canvas = tk.Canvas(self, bg="#ADD8E6")  # Устанавливаем голубой фон для canvas
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ADD8E6")
        
        # Настроим канвас
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Размещение канваса и полосы прокрутки
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Функция обновления области прокрутки
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", on_frame_configure)

        # Поля ввода
        username_label = tk.Label(scrollable_frame, text="Логин преподавателя:", bg="#ADD8E6")
        username_label.pack(fill="x", padx=5, pady=2)
        username_entry = tk.Entry(scrollable_frame)
        username_entry.pack(fill="x", padx=5, pady=2)

        password_label = tk.Label(scrollable_frame, text="Пароль:", bg="#ADD8E6")
        password_label.pack(fill="x", padx=5, pady=2)
        password_entry = tk.Entry(scrollable_frame, show="*")
        password_entry.pack(fill="x", padx=5, pady=2)

        name_label = tk.Label(scrollable_frame, text="ФИО преподавателя:", bg="#ADD8E6")
        name_label.pack(fill="x", padx=5, pady=2)
        name_entry = tk.Entry(scrollable_frame)
        name_entry.pack(fill="x", padx=5, pady=2)

        subject_label = tk.Label(scrollable_frame, text="Предмет:", bg="#ADD8E6")
        subject_label.pack(fill="x", padx=5, pady=2)
        subject_entry = tk.Entry(scrollable_frame)
        subject_entry.pack(fill="x", padx=5, pady=2)

        education_label = tk.Label(scrollable_frame, text="Образование:", bg="#ADD8E6")
        education_label.pack(fill="x", padx=5, pady=2)
        education_entry = tk.Entry(scrollable_frame)
        education_entry.pack(fill="x", padx=5, pady=2)

        education_level_label = tk.Label(scrollable_frame, text="Уровень образования:", bg="#ADD8E6")
        education_level_label.pack(fill="x", padx=5, pady=2)
        education_level_entry = tk.Entry(scrollable_frame)
        education_level_entry.pack(fill="x", padx=5, pady=2)

        retraining_label = tk.Label(scrollable_frame, text="Переподготовка:", bg="#ADD8E6")
        retraining_label.pack(fill="x", padx=5, pady=2)
        retraining_entry = tk.Entry(scrollable_frame)
        retraining_entry.pack(fill="x", padx=5, pady=2)

        qualification_improvement_label = tk.Label(scrollable_frame, text="Повышение квалификации:", bg="#ADD8E6")
        qualification_improvement_label.pack(fill="x", padx=5, pady=2)
        qualification_improvement_entry = tk.Entry(scrollable_frame)
        qualification_improvement_entry.pack(fill="x", padx=5, pady=2)

        # Даты
        def validate_date_input(entry):
            """Функция для проверки даты в формате DD.MM.YYYY"""
            date_pattern = r"^\d{2}\.\d{2}\.\d{4}$"  # Формат даты: ДД.ММ.ГГГГ
            date = entry.get()
            if date:  # Если дата не пустая, проверяем на формат
                if not re.match(date_pattern, date):
                    messagebox.showerror("Ошибка", "Введите дату в формате DD.MM.YYYY")
                    return False
            return True

        work_start_date_label = tk.Label(scrollable_frame, text="Дата начала трудовой деятельности:", bg="#ADD8E6")
        work_start_date_label.pack(fill="x", padx=5, pady=2)
        work_start_date_entry = tk.Entry(scrollable_frame)
        work_start_date_entry.pack(fill="x", padx=5, pady=2)

        teaching_start_date_label = tk.Label(scrollable_frame, text="Дата начала преподавательской деятельности:",
                                             bg="#ADD8E6")
        teaching_start_date_label.pack(fill="x", padx=5, pady=2)
        teaching_start_date_entry = tk.Entry(scrollable_frame)
        teaching_start_date_entry.pack(fill="x", padx=5, pady=2)

        work_in_institution_start_date_label = tk.Label(scrollable_frame,
                                                        text="Дата начала работы в учебном заведении:", bg="#ADD8E6")
        work_in_institution_start_date_label.pack(fill="x", padx=5, pady=2)
        work_in_institution_start_date_entry = tk.Entry(scrollable_frame)
        work_in_institution_start_date_entry.pack(fill="x", padx=5, pady=2)

        # Проверка на ввод номера телефона
        def validate_phone_input(event, entry):
            phone = entry.get()
            if event.keysym == "BackSpace":  # Разрешаем удаление с помощью Backspace
                return None
            # Разрешаем только цифры и максимальную длину 11 символов
            if not event.char.isdigit() and event.char != "":
                return 'break'  # Запрещаем ввод, если это не цифры
            if len(phone + event.char) > 11:
                return 'break'  # Запрещаем ввод, если длина больше 11
            return None

        phone_number_label = tk.Label(scrollable_frame, text="Номер телефона:", bg="#ADD8E6")
        phone_number_label.pack(fill="x", padx=5, pady=2)
        phone_number_entry = tk.Entry(scrollable_frame)
        phone_number_entry.pack(fill="x", padx=5, pady=2)

        # Привязываем обработчик к полю ввода номера телефона
        phone_number_entry.bind("<KeyPress>", lambda event: validate_phone_input(event, phone_number_entry))

        birth_date_label = tk.Label(scrollable_frame, text="Дата рождения:", bg="#ADD8E6")
        birth_date_label.pack(fill="x", padx=5, pady=2)
        birth_date_entry = tk.Entry(scrollable_frame)
        birth_date_entry.pack(fill="x", padx=5, pady=2)

        address_label = tk.Label(scrollable_frame, text="Адрес:", bg="#ADD8E6")
        address_label.pack(fill="x", padx=5, pady=2)
        address_entry = tk.Entry(scrollable_frame)
        address_entry.pack(fill="x", padx=5, pady=2)

        qualification_category_label = tk.Label(scrollable_frame, text="Квалификационная категория:", bg="#ADD8E6")
        qualification_category_label.pack(fill="x", padx=5, pady=2)
        qualification_category_entry = tk.Entry(scrollable_frame)
        qualification_category_entry.pack(fill="x", padx=5, pady=2)

        certification_date_label = tk.Label(scrollable_frame, text="Дата аттестации:", bg="#ADD8E6")
        certification_date_label.pack(fill="x", padx=5, pady=2)
        certification_date_entry = tk.Entry(scrollable_frame)
        certification_date_entry.pack(fill="x", padx=5, pady=2)

        # Функция для сохранения данных преподавателя
        def save_teacher():
            # Проверка корректности даты
            if not (validate_date_input(work_start_date_entry) and
                    validate_date_input(teaching_start_date_entry) and
                    validate_date_input(work_in_institution_start_date_entry) and
                    validate_date_input(birth_date_entry) and
                    validate_date_input(certification_date_entry)):
                return

            username = username_entry.get()
            password = password_entry.get()
            name = name_entry.get()

            # Проверка на пустые поля
            if not username or not password or not name:
                messagebox.showerror("Ошибка", "Логин, пароль и ФИО должны быть заполнены")
                return



            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM teachers WHERE username = ?", (username,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует.")
                return
            cursor.execute(''' 
                INSERT INTO teachers (username, password, name, subject, education, education_level, retraining, 
                                        qualification_improvement, labor_start_date, teaching_start_date,
                                         institution_start_date, phone_number, birth_date, address, 
                                        qualification_category, attestation_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username_entry.get(), password_entry.get(), name_entry.get(),
                  subject_entry.get(), education_entry.get(), education_level_entry.get(),
                  retraining_entry.get(), qualification_improvement_entry.get(),
                  work_start_date_entry.get(), teaching_start_date_entry.get(),
                  work_in_institution_start_date_entry.get(), phone_number_entry.get(),
                  birth_date_entry.get(), address_entry.get(),
                  qualification_category_entry.get(), certification_date_entry.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Преподаватель добавлен")
            self.developer_dashboard()
        save_button = tk.Button(scrollable_frame, text="Сохранить", command=save_teacher, bg="light green", fg="black")
        save_button.pack(pady=10)
        back_button = tk.Button(scrollable_frame, text="Назад", bg="red", fg="black", command=lambda: self.add_user())
        back_button.pack(pady=10)

    def update_teacher(self):
        for widget in self.winfo_children():
            widget.destroy()

        # Создаем Canvas и Scrollbar
        canvas = tk.Canvas(self, bg="#ADD8E6")  # Устанавливаем голубой фон для canvas
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ADD8E6")

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        search_label = tk.Label(scrollable_frame, text="Поиск преподавателя по имени:", bg="#ADD8E6", fg="black")
        search_label.pack(fill="x", pady=2)
        search_entry = tk.Entry(scrollable_frame)
        search_entry.pack(fill="x", padx=20, pady=2)
        # Функция для поиска преподавателя в базе данных по имени


        def search_teacher():
            name_to_search = search_entry.get()

            if not name_to_search:
                messagebox.showerror("Ошибка", "Введите имя преподавателя для поиска")
                return

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM teachers WHERE name = ?", (name_to_search,))
            teacher = cursor.fetchone()
            conn.close()

            if teacher:
                # Заполняем поля данными найденного преподавателя
                username_entry.delete(0, tk.END)
                username_entry.insert(0, teacher[1])

                password_entry.delete(0, tk.END)
                password_entry.insert(0, teacher[2])

                full_name_entry.delete(0, tk.END)
                full_name_entry.insert(0, teacher[3])

                subject_entry.delete(0, tk.END)
                subject_entry.insert(0, teacher[4])

                education_entry.delete(0, tk.END)
                education_entry.insert(0, teacher[5])

                education_level_entry.delete(0, tk.END)
                education_level_entry.insert(0, teacher[6])

                retraining_entry.delete(0, tk.END)
                retraining_entry.insert(0, teacher[7])
                qualification_improvement_entry.delete(0, tk.END)
                qualification_improvement_entry.insert(0, teacher[8])

                phone_number_entry.delete(0, tk.END)
                phone_number_entry.insert(0, teacher[12])

                work_start_date_entry.delete(0, tk.END)
                work_start_date_entry.insert(0, teacher[9])

                teaching_start_date_entry.delete(0, tk.END)
                teaching_start_date_entry.insert(0, teacher[10])

                work_in_institution_start_date_entry.delete(0, tk.END)
                work_in_institution_start_date_entry.insert(0, teacher[11])

                birth_date_entry.delete(0, tk.END)
                birth_date_entry.insert(0, teacher[13])

                address_entry.delete(0, tk.END)
                address_entry.insert(0, teacher[14])

                qualification_category_entry.delete(0, tk.END)
                qualification_category_entry.insert(0, teacher[15])

                certification_date_entry.delete(0, tk.END)
                certification_date_entry.insert(0, teacher[16])
            else:
                messagebox.showerror("Ошибка", "Преподаватель не найден")

        # Кнопка для поиска преподавателя
        search_button = tk.Button(scrollable_frame, text="Найти преподавателя", command=search_teacher, bg="light blue", fg="black")
        search_button.pack(pady=10)

        # Поля ввода для редактирования данных
        username_label = tk.Label(scrollable_frame, text="Логин преподавателя:", bg="#ADD8E6", fg="black")
        username_label.pack(fill="x", pady=5)
        username_entry = tk.Entry(scrollable_frame)
        username_entry.pack(fill="x", padx=50, pady=5)

        password_label = tk.Label(scrollable_frame, text="Пароль:", bg="#ADD8E6", fg="black")
        password_label.pack(fill="x", pady=5)
        password_entry = tk.Entry(scrollable_frame, show="*")
        password_entry.pack(fill="x", padx=50, pady=5)

        full_name_label = tk.Label(scrollable_frame, text="ФИО преподавателя:", bg="#ADD8E6", fg="black")
        full_name_label.pack(fill="x", pady=5)
        full_name_entry = tk.Entry(scrollable_frame)
        full_name_entry.pack(fill="x", padx=50, pady=5)

        subject_label = tk.Label(scrollable_frame, text="Предмет:", bg="#ADD8E6")
        subject_label.pack(fill="x", pady=5)
        subject_entry = tk.Entry(scrollable_frame)
        subject_entry.pack(fill="x", padx=50, pady=5)

        education_label = tk.Label(scrollable_frame, text="Образование:", bg="#ADD8E6")
        education_label.pack(fill="x", pady=5)
        education_entry = tk.Entry(scrollable_frame)
        education_entry.pack(fill="x", padx=50, pady=5)

        education_level_label = tk.Label(scrollable_frame, text="Уровень образования:", bg="#ADD8E6")
        education_level_label.pack(fill="x", pady=5)
        education_level_entry = tk.Entry(scrollable_frame)
        education_level_entry.pack(fill="x", padx=50, pady=5)

        retraining_label = tk.Label(scrollable_frame, text="Переподготовка:", bg="#ADD8E6")
        retraining_label.pack(fill="x", pady=5)
        retraining_entry = tk.Entry(scrollable_frame)
        retraining_entry.pack(fill="x", padx=50, pady=5)

        qualification_improvement_label = tk.Label(scrollable_frame, text="Повышение квалификации:", bg="#ADD8E6")
        qualification_improvement_label.pack(fill="x", pady=5)
        qualification_improvement_entry = tk.Entry(scrollable_frame)
        qualification_improvement_entry.pack(fill="x", padx=50, pady=5)

        # Проверка на ввод номера телефона
        def validate_phone_input(event, entry):
            phone = entry.get()
            # Разрешаем только цифры и максимальную длину 11 символов
            if event.keysym == "BackSpace":  # Разрешаем удаление с помощью Backspace
                return None
            if not event.char.isdigit() and event.char != "":
                return 'break'  # Запрещаем ввод, если это не цифры
            if len(phone + event.char) > 11:
                return 'break'  # Запрещаем ввод, если длина больше 11
            return None  # Разрешаем ввод

        phone_number_label = tk.Label(scrollable_frame, text="Номер телефона:", bg="#ADD8E6", fg="black")
        phone_number_label.pack(fill="x", pady=5)
        phone_number_entry = tk.Entry(scrollable_frame)
        phone_number_entry.pack(fill="x", padx=50, pady=5)

        # Привязываем обработчик к полю ввода номера телефона
        phone_number_entry.bind("<KeyPress>", lambda event: validate_phone_input(event, phone_number_entry))
        # Даты
        def validate_date_input(entry):
            """Функция для проверки даты в формате DD.MM.YYYY"""
            date_pattern = r"^\d{2}\.\d{2}\.\d{4}$"  # Формат даты: ДД.ММ.ГГГГ
            date = entry.get()
            if date:  # Если дата не пустая, проверяем на формат
                if not re.match(date_pattern, date):
                    messagebox.showerror("Ошибка", "Введите дату в формате DD.MM.YYYY")
                    return False
            return True
        work_start_date_label = tk.Label(scrollable_frame, text="Дата начала трудовой деятельности:", bg="#ADD8E6", fg="black")
        work_start_date_label.pack(fill="x", pady=5)
        work_start_date_entry = tk.Entry(scrollable_frame)
        work_start_date_entry.pack(fill="x", padx=50, pady=5)

        teaching_start_date_label = tk.Label(scrollable_frame, text="Дата начала преподавательской деятельности:", bg="#ADD8E6", fg="black")
        teaching_start_date_label.pack(fill="x", pady=5)
        teaching_start_date_entry = tk.Entry(scrollable_frame)
        teaching_start_date_entry.pack(fill="x", padx=50, pady=5)

        work_in_institution_start_date_label = tk.Label(scrollable_frame, text="Дата начала работы в учебном заведении:", bg="#ADD8E6", fg="black")
        work_in_institution_start_date_label.pack(fill="x", pady=5)
        work_in_institution_start_date_entry = tk.Entry(scrollable_frame)
        work_in_institution_start_date_entry.pack(fill="x", padx=50, pady=5)

        birth_date_label = tk.Label(scrollable_frame, text="Дата рождения:", bg="#ADD8E6", fg="black")
        birth_date_label.pack(fill="x", pady=5)
        birth_date_entry = tk.Entry(scrollable_frame)
        birth_date_entry.pack(fill="x", padx=50, pady=5)

        address_label = tk.Label(scrollable_frame, text="Адрес:", bg="#ADD8E6", fg="black")
        address_label.pack(fill="x", pady=5)
        address_entry = tk.Entry(scrollable_frame)
        address_entry.pack(fill="x", padx=50, pady=5)

        qualification_category_label = tk.Label(scrollable_frame, text="Квалификационная категория:", bg="#ADD8E6", fg="black")
        qualification_category_label.pack(fill="x", pady=5)
        qualification_category_entry = tk.Entry(scrollable_frame)
        qualification_category_entry.pack(fill="x", padx=50, pady=5)

        certification_date_label = tk.Label(scrollable_frame, text="Дата аттестации:", bg="#ADD8E6", fg="black")
        certification_date_label.pack(fill="x", pady=5)
        certification_date_entry = tk.Entry(scrollable_frame)
        certification_date_entry.pack(fill="x", padx=50, pady=5)
        # Функция для обновления данных преподавателя
        def update_teacher_data():
            # Проверка корректности даты (если они введены)
            if not (validate_date_input(work_start_date_entry) and
                    validate_date_input(teaching_start_date_entry) and
                    validate_date_input(work_in_institution_start_date_entry) and
                    validate_date_input(birth_date_entry) and
                    validate_date_input(certification_date_entry)):
                return

            username = username_entry.get()
            password = password_entry.get()
            name = full_name_entry.get()
            name_to_search = search_entry.get()
            # Проверка на пустые поля
            if not username or not password or not name:
                messagebox.showerror("Ошибка", "Логин, пароль и ФИО должны быть заполнены")
                return
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            cursor.execute(''' 
                            UPDATE teachers
                            SET username = ?, password = ?, name = ?, subject = ?, 
                                education = ?, education_level = ?, retraining = ?, 
                                qualification_improvement = ?, labor_start_date = ?, 
                                teaching_start_date = ?, institution_start_date = ?, 
                                phone_number = ?, birth_date = ?, address = ?, 
                                qualification_category = ?, attestation_date = ?
                            WHERE name = ?
                        ''', (username_entry.get(), password_entry.get(), full_name_entry.get(),
                              subject_entry.get(), education_entry.get(), education_level_entry.get(),
                              retraining_entry.get(), qualification_improvement_entry.get(),
                              work_start_date_entry.get(), teaching_start_date_entry.get(),
                              work_in_institution_start_date_entry.get(), phone_number_entry.get(),
                              birth_date_entry.get(), address_entry.get(),
                              qualification_category_entry.get(), certification_date_entry.get(),name_to_search))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Данные преподавателя обновлены")
            self.developer_dashboard()

        # Кнопки для обновления и возврата
        update_button = tk.Button(scrollable_frame, text="Обновить данные преподавателя", command=update_teacher_data,
                                  bg="light blue", fg="black")
        update_button.pack(pady=20)
        back_button = tk.Button(scrollable_frame, text="Назад", bg="red", fg="black", command= self.developer_dashboard)
        back_button.pack(pady=20)

    def delete_user(self):
        # Окно для удаления пользователя
        delete_window = tk.Toplevel(self)
        delete_window.title("Удаление администратора")

        # Поле ввода для логина пользователя, которого нужно удалить
        tk.Label(delete_window, text="Логин").grid(row=0, column=0, pady=5)
        username_entry = tk.Entry(delete_window)
        username_entry.grid(row=0, column=1, pady=5)

        # Кнопка для удаления пользователя
        def delete_user_action():
            username = username_entry.get()
            # Проверка на пустой логин
            if not username:
                messagebox.showerror("Ошибка", "Логин не может быть пустым.")
                return

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            # Проверяем, существует ли пользователь с таким логином в таблице admin_users
            cursor.execute('SELECT * FROM admins WHERE username = ?', (username,))
            existing_user = cursor.fetchone()
            if not existing_user:
                messagebox.showerror("Ошибка", "Пользователь с таким логином не найден.")
                conn.close()
                return

            try:
                # Удаление пользователя из таблицы admin_users
                cursor.execute('DELETE FROM admins WHERE username = ?', (username,))
                conn.commit()

                messagebox.showinfo("Успех", f"Пользователь {username} удален.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении пользователя: {str(e)}")
            finally:
                conn.close()

        # Кнопка для выполнения удаления
        delete_button = tk.Button(delete_window, text="Удалить", command=delete_user_action, bg="red", fg="black")
        delete_button.grid(row=1, column=0, columnspan=2, pady=10)

    def delete_users(self):
        # Окно для удаления пользователя
        delete_window = tk.Toplevel(self)
        delete_window.title("Удаление преподавателя")

        # Поле ввода для логина пользователя, которого нужно удалить
        tk.Label(delete_window, text="Логин").grid(row=0, column=0, pady=5)
        username_entry = tk.Entry(delete_window)
        username_entry.grid(row=0, column=1, pady=5)

        # Кнопка для удаления пользователя
        def delete_user_action():
            username = username_entry.get()
            # Проверка на пустой логин
            if not username:
                messagebox.showerror("Ошибка", "Логин не может быть пустым.")
                return

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            # Проверяем, существует ли пользователь с таким логином в таблице admin_users
            cursor.execute('SELECT * FROM teachers WHERE username = ?', (username,))
            existing_user = cursor.fetchone()
            if not existing_user:
                messagebox.showerror("Ошибка", "Пользователь с таким логином не найден.")
                conn.close()
                return

            try:
                # Если это преподаватель, удаляем его также из таблицы teachers
                cursor.execute('DELETE FROM teachers WHERE username = ?', (username,))
                conn.commit()

                messagebox.showinfo("Успех", f"Пользователь {username} удален.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении пользователя: {str(e)}")
            finally:
                conn.close()

        # Кнопка для выполнения удаления
        delete_button = tk.Button(delete_window, text="Удалить", command=delete_user_action, bg="red", fg="black")
        delete_button.grid(row=1, column=0, columnspan=2, pady=10)

    # Просмотр преподавателей (для разработчиков)
    def view_teachers(self):
        self.clear_window()
        logout_button = tk.Button(self.root, text="Назад", width=20, command=self.developer_dashboard, bg="red", fg="black")
        logout_button.grid(row=0, column=0, columnspan=2, pady=10)

        label = tk.Label(self.root, text="Список преподавателей", bg="#ADD8E6", font=("Arial", 14))
        label.grid(row=1, column=0, columnspan=2, pady=20)
        
        # Создаем Canvas и Scrollbar
        canvas = tk.Canvas(self.root)
        canvas.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)
        teacher_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=teacher_frame, anchor="nw")

        teachers = self.get_all_teachers()
        for teacher in teachers:
            teacher_info = (f"ФИО: {teacher[3]}\nПредмет: {teacher[4]}\nОбразование: {teacher[5]}\n"
                            f"Уровень образования: {teacher[6]}\nПереподготовка: {teacher[7]}\n"
                            f"Повышение квалификации: {teacher[8]}\nДата начала трудовой деятельности: {teacher[9]}\n"
                            f"Дата начала преподавания: {teacher[10]}\nДата начала работы в учебном заведении: {teacher[11]}\n"
                            f"Номер телефона: {teacher[12]}\nДата рождения: {teacher[13]}\nАдрес: {teacher[14]}\n"
                            f"Квалификационная категория: {teacher[15]}\nДата аттестации: {teacher[16]}\n")
            teacher_label = tk.Label(teacher_frame, text=teacher_info, font=("Arial", 12), anchor="w")
            teacher_label.grid(row=teachers.index(teacher), column=0, pady=5, sticky="w")

        teacher_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def view_teacher(self):
        self.clear_window()

        logout_button = tk.Button(self.root, text="Назад", width=20, command=self.rector_dashboard, bg="red", fg="black")
        logout_button.grid(row=0, column=0, columnspan=2, pady=10)

        label = tk.Label(self.root, text="Список преподавателей", bg="#ADD8E6", font=("Arial", 14))
        label.grid(row=1, column=0, columnspan=2, pady=20)

        # Создаем Canvas и Scrollbar
        canvas = tk.Canvas(self.root)
        canvas.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)
        teacher_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=teacher_frame, anchor="nw")

        teachers = self.get_all_teachers()
        for teacher in teachers:
            teacher_info = (f"ФИО: {teacher[3]}\nПредмет: {teacher[4]}\nОбразование: {teacher[5]}\n"
                            f"Уровень образования: {teacher[6]}\nПереподготовка: {teacher[7]}\n"
                            f"Повышение квалификации: {teacher[8]}\n"
                            f"Дата начала трудовой деятельности: {teacher[9]}\nДата начала преподавания: {teacher[10]}\n"
                            f"Дата начала работы в учебном заведении: {teacher[11]}\nНомер телефона: {teacher[12]}\n"
                            f"Дата рождения: {teacher[13]}\nАдрес: {teacher[14]}\nКвалификационная категория: {teacher[15]}\n"
                            f"Дата аттестации: {teacher[16]}\n")
            teacher_label = tk.Label(teacher_frame, text=teacher_info, font=("Arial", 12), anchor="w")
            teacher_label.grid(row=teachers.index(teacher), column=0, pady=5, sticky="w")

        teacher_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    # Поиск преподавателя по имени (для ректора)
    def search_teacher_by_name(self):
        search_name = self.search_teacher_entry.get()

        if not search_name:
            messagebox.showerror("Ошибка", "Поле не должно быть пустым.")
            return

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teachers WHERE name LIKE ?', ('%' + search_name + '%',))
        teachers = cursor.fetchall()
        conn.close()

        if teachers:
            self.clear_window()
            for teacher in teachers:
                teacher_label = tk.Label(self, text=f"ФИО: {teacher[3]}\nПредмет: {teacher[4]}\n"
                                         f"Образование: {teacher[5]}\nУровень образования: {teacher[6]}\n"
                                         f"Переподготовка: {teacher[7]}\nПовышение квалификации: {teacher[8]}\n"
                                         f"Дата начала трудовой деятельности: {teacher[9]}\nДата начала преподавания: {teacher[10]}\n"
                                         f"Дата начала работы в учебном заведении: {teacher[11]}\nНомер телефона: {teacher[12]}\n"
                                         f"Дата рождения: {teacher[13]}\nАдрес: {teacher[14]}\nКвалификационная категория: {teacher[15]}\n"
                                         f"Дата аттестации: {teacher[16]}\n", bg="#ADD8E6", font=("Arial", 12))
                teacher_label.pack(pady=5)
        else:
            messagebox.showerror("Ошибка", "Преподаватель не найден.")

        logout_button = tk.Button(self.root, text="Назад", width=20, command=self.rector_dashboard, bg="red",
                                  fg="black")
        logout_button.pack(pady=20)

    def add_schedule(self):
        self.clear_window()

        # Список преподавателей для выбора
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT teacher_id, name FROM teachers")
        teachers = cursor.fetchall()
        conn.close()

        teacher_label = tk.Label(self, text="Выберите преподавателя:", bg="#ADD8E6")
        teacher_label.pack(pady=10)

        teacher_names = [teacher[1] for teacher in teachers]
        teacher_var = tk.StringVar(self)
        teacher_var.set(teacher_names[0])  # Установим первый элемент как выбранный
        teacher_option_menu = tk.OptionMenu(self, teacher_var, *teacher_names)
        teacher_option_menu.pack(pady=5)

        day_label = tk.Label(self, text="День недели:", bg="#ADD8E6")
        day_label.pack(pady=5)
        day_entry = tk.Entry(self)
        day_entry.pack(pady=5)

        time_label = tk.Label(self, text="Время:", bg="#ADD8E6")
        time_label.pack(pady=5)
        time_entry = tk.Entry(self)
        time_entry.pack(pady=5)

        subject_label = tk.Label(self, text="Предмет:", bg="#ADD8E6")
        subject_label.pack(pady=5)
        subject_entry = tk.Entry(self)
        subject_entry.pack(pady=5)

        cabinet_label = tk.Label(self, text="Кабинет:", bg="#ADD8E6")
        cabinet_label.pack(pady=5)
        cabinet_entry = tk.Entry(self)
        cabinet_entry.pack(pady=5)

        def save_schedule():
            selected_teacher_name = teacher_var.get()
            day = day_entry.get()
            time_slot = time_entry.get()
            subject = subject_entry.get()
            cabinet = cabinet_entry.get()
            # Проверка на пустые поля
            if not day or not time_slot or not subject or not cabinet:
                messagebox.showerror("Ошибка", "Все данные должны быть заполнены")
                return

            # Получаем ID преподавателя по имени
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT teacher_id FROM teachers WHERE name = ?", (selected_teacher_name,))
            teacher_id = cursor.fetchone()[0]

            # Добавление расписания в таблицу
            cursor.execute("INSERT INTO schedule (teacher_id, day_of_week, time_slot, subject, cabinet) VALUES (?, ?, ?, ?, ?)",
                           (teacher_id, day, time_slot, subject, cabinet))
            conn.commit()
            conn.close()

            # Оповещение
            tk.messagebox.showinfo("Информация", "Расписание успешно добавлено!")
            self.developer_dashboard()

        save_button = tk.Button(self, text="Сохранить расписание", command=save_schedule, bg="#FF4500", fg="white")
        save_button.pack(pady=20)
        back_button = tk.Button(self, text="Назад", bg="red", fg="black", command=self.developer_dashboard)
        back_button.pack()

    def export_schedule(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schedule")
        schedules = cursor.fetchall()
        conn.close()

        if not schedules:
            messagebox.showwarning("Нет данных", "Нет данных для выгрузки.")
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Schedule"
        ws.append(["ID", "ID преподавателя", "День недели", "Время", "Предмет", "Кабинет"])

        for schedule in schedules:
            ws.append([schedule[0], schedule[1], schedule[2], schedule[3], schedule[4], schedule[5]])

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if filepath:
            with open(filepath, 'wb') as f:
                f.write(buf.read())
            messagebox.showinfo("Успех", "Файл успешно сохранен!")

    def get_all_teachers(self):
        # Получение всех преподавателей
        self.cursor.execute("SELECT * FROM teachers")
        return self.cursor.fetchall()

    # Очистка окна
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

# Запуск программы
if __name__ == "__main__":
    app = MainApp()  # Создаем экземпляр MainApp
    app.mainloop()