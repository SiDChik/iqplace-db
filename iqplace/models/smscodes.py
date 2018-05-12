from iqplace.db.fields.field import Field
from iqplace.db.model import DBModel
import aiohttp

from iqplace.integrations.sms import send_sms


class SMSCodes(DBModel):
    collection_name = 'sms_codes'

    phone = Field()
    code = Field()
    deviceID = Field()

    async def save(self):
       await super(SMSCodes, self).save()

       await send_sms(self.phone, 'Код подтверждения: %s' % self.code)


