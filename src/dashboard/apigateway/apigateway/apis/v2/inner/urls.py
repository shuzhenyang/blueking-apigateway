# -*- coding: utf-8 -*-
#
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - API 网关 (BlueKing - APIGateway) available.
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
from django.urls import include, path

from . import views

urlpatterns = [
    # /api/v2/inner/ 用于 paasv3 内部调用; 鉴权：来自于网关（主动授权）
    # 所有的接口必须隐藏 + 不允许申请权限（需主动授权）
    # 作为 resource 注册到网关时
    # 1. isPublic: false              不公开
    # 2. allowApplyPermission: false  不允许申请权限 (走的是 主动授权)
    # 3. authConfig:
    #      userVerifiedRequired: false   不需要用户认证
    #      appVerifiedRequired: true     需要应用认证
    #      resourcePermissionRequired: true 需要资源权限
    path(
        "gateways/",
        include(
            [
                # GET /api/v2/inner/gateways/
                path("", views.GatewayListApi.as_view(), name="openapi.v2.inner.gateway.list"),
                path(
                    "<slug:gateway_name>/",
                    include(
                        [
                            # GET /api/v2/inner/gateways/{gateway_name}/
                            path("", views.GatewayRetrieveApi.as_view(), name="openapi.v2.inner.gateway.retrieve"),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
