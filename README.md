**Crew Match Backend Python**

Usage
===

```bash
    git clone git@github.com:Joint-Venture-AI/Crew-Match-Backend.git
    cd Crew-Match-Backend
    python -m venv venv
    venv/Scripts/activate
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
    # Set in case of gmail/smtp else remove
    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=youremail@gmail.com
    EMAIL_HOST_PASSWORD=gmail_app_password
    
```
Apis
===

```bash
    User

    /user/create/ done
    /user/token/ done
    /user/send-otp/ done
    /user/verify/ done
    /user/update/ done
    /user/change-password/ done
    /user/reset-password/ done
    /user/retrieve-profile/<:id>/ done
    /user/update-profile/<:id>/ done

```

PostgreSQL
===
```bash
    CREATE DATABASE db_name;
    CREATE USER username WITH PASSWORD 'password';
    GRANT ALL PRIVILEGES ON DATABASE db_name TO username;
    GRANT ALL PRIVILEGES ON SCHEMA public TO username;
```
