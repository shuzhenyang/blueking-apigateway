# -*- coding: utf-8 -*-
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
import random

from faker import Faker

fake = Faker()


def generate_example(schema):
    """
    根据jsonschema 返回 example
    """
    if "example" in schema:
        return schema["example"]

    if "enum" in schema:
        return random.choice(schema["enum"])

    type_handlers = {
        "object": handle_object,
        "array": handle_array,
        "string": handle_string,
        "integer": handle_integer,
    }

    handler = type_handlers.get(schema["type"], handle_default)
    return handler(schema)


def handle_object(schema):
    example = {}
    for key, value in schema["properties"].items():
        example[key] = generate_example(value)
    return example


def handle_array(schema):
    return [generate_example(schema["items"])]


def handle_string(schema):
    if "format" in schema and schema["format"] == "email":
        return fake.email()
    return fake.word()


def handle_integer(schema):
    return fake.random_int(min=schema.get("minimum", 0), max=schema.get("maximum", 100))


def handle_default(schema):
    return None
