import datetime

import jwt

from iqplace.app import IQPlaceApp


async def login_user(user, deviceID=None):
    app = IQPlaceApp()
    token_payload = {
        'user_id': str(user.id),
        'deviceID': deviceID,
        'created_at': datetime.datetime.utcnow().isoformat()
    }

    encoded = jwt.encode(token_payload, app.private_key, algorithm='RS256')

    return encoded.decode()
