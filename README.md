# 💼 Career Portal

**Career Portal** is a Flask-based web application that helps users discover curated opportunities including **Jobs**, **Internships**, and **Hackathons**. The platform is maintained by an admin who can manage and update opportunities, ensuring users get access to the latest openings.

---

## 🚀 Features

- 🧑‍🎓 **Explore Opportunities**
  - Browse categorized listings: Jobs, Internships, Hackathons
  - View detailed opportunity information
  - Apply through an integrated form with resume upload

- 👨‍💼 **Admin Dashboard**
  - Login-secured admin panel
  - Add, edit, or delete opportunities
  - View submissions from applicants

- 📦 **Backend Integration**
  - Data stored in **MongoDB**
  - Flask-based server for routing, logic, and APIs

---

## 🛠️ Tech Stack

| Layer        | Technology                  |
|--------------|-----------------------------|
| Frontend     | HTML, CSS, Bootstrap, JS    |
| Backend      | Python, Flask               |
| Database     | MongoDB                     |
| File Storage | Local/Cloud (resumes)       |
| Auth         | Flask-Login (for admin)     |

---

## 🖥️ Pages Overview

- `/` – Home page with categories: Jobs, Internships, Hackathons  
- `/opportunities/<category>` – Lists all entries under a category  
- `/opportunity/<id>` – View details of a specific opportunity  
- `/apply/<id>` – Application form with file upload  
- `/admin/login` – Admin login  
- `/admin/dashboard` – Admin dashboard for opportunity management  

---

## 📂 Folder Structure

```
career-portal/
├── app.py
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── opportunities.html
│   ├── apply.html
│   └── ...
├── static/
│   ├── css/
│   └── js/
├── models/
│   └── database.py
├── uploads/
│   └── (resume files)
├── requirements.txt
└── README.md
```

---

## 📝 Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/your-username/career-portal.git
cd career-portal
```

2. **Create a virtual environment & activate it**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables (optional)**
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
```

5. **Run the app**
```bash
flask run
```

6. **Open in browser**

Visit: [http://localhost:5000](http://localhost:5000)

---

## 📈 Future Enhancements

- Email notifications to admin & applicants  
- Deadline-based filters and sorting  
- Mobile-first responsive design  
- Search bar and opportunity tags  
- Resume parsing and smart screening

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue to discuss your idea first.

---

## 📝 License

Licensed under the [MIT License](LICENSE).

---
