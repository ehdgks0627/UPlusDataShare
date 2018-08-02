import requests


class UPlusDataManager:
    """
    U+ 데이터가 한번에 1GB밖에 안보내지길래 만든 자동화 툴
    40GB 공유할라하는데 인증까지 40번...?
    일하자 U+ !!!
    """

    def __init__(self):
        """URL을 정의하고 세션을 생성합니다."""
        self.session = requests.Session()
        self.login_url = "https://www.uplus.co.kr/idi/mbrm/info/ReqWbmbLgin.hpi"
        self.auth_req_url = "https://www.uplus.co.kr/sys/comm/RetrievePopSmsAuthNum.hpix"
        self.auth_url = "https://www.uplus.co.kr/sys/comm/RetrieveSmsAuthNumCnfm.hpix"
        self.gift_url = "https://www.uplus.co.kr/ent/spps/cgdc/SaveDataGift.hpi"
        self.cert_key = ""
        self.cert_value = ""

    def set_defualt_header():
        """세션의 해더를 기본값으로 설정합니다."""
        self.session.headers["Accept"] = "*/*"
        self.session.headers["Accept-Encoding"] = "gzip, deflate, br"
        self.session.headers["Accept-Language"] = "ko,ko-KR;q=0.9,en;q=0.8,en-US;q=0.7"
        self.session.headers["Connection"] = "keep-alive"
        self.session.headers["Content-Length"] = "343"
        self.session.headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        self.session.headers["Host"] = "www.uplus.co.kr"
        self.session.headers["HPI_AJAX_TYPE"] = "ajaxCommSubmit"
        self.session.headers["HPI_HTTP_TYPE"] = "ajax"
        self.session.headers["Origin"] = "https://www.uplus.co.kr"
        self.session.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36"
        self.session.headers["X-Requested-With"] = "XMLHttpRequest"

    def login(self, login_id, login_pw):
        """U+에 로그인합니다"""
        self.session.headers["Referer"] = "https://www.uplus.co.kr/home/Index.hpi"
        data = {
            "lginDvCd": "1",
            "eventR": "",
            "evntsrlno": "",
            "menuId": "",
            "myMenuRetCd": "",
            "lgnCtn_top": "1",
            "intgWbmbId1": login_id,
            "intgWbmbPwd1": login_pw,
            "coMymaCd": "N",
            "intgWbmbId": login_id,
            "intgWbmbPwd": login_pw
        }

        response = self.session.post(self.login_url, data=data)
        self.dump_response(response, False)

        return True

    def auth_req_sms(self, sender):
        """SMS 인증을 요청합니다."""
        self.session.headers["Referer"] = "https://www.uplus.co.kr/sys/comm/RetrieveAuthSMSPage.hpi"
        data = {
            "isOver": "N",
            "ctnNo1": sender.split("-")[0],
            "ctnNo2": sender.split("-")[1],
            "ctnNo3": sender.split("-")[2],
            "ctnNo": "010074699464",
            "ownyn": "Y",
            "CreateAgreeChk02": "on"
        }

        response = self.session.post(self.auth_req_url, data=data)
        self.dump_response(response)

        return True

    def auth_sms(self, sender, auth_code):
        data = {
            "authNum": auth_code,
            "selcCom": "undefined",
            "ctnNo": sender,
            "authSeq": "undefined",
            "ssn": "undefined",
        }

        response = self.session.post(self.auth_url, data=data)
        self.dump_response(response)

        self.cert_key = response.json()[0]
        self.cert_value = response.json()[1]

        return True

    def gift(self, sender, receiver, cnt):
        """데이터를 공유합니다. 공유에 앞서 SMS 인증이 되어야 합니다."""
        self.session.headers["Referer"] = "https://www.uplus.co.kr/ent/spps/cgdc/RetrieveDataGift.hpi"

        data = {
            "rcvProdNo1": receiver.split("-")[0],
            "rcvProdNo2": receiver.split("-")[1],
            "rcvProdNo3": receiver.split("-")[2],
            "ctnNo1": sender.split("-")[0],
            "ctnNo2": sender.split("-")[1],
            "ctnNo3": sender.split("-")[2],
            "rcvData": cnt,
            "ctnNo": sender.replace("-", ""),
            "HPI_SMS_RETURN_FORMNM": "frmForm",
            "HPI_SMS_RETURN_CALLBACKFUNC": "hpi.ent.spps.cgdc.callbackCnfmSMSAuth",
            "certKey": self.cert_key,
            "certValue": self.cert_value,
            "ajaxYn": "Y"
        }

        response = self.session.post(self.gift_url, data=data)
        self.dump_response(response, False)

        return True


    def send_data(self, sender, receiver, cnt, auth_code):
        self.auth_sms(sender, auth_code)
        self.gift(sender, receiver, cnt)

    def dump_response(self, response, dump_data=True):
        assert(type(response) == requests.models.Response)
        print("Status Code : " + str(response.status_code))
        if dump_data:
            print("Response Data : " + response.text)

