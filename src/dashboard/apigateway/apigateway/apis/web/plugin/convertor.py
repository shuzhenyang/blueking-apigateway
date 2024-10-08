#
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - API 网关(BlueKing - APIGateway) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
#
"""
插件数据转换器

- 前端插件表单和后端存储的数据，可能不一致，需要自定义转换逻辑
- 尽量使用插件表单的数据，减少不必要的转换

-------------------

为了更好的支持插件表单的编辑和展示，前端产生的数据直接存储，不做任何转换; apisix 使用的配置单独在发布时做处理

NOTE:
1. 新插件尽量不写 convertor, 直接保存表单的数据，在 转换成 apisix 配置的时候，进行转换 (以确保编辑态的数据顺序和内容)
2. 存量已经编写了 convertor 的插件暂时不动
"""

import ast
import json
from typing import Any, ClassVar, Dict

from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from apigateway.apps.plugin.constants import PluginTypeCodeEnum
from apigateway.utils.yaml import yaml_dumps, yaml_loads


class BasePluginYamlConvertor:
    def to_internal_value(self, payload: str) -> str:
        return payload

    def to_representation(self, payload: str) -> str:
        return payload


class RateLimitYamlConvertor(BasePluginYamlConvertor):
    """
    前端传入的数据样例
    rates:
      default:
        period: 1
        tokens: 1
      specials:
        - period: 1
          bk_app_code: test
          tokens: 10

    存储的数据样例
    rates:
      __default:
        - period: 1
          tokens: 1
      test:
        - period: 1
          tokens: 10
    """

    def to_internal_value(self, payload: str) -> str:
        loaded_data = yaml_loads(payload)

        result: Dict[str, dict] = {"rates": {}}
        # 特殊应用频率
        for item in loaded_data["rates"].get("specials", []):
            bk_app_code = item["bk_app_code"]
            if bk_app_code in result["rates"]:
                raise ValidationError(
                    {"bk_app_code": _(f"蓝鲸应用ID重复: {bk_app_code}").format(bk_app_code=bk_app_code)}
                )

            result["rates"][bk_app_code] = [{"period": item["period"], "tokens": item["tokens"]}]

        # 蓝鲸应用默认频率
        default_rate = loaded_data["rates"]["default"]
        result["rates"]["__default"] = [{"period": default_rate["period"], "tokens": default_rate["tokens"]}]

        return yaml_dumps(result)

    def to_representation(self, payload: str) -> str:
        loaded_data = yaml_loads(payload)

        result: Dict[str, dict] = {"rates": {"default": {}, "specials": []}}
        for bk_app_code, rates in loaded_data["rates"].items():
            # 目前仅支持单个频率配置
            rate = rates[0]

            if bk_app_code == "__default":
                result["rates"]["default"] = {"period": rate["period"], "tokens": rate["tokens"]}
            else:
                result["rates"]["specials"].append(
                    {
                        "period": rate["period"],
                        "tokens": rate["tokens"],
                        "bk_app_code": bk_app_code,
                    }
                )

        return yaml_dumps(result)


class IPRestrictionYamlConvertor(BasePluginYamlConvertor):
    def to_representation(self, payload: str) -> str:
        """this is a compatibility method, for old data, convert to new format"""
        # may startswith `whitelist: |-` or `whitelist: |+`
        if payload.startswith(("whitelist: |", "blacklist: |")):
            return payload

        # old: whitelist:\n  - 1.1.1.1\n  - 2.2.2.2\n  - 1.1.1.1/24
        # new: whitelist: |-\n  127.0.0.1\n\n  1.1.1.1\n\n  # abcde\n\n  2.2.2.2\n\n  3.3.3.3
        if payload.startswith("whitelist:") and (not payload.startswith("whitelist: |-")):
            return payload.replace("- ", "").replace("whitelist:", "whitelist: |-")

        if payload.startswith("blacklist:") and (not payload.startswith("blacklist: |-")):
            return payload.replace("- ", "").replace("blacklist:", "blacklist: |-")

        return payload


class RequestValidationYamlConvertor(BasePluginYamlConvertor):
    def to_internal_value(self, payload: str) -> str:
        loaded_data = yaml_loads(payload)
        result: Dict[str, Any] = {}

        if loaded_data["header_schema"]:
            header_schema_result = json.loads(loaded_data["header_schema"])
            result["header_schema"] = header_schema_result

        if loaded_data["body_schema"]:
            body_schema_result = json.loads(loaded_data["body_schema"])
            result["body_schema"] = body_schema_result

        result["rejected_code"] = loaded_data["rejected_code"]
        result["rejected_msg"] = loaded_data["rejected_msg"]

        return json.dumps(result)

    def to_representation(self, payload: str) -> str:
        data = json.loads(payload)

        header_schema_str = ""
        if "header_schema" in data:
            header_schema_str = json.dumps(data["header_schema"])

        body_schema_str = ""
        if "body_schema" in data:
            body_schema_str = json.dumps(data["body_schema"])

        result: Dict[str, Any] = {
            "header_schema": header_schema_str,
            "body_schema": body_schema_str,
            "rejected_code": data["rejected_code"],
            "rejected_msg": data["rejected_msg"],
        }

        return yaml_dumps(result)


class FaultInjectionYamlConvertor(BasePluginYamlConvertor):
    # 这个前端传来的数据转换为存储数据的方法

    def _vars_convert_to_internal_list(self, input_list):
        # 解析每个字符串元素，并将它们转换为列表
        # 如果是 单独一条的数据，示例： ["['arg_height', '!', 15]"]  =>  [[['arg_height', '!', 15]]]
        # 如果是 多条的数据， 示例： ['[ "arg_age","==",18 ]', '[ "arg_age","==",19 ],[ "arg_age","==",20 ]']
        #                转换为： [[['arg_age', '==',18 ]], [['arg_age', '==', 19],['arg_age', '==', 20]]]
        parsed_lists = []
        for item in input_list:
            if (
                item.count(",") > 3
            ):  # 判断逗号是不是大于3个, 如果是ast.literal_eval()方法转换为元组(a,b),所以需要加个list()进行转换
                parsed_lists.append(list(ast.literal_eval(item)))
            else:  # 如果逗号小于3个，则判断它是一条数据
                parsed_lists.append([ast.literal_eval(item)])

        return parsed_lists

    def _vars_convert_to_representation_list(self, input_list):
        # 如果是 单独一条的数据，示例： [[['arg_height', '!', 15]]]  =>  ["['arg_height', '!', 15]"]
        # 如果是 多条的数据， 示例： [[['arg_age', '==',18 ]], [['arg_age', '==', 19],['arg_age', '==', 20]]]
        #                转换为： ['[ "arg_age","==",18 ]', '[ "arg_age","==",19 ],[ "arg_age","==",20 ]'] 以便给前端展示字符串数组
        parsed_lists = []

        for item in input_list:
            # 将子列表的元素转换为字符串，并用逗号分隔
            item_str = ", ".join(str(one) for one in item)  # 获取每一个item里面每一项的
            # 将转换后的字符串添加到列表中
            parsed_lists.append(item_str)

        return parsed_lists

    def _internal_abort_value(self, abort: Dict) -> Dict:
        abort_dict: Dict[str, Any] = {}
        if abort.get("http_status"):
            abort_dict["http_status"] = abort["http_status"]
        if abort.get("body"):
            abort_dict["body"] = abort["body"]
        if abort.get("percentage"):
            abort_dict["percentage"] = abort["percentage"]
        if abort.get("vars"):
            abort_dict["vars"] = self._vars_convert_to_internal_list(abort.get("vars"))
        return abort_dict

    def _internal_delay_value(self, delay: Dict) -> Dict:
        delay_dict: Dict[str, Any] = {}
        if delay.get("duration"):
            delay_dict["duration"] = delay["duration"]
        if delay.get("percentage"):
            delay_dict["percentage"] = delay["percentage"]
        if delay.get("vars"):
            delay_dict["vars"] = self._vars_convert_to_internal_list(delay.get("vars"))
        return delay_dict

    def to_internal_value(self, payload: str) -> str:
        loaded_data = yaml_loads(payload)
        result: Dict[str, Dict] = {}

        abort = loaded_data.get("abort")
        delay = loaded_data.get("delay")

        if abort:
            abort_dict = self._internal_abort_value(abort)
            if abort_dict:
                result["abort"] = abort_dict

        if delay:
            delay_dict = self._internal_delay_value(delay)
            if delay_dict:
                result["delay"] = delay_dict

        return yaml_dumps(result)

    def to_representation(self, payload: str) -> str:
        loaded_data = yaml_loads(payload)
        abort_data = loaded_data.get("abort")
        delay_data = loaded_data.get("delay")

        result: Dict[str, Dict] = {}
        abort_dict: Dict[str, Any] = {}
        delay_dict: Dict[str, Any] = {}

        if abort_data:
            for key in ["body", "http_status", "percentage"]:
                if abort_data.get(key):
                    abort_dict[key] = abort_data[key]
            if abort_data.get("vars"):
                abort_vars = abort_data["vars"]
                abort_dict["vars"] = self._vars_convert_to_representation_list(abort_vars)

            result["abort"] = abort_dict

        if delay_data:
            for key in ["duration", "percentage"]:
                if delay_data.get(key):
                    delay_dict[key] = delay_data.get(key)
            if delay_data.get("vars"):
                delay_dict["vars"] = self._vars_convert_to_representation_list(delay_data["vars"])

            result["delay"] = delay_dict

        return yaml_dumps(result)


class PluginConfigYamlConvertor:
    type_code_to_convertor: ClassVar[Dict[str, BasePluginYamlConvertor]] = {
        PluginTypeCodeEnum.BK_RATE_LIMIT.value: RateLimitYamlConvertor(),
        PluginTypeCodeEnum.BK_IP_RESTRICTION.value: IPRestrictionYamlConvertor(),
        PluginTypeCodeEnum.REQUEST_VALIDATION.value: RequestValidationYamlConvertor(),
        PluginTypeCodeEnum.FAULT_INJECTION.value: FaultInjectionYamlConvertor(),
    }

    def __init__(self, type_code: str):
        self.type_code = type_code

    def to_internal_value(self, payload: str) -> str:
        convertor = self.type_code_to_convertor.get(self.type_code)
        if not convertor:
            return payload
        return convertor.to_internal_value(payload)

    def to_representation(self, payload: str) -> str:
        convertor = self.type_code_to_convertor.get(self.type_code)
        if not convertor:
            return payload
        return convertor.to_representation(payload)
