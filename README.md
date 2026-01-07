Crew Match
==

An online dating app serving the following features:

    + Find crewship members based on profile preference
    + Swipe based like/dislike/match
    + Text messaging

System Requirements
==

```
    Python 3.13.x
    Docker
```

Usage
===

```bash
    docker run -d --name redis -p 6379:6379 redis
    git clone git@github.com:Joint-Venture-AI/Crew-Match-Backend.git
    cd Crew-Match-Backend
    python -m venv venv
    source venv/bin/activate # venv\Scripts\activate on windows
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
```

ENV
===

```bash
    DEBUG=True
    SECRET_KEY=long_string
    DB_ENGINE=django.db.backends.sqlite3
    DB_NAME=db.sqlite3
    DB_USER=TEST
    DB_PASSWORD=TEST
    DB_HOST=localhost
    DB_PORT=5432
    STRIPE_PUBLIC_KEY=stripe_pub_key
    STRIPE_SECRET_KEY=stripe_sec_key
    STRIPE_WEBHOOK_KEY=stripe_webhook_key
    STRIPE_SUCCESS_URL=http://localhost:8000/payment/success/
    STRIPE_CANCEL_URL=http://localhost:8000/payment/cancel/
    # Set in case of gmail/smtp
    # EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    # EMAIL_HOST=smtp.gmail.com
    # EMAIL_PORT=587
    # EMAIL_HOST_USER=youremail@gmail.com
    # EMAIL_HOST_PASSWORD=gmail_app_password
    
```
