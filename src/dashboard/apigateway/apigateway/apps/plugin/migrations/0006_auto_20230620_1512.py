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
# Generated by Django 3.2.18 on 2023-06-20 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plugin', '0005_auto_20230227_2006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pluginbinding',
            name='scope_type',
            field=models.CharField(choices=[('stage', '环境'), ('resource', '资源')], db_index=True, max_length=32),
        ),
        migrations.AlterField(
            model_name='pluginconfig',
            name='description',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='pluginconfig',
            name='description_en',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
