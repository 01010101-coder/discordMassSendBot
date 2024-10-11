import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, filedialog
import json
import asyncio
import threading
from discord.ext import commands


# Создание GUI приложения
class DiscordSelfBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord SelfBot Messenger")

        # Центрирование всех виджетов
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame = tk.Frame(root)
        main_frame.grid(row=0, column=0)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Кнопка справки в правом верхнем углу
        help_button = tk.Button(self.root, text="Справка", command=self.show_help)
        help_button.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

        # Токен
        tk.Label(main_frame, text="Токен").grid(row=0, column=0, sticky="ew", pady=5)
        self.token_entry = tk.Entry(main_frame, width=50)
        self.token_entry.grid(row=0, column=1, columnspan=2, pady=5)

        # Задержка
        tk.Label(main_frame, text="Задержка (в секундах)").grid(row=1, column=0, sticky="ew", pady=5)
        self.delay_entry = tk.Entry(main_frame, width=10)
        self.delay_entry.grid(row=1, column=1, pady=5)

        # Ввод сообщения вручную
        tk.Label(main_frame, text="Сообщение").grid(row=2, column=0, sticky="ew", pady=5)
        self.message_entry = tk.Text(main_frame, width=50, height=5)
        self.message_entry.grid(row=2, column=1, columnspan=2, pady=5)

        # Добавление ID вручную
        tk.Label(main_frame, text="Добавить ID пользователя").grid(row=3, column=0, sticky="ew", pady=5)
        self.add_id_entry = tk.Entry(main_frame, width=30)
        self.add_id_entry.grid(row=3, column=1, pady=5)

        tk.Label(main_frame, text="Имя пользователя").grid(row=3, column=2, sticky="ew", pady=5)
        self.add_name_entry = tk.Entry(main_frame, width=20)
        self.add_name_entry.grid(row=3, column=3, pady=5)

        tk.Button(main_frame, text="Добавить ID", command=self.add_id).grid(row=3, column=4, pady=5)

        # Таблица с ID пользователей
        self.id_table = ttk.Treeview(main_frame, columns=("ID", "Name"), show="headings")
        self.id_table.heading("ID", text="ID пользователя")
        self.id_table.heading("Name", text="Имя пользователя")
        self.id_table.grid(row=4, column=0, columnspan=5, pady=5)

        # Кнопка запуска
        tk.Button(main_frame, text="Запустить", command=self.run_bot).grid(row=5, column=0, columnspan=5, pady=10)

        # Консоль для вывода сообщений
        tk.Label(main_frame, text="Консоль").grid(row=6, column=0, columnspan=5, pady=5)
        self.console_output = scrolledtext.ScrolledText(main_frame, width=60, height=10, state='disabled')
        self.console_output.grid(row=7, column=0, columnspan=5, pady=5)

        # Кнопки для сохранения и загрузки конфигов
        tk.Button(main_frame, text="Сохранить конфиг", command=self.save_config).grid(row=8, column=1, pady=5)
        tk.Button(main_frame, text="Загрузить конфиг", command=self.load_config).grid(row=8, column=2, pady=5)

        # Переменные для хранения данных
        self.id_list = []
        self.message = ""

        # Discord Bot setup
        self.bot = commands.Bot(command_prefix='/', self_bot=True)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        @self.bot.event
        async def on_ready():
            self.print_to_console("Бот успешно запущен и готов к работе.")
            await self.send_messages()

    def add_id(self):
        user_id = self.add_id_entry.get().strip()
        user_name = self.add_name_entry.get().strip()
        if user_id and user_id not in [uid for uid, _ in self.id_list]:
            self.id_list.append((user_id, user_name))
            self.update_id_table()
            self.add_id_entry.delete(0, tk.END)
            self.add_name_entry.delete(0, tk.END)

    def update_id_table(self):
        for row in self.id_table.get_children():
            self.id_table.delete(row)
        for user_id, user_name in self.id_list:
            self.id_table.insert("", "end", values=(user_id, user_name))

    def run_bot(self):
        token = self.token_entry.get().strip()
        delay = self.delay_entry.get().strip()
        self.message = self.message_entry.get("1.0", tk.END).strip()

        if not token:
            messagebox.showerror("Ошибка", "Пожалуйста, введите токен.")
            return
        if not delay.isdigit():
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректную задержку.")
            return
        if not self.id_list:
            messagebox.showerror("Ошибка", "Пожалуйста, добавьте хотя бы один ID пользователя.")
            return
        if not self.message:
            messagebox.showerror("Ошибка", "Пожалуйста, введите сообщение.")
            return

        self.delay = int(delay)

        # Создание нового экземпляра бота перед каждым запуском
        self.bot = commands.Bot(command_prefix='/', self_bot=True)
        self.setup_bot_events()

        threading.Thread(target=self.run_bot_in_thread, args=(token,), daemon=True).start()

    def setup_bot_events(self):
        @self.bot.event
        async def on_ready():
            self.print_to_console("Бот успешно запущен и готов к работе.")
            await self.send_messages()

    async def start_bot(self, token):
        try:
            await self.bot.start(token)
        except Exception as e:
            self.print_to_console(f"Ошибка при запуске бота: {e}")
        finally:
            await self.bot.close()

    async def send_messages(self):
        for user_id, user_name in self.id_list:
            try:
                user = await self.bot.fetch_user(int(user_id))
                if user:
                    personalized_message = self.message.replace("{name}", user_name)
                    await user.send(personalized_message)
                    self.print_to_console(f"Сообщение отправлено пользователю {user_name} ({user_id})")
                await asyncio.sleep(self.delay)
            except Exception as e:
                self.print_to_console(f"Ошибка при отправке сообщения пользователю {user_name} ({user_id}): {e}")

        await self.bot.close()
        messagebox.showinfo("Готово", "Сообщения отправлены!")

    def print_to_console(self, message):
        self.console_output.config(state='normal')
        self.console_output.insert(tk.END, message + '\n')
        self.console_output.config(state='disabled')
        self.console_output.yview(tk.END)

    def save_config(self):
        config = {
            "token": self.token_entry.get().strip(),
            "delay": self.delay_entry.get().strip(),
            "message": self.message_entry.get("1.0", tk.END).strip(),
            "users": [{"id": user_id, "name": user_name} for user_id, user_name in self.id_list]
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as config_file:
                json.dump(config, config_file, indent=4)
            self.print_to_console(f"Конфиг сохранен: {file_path}")

    def load_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as config_file:
                config = json.load(config_file)

            self.token_entry.delete(0, tk.END)
            self.token_entry.insert(0, config.get("token", ""))
            self.delay_entry.delete(0, tk.END)
            self.delay_entry.insert(0, config.get("delay", ""))
            self.message_entry.delete("1.0", tk.END)
            self.message_entry.insert("1.0", config.get("message", ""))

            self.id_list = [(user.get("id"), user.get("name")) for user in config.get("users", [])]
            self.update_id_table()

            self.print_to_console(f"Конфиг загружен: {file_path}")

    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Справка")
        help_window.geometry("500x500")

        try:
            with open("help.txt", "r", encoding="utf-8") as help_file:
                help_text = help_file.read()
        except FileNotFoundError:
            help_text = "Файл справки не найден."

        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=10, pady=10)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state='disabled')
        help_text_widget.pack(expand=True, fill='both')

    def run_bot_in_thread(self, token):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_bot(token))


if __name__ == "__main__":
    root = tk.Tk()
    app = DiscordSelfBotApp(root)
    root.mainloop()
