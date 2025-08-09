python manage.py shell -c "
import base64, os
# Generate 32 random bytes
key = base64.urlsafe_b64encode(os.urandom(32)).decode()
print(key)"
