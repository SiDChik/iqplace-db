import base64
import hashlib
import os
import rapidjson
import uuid
from random import randint

import facebook
import vk
from aiohttp import ClientSession
from aiovk import TokenSession, API
from bson import ObjectId
from sanic.response import json, HTTPResponse

from iqplace.app import IQPlaceApp
from iqplace.auth.utils import login_user, decode_token
from iqplace.helpers import detect_login_field, normalized_phone
from iqplace.models.smscodes import SMSCodes
from iqplace.models.user import User


async def login(request):
    login = request.json.get('login', '').lower()
    password = request.json.get('password', '')
    deviceID = request.json.get('deviceID')

    field = detect_login_field(login)

    criteria = {}
    criteria[field] = login

    user = await User.manager.find(criteria)

    if not len(user):
        return json({
            'error': 'doesntexiss'
        }, 400)

    user = user[0]

    ps = password + user.salt
    hashed_password = hashlib.sha512(ps.encode()).hexdigest()
    if hashed_password != user.password:
        return json({
            'error': 'doesntexiss'
        }, 400)

    token = await login_user(user, deviceID)

    return json({
        'token': token
    })


async def login_sms(request):
    phone = normalized_phone(request.json.get('phone', ''))
    code = request.json.get('code', '')
    deviceID = request.json.get('deviceID')

    criteria = {
        'phone': phone,
        'code': code,
        'deviceID': deviceID
    }

    code_obj = await SMSCodes.manager.find(criteria)

    if len(code_obj):
        await SMSCodes.manager.delete(criteria)

        user = await User.manager.find({
            'phone': phone
        })

        if not len(user):
            user = User(phone=phone, groups=['user'])
            await user.save()
        else:
            user = user[0]

        token = await login_user(user, deviceID)

        return json({
            'token': token
        })

    return json({
        'error': True
    }, 400)


async def registration(request):
    login = request.json.get('login', '').lower()
    password = request.json.get('password', '')
    deviceID = request.json.get('deviceID')

    field = detect_login_field(login)

    criteria = {}
    criteria[field] = login

    user = await User.manager.find(criteria)

    if len(user):
        return json({
            'error': True
        }, 400)

    # gen salt
    salt = uuid.uuid4().hex
    ps = password + salt
    hashed_password = hashlib.sha512(ps.encode()).hexdigest()

    criteria.update({
        'password': hashed_password,
        'salt': salt
    })

    user = User(**criteria)
    await user.save()

    token = await login_user(user, deviceID)

    return json({
        'token': token
    })


async def check_registration(request):
    login = request.json.get('login', '').lower()
    deviceID = request.json.get('deviceID')

    field = detect_login_field(login)

    if field == 'phone':
        login = normalized_phone(login)

    check = {}
    check[field] = login

    check = await User.manager.find(check)
    if len(check) and field != 'phone':
        return json({
            'error': True,
            'code': 100
        }, status=400)
    # 3 ways
    if field == 'phone':
        await SMSCodes.manager.delete({
            'deviceID': deviceID,
            'phone': login
        })

        code = randint(1000, 9999)
        code_obj = SMSCodes(
            code=code,
            phone=login,
            deviceID=deviceID
        )
        await code_obj.save()

        return json({
            'nextStep': 'login_phone' if len(check) else 'confirm_phone',
            'phone': login
        })

    return json({
        'nextStep': 'set_password',
        'login': login
    })


async def login_social(request):
    social = request.json.get('social', '').lower()
    deviceID = request.json.get('deviceID', '').lower()
    access_token = request.json.get('access_token', '')

    criteria = None
    if social == 'vk':
        session = TokenSession(access_token=access_token)
        api = API(session)
        info = await api.users.get()
        info = info[0]
        criteria = {
            'vk': info['id']
        }

    if social == 'fb':
        cs = ClientSession()
        url = 'https://graph.facebook.com/v2.11/me/?access_token=%s' % access_token
        resp = await cs.get(url)
        info = await resp.json()
        resp.close()
        cs.close()
        criteria = {
            'fb': info['id']
        }

    if criteria:
        user = await User.manager.find(criteria)

        if not len(user):
            user = User(vk=info['id'], firstName=info.get('first_name'), lastName=info.get('last_name'),
                        groups=['user'])
            await user.save()
        else:
            user = user[0]

        token = await login_user(user, deviceID)

        return json({
            'token': token
        })

    pass

    return json({
        'erorr': 'true'
    }, 400)


async def me(request):
    token = request.headers.get('authorization')
    deviceID = request.headers.get('deviceid')

    token_info = decode_token(token)

    if deviceID != token_info.get('deviceID'):
        return json({
            'ok': False
        }, status=403)

    user = await User.manager.find_one({'_id': ObjectId(token_info['user_id'])})
    if not user:
        return json({
            'ok': False
        }, 404)

    if request.method == 'PATCH':
        avatar = request.json.pop('avatar', None)
        if avatar:
            config = IQPlaceApp().config

            content = base64.b64decode(avatar)
            uid = uuid.uuid4().hex
            url = 'users/%s.jpg' % (user.id)
            path = '%s/%s' % (config.UPLOAD_DIR, url)

            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            f = open(path, 'wb')
            f.write(content)
            f.close()

            user.avatar = url

        user.update(**request.json)
        await user.save()

    return HTTPResponse(user.public_json(), content_type="application/json")
