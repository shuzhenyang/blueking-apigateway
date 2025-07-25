#
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - API 网关(BlueKing - APIGateway) available.
# Copyright (C) 2025 Tencent. All rights reserved.
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

from django.test import TestCase

from apigateway.apps.audit.constants import OpTypeEnum
from apigateway.apps.audit.models import AuditEventLog
from apigateway.biz.audit import Auditor


class TestRecordAuditLog(TestCase):
    def test_record_audit_log(self):
        data = [
            {
                "username": "admin",
                "op_type": OpTypeEnum.CREATE,
                "gateway_id": "1",
                "instance_id": 123,
                "instance_name": "gateway: test",
                "data_before": '{"name": "test"}',
                "data_after": '{"name": "test"}',
                "comment": "test",
            }
        ]
        for test in data:
            Auditor.record_gateway_op_success(**test)
            logs = AuditEventLog.objects.filter(op_object_id="123")
            self.assertTrue(logs.exists())
            self.assertEqual(logs.count(), 1)
