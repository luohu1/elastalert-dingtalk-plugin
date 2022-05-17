import json

import requests
from elastalert.alerts import Alerter, DateTimeEncoder
from elastalert.util import EAException, elastalert_logger
from requests.exceptions import RequestException


class DingtalkAlerter(Alerter):

    # By setting required_options to a set of strings
    # You can ensure that the rule config file specifies all
    # of the options. Otherwise, ElastAlert will throw an exception
    # when trying to load the rule.
    required_options = frozenset(['dingtalk_webhook', ])

    def __init__(self, rule):
        super(DingtalkAlerter, self).__init__(rule)
        self.dingtalk_webhook = self.rule['dingtalk_webhook']
        self.dingtalk_msgtype = self.rule.get('dingtalk_msgtype', 'markdown')
        self.dingtalk_msgtype = 'markdown'

    # Alert is called
    def alert(self, matches):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json;charset=utf-8"
        }
        title = self.create_title(matches)
        body = self.create_alert_body(matches)
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": body
            },
            "at": {
                "isAtAll": False
            }
        }
        try:
            response = requests.post(self.dingtalk_webhook, data=json.dumps(payload, cls=DateTimeEncoder),
                                     headers=headers, timeout=86400)
            response.raise_for_status()
        except RequestException as e:
            raise EAException("Error posting HTTP Post alert: %s" % e)
        elastalert_logger.info("HTTP Post alert sent.")

    # get_info is called after an alert is sent to get data that is written back
    # to Elasticsearch in the field "alert_info"
    # It should return a dict of information relevant to what the alert does
    def get_info(self):
        return {'type': 'DingtalkAlerter',
                'dingtalk_webhook': self.dingtalk_webhook}
