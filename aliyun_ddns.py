#!/usr/bin/env python
# coding=utf-8

import os
import time
import sys
import urllib.request
from typing import List

from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_alidns20150109.client import Client as Alidns20150109Client

# AccessKey ID and AccessKey Secret
ACCESS_KEY_ID = '<PUT-IN-YOUR-ACCESS_KEY_ID-HERE>'
ACCESS_KEY_SECRET = 'PUT-IN-YOUR-ACCESS_KEY_SECRET-HERE'
# Domain name and sub domain name
DOMAIN_NAME = 'example.com'
RRKEY_WORD = 'device.ddns'


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> Alidns20150109Client:
        config = open_api_models.Config(
            access_key_id=ACCESS_KEY_ID,
            access_key_secret=ACCESS_KEY_SECRET
        )
        config.endpoint = 'alidns.cn-hangzhou.aliyuncs.com'
        return Alidns20150109Client(config)

    @staticmethod
    def describe_domain_record(
        args: List[str],
    ) -> None:
        client = Sample.create_client('accessKeyId', 'accessKeySecret')
        describe_domain_records_request = alidns_20150109_models.DescribeDomainRecordsRequest(
            domain_name=DOMAIN_NAME,
            rrkey_word=RRKEY_WORD
        )
        runtime = util_models.RuntimeOptions()
        try:
            return client.describe_domain_records_with_options(
                describe_domain_records_request, runtime)
        except Exception as error:
            print(error)
            UtilClient.assert_as_string(error.message)

    @staticmethod
    def add_domain_record(
        args: List[str],
    ) -> None:
        client = Sample.create_client('accessKeyId', 'accessKeySecret')
        add_domain_record_request = alidns_20150109_models.AddDomainRecordRequest(
            domain_name=DOMAIN_NAME,
            rr=RRKEY_WORD,
            type='A',
            value=args[0]
        )
        runtime = util_models.RuntimeOptions()
        try:
            return client.add_domain_record_with_options(
                add_domain_record_request, runtime)
        except Exception as error:
            print(error)
            UtilClient.assert_as_string(error.message)

    @staticmethod
    def update_domain_record(
        args: List[str],
    ) -> None:
        client = Sample.create_client('accessKeyId', 'accessKeySecret')
        update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
            record_id=args[1],
            type='A',
            rr=RRKEY_WORD,
            value=args[0]
        )
        runtime = util_models.RuntimeOptions()
        try:
            return client.update_domain_record_with_options(
                update_domain_record_request, runtime)
        except Exception as error:
            print(error)
            UtilClient.assert_as_string(error.message)


def wirte_to_file(path, content):
    with open(path, 'w') as f:
        f.write(content)


def get_internet_ip():
    with urllib.request.urlopen('http://www.3322.org/dyndns/getip') as response:
        html = response.read()
        ip = str(html, encoding='utf-8').replace("\n", "")
    return ip


if __name__ == '__main__':
    while True:
        if os.path.exists("./ip"):
            pass
        else:
            wirte_to_file("./ip", "0.0.0.0")

        ip = get_internet_ip()

        with open("./ip", 'r') as f:
            old_ip = f.read()
        if ip == old_ip:
            print("Local IP did not change.", "\nnew_ip:", ip, "\nold_ip:", old_ip)
        else:
            response = Sample.describe_domain_record(
                sys.argv[1:]).body.to_map()
            total_count = response["TotalCount"]
            if total_count == 0:
                add_domain_record_result_request_id = Sample.add_domain_record([ip]).body.to_map()[
                    "RequestId"]
                if add_domain_record_result_request_id:
                    print("Add domain record succeeded! RequestId:",
                          add_domain_record_result_request_id)
                wirte_to_file("./ip", ip)
                print("Local IP has been changed.", "\nnew_ip:", ip, "\nold_ip:", old_ip)
            elif total_count == 1:
                record_id = response["DomainRecords"]["Record"][0]["RecordId"]
                update_domain_record_result_request_id = Sample.update_domain_record(
                    [ip, record_id]).body.to_map()["RequestId"]
                print("Update domain record succeeded! RequestId:",
                      update_domain_record_result_request_id)
                wirte_to_file("./ip", ip)
                print("Local IP has been changed.", "\nnew_ip:", ip, "\nold_ip:", old_ip)
            else:
                print("There are %d resolve record, please check and delete first！" % total_count)
        time.sleep(600)
