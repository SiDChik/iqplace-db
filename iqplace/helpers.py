import base64
import datetime
import re
import uuid

import rapidjson
from bson import ObjectId, DBRef, RE_TYPE, Regex, text_type, SON, MinKey, MaxKey, Timestamp, Code, Binary
import _pickle as cPickle


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def json_default(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, DBRef):
        return rapidjson.dumps(obj.as_doc(), default=json_default)
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, (RE_TYPE, Regex)):
        flags = ""
        if obj.flags & re.IGNORECASE:
            flags += "i"
        if obj.flags & re.LOCALE:
            flags += "l"
        if obj.flags & re.MULTILINE:
            flags += "m"
        if obj.flags & re.DOTALL:
            flags += "s"
        if obj.flags & re.UNICODE:
            flags += "u"
        if obj.flags & re.VERBOSE:
            flags += "x"
        if isinstance(obj.pattern, text_type):
            pattern = obj.pattern
        else:
            pattern = obj.pattern.decode('utf-8')
        return SON([("$regex", pattern), ("$options", flags)])
    if isinstance(obj, MinKey):
        return {"$minKey": 1}
    if isinstance(obj, MaxKey):
        return {"$maxKey": 1}
    if isinstance(obj, Timestamp):
        return {"$timestamp": SON([("t", obj.time), ("i", obj.inc)])}
    if isinstance(obj, Code):
        return SON([('$code', str(obj)), ('$scope', obj.scope)])
    if isinstance(obj, Binary):
        return SON([
            ('$binary', base64.b64encode(obj).decode()),
            ('$type', "%02x" % obj.subtype)])
    if isinstance(obj, bytes):
        return SON([
            ('$binary', base64.b64encode(obj).decode()),
            ('$type', "00")])
    if isinstance(obj, uuid.UUID):
        return {"$uuid": obj.hex}
    raise TypeError("%r is not JSON serializable" % obj)


def deepcopy(obj):
    return cPickle.loads(cPickle.dumps(obj, -1))


def detect_login_field(login):
    if '@' in login:
        return 'email'

    if login.startswith('+'):
        return 'phone'

    if login[0].isdigit():
        return 'phone'

    return 'login'


def normalized_phone(phone):
    phone = re.sub("\D", "", phone)
    if len(phone) == 10 and phone.startswith('9'):
        phone = '+7%s' % phone
    elif len(phone) == 11 and phone.startswith('8'):
        phone = '+7%s' % phone[1:]
    else:
        phone = '+%s' % phone
    return phone