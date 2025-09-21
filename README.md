# AI-Powered Expense Tracker

A modern, intuitive desktop application to manage personal finances with the power of data visualization and AI insights.

## Features

- **Expense Logging**: Easily add, edit, and delete expense entries with date, amount, category, and description
- **Data Visualization**: View your spending patterns through interactive charts and graphs
- **AI Insights**: Get personalized financial insights powered by Google's Gemini AI
- **Filtering**: Filter expenses by date range for targeted analysis
- **Modern UI**: Clean, intuitive interface built with CustomTkinter

## Technology Stack

- **Python**: Core programming language
- **CustomTkinter**: Modern UI framework for desktop applications
- **SQLite**: Local database for storing expense data
- **Matplotlib**: Data visualization library for creating charts
- **Gemini 2.0 Flash API**: Google's latest AI model for generating financial insights

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Pip package manager

### Installation

1. Clone this repository or download the source code

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python expense_tracker.py
```

### AI Features Setup

To use the AI insights feature, you'll need a Google Gemini API key:

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your API key
2. Enter your API key in the application's AI Insights tab

## Usage Guide

### Adding Expenses

1. Navigate to the "Add Expense" tab
2. Fill in the date, amount, category, and description
3. Click "Add Expense"

### Viewing and Managing Expenses

1. Go to the "View Expenses" tab
2. Use the date filters to narrow down the list
3. Select an expense to edit or delete it

### Analyzing Spending Patterns

1. Visit the "Dashboard" tab
2. View the category breakdown, monthly spending, and trends charts
3. Click "Refresh Charts" to update with the latest data

### Getting AI Insights

1. Go to the "AI Insights" tab
2. Enter your Gemini API key
3. Click "Generate Insights" to receive personalized financial analysis

## Project Structure

- `expense_tracker.py`: Main application file
- `requirements.txt`: List of Python dependencies
- `data/expenses.db`: SQLite database (created on first run)

## Development Approach

This project follows a phased development approach:

1. **Foundation**: Core app structure and expense logging
2. **Visualization**: Charts and dashboard for visual analysis
3. **AI Integration**: AI-powered spending overview
4. **Polish**: Refined UI/UX and additional features