# NEXTSTEP - Education Platform

A comprehensive web-based education platform built with Django that democratizes access to quality technical education by eliminating "analysis paralysis" for students.

## Features

- **User Authentication**: Secure registration and login system
- **Dynamic Roadmap Generator**: Step-by-step learning paths tailored to career goals
- **Free & Paid Resource Categorization**: Transparent resource labeling with direct links
- **Progress Analytics**: Interactive charts and skill heatmaps using Matplotlib/Seaborn
- **Articles & Tutorials**: Community-driven educational content
- **Internship Opportunities**: Browse and apply for internships
- **Job Board**: Extended full-time and part-time job listings
- **Communities & Study Groups**: Peer matching and collaboration tools
- **CSV Bulk Import**: Admin tools for adding career paths and resources
- **Budget Filter**: Show free resources only or include paid options

## Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, Alpine.js
- **Database**: SQLite3
- **Visualization**: Matplotlib, Seaborn, Pandas
- **Forms**: Django Crispy Forms with Bootstrap 5

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```
5. Collect static files:
   ```bash
   python manage.py collectstatic
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
nextstep/
├── accounts/          # User authentication, profiles, dashboard
├── analytics/         # Progress tracking and visualizations
├── articles/          # Articles and tutorials
├── communities/       # Study groups and peer matching
├── internships/       # Internship opportunities
├── jobs/              # Job board
├── roadmaps/          # Core roadmap generator
├── nextstep/          # Project settings
├── templates/         # HTML templates
├── static/            # CSS, JS, images
└── media/             # User uploads
```

## License

MIT License
