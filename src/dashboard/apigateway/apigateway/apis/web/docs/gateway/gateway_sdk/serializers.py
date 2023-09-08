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
from rest_framework import serializers

from apigateway.apps.support.constants import ProgrammingLanguageEnum


class SDKListInputSLZ(serializers.Serializer):
    language = serializers.ChoiceField(choices=ProgrammingLanguageEnum.get_choices())

    class Meta:
        ref_name = "apigateway.apis.web.docs.gateway.gateway_sdk"


class StageSLZ(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        ref_name = "apigateway.apis.web.docs.gateway.gateway_sdk"


class ResourceVersionSLZ(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    display = serializers.CharField(read_only=True)


class SDKSLZ(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    version = serializers.CharField(read_only=True)
    url = serializers.CharField(read_only=True)
    install_command = serializers.CharField(read_only=True)

    class Meta:
        ref_name = "apigateway.apis.web.docs.gateway.gateway_sdk"


class StageSDKOutputSLZ(serializers.Serializer):
    stage = StageSLZ()
    resource_version = ResourceVersionSLZ()
    sdk = SDKSLZ(allow_null=True)


class SDKUsageExampleInputSLZ(serializers.Serializer):
    language = serializers.ChoiceField(choices=ProgrammingLanguageEnum.get_choices())
    stage_name = serializers.CharField()
    resource_name = serializers.CharField()


class SDKUsageExampleOutputSLZ(serializers.Serializer):
    content = serializers.CharField(allow_blank=True)