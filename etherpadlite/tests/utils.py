testserver = {
    'title': 'Testserver',
    'url': 'http://www.example.com',
    'apikey': '1234567'
}


class EtherpadLiteClientMock(object):
    """ A class to mock the EtherpadLiteClient for easy testing without having
    a Etherpad-lite server running in the background.
    """

    def __init__(self, apiKey=None, baseUrl=None):
        if apiKey:
            self.apiKey = apiKey

        if baseUrl:
            self.baseUrl = baseUrl

    def createGroupIfNotExistsFor(self, group_information):
        """ Simply return the group_information 'as it is' instead of building
        a cryptic hash.
        """
        return {'groupID': group_information}

    def deleteGroup(self, *args):
        pass

    def createAuthorIfNotExistsFor(self, user_id, name=''):
        """ Simply return the user_id 'as it is' instead of building a cryptic
        hash.
        """
        return {'authorID': user_id}

    def createGroupPad(self, group_id, name):
        pass

    def deletePad(self, pad_id):
        pass

    def getPublicStatus(self, pad_id):
        pad_name = pad_id.split('$')[-1]
        if pad_name == 'R2D2':
            return {'publicStatus': True}
        else:
            return {'publicStatus': False}

    def getReadOnlyID(self, pad_id):
        return pad_id

    def createSession(self, group_id, author_id, time_tupple):
        if True:
            return {'sessionID': 'abcdefg'}
        else:
            e = Exception()
            e.reason = "Testerrormessage"
            raise e
