# Career Portal

A comprehensive Django-based career portal for managing job opportunities, internships, and hackathons. The platform helps students and job seekers track applications, manage activity points, and prepare for interviews through mock tests.

## Features

- **Opportunity Management**
  - Jobs
  - Internships
  - Hackathons
  - Application tracking
  - Activity points system

- **User Features**
  - Application submission
  - Resume upload
  - Mock test access
  - Activity points tracking
  - Dark/Light mode

## Technology Stack

- Python 3.12
- Django 4.1/5.0
- Bootstrap 5
- JavaScript/jQuery
- SQLite (default) / PostgreSQL (production)

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/career-portal.git
cd career-portal
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser
```bash
python manage.py createsuperuser
```

7. Run the development server
```bash
python manage.py runserver
```

## Project Structure

```
career-portal/
├── career/
│   ├── migrations/
│   ├── templates/
│   │   └── career/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── careerportal/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
│   ├── css/
│   └── js/
├── media/
│   └── resumes/
├── manage.py
├── requirements.txt
└── README.md
```

## Usage

1. Access admin panel at `/admin`
2. Create opportunities (jobs/internships/hackathons)
3. Users can:
   - View opportunities
   - Submit applications
   - Upload resumes
   - Track activity points
   - Access mock tests

## Development

### Setting up development environment

1. Install development dependencies
```bash
pip install -r requirements-dev.txt
```

2. Setup pre-commit hooks
```bash
pre-commit install
```

### Running tests
```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, contact [your-email@example.com](mailto:your-email@example.com) or open an issue in the repository.

## Acknowledgments

- Django Documentation
- Bootstrap Documentation
- Contributors list
