import base64
import os
import rapidjson
import uuid

from sanic.response import json, HTTPResponse

from iqplace.app import IQPlaceApp
from iqplace.helpers import deepcopy, json_default
from iqplace.models.marker import Marker


async def create(request):
    data = deepcopy(request.json)

    data['images'] = []

    marker = Marker(**data)
    await marker.save()

    config = IQPlaceApp().config

    images = []

    for num, image in enumerate(request.json['images']):
        content = base64.b64decode(image)
        uid = uuid.uuid4().hex
        url = 'markers/%s/%s.jpg' % (marker.id, uid)
        path = '%s/%s' % (config.UPLOAD_DIR, url)

        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        f = open(path, 'wb')
        f.write(content)
        f.close()

        images.append(url)

    marker.images = images
    await marker.save()

    return HTTPResponse(marker.to_json(), content_type="application/json")


async def get_list(request):
    markers = await Marker.manager.find({})
    out = rapidjson.dumps([x.serialize() for x in markers], default=json_default)
    return HTTPResponse(out, content_type="application/json")
