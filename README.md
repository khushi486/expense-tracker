# 💰 Expense Tracker Web Application

## 📊 Project Overview

This is a **Flask-based Expense Tracker Web Application** that helps users manage their daily expenses efficiently.
The application allows users to **add, edit, delete, and analyze expenses** with useful insights like category-wise and date-wise spending.
It also includes a **secure user authentication system**, ensuring that each user can safely manage their own data.
---

## 🎯 Key Features

* 🔐 User Registration & Login (Authentication System)
* ➕ Add Expenses
* ✏️ Edit Expenses
* ❌ Delete Expenses
* 📅 Filter by Date Range
* 📂 Filter by Category
* 📊 Category-wise Expense Analysis
* 📈 Daily Expense Tracking
* 📥 Export Data to CSV

---

## 🛠️ Tech Stack

* **Backend:** Python (Flask)
* **Database:** SQLite (SQLAlchemy ORM)
* **Frontend:** HTML, CSS (Jinja Templates)
* **Libraries:**

  * Flask
  * Flask-SQLAlchemy
  * Werkzeug (Password Hashing)

---

## 🗂️ Project Structure

```
expense-tracker/
│── app.py
│── templates/
│   ├── login.html
│   ├── register.html
│   ├── index.html
│   ├── edit.html
│── instance/
│   └── expense.db
│── README.md
```

---

## 🧩 Database Models

### Expense

* amount (Float)
* category (String)
* date (Date)
* description (String)

### User

* username (Unique)
* password (Hashed)

---

## 📈 Functionalities

* Manage daily expenses easily
* Filter expenses based on date and category
* Analyze spending patterns
* Export filtered data as CSV

---

## 🚀 How to Run This Project

### 1️⃣ Clone the Repository

```
git clone https://github.com/khushi486/expense-tracker.git
cd expense-tracker
```

### 2️⃣ Install Dependencies

```
pip install flask flask_sqlalchemy
```

### 3️⃣ Run the Application

```
python app.py
```

### 4️⃣ Open in Browser

```
http://127.0.0.1:4848
```

---

## 🔐 Authentication

* Users must register before login
* Passwords are stored securely using hashing
* Sessions are managed using Flask

---

## 📊 Future Improvements

* Add advanced charts (Chart.js / Plotly)
* Deploy application online
* Add budget tracking feature
* Improve UI/UX design
* Mobile responsiveness

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork and improve this project.

---

## 📧 Contact

**Khushi Dakhare**
khushidakhare48@gmail.com
https://www.linkedin.com/in/khushi-dakhare-3605bb318/

## ⭐ Acknowledgement

This project was built to practice **Flask, database management, and full-stack web development fundamentals**.
