import ast


def getLoginToken(self, data):
    """Method to get a login token"""
    user_login = self.client().post('/login', data=data, content_type="application/json")
    self.assertEqual(user_login.status_code, 201)
    token = ast.literal_eval(user_login.data.decode())

    return token['User']['token']


def headerSetUp(self, setUp, data):

    if setUp == 0:
        headers = {
                'content-type': "application/json",
                'x-access-token': 'Invalid Token'
        }
        return headers
    elif setUp == 1:
        logintoken = getLoginToken(self, data)
        headers = {
            'content-type': "application/json",
            'x-access-token': logintoken
        }
        return headers
    else:
        print("Please input the set up type!")
