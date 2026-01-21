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

.env
===

```bash
    ALLOWED_HOSTS=api.crewsh.com,localhost,127.0.0.1
    DEBUG=True
    SECRET_KEY=ldfj#lkjv}ldjf]salkdjf23434lkj@.,,xclkjdsflskdfjoierjeldfjas.dfjeiorujldksfjlk1d24f5sdf4
    #DB_ENGINE=django.db.backends.postgresql
    #DB_NAME=crewmatch
    #DB_USER=crewmatch
    #DB_PASSWORD=crewmatch
    #DB_HOST=localhost
    #DB_PORT=5432
    STRIPE_PUBLIC_KEY=pk_test_51LwyfxKOgqVegdKnlxccCUSOJ2Yy89pgOJ83boyRFQKjGVlovgmjvuyznDpMimLAc98zq6rXHwcoVo8jC7HoyGiA00sUWXMemo
    STRIPE_SECRET_KEY=sk_test_51LwyfxKOgqVegdKnszeJzBdJPO6RLcdV7Zndhw21kyDWxx0sykxYJeGRCfQk25sSXDpsbhCY2tyjBYqBLwIX27GR00dS8oDqdb
    STRIPE_WEBHOOK_KEY=whsec_766582fe83be2e98f96e65a53a0f4f5f7a50a385472e612f8a09ab9ab248b737
    STRIPE_SUCCESS_URL=http://localhost:8001/api/subscription/success/
    STRIPE_CANCEL_URL=http://localhost:8001/api/subscription/cancel/
    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    EMAIL_HOST=smtp.hostinger.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=noreply@crewsh.com
    EMAIL_HOST_PASSWORD=Nobody@1314
    DOMAIN=http://10.10.12.10:3000
    HOST=http://10.10.12.10:3000
    ON_PRODUCTION=False
    CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://10.10.12.10:3000,https://api.crewsh.com,wss://api.crewsh.com
    
```
