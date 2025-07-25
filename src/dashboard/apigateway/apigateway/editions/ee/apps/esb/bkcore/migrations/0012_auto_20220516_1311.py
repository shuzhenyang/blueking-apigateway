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
# Generated by Django 2.0.13 on 2022-05-16 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bkcore", "0011_auto_20220422_1534"),
    ]

    operations = [
        migrations.AddField(
            model_name="componentsystem",
            name="comment_en",
            field=models.TextField(blank=True, default=None, null=True, verbose_name="备注(en)"),
        ),
        migrations.AddField(
            model_name="doccategory",
            name="name_en",
            field=models.CharField(blank=True, default=None, max_length=32, null=True, verbose_name="名称(en)"),
        ),
    ]
