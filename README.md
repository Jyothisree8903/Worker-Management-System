# Worker-Management-System

A desktop-based application to manage labour workers' attendance, wages, and payments with secure user authentication. Designed for environments like home construction or farm work where multiple users manage daily wage workers.

## Problem Statement

In labour-intensive projects, multiple users handle payments and worker coordination. This leads to confusion and inconsistency. This system provides a centralized, transparent platform to:

- Track attendance
- Manage payments
- Calculate wages based on gender
- Enable user accountability

> Full problem statement and use case details are in [`problem.docx`](problem.docx).

---
##  Features

- Secure User Login & Registration
- Gender-Based Wage Assignment (₹1000/day for males, ₹800/day for females)
- Attendance Tracking (by date)
- Payment Logging (user-wise and date-wise)
- Automated Wage Calculation
- Report Generation with filters:
  - By name, gender, or date range
  - Pending/Overpaid amounts
  - Full payment history per worker
- Export to Excel (`worker_data.xlsx`)

---
## Technologies Used

- Python
- Tkinter (GUI)
- SQLite (Database)
- Pandas (Data export to Excel)

---
##  Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/worker-management-system.git
   cd worker-management-system
2. Run the app
python Final\ code.py
This will launch the Tkinter GUI.

3. Database

worker_mgmt.db is automatically created if not present.

Tables: users, workers, attendance, payments.
