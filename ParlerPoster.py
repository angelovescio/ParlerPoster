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
from requests_toolbelt import MultipartEncoder

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
#https://www.parler.com/functions/post/create/
BASE_URL = "https://www.parler.com/functions"
BASE_V1_URL = "https://www.parler.com/functions"
LOGIN_URL = "/sessions/authentication/login/login.php"
CAPTCHA_URL = "/login/captcha/new"
CAPTCHA_SUBMIT_URL = "/login/captcha/submit"
SMS_OTP_SUBMIT_URL = "/login/sms/otp/submit"
PROFILE_URL = "https://www.parler.com/pages/feed.php"
POST_URL = "/post/create/PostParleyController.php"

#v1 fields
FEED_URL = "https://www.parler.com/pages/feed.php"

proxies = {
    'https': 'http://127.0.0.1:8080',
}


class ParlerApi:
    def __init__(self, user_name, pass_word):
        self.username = user_name
        self.password = pass_word
        self.cookie = None
        self.PHPSESSID = None
        self.parler_auth_token = None
        self.boundary = '----WebKitFormBoundary' \
           + ''.join(random.sample(string.ascii_letters + string.digits, 16))
        self.m = None

    # string request_url, json post_data
    def api_factory(self, method="POST", request_url="login", post_data=None, header_data=None):
        print("request_url = " + request_url)
        response_code = 200
        request_body = ()

        # if self.parler_auth_token is not None:
        #     print("parler_auth_token is " + self.parler_auth_token)
        #     header_data = {
        #         "cookie": "PHPSESSID=" + self.PHPSESSID + "; parler_auth_token="+self.parler_auth_token
        #     }
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
            if self.parler_auth_token is not None and self.m is not None:
                header_data = {
                    "content-type": "Content-Type: multipart/form-data; boundary=" + self.boundary,
                    "content-length": str(len(str_post_data) - 1),
                    "cookie": "PHPSESSID=" + self.PHPSESSID + "; parler_auth_token="+self.parler_auth_token
                }
                r = requests.post(request_url, data=self.m, headers=header_data)
            else:
                r = requests.post(request_url, data=post_data, headers=header_data)
            # r = requests.post(request_url, proxies=proxies, verify=False, data=request_body, headers=header_data)
            
        else:
            # r = requests.get(request_url, proxies=proxies, verify=False, headers=header_data)
            r = requests.get(request_url, headers=header_data)
        if r is not None:
            # if there are cookies in the RequestsCookieJar, set them
            # <RequestsCookieJar[<Cookie jst=eyJhbG...BQ for .parler.com/>, <Cookie mst=s%3ALL...0I for .parler.com/>]>
            for cookie in r.cookies:
                print(cookie)
                if cookie.name == 'parler_auth_token':
                    self.parler_auth_token = cookie.value
                if cookie.name == 'PHPSESSID':
                    self.PHPSESSID = cookie.value
            if self.parler_auth_token is not None and self.PHPSESSID is not None:
                self.cookie = "PHPSESSID=" + self.PHPSESSID + "; parler_auth_token="+self.parler_auth_token
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
            "device_id": get_random_string(8)
        }
        json_params = json.dumps(params)
        self.api_factory("GET", BASE_URL + LOGIN_URL)
        print("JSON_PARAMS " + json_params)
        print("BOUNDARY " + self.boundary)
        self.m = MultipartEncoder(fields=params, boundary=self.boundary)
        result = self.api_factory("POST", BASE_URL + LOGIN_URL, json_params)
        # self.identifier = json.loads(result.text)['key']
        return result

    def submit_post(self, post_text):
        params = {
            "textarea": post_text,
            "echo_post_id": "undefined",
            "file": "",
            "sensitivecontent": "false",
            "post_id": "undefined"
        }
        print(self.m)
        print(self.boundary)
        print(self.cookie)
        self.m = MultipartEncoder(fields=params, boundary=self.boundary)
        header_data = {
                    "content-type": "multipart/form-data; boundary=" + self.boundary,
                    "cookie": "PHPSESSID=" + self.PHPSESSID + "; parler_auth_token="+self.parler_auth_token
                }
        req = requests.post(BASE_V1_URL + POST_URL, headers=header_data, data=self.m)
        print(req.text)
        print(req.request.url)
        print(req.request.body)
        print(req.request.headers)
        # self.api_factory("POST", BASE_V1_URL + POST_URL, params)

    def get_feed(self):
        print(self.m)
        print(self.boundary)
        print(self.cookie)
        # self.m = MultipartEncoder(fields=params, boundary=self.boundary)
        header_data = {
                    "content-type": "multipart/form-data; boundary=" + self.boundary,
                    "cookie": "PHPSESSID=" + self.PHPSESSID + "; parler_auth_token="+self.parler_auth_token
                }
        req = requests.post(FEED_URL, headers=header_data)
        print(req.text)
        print(req.request.url)
        print(req.request.body)
        print(req.request.headers)


        # params = {}
        # retval = ""
        # if self.identifier is not None and self.mst is not None:
        #     retval = self.api_factory("GET", BASE_V1_URL + FEED_URL, params).text
        # return retval

    # test the waters to see if we can pull a profile, if not, erase the current cookies,
    #  and replace the file
    def get_profile_load_cookies(self):
        params = {}
        result_code = self.api_factory("GET", PROFILE_URL)
        if result_code.status_code == 200:
            return True
        elif result_code.status_code == 302:
            os.remove("parler.cookies")
            self.login()
            self.captcha()
            self.submit_captcha()
            self.submit_otp()
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
    r = parler.login()
    print(r)
    able_to_post = parler.get_profile_load_cookies()
    while able_to_post:
        print("Enter 1 for POST and 2 for FEED: ")
        post_data = sys.stdin.readline().strip('\n')
        if int(post_data) == 1:
            print("What would you like to post?: ")
            posting_data = sys.stdin.readline().strip('\n')
            parler.submit_post(posting_data)
        elif int(post_data) == 2:
            print(parler.get_feed())