# currency_converter.py

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter - Конвертер валют")
        self.root.geometry("850x650")
        self.root.resizable(True, True)
        
        # API configuration
        self.api_key = ""  # Вставьте ваш API ключ здесь
        self.api_url = "https://v6.exchangerate-api.com/v6/{}/latest/{}"
        
        # Data storage
        self.history = []
        self.history_file = "conversion_history.json"
        self.currencies = []
        
        # Load existing history
        self.load_history()
        
        # Fetch available currencies
        self.fetch_currencies()
        
        # Setup UI
        self.setup_ui()
    
    def fetch_currencies(self):
        """Fetch available currencies from API"""
        if not self.api_key:
            # Default currencies if no API key
            self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "KZT", "UAH", "BYN"]
            return
            
        try:
            url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/codes"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('result') == 'success':
                self.currencies = [code[0] for code in data.get('supported_codes', [])]
                self.currencies.sort()
            else:
                # Fallback currencies
                self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "KZT", "UAH", "BYN"]
        except Exception as e:
            print(f"Error fetching currencies: {e}")
            self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "KZT", "UAH", "BYN"]
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ==================== API KEY FRAME ====================
        api_frame = ttk.LabelFrame(main_frame, text="API Настройки", padding="10")
        api_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, padx=5, pady=5)
        self.api_key_var = tk.StringVar(value=self.api_key)
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=40, show="*")
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.save_api_button = ttk.Button(api_frame, text="Сохранить API Key", command=self.save_api_key)
        self.save_api_button.grid(row=0, column=2, padx=5, pady=5)
        
        # ==================== CONVERSION FRAME ====================
        conv_frame = ttk.LabelFrame(main_frame, text="Конвертация валют", padding="10")
        conv_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # From currency
        ttk.Label(conv_frame, text="Из валюты:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.from_currency_var = tk.StringVar(value="USD")
        self.from_combo = ttk.Combobox(conv_frame, textvariable=self.from_currency_var, 
                                        values=self.currencies, width=15)
        self.from_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # To currency
        ttk.Label(conv_frame, text="В валюту:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.to_currency_var = tk.StringVar(value="EUR")
        self.to_combo = ttk.Combobox(conv_frame, textvariable=self.to_currency_var, 
                                      values=self.currencies, width=15)
        self.to_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Amount
        ttk.Label(conv_frame, text="Сумма:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(conv_frame, textvariable=self.amount_var, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Convert button
        self.convert_button = ttk.Button(conv_frame, text="Конвертировать", command=self.convert_currency)
        self.convert_button.grid(row=1, column=2, columnspan=2, pady=10)
        
        # Result
        ttk.Label(conv_frame, text="Результат:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.result_var = tk.StringVar()
        self.result_entry = ttk.Entry(conv_frame, textvariable=self.result_var, 
                                       font=("Arial", 12, "bold"), width=40, state="readonly")
        self.result_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Rate display
        self.rate_var = tk.StringVar()
        self.rate_label = ttk.Label(conv_frame, textvariable=self.rate_var, foreground="blue")
        self.rate_label.grid(row=3, column=0, columnspan=4, pady=5)
        
        # ==================== HISTORY FRAME ====================
        history_frame = ttk.LabelFrame(main_frame, text="История конвертаций", padding="10")
        history_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create Treeview
        columns = ("Дата", "Сумма", "Из", "В", "Результат", "Курс")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        # Define headings
        self.tree.heading("Дата", text="Дата и время")
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Из", text="Из валюты")
        self.tree.heading("В", text="В валюту")
        self.tree.heading("Результат", text="Результат")
        self.tree.heading("Курс", text="Курс")
        
        # Define columns
        self.tree.column("Дата", width=150)
        self.tree.column("Сумма", width=100)
        self.tree.column("Из", width=80)
        self.tree.column("В", width=80)
        self.tree.column("Результат", width=150)
        self.tree.column("Курс", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout for table
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # ==================== BUTTONS FRAME ====================
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Clear history button
        self.clear_button = ttk.Button(buttons_frame, text="Очистить историю", command=self.clear_history)
        self.clear_button.grid(row=0, column=0, padx=5)
        
        # Save button
        self.save_button = ttk.Button(buttons_frame, text="Сохранить историю", command=self.save_history)
        self.save_button.grid(row=0, column=1, padx=5)
        
        # Load button
        self.load_button = ttk.Button(buttons_frame, text="Загрузить историю", command=self.load_history)
        self.load_button.grid(row=0, column=2, padx=5)
        
        # Refresh currencies button
        self.refresh_button = ttk.Button(buttons_frame, text="Обновить список валют", command=self.refresh_currencies)
        self.refresh_button.grid(row=0, column=3, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        conv_frame.columnconfigure(3, weight=1)
    
    def save_api_key(self):
        """Save API key"""
        self.api_key = self.api_key_var.get().strip()
        if self.api_key:
            # Optionally save to file
            try:
                with open("api_key.txt", "w") as f:
                    f.write(self.api_key)
                messagebox.showinfo("Успех", "API ключ сохранен")
                self.refresh_currencies()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить ключ: {e}")
        else:
            messagebox.showwarning("Предупреждение", "API ключ не введен")
    
    def refresh_currencies(self):
        """Refresh currency list"""
        self.fetch_currencies()
        self.from_combo['values'] = self.currencies
        self.to_combo['values'] = self.currencies
        messagebox.showinfo("Успех", f"Загружено {len(self.currencies)} валют")
    
    def get_exchange_rate(self, from_currency, to_currency):
        """Get exchange rate from API"""
        if not self.api_key:
            # Mock rates for demo
            mock_rates = {
                ("USD", "EUR"): 0.92,
                ("EUR", "USD"): 1.09,
                ("USD", "RUB"): 91.50,
                ("RUB", "USD"): 0.011,
                ("EUR", "RUB"): 99.50,
                ("RUB", "EUR"): 0.010,
            }
            return mock_rates.get((from_currency, to_currency), 1.0)
        
        try:
            url = self.api_url.format(self.api_key, from_currency)
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('result') == 'success':
                rate = data['conversion_rates'].get(to_currency)
                if rate:
                    return rate
                else:
                    messagebox.showerror("Ошибка", f"Валюта {to_currency} не найдена")
                    return None
            else:
                messagebox.showerror("Ошибка", f"API ошибка: {data.get('error-type', 'Unknown')}")
                return None
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к API: {e}")
            return None
    
    def convert_currency(self):
        """Convert currency"""
        # Validate amount
        amount_str = self.amount_var.get().strip()
        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму для конвертации")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом")
            return
        
        # Get currencies
        from_currency = self.from_currency_var.get()
        to_currency = self.to_currency_var.get()
        
        if not from_currency or not to_currency:
            messagebox.showerror("Ошибка", "Выберите валюты")
            return
        
        # Get exchange rate
        rate = self.get_exchange_rate(from_currency, to_currency)
        if rate is None:
            return
        
        # Calculate result
        result = amount * rate
        
        # Display result
        result_str = f"{result:.2f} {to_currency}"
        self.result_var.set(result_str)
        self.rate_var.set(f"Курс: 1 {from_currency} = {rate:.4f} {to_currency}")
        
        # Add to history
        self.add_to_history(amount, from_currency, to_currency, result, rate)
    
    def add_to_history(self, amount, from_currency, to_currency, result, rate):
        """Add conversion to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        record = {
            "timestamp": timestamp,
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "result": result,
            "rate": rate
        }
        
        self.history.insert(0, record)  # Add to beginning
        self.refresh_history_table()
        self.save_history()
    
    def refresh_history_table(self):
        """Refresh the history table"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add history items
        for record in self.history:
            self.tree.insert("", tk.END, values=(
                record['timestamp'],
                f"{record['amount']:.2f}",
                record['from_currency'],
                record['to_currency'],
                f"{record['result']:.2f}",
                f"{record['rate']:.4f}"
            ))
    
    def clear_history(self):
        """Clear all history"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.refresh_history_table()
            self.save_history()
            messagebox.showinfo("Успех", "История очищена")
    
    def save_history(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")
            return False
    
    def load_history(self):
        """Load history from JSON file"""
        if not os.path.exists(self.history_file):
            self.history = []
            return
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
            self.refresh_history_table()
            messagebox.showinfo("Успех", f"Загружено {len(self.history)} операций из истории")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {str(e)}")
            self.history = []
            return False

def main():
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()