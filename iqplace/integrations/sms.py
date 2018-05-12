import aiohttp

from iqplace.app import IQPlaceApp


async def send_sms(phone, message):
    session = aiohttp.ClientSession()

    url = 'http://smspilot.ru/api.php'

    res = await session.get(url, params={
        'send': message,
        'to': phone,
        'apikey': IQPlaceApp().config['SMS_PILOT_TOKEN'],
        'from': 'INFORM',
        'format': 'json'
    })

    res.close()
    await session.close()