web: gunicorn app:app --bind 0.0.0.0:$PORT --access-logfile - --access-logformat '%({x-forwarded-for}i)s "%(m)s %(U)s" %(s)s %(b)s %(D)sus'
