# Resume API

## What's new:

### Two features/improvements included in JWT Auth (restframework_simplejwt)

1. Fix: Disable refresh token for inactive user(https://github.com/jazzband/djangorestframework-simplejwt/pull/814/commits/76741ff9ae347c8e7d52101c4bc11985f3940992)

2. Add the refresh token to the outstanding db after refreshing(https://github.com/jazzband/djangorestframework-simplejwt/pull/696)


## Overview

The Resume API provides a platform for users to create and manage their resumes. It supports account creation, issues JWT tokens needed for resume management, and enforces a throttling limit of 200 requests per day for all user types. Users can create, update, and delete their resumes through this API.

**Note:** 
To enhance security, JWTs are now actively managed:

Token Blacklisting: JWTs can be blacklisted, preventing their further use.

Scheduled Token Deletion: Blacklisted tokens are automatically deleted after 1 day. This process is managed by a scheduled task that runs daily at 00:00 UTC, utilizing Celery Beat for scheduling and Celery Worker for task execution. Redis serves as the message broker, and the database backend stores task results.

## Getting Started

Follow these instructions to set up and run the API:

### Prerequisites

- Python 3.11
- Django 4.2.8

### Installation

1. **Install Dependencies:**

   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Helper Commands:**

   - Optional: `python manage.py flush`
   - Optional: `python manage.py reset_db`
   - Optional: `python manage.py clean_pyc`
   - `python delete_migrations.py`
   - `python manage.py makemigrations`
   - `python manage.py migrate`
   - `python manage.py createcachetable`
   - `python manage.py migrate django_celery_beat`
   - `python manage.py migrate django_celery_results`
   - `python manage.py runserver 8000`
   - `ngrok http --domain=diverse-intense-whippet.ngrok-free.app 8000`
   - `celery -A resume_api worker --reload --pool=solo --loglevel=info`
   - `celery -A resume_api beat --loglevel=info`

3. **Update 1:**
   - Management Command to delete blacklisted tokens:
     --`python manage.py delete_blacklisted_tokens`

4. **Update 2**
     - compression middleware added
     - maintainance middleware added
     - 503.html for maintainance mode 

### Running the API Using Docker

To build and start the API using Docker, follow these steps:

1. **Build and Start the Containers:**

   ```bash
   docker-compose up --build
   ```

Visit the API at http://localhost:8000/api/schema/swagger-ui/.