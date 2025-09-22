import os
import calendar
import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import customtkinter as ctk
import matplotlib
matplotlib.use('TkAgg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import google.generativeai as genai
from PIL import Image, ImageTk
from tkinter import ttk # Import ttk for Treeview styling if needed
from tkcalendar import DateEntry # Import DateEntry for calendar widget

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ExpenseTracker(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("AI-Powered Expense Tracker")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Make the application open in full screen mode
        self.is_fullscreen = False
        self._previous_geometry = None
        self._previous_state = None

        def enter_fullscreen():
            try:
                self._previous_geometry = self.geometry()
                self._previous_state = self.state()
            except Exception:
                self._previous_geometry = None
                self._previous_state = None
            # Use native maximized window to keep title bar (close/minimize)
            self.overrideredirect(False)
            self.attributes('-topmost', False)
            self.state('zoomed')
            self.is_fullscreen = True

        def exit_fullscreen():
            # Restore native window frame and previous size/position
            self.overrideredirect(False)
            self.attributes('-topmost', False)
            if self._previous_geometry:
                try:
                    # First restore normal state, then geometry
                    self.state('normal')
                    self.geometry(self._previous_geometry)
                except Exception:
                    pass
            # If previous state was maximized, re-maximize after restoring geometry
            if self._previous_state == 'zoomed':
                try:
                    self.state('zoomed')
                except Exception:
                    pass
            self.is_fullscreen = False

        def toggle_fullscreen(event=None):
            if self.is_fullscreen:
                exit_fullscreen()
            else:
                enter_fullscreen()

        # Bind keys to control fullscreen
        self.bind('<Escape>', lambda e: exit_fullscreen())
        self.bind('<F11>', toggle_fullscreen)

        # Expose controls for use in UI callbacks
        self.enter_fullscreen = enter_fullscreen
        self.exit_fullscreen = exit_fullscreen
        self.toggle_fullscreen = toggle_fullscreen
 
        # Start in true fullscreen
        enter_fullscreen()

        # Initialize database
        self.init_database()

        # Create UI components
        self.create_ui()

    def init_database(self):
        """Initialize SQLite database and create tables if they don't exist"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Connect to SQLite database (creates it if it doesn't exist)
            self.conn = sqlite3.connect('data/expenses.db')
            self.cursor = self.conn.cursor()
            
            # Create expenses table if it doesn't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT
                )
            ''')
            
            # Create categories table if it doesn't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')
            
            # Insert default categories if they don't exist
            default_categories = [
                ('Food & Groceries',),
                ('Transportation',),
                ('Bills & Utilities',),
                ('Entertainment',),
                ('Shopping',),
                ('Health',),
                ('Education',),
                ('Other',)
            ]
            
            for category in default_categories:
                try:
                    self.cursor.execute("INSERT INTO categories (name) VALUES (?)", category)
                except sqlite3.IntegrityError:
                    # Category already exists, skip
                    pass
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def create_ui(self):
        """Create the main UI components"""
        # Create main frame with grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
 
        # Create tabview for different sections
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Footer
        self.footer_label = ctk.CTkLabel(self, text="Made by Amol", anchor="e")
        self.footer_label.grid(row=1, column=0, sticky="e", padx=20, pady=(0, 10))
        
        # Load icons
        self.add_expense_icon = self.load_icon("add_expense_icon.png", 24, 24)
        self.view_expenses_icon = self.load_icon("view_expenses_icon.png", 24, 24)
        self.dashboard_icon = self.load_icon("dashboard_icon.png", 24, 24)
        self.ai_insights_icon = self.load_icon("ai_insights_icon.png", 24, 24)

        # Add tabs with icons
        self.tabview.add("Add Expense")
        self.tabview.add("View Expenses")
        self.tabview.add("Dashboard")
        self.tabview.add("AI Insights")
        
        # Configure tab grid layout
        for tab in ["Add Expense", "View Expenses", "Dashboard", "AI Insights"]:
            self.tabview.tab(tab).grid_columnconfigure(0, weight=1)
            self.tabview.tab(tab).grid_rowconfigure(0, weight=1)
        
        # Set up each tab's content
        self.setup_add_expense_tab()
        self.setup_view_expenses_tab()
        self.setup_dashboard_tab()
        self.setup_ai_insights_tab()

    def setup_add_expense_tab(self):
        """Set up the Add Expense tab content"""
        tab = self.tabview.tab("Add Expense")
        
        # Create a frame for the form
        form_frame = ctk.CTkFrame(tab)
        form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=3)
        
        # Date input with calendar widget
        ctk.CTkLabel(form_frame, text="Date:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        # Create a frame to hold the DateEntry widget
        date_frame = tk.Frame(form_frame)
        date_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Create DateEntry widget with current date
        self.date_entry = DateEntry(date_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(fill='both', expand=True)
        
        # Amount input
        ctk.CTkLabel(form_frame, text="Amount:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.amount_entry = ctk.CTkEntry(form_frame)
        self.amount_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Category dropdown
        ctk.CTkLabel(form_frame, text="Category:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        # Get categories from database
        self.cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in self.cursor.fetchall()]
        
        self.category_var = ctk.StringVar(value=categories[0] if categories else "")
        self.category_dropdown = ctk.CTkOptionMenu(form_frame, variable=self.category_var, values=categories)
        self.category_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # Description input
        ctk.CTkLabel(form_frame, text="Description:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.description_entry = ctk.CTkTextbox(form_frame, height=100)
        self.description_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        # Submit button
        submit_button = ctk.CTkButton(form_frame, text="Add Expense", command=self.add_expense)
        submit_button.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

    def setup_view_expenses_tab(self):
        """Set up the View Expenses tab content"""
        tab = self.tabview.tab("View Expenses")
        
        # Create a frame for the expenses list
        list_frame = ctk.CTkFrame(tab)
        list_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        # Filter controls
        filter_frame = ctk.CTkFrame(list_frame)
        filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        filter_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # From date filter with calendar widget
        ctk.CTkLabel(filter_frame, text="From:").grid(row=0, column=0, padx=5, pady=5)
        # Create a frame to hold the DateEntry widget
        from_date_frame = tk.Frame(filter_frame)
        from_date_frame.grid(row=0, column=1, padx=5, pady=5)
        
        # Create DateEntry widget
        self.from_date_entry = DateEntry(from_date_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.from_date_entry.pack(fill='both', expand=True)
        
        # Set default "From" date to the oldest expense date if available
        oldest_expense = self.get_oldest_expense()
        if oldest_expense:
            try:
                self.from_date_entry.set_date(oldest_expense[0])
            except:
                pass # Fallback to default if date format is invalid

        # To date filter with calendar widget
        ctk.CTkLabel(filter_frame, text="To:").grid(row=0, column=2, padx=5, pady=5)
        # Create a frame to hold the DateEntry widget
        to_date_frame = tk.Frame(filter_frame)
        to_date_frame.grid(row=0, column=3, padx=5, pady=5)
        
        # Create DateEntry widget
        self.to_date_entry = DateEntry(to_date_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.to_date_entry.pack(fill='both', expand=True)
        
        # Filter button
        filter_button = ctk.CTkButton(filter_frame, text="Filter", command=self.filter_expenses)
        filter_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Expenses list (using a Treeview inside a CTkFrame)
        self.expenses_tree_frame = ctk.CTkFrame(list_frame)
        self.expenses_tree_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Create Treeview for expenses
        self.expenses_tree = ttk.Treeview(
            self.expenses_tree_frame,
            columns=("id", "date", "amount", "category", "description"),
            show="headings"
        )
        
        # Define headings
        self.expenses_tree.heading("id", text="ID")
        self.expenses_tree.heading("date", text="Date")
        self.expenses_tree.heading("amount", text="Amount (₹)")
        self.expenses_tree.heading("category", text="Category")
        self.expenses_tree.heading("description", text="Description")
        
        # Define columns
        self.expenses_tree.column("id", width=50)
        self.expenses_tree.column("date", width=100)
        self.expenses_tree.column("amount", width=100)
        self.expenses_tree.column("category", width=150)
        self.expenses_tree.column("description", width=300)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.expenses_tree_frame, orient="vertical", command=self.expenses_tree.yview)
        self.expenses_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack Treeview and scrollbar
        self.expenses_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons for edit and delete
        button_frame = ctk.CTkFrame(list_frame)
        button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        edit_button = ctk.CTkButton(button_frame, text="Edit Selected", command=self.edit_expense)
        edit_button.pack(side="left", padx=5, pady=5)
        
        delete_button = ctk.CTkButton(button_frame, text="Delete Selected", command=self.delete_expense)
        delete_button.pack(side="left", padx=5, pady=5)
        
        # Load expenses
        self.load_expenses()

    def setup_dashboard_tab(self):
        """Set up the Dashboard tab with charts"""
        tab = self.tabview.tab("Dashboard")
        
        # Create a frame for the dashboard
        dashboard_frame = ctk.CTkFrame(tab)
        dashboard_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        dashboard_frame.grid_columnconfigure(0, weight=1)
        dashboard_frame.grid_columnconfigure(1, weight=1)
        dashboard_frame.grid_rowconfigure(0, weight=0)  # Date filter row
        dashboard_frame.grid_rowconfigure(1, weight=1)  # Charts row 1
        dashboard_frame.grid_rowconfigure(2, weight=1)  # Charts row 2
        
        # Add date filter controls
        filter_frame = ctk.CTkFrame(dashboard_frame)
        filter_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        filter_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # From date filter with calendar widget
        ctk.CTkLabel(filter_frame, text="From:").grid(row=0, column=0, padx=5, pady=5)
        # Create a frame to hold the DateEntry widget
        from_date_frame = tk.Frame(filter_frame)
        from_date_frame.grid(row=0, column=1, padx=5, pady=5)
        
        # Create DateEntry widget
        self.dashboard_from_date = DateEntry(from_date_frame, width=12, background='darkblue',
                                           foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.dashboard_from_date.pack(fill='both', expand=True)
        
        # Set default "From" date to the oldest expense date if available
        oldest_expense = self.get_oldest_expense()
        if oldest_expense:
            try:
                self.dashboard_from_date.set_date(oldest_expense[0])
            except:
                pass # Fallback to default if date format is invalid

        # To date filter with calendar widget
        ctk.CTkLabel(filter_frame, text="To:").grid(row=0, column=2, padx=5, pady=5)
        # Create a frame to hold the DateEntry widget
        to_date_frame = tk.Frame(filter_frame)
        to_date_frame.grid(row=0, column=3, padx=5, pady=5)
        
        # Create DateEntry widget
        self.dashboard_to_date = DateEntry(to_date_frame, width=12, background='darkblue',
                                         foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.dashboard_to_date.pack(fill='both', expand=True)
        
        # Filter button
        filter_button = ctk.CTkButton(filter_frame, text="Apply Filter", command=self.update_charts)
        filter_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Placeholder for category pie chart
        self.category_chart_frame = ctk.CTkFrame(dashboard_frame)
        self.category_chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Placeholder for monthly bar chart
        self.monthly_chart_frame = ctk.CTkFrame(dashboard_frame)
        self.monthly_chart_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Placeholder for spending trends line chart
        self.trends_chart_frame = ctk.CTkFrame(dashboard_frame)
        self.trends_chart_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Button to refresh charts
        refresh_button = ctk.CTkButton(dashboard_frame, text="Refresh Charts", command=self.update_charts)
        refresh_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        
        # Initialize charts
        self.update_charts()

    def load_icon(self, icon_name, width, height):
        """Load an icon from the assets/icons directory."""
        try:
            image_path = os.path.join("assets", "icons", icon_name)
            original_image = Image.open(image_path)
            resized_image = original_image.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(resized_image)
        except FileNotFoundError:
            print(f"Warning: Icon file not found: {icon_name}")
            return None
        except Exception as e:
            print(f"Error loading icon {icon_name}: {e}")
            return None

    def setup_ai_insights_tab(self):
        """Set up the AI Insights tab"""
        tab = self.tabview.tab("AI Insights")
        
        # Create a frame for AI insights
        ai_frame = ctk.CTkFrame(tab)
        ai_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        ai_frame.grid_columnconfigure(0, weight=1)
        ai_frame.grid_rowconfigure(1, weight=1)
        
        # Header and generate button
        header_frame = ctk.CTkFrame(ai_frame)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header_frame, text="AI Insights powered by Gemini 1.5 Flash", 
                     font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        generate_button = ctk.CTkButton(header_frame, text="Generate Insights", command=self.generate_ai_insights)
        generate_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Insights display area
        self.insights_textbox = ctk.CTkTextbox(ai_frame, height=400, wrap="word")
        self.insights_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.insights_textbox.configure(state="disabled")

    def add_expense(self):
        """Add a new expense to the database"""
        try:
            # Get values from form
            date = self.date_entry.get_date().strftime("%Y-%m-%d")
            amount_str = self.amount_entry.get()
            category = self.category_var.get()
            description = self.description_entry.get("1.0", tk.END).strip()
            
            # Validate inputs
            if not date or not amount_str or not category:
                messagebox.showerror("Input Error", "Date, amount, and category are required fields.")
                return
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except ValueError:
                messagebox.showerror("Input Error", "Amount must be a positive number.")
                return
            
            # Insert into database
            self.cursor.execute(
                "INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)",
                (date, amount, category, description)
            )
            self.conn.commit()
            
            # Clear form
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.amount_entry.delete(0, tk.END)
            self.description_entry.delete("1.0", tk.END)
            
            messagebox.showinfo("Success", "Expense added successfully!")
            
            # Refresh expenses list
            self.load_expenses()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def load_expenses(self, where_clause="", params=()):
        """Load expenses from database into the treeview"""
        try:
            # Clear existing items
            for item in self.expenses_tree.get_children():
                self.expenses_tree.delete(item)
            
            # Construct query
            query = "SELECT id, date, amount, category, description FROM expenses"
            if where_clause:
                query += f" WHERE {where_clause}"
            query += " ORDER BY date DESC"
            
            # Execute query
            self.cursor.execute(query, params)
            
            # Insert into treeview
            for row in self.cursor.fetchall():
                row_id, date_str, amount_val, category, description = row
                amount_display = f"₹{amount_val:.2f}"
                self.expenses_tree.insert("", tk.END, values=(row_id, date_str, amount_display, category, description))
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def filter_expenses(self):
        """Filter expenses based on date range"""
        try:
            # Get dates from DateEntry widgets and format them
            from_date = self.from_date_entry.get_date().strftime("%Y-%m-%d") if self.from_date_entry.get() else ""
            to_date = self.to_date_entry.get_date().strftime("%Y-%m-%d") if self.to_date_entry.get() else ""
            
            where_clauses = []
            params = []
            
            if from_date:
                where_clauses.append("date >= ?")
                params.append(from_date)
            
            if to_date:
                where_clauses.append("date <= ?")
                params.append(to_date)
            
            where_clause = " AND ".join(where_clauses) if where_clauses else ""
            
            self.load_expenses(where_clause, tuple(params))
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def edit_expense(self):
        """Edit the selected expense"""
        selected_item = self.expenses_tree.selection()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select an expense to edit.")
            return
        
        # Get the selected expense data
        expense_id = self.expenses_tree.item(selected_item[0], 'values')[0]
        
        # Create a new window for editing
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Expense")
        edit_window.geometry("500x400")
        edit_window.grab_set()  # Make the window modal
        
        # Get expense details
        self.cursor.execute(
            "SELECT date, amount, category, description FROM expenses WHERE id = ?",
            (expense_id,)
        )
        expense = self.cursor.fetchone()
        
        if not expense:
            messagebox.showerror("Error", "Expense not found.")
            edit_window.destroy()
            return
        
        # Create form fields
        edit_window.grid_columnconfigure(1, weight=1)
        
        # Date with calendar widget
        ctk.CTkLabel(edit_window, text="Date:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        # Create a frame to hold the DateEntry widget
        date_frame = tk.Frame(edit_window)
        date_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Create DateEntry widget with expense date
        date_entry = DateEntry(date_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        date_entry.pack(fill='both', expand=True)
        
        # Set the date to the expense date
        try:
            date_entry.set_date(expense[0])
        except:
            # If there's an error with the date format, use current date
            date_entry.set_date(datetime.now().strftime("%Y-%m-%d"))
        
        # Amount
        ctk.CTkLabel(edit_window, text="Amount:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        amount_entry = ctk.CTkEntry(edit_window)
        amount_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        amount_entry.insert(0, expense[1])
        
        # Category
        ctk.CTkLabel(edit_window, text="Category:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        # Get categories from database
        self.cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in self.cursor.fetchall()]
        
        category_var = ctk.StringVar(value=expense[2])
        category_dropdown = ctk.CTkOptionMenu(edit_window, variable=category_var, values=categories)
        category_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # Description
        ctk.CTkLabel(edit_window, text="Description:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        description_entry = ctk.CTkTextbox(edit_window, height=100)
        description_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        description_entry.insert("1.0", expense[3] if expense[3] else "")
        
        # Save button
        def save_changes():
            try:
                # Get values from form
                date = date_entry.get_date().strftime("%Y-%m-%d")
                amount_str = amount_entry.get()
                category = category_var.get()
                description = description_entry.get("1.0", tk.END).strip()
                
                # Validate inputs
                if not date or not amount_str or not category:
                    messagebox.showerror("Input Error", "Date, amount, and category are required fields.")
                    return
                
                try:
                    amount = float(amount_str)
                    if amount <= 0:
                        raise ValueError("Amount must be positive")
                except ValueError:
                    messagebox.showerror("Input Error", "Amount must be a positive number.")
                    return
                
                # Update database
                self.cursor.execute(
                    "UPDATE expenses SET date = ?, amount = ?, category = ?, description = ? WHERE id = ?",
                    (date, amount, category, description, expense_id)
                )
                self.conn.commit()
                
                messagebox.showinfo("Success", "Expense updated successfully!")
                edit_window.destroy()
                
                # Refresh expenses list
                self.load_expenses()
                
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        
        save_button = ctk.CTkButton(edit_window, text="Save Changes", command=save_changes)
        save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

    def delete_expense(self):
        """Delete the selected expense"""
        selected_item = self.expenses_tree.selection()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select an expense to delete.")
            return
        
        # Get the selected expense ID
        expense_id = self.expenses_tree.item(selected_item[0], 'values')[0]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this expense?"):
            try:
                # Delete from database
                self.cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                self.conn.commit()
                
                messagebox.showinfo("Success", "Expense deleted successfully!")
                
                # Refresh expenses list
                self.load_expenses()
                
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def get_oldest_expense(self):
        """Retrieve the oldest expense from the database."""
        try:
            self.cursor.execute("SELECT date, amount, category, description FROM expenses ORDER BY date ASC LIMIT 1")
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to retrieve oldest expense: {e}")
            return None

    def _get_chart_theme_colors(self):
        """Returns a dictionary of colors for charts based on the current CTk theme."""
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            return {
                "bg_color": "#242424",
                "text_color": "#EAEAEA",
                "tick_color": "#AAB0B5",
                "grid_color": "#3A3A3A"
            }
        else:  # Light mode
            return {
                "bg_color": "#DBDBDB",
                "text_color": "#242424",
                "tick_color": "#5C5C5C",
                "grid_color": "#C2C2C2"
            }

    def update_charts(self):
        """Update all charts in the dashboard"""
        # Get date filters from DateEntry widgets
        from_date = ""
        to_date = ""
        
        if hasattr(self, 'dashboard_from_date'):
            try:
                from_date = self.dashboard_from_date.get_date().strftime("%Y-%m-%d") if self.dashboard_from_date.get() else ""
            except:
                from_date = ""
                
        if hasattr(self, 'dashboard_to_date'):
            try:
                to_date = self.dashboard_to_date.get_date().strftime("%Y-%m-%d") if self.dashboard_to_date.get() else ""
            except:
                to_date = ""
        
        # Update all charts with date filters
        self.update_category_chart(from_date, to_date)
        self.update_monthly_chart(from_date, to_date)
        self.update_trends_chart(from_date, to_date)

    def update_category_chart(self, from_date="", to_date=""):
        """Update the category pie chart with optional date filters"""
        try:
            for widget in self.category_chart_frame.winfo_children():
                widget.destroy()
            plt.close('all')
            
            # Build query with date filters
            query = "SELECT category, SUM(amount) FROM expenses"
            params = []
            where_clauses = []
            
            if from_date:
                where_clauses.append("date >= ?")
                params.append(from_date)
            
            if to_date:
                where_clauses.append("date <= ?")
                params.append(to_date)
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += " GROUP BY category HAVING SUM(amount) > 0 ORDER BY SUM(amount) DESC"
            
            self.cursor.execute(query, params)
            category_data = self.cursor.fetchall()

            if not category_data:
                ctk.CTkLabel(self.category_chart_frame, text="No expense data available.").pack(expand=True)
                return

            theme_colors = self._get_chart_theme_colors()
            
            fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
            fig.patch.set_facecolor(theme_colors["bg_color"])

            categories = [row[0] for row in category_data]
            amounts = [row[1] for row in category_data]
            
            colors = plt.cm.viridis_r([i/len(amounts) for i in range(len(amounts))])

            wedges, _, autotexts = ax.pie(
                amounts,
                autopct='%1.1f%%',
                startangle=140,
                pctdistance=0.85,
                colors=colors,
                wedgeprops=dict(width=0.4, edgecolor=theme_colors["bg_color"])
            )

            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(9)
                autotext.set_fontweight('bold')

            ax.axis('equal')
            ax.set_title("Spending by Category", color=theme_colors["text_color"], pad=20, weight='bold')

            legend = ax.legend(wedges, categories,
                               title="Categories",
                               loc="center left",
                               bbox_to_anchor=(1, 0, 0.5, 1),
                               frameon=False)
            plt.setp(legend.get_texts(), color=theme_colors["text_color"])
            plt.setp(legend.get_title(), color=theme_colors["text_color"], weight='bold')

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.category_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Chart Error", f"Could not update category chart: {e}")

    def update_monthly_chart(self, from_date="", to_date=""):
        """Update the time-based spending chart with optional date filters"""
        try:
            for widget in self.monthly_chart_frame.winfo_children():
                widget.destroy()
            plt.close('all')
            
            # Create a frame for view options
            options_frame = ctk.CTkFrame(self.monthly_chart_frame)
            options_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            # Create radio buttons for view options
            view_var = tk.StringVar(value="monthly")
            
            def update_view():
                # Get the selected view option
                view_type = view_var.get()
                self._render_time_chart(view_type, from_date, to_date)
            
            # Radio buttons for different time views
            monthly_radio = ctk.CTkRadioButton(options_frame, text="Monthly", variable=view_var, value="monthly", command=update_view)
            monthly_radio.pack(side=tk.LEFT, padx=10)
            
            weekly_radio = ctk.CTkRadioButton(options_frame, text="Weekly", variable=view_var, value="weekly", command=update_view)
            weekly_radio.pack(side=tk.LEFT, padx=10)
            
            daily_radio = ctk.CTkRadioButton(options_frame, text="Daily", variable=view_var, value="daily", command=update_view)
            daily_radio.pack(side=tk.LEFT, padx=10)
            
            # Create a frame for the chart
            self.time_chart_frame = ctk.CTkFrame(self.monthly_chart_frame)
            self.time_chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Initial render with monthly view
            self._render_time_chart("monthly", from_date, to_date)
            
        except Exception as e:
            messagebox.showerror("Chart Error", f"Could not update time-based chart: {e}")
    
    def _render_time_chart(self, view_type, from_date="", to_date=""):
        """Render the time-based chart based on the selected view type"""
        try:
            for widget in self.time_chart_frame.winfo_children():
                widget.destroy()
            plt.close('all')
            
            # Build query with date filters based on view type
            if view_type == "monthly":
                time_format = "%Y-%m"
                display_format = "%b %Y"
                title = "Monthly Spending"
                limit = 6
                date_extract = "strftime('%Y-%m', date)"
            elif view_type == "weekly":
                time_format = "%Y-%W"
                display_format = "Week %W, %Y"
                title = "Weekly Spending"
                limit = 8
                date_extract = "strftime('%Y-%W', date)"
            else:  # daily
                time_format = "%Y-%m-%d"
                display_format = "%b %d"
                title = "Daily Spending"
                limit = 14
                date_extract = "date"
            
            query = f"SELECT {date_extract} as time_period, SUM(amount) FROM expenses"
            params = []
            where_clauses = []
            
            if from_date:
                where_clauses.append("date >= ?")
                params.append(from_date)
            
            if to_date:
                where_clauses.append("date <= ?")
                params.append(to_date)
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += f" GROUP BY time_period ORDER BY time_period DESC LIMIT {limit}"
            
            self.cursor.execute(query, params)
            time_data = self.cursor.fetchall()
 
            if not time_data:
                ctk.CTkLabel(self.time_chart_frame, text="No expense data available.").pack(expand=True)
                return

            time_data.reverse()
            theme_colors = self._get_chart_theme_colors()
            
            fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
            fig.patch.set_facecolor(theme_colors["bg_color"])
            ax.set_facecolor(theme_colors["bg_color"])

            # Format time periods based on view type
            if view_type == "weekly":
                time_periods = [f"W{row[0].split('-')[1]} {row[0].split('-')[0]}" for row in time_data]
            elif view_type == "daily":
                time_periods = [datetime.strptime(row[0], "%Y-%m-%d").strftime("%b %d") for row in time_data]
            else:  # monthly
                time_periods = [datetime.strptime(row[0], "%Y-%m").strftime("%b %Y") for row in time_data]
            # Keep the raw keys to compute ranges on click
            time_keys = [row[0] for row in time_data]
                
            amounts = [row[1] for row in time_data]

            bars = ax.bar(time_periods, amounts, color='#00A6A6')

            ax.set_ylabel('Total Spending (₹)', color=theme_colors["text_color"]) 
            ax.set_title(title, color=theme_colors["text_color"], pad=20, weight='bold')
            
            ax.tick_params(axis='x', colors=theme_colors["text_color"]) 
            ax.tick_params(axis='y', colors=theme_colors["text_color"]) 

            for spine in ['top', 'right']:
                ax.spines[spine].set_visible(False)
            for spine in ['bottom', 'left']:
                ax.spines[spine].set_color(theme_colors["tick_color"]) 

            plt.xticks(rotation=30, ha='right')

            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'₹{height:.0f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', color=theme_colors["text_color"]) 

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.time_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            # Helper: compute from/to dates for a time key
            def compute_range(key: str):
                if view_type == 'daily':
                    return key, key
                if view_type == 'monthly':
                    year, month = map(int, key.split('-'))
                    start = f"{year:04d}-{month:02d}-01"
                    last_day = calendar.monthrange(year, month)[1]
                    end = f"{year:04d}-{month:02d}-{last_day:02d}"
                    return start, end
                # weekly: key like YYYY-WW (sqlite %W)
                year, week = key.split('-')
                year_i, week_i = int(year), int(week)
                # Monday of the given week (week 00 allowed). Use %Y-%W-%w with Monday=1
                try:
                    monday = datetime.strptime(f"{year}-{week}-1", "%Y-%W-%w")
                except Exception:
                    # Fallback: first Monday of year + weeks
                    jan1 = datetime(year_i, 1, 1)
                    monday = jan1 if jan1.weekday() == 0 else (jan1 + timedelta(days=(7 - jan1.weekday())))
                    monday = monday + timedelta(weeks=week_i)
                start = monday.strftime("%Y-%m-%d")
                end = (monday + timedelta(days=6)).strftime("%Y-%m-%d")
                return start, end

            # Click handler to update pie chart based on clicked bar
            def on_bar_click(event):
                if event.inaxes != ax:
                    return
                for idx, bar in enumerate(bars):
                    contains, _ = bar.contains(event)
                    if contains:
                        key = time_keys[idx]
                        start_date, end_date = compute_range(key)
                        # Update category pie chart for this range
                        self.update_category_chart(start_date, end_date)
                        break

            canvas.mpl_connect('button_press_event', on_bar_click)

            # Change cursor when hovering over clickable bars
            tk_widget = canvas.get_tk_widget()

            def on_motion(event):
                if event.inaxes != ax:
                    try:
                        tk_widget.config(cursor="arrow")
                    except Exception:
                        pass
                    return
                hovering = False
                for bar in bars:
                    contains, _ = bar.contains(event)
                    if contains:
                        hovering = True
                        break
                try:
                    tk_widget.config(cursor="hand2" if hovering else "arrow")
                except Exception:
                    pass

            def on_leave(event):
                try:
                    tk_widget.config(cursor="arrow")
                except Exception:
                    pass

            canvas.mpl_connect('motion_notify_event', on_motion)
            canvas.mpl_connect('figure_leave_event', on_leave)

        except Exception as e:
            messagebox.showerror("Chart Error", f"Could not update {view_type} chart: {e}")

    def update_trends_chart(self, from_date="", to_date=""):
        """Update the spending trends line chart with optional date filters"""
        try:
            for widget in self.trends_chart_frame.winfo_children():
                widget.destroy()
            plt.close('all')
            
            # Build query with date filters for top categories
            query = "SELECT category, SUM(amount) FROM expenses"
            params = []
            where_clauses = []
            
            if from_date:
                where_clauses.append("date >= ?")
                params.append(from_date)
            
            if to_date:
                where_clauses.append("date <= ?")
                params.append(to_date)
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += " GROUP BY category ORDER BY SUM(amount) DESC LIMIT 3"
            
            self.cursor.execute(query, params)
            top_categories = [row[0] for row in self.cursor.fetchall()]

            if not top_categories:
                ctk.CTkLabel(self.trends_chart_frame, text="No expense data available.").pack(expand=True)
                return

            category_data = {}
            all_months = set()
            for category in top_categories:
                # Build query with date filters for each category's monthly data
                query = "SELECT strftime('%Y-%m', date) as month, SUM(amount) FROM expenses WHERE category = ?"
                cat_params = [category]
                
                if from_date:
                    query += " AND date >= ?"
                    cat_params.append(from_date)
                
                if to_date:
                    query += " AND date <= ?"
                    cat_params.append(to_date)
                
                query += " GROUP BY month ORDER BY month"
                
                self.cursor.execute(query, cat_params)
                data = self.cursor.fetchall()
                category_data[category] = dict(data)
                all_months.update(row[0] for row in data)

            if len(all_months) < 2:
                ctk.CTkLabel(self.trends_chart_frame, text="Not enough monthly data for a trend.").pack(expand=True)
                return

            sorted_months = sorted(list(all_months))
            theme_colors = self._get_chart_theme_colors()

            fig, ax = plt.subplots(figsize=(10, 4), dpi=100)
            fig.patch.set_facecolor(theme_colors["bg_color"])
            ax.set_facecolor(theme_colors["bg_color"])

            colors = ['#00A6A6', '#F28F3B', '#F23D5E']

            for i, category in enumerate(top_categories):
                amounts = [category_data[category].get(month, 0) for month in sorted_months]
                month_labels = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in sorted_months]
                ax.plot(month_labels, amounts, marker='o', linestyle='-', color=colors[i % len(colors)], label=category)

            ax.set_ylabel('Total Spending (₹)', color=theme_colors["text_color"])
            ax.set_title('Spending Trends by Top Categories', color=theme_colors["text_color"], pad=20, weight='bold')

            ax.tick_params(axis='x', colors=theme_colors["text_color"])
            ax.tick_params(axis='y', colors=theme_colors["text_color"])
            
            for spine in ['top', 'right']:
                ax.spines[spine].set_visible(False)
            for spine in ['bottom', 'left']:
                ax.spines[spine].set_color(theme_colors["tick_color"])
                
            ax.grid(axis='y', linestyle='--', color=theme_colors["grid_color"], alpha=0.5)

            legend = ax.legend(frameon=False)
            plt.setp(legend.get_texts(), color=theme_colors["text_color"])

            plt.xticks(rotation=30, ha='right')
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.trends_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Chart Error", f"Could not update trends chart: {e}")

    def generate_ai_insights(self):
        """Generate AI insights using Gemini API"""
        try:
            # IMPORTANT: Replace with your actual Gemini API key.
            # It's recommended to load this from an environment variable or a config file.
            api_key = os.getenv("GEMINI_API_KEY", "AIzaSyAENpIPg_f8VjR9UHjG-wPvOEjSzqtIeKI") # Fallback to hardcoded key if not set
            if api_key == "AIzaSyAENpIPg_f8VjR9UHjG-wPvOEjSzqtIeKI":
                # A simple check for the default placeholder key
                print("Warning: Using a placeholder API key. Please set your GEMINI_API_KEY environment variable.")


            genai.configure(api_key=api_key)
            
            self.cursor.execute("SELECT SUM(amount) FROM expenses")
            total_spending = self.cursor.fetchone()[0] or 0
            
            if total_spending == 0:
                messagebox.showinfo("AI Insights", "No expense data to analyze. Please add some expenses first.")
                return

            self.cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC")
            category_spending = self.cursor.fetchall()
            
            self.cursor.execute("SELECT strftime('%Y-%m', date) as month, SUM(amount) FROM expenses GROUP BY month ORDER BY month DESC LIMIT 3")
            monthly_spending = self.cursor.fetchall()
            
            prompt = f"""As a helpful financial advisor, analyze the following expense data (currency: INR ₹) and provide insights.
The user wants a clear, concise summary of their spending habits and actionable advice.

**Expense Data Summary:**

* **Total Recorded Spending:** ₹{total_spending:.2f}

**Spending by Category:**
"""
            
            for category, amount in category_spending:
                percentage = (amount / total_spending) * 100
                prompt += f"* **{category}:** ₹{amount:.2f} ({percentage:.1f}%)\n"
            
            prompt += "\n**Recent Monthly Spending (last 3 months with data):**\n"
            if monthly_spending:
                for month, amount in monthly_spending:
                    prompt += f"* **{datetime.strptime(month, '%Y-%m').strftime('%B %Y')}:** ₹{amount:.2f}\n"
            else:
                prompt += "* Not enough data for monthly trend analysis.\n"
            
            prompt += """
---
**Your Analysis and Recommendations:**

Based on this data, please provide the following in a friendly and encouraging tone:
1.  **Spending Overview:** A brief, one-paragraph summary of the overall spending pattern.
2.  **Key Observation:** Point out the most significant finding (e.g., a dominant category, a sudden increase in spending).
3.  **Actionable Tips:** Provide 2-3 specific, practical suggestions for managing expenses better. Frame them as positive steps.

Format the response using markdown for clarity and readability.
"""
            
            self.insights_textbox.configure(state="normal")
            self.insights_textbox.delete("1.0", tk.END)
            self.insights_textbox.insert("1.0", "🤖 Generating insights, please wait...")

            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            
            self.insights_textbox.delete("1.0", tk.END)
            self.insights_textbox.insert("1.0", response.text)
            self.insights_textbox.configure(state="disabled")
            
        except Exception as e:
            self.insights_textbox.delete("1.0", tk.END)
            self.insights_textbox.insert("1.0", f"Sorry, an error occurred while generating insights.\n\nDetails: {e}")
            self.insights_textbox.configure(state="disabled")
            messagebox.showerror("AI Error", f"An error occurred: {e}")

    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if hasattr(self, 'conn'):
                self.conn.close()
            self.destroy()

# Run the application
if __name__ == "__main__":
    app = ExpenseTracker()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)  # Handle window close event
    app.mainloop()
