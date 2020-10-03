import json
import base64
import argparse
import requests
from io import BytesIO
import lxml.html
from PIL import Image
import sys
import os.path
from os import path
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

BASE_URL = "https://api.parler.com/v2"
BASE_V1_URL = "https://api.parler.com/v1"
LOGIN_URL = "/login/new"
CAPTCHA_URL = "/login/captcha/new"
CAPTCHA_SUBMIT_URL = "/login/captcha/submit"
SMS_OTP_SUBMIT_URL = "/login/sms/otp/submit"
PROFILE_URL = "/profile"
POST_URL = "/post"

# proxies = {
#     'https': 'http://127.0.0.1:8080',
# }


class ParlerApi:
    def __init__(self, user_name, pass_word):
        self.username = user_name
        self.password = pass_word
        self.captchapic = None
        self.identifier = None
        self.jst = None
        self.mst = None

    # string request_url, json post_data
    def api_factory(self, method="POST", request_url="login", post_data=None, header_data=None):
        response_code = 200
        request_body = ()

        if self.mst is not None and self.jst is not None and self.identifier is not None:
            header_data = {
                "cookie": "mst="+self.mst+"; jst="+self.jst
            }
        if post_data is not None:
            request_body = post_data
            # request_body = json.dumps(post_data)
        if header_data is not None:
            # set the headers for the HTTP Request
            pass
        r = None
        print(str(post_data))
        str_post_data = str(post_data)
        if method == "POST":
            header_data = {
                "content-type": "application/json",
                "content-length": str(len(str_post_data) - 1)
            }
            if self.mst is not None and self.jst is not None and self.identifier is not None:
                header_data = {
                    "content-type": "application/json",
                    "content-length": str(len(str_post_data) - 1),
                    "cookie": "mst=" + self.mst + "; jst=" + self.jst
                }
            # r = requests.post(request_url, proxies=proxies, verify=False, data=request_body, headers=header_data)
            r = requests.post(request_url, data=request_body, headers=header_data)
        else:
            # r = requests.get(request_url, proxies=proxies, verify=False, headers=header_data)
            r = requests.get(request_url, headers=header_data)
        if r is not None:
            # if there are cookies in the RequestsCookieJar, set them
            # <RequestsCookieJar[<Cookie jst=eyJhbG...BQ for .parler.com/>, <Cookie mst=s%3ALL...0I for .parler.com/>]>
            for cookie in r.cookies:
                if cookie.name == 'jst':
                    self.jst = cookie.value
                if cookie.name == 'mst':
                    self.mst = cookie.value
        return r

    # send the login request
    '''
    DeviceId can be anything, but must be set to something
    {identifier: "first.last@mail.com", password: "********", deviceId: "P5NfcFnooA502HrG"}
    '''
    # save the result
    '''
    {"key":"df7ef007-45c5-4b32-8a5c-7407baee39ba","state":"CAPTCHA","optional":false}
    '''

    def login(self):
        params = {
            "identifier": self.username,
            "password": self.password,
            "deviceId": get_random_string(8)
        }
        json_params = json.dumps(params)
        result = self.api_factory("POST", BASE_URL + LOGIN_URL, json_params)
        self.identifier = json.loads(result.text)['key']
        return result

    # send the captcha request
    '''
    {identifier: "df7ef007-45c5-4b32-8a5c-7407baee39ba"}
    '''
    # save the result
    '''
    {"image":"b64image"}
    '''

    def captcha(self):
        # params = {
        #     "identifier": self.identifier,
        # }
        params = '{\"identifier\": \"' + self.identifier + '\"}'
        result = self.api_factory("POST", BASE_URL + CAPTCHA_URL, params)
        if result.status_code == 200:
            self.captchapic = base64.b64decode(json.loads(result.text)['image'])
            image = Image.open(BytesIO(self.captchapic))
            image.show()
        return result

    # base64 decode
    # read image
    # display image
    # get stdin image response
    # send response
    '''
    {identifier: "df7ef007-45c5-4b32-8a5c-7407baee39ba", solution: "FfkGDP5R"}
    '''
    # read result
    '''
    {"state":"SMSOTP","optional":false}
    '''

    def submit_captcha(self):
        print("Enter captcha solution: ")
        # read from stdin
        captcha = sys.stdin.readline().strip('\n')
        # params = {
        #     "identifier": self.identifier,
        #     "solution": captcha
        # }
        params = '{\"identifier\": \"' + self.identifier + '\", \"solution\": \"' + captcha + '\"}'
        result = self.api_factory("POST", BASE_URL + CAPTCHA_SUBMIT_URL, params)
        return result

    # submit sms otp
    '''
    {identifier: "df7ef007-45c5-4b32-8a5c-7407baee39ba", code: "404711"}
    '''
    # read result
    '''
    {"state":"FINISHED","optional":false,"userData":{"user":{"id":"1086023ae7ca4b4caced7abf70c5c52a","name":"carltron","pb_private":false,"username":"carltron","verified":false,"accountColor":"","profilePhoto":"","coverPhoto":"","bio":"Friendly, neighborhood tattletale.","blocked":false,"followed":false,"hasPhone":true,"human":false,"integration":false,"joined":"20200901183902","muted":false,"rss":false,"subscribed":false,"verifiedComments":false,"badgesList":[],"state":1,"score":"0"},"firstTime":false,"settings":{"commentStyleBasic":false,"discoverByEmail":false,"hideBlockedAndMuted":false,"disableMessaging":false,"admin":{"language":"english","parlerBranding":true,"showAds":true,"comments":{"canContainLinks":true,"canContainMedia":true,"defaultOrder":"newest","usersCanChangeOrder":true},"spam":{"action":"remove","autoBan":false,"minReports":0}},"notifications":{"autoSubscribe":false,"commentDownVoted":true,"commentReply":true,"commentVoted":true,"conversationRequest":true,"dailyHighlights":true,"dislikes":true,"echos":true,"emergencyServices":true,"likes":true,"newFollower":true,"newMessage":true,"someonePosts":true,"tagged":true,"unfollowed":true,"email":{"directMessage":false,"newFeatures":false,"newNotification":false,"shouldReceiveEmail":false,"surveys":false},"filters":{"newAccount":false,"noProfilePhoto":false,"notFollowed":false,"notFollowing":false,"spam":true,"unverified":false},"profileViewed":false},"moderation":{"aiEnabled":false,"defaultBehavior":"pending","defaultFilterAction":"muteComment","spamAction":"nothing","spamFlagging":"five","verifiedComments":false},"allowFindMeFromPhoneOrEmail":true}}}
    '''
    # read HTTP Response Headers
    '''
    access-control-allow-credentials: true
    access-control-allow-origin: https://parler.com
    content-length: 1636
    content-type: application/json; charset=utf-8
    date: Sat, 03 Oct 2020 01:23:22 GMT
    set-cookie: mst=s%3AMizj4yuWKCKvLmabnW98c2utuG7ngCaJMJRNUNX4Q...; Max-Age=5184000; Domain=parler.com; Path=/; Expires=Wed, 02 Dec 2020 01:23:22 GMT; HttpOnly; Secure; SameSite=Lax
    set-cookie: jst=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzZXNz...; Max-Age=300; Domain=parler.com; Path=/; Expires=Sat, 03 Oct 2020 01:28:22 GMT; HttpOnly; Secure; SameSite=Lax
    status: 200
    vary: Origin
    x-ratelimit-limit: 5
    x-ratelimit-remaining: 4
    x-ratelimit-reset: 1601688207
    '''

    def submit_otp(self):
        print("Submit OTP Code: ")
        # read from stdin
        otp = sys.stdin.readline().strip('\n')
        # params = {
        #     "identifier": self.identifier,
        #     "code": otp
        # }
        params = '{\"identifier\": \"' + self.identifier + '\", \"code\": \"' + otp + '\"}'
        result = self.api_factory("POST", BASE_URL + SMS_OTP_SUBMIT_URL, params)
        if self.mst is not None and self.jst is not None and self.identifier is not None:
            with open("parler.cookies", "w") as f:
                f.write("mst:" + self.mst + "\n")
                f.write("jst:" + self.jst + "\n")
                f.write("identifier:" + self.identifier + "\n")
        return result

    # post to feed with Cookies from Response Headers as the Request Headers
    '''
    {body: "Testing the waters", parent: null, links: [], state: 4, sensitive: false}
    '''
    '''
    set-cookie: mst=s%3AMizj4yuWKCKvLmabnW98c2utuG7ngCaJMJRNUNX4Q...jTc; Max-Age=5184000; Domain=parler.com; Path=/; Expires=Wed, 02 Dec 2020 02:35:01 GMT; HttpOnly; Secure; SameSite=Lax
    set-cookie: jst=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzZXNz...uSg; Max-Age=300; Domain=parler.com; Path=/; Expires=Sat, 03 Oct 2020 02:40:01 GMT; HttpOnly; Secure; SameSite=Lax
    '''

    '''
    {body: "Again", parent: null, links: [], state: 4, sensitive: false}
    '''

    def submit_post(self, post_text):
        params = '{\"body\": \"'+post_text+'\", \"parent\": null, \"links\": [], \"state\": 4, \"sensitive\": false}'
        if self.identifier is not None and self.mst is not None:
            self.api_factory("POST", BASE_V1_URL + POST_URL, params)

    def get_post(self):
        params = {}
        if self.identifier is not None and self.mst is not None:
            self.api_factory("POST", BASE_V1_URL + POST_URL, params)

    # test the waters to see if we can pull a profile, if not, erase the current cookies,
    #  and replace the file
    def get_profile_load_cookies(self):
        params = {}
        result_code = self.api_factory("GET", BASE_V1_URL + PROFILE_URL)
        if result_code.status_code == 200:
            return True
        else:
            if path.exists("parler.cookies"):
                with open("parler.cookies", 'r') as f:
                    for line in f.readlines():
                        if line.startswith("mst:"):
                            self.mst = line[len("mst:"):].strip('\n')
                        elif line.startswith("jst:"):
                            self.jst = line[len("jst:"):].strip('\n')
                        elif line.startswith("identifier:"):
                            self.identifier = line[len("identifier:"):].strip('\n')
                result_code = self.api_factory("GET", BASE_V1_URL + PROFILE_URL)
                if result_code.status_code == 200:
                    return True
                else:
                    os.remove("parler.cookies")
                    return False
            else:
                self.login()
                self.captcha()
                self.submit_captcha()
                self.submit_otp()
                return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='ParlerApi')
    parser.add_argument('-u', '--username', help='User to login as for %(prog)', required=True)
    parser.add_argument('-p', '--password', help='Password for login on %(prog)', required=True)
    args = parser.parse_args()
    username = args.username
    password = args.password
    parler = ParlerApi(username, password)
    able_to_post = parler.get_profile_load_cookies()
    while able_to_post:
        print("What would you like to post?: ")
        post_data = sys.stdin.readline().strip('\n')
        parler.submit_post(post_data)