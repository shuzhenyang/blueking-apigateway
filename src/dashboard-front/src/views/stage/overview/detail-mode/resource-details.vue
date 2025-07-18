<template>
  <div class="release-sideslider">
    <bk-sideslider
      v-model:is-show="isShow"
      :width="960"
      :title="`${t('资源详情')}【${info.name}】`"
      quick-close
      @hidden="emit('hidden')"
    >
      <template #default>
        <div class="sideslider-content">
          <p
            class="title mt15"
          >
            {{ t("基本信息") }}
          </p>
          <bk-container class="ag-kv-box" :col="14" :margin="6">
            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("资源名称") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">
                  {{ currentSource.name }}
                </div>
              </bk-col>
            </bk-row>

            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("资源地址") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">{{ currentSource.path }}</div>
              </bk-col>
            </bk-row>

            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("描述") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">{{ currentSource.description }}</div>
              </bk-col>
            </bk-row>

            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("标签") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">
                  <template v-if="currentSource.gateway_label_ids?.length">
                    <bk-tag
                      v-for="tag in labels?.filter((label) => {
                        if (currentSource.gateway_label_ids?.includes(label.id))
                          return true;
                      })"
                      :key="tag.id"
                    >{{ tag.name }}</bk-tag
                    >
                  </template>
                  <template v-else>
                    --
                  </template>
                </div>
              </bk-col>
            </bk-row>

            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("认证方式") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">
                  {{
                    getResourceAuth(
                      currentSource?.contexts?.resource_auth?.config
                    )
                  }}</div>
              </bk-col>
            </bk-row>

            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("校验应用权限") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">
                  {{
                    getPermRequired(
                      currentSource?.contexts?.resource_auth?.config
                    )
                  }}
                </div>
              </bk-col>
            </bk-row>

            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("是否公开") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">
                  {{ currentSource?.is_public ? t("是") : t("否") }}
                  {{
                    currentSource?.allow_apply_permission
                      ? `(${t("允许申请权限")})`
                      : `(${t("不允许申请权限")})`
                  }}
                </div>
              </bk-col>
            </bk-row>
          </bk-container>

          <p
            class="title mt15"
          >
            {{ t("请求配置") }}
          </p>
          <bk-container class="ag-kv-box" :col="14" :margin="6">
            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("请求方法") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">
                  <bk-tag :theme="getMethodsTheme(currentSource.method)">
                    {{ currentSource.method }}
                  </bk-tag>
                </div>
              </bk-col>
            </bk-row>

            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("请求路径") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">{{ currentSource.path }}</div>
              </bk-col>
            </bk-row>

            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("启用 Websocket") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">{{ currentSource.enable_websocket ? t('是') : t('否') }}</div>
              </bk-col>
            </bk-row>
          </bk-container>

          <p class="title">
            {{ t('请求参数') }}
          </p>
          <div>
            <div
              v-if="!Object.keys(currentSource.openapi_schema || {}).length || currentSource.openapi_schema.none_schema"
              style="padding-bottom: 24px;color: #313238;"
            >{{ t('该资源无请求参数') }}
            </div>
            <RequestParams v-else :detail="currentSource" readonly />
          </div>

          <p
            class="title mt15"
          >
            {{ t("后端配置") }}
          </p>
          <bk-container class="ag-kv-box" :col="14" :margin="6">
            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("后端服务") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">
                  {{
                    currentSource?.proxy?.backend?.name
                  }}
                </div>
              </bk-col>
            </bk-row>

            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("请求方法") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">
                  <bk-tag :theme="getMethodsTheme(currentSource?.proxy?.config?.method)">
                    {{
                      currentSource?.proxy?.config?.method
                    }}
                  </bk-tag>
                </div>
              </bk-col>
            </bk-row>

            <bk-row v-if="currentSource?.proxy?.config?.timeout !== 0">
              <bk-col :span="4">
                <label class="ag-key">{{ t("自定义超时时间") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">
                  {{ currentSource?.proxy?.config?.timeout }}
                </div>
              </bk-col>
            </bk-row>

            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("请求路径") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">
                  {{
                    currentSource?.proxy?.config?.path
                  }}
                </div>
              </bk-col>
            </bk-row>
          </bk-container>

          <p class="title">
            {{ t("响应参数") }}
          </p>
          <div>
            <ResponseParams
              v-if="Object.keys(currentSource.openapi_schema?.responses || {}).length"
              :detail="currentSource"
              readonly
            />
            <div v-else style="padding-bottom: 24px;color: #313238;">{{ t('该资源无响应参数') }}</div>
          </div>

          <p
            class="title mt15"
          >
            {{ t("文档") }}
          </p>
          <bk-container class="ag-kv-box" :col="14" :margin="6">
            <bk-row>
              <bk-col :span="4">
                <label class="ag-key">{{ t("文档更新时间") }}:</label>
              </bk-col>
              <bk-col :span="10">
                <div class="ag-value">
                  <template v-if="localLanguage === 'en'">
                    {{ currentSource?.doc_updated_time?.en || "--" }}
                  </template>
                  <template v-else>
                    {{ currentSource?.doc_updated_time?.zh || "--" }}
                  </template>
                </div>
              </bk-col>
            </bk-row>
          </bk-container>

          <template v-for="plugin in currentSource.plugins" :key="plugin.id">
            <p class="title plugin-display">
              {{ t("插件") }}: {{ plugin.name }}
            </p>
            <ConfigDisplayTable :plugin="plugin" />
          </template>

        </div>
      </template>
    </bk-sideslider>
  </div>
</template>

<script lang="ts" setup>
import {
  computed,
  ref,
  watch,
} from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import cookie from 'cookie';
import { getGatewayLabels } from '@/http';
import { getMethodsTheme } from '@/common/util';
import ConfigDisplayTable from '@/views/components/plugin-manage/config-display-table.vue';
import RequestParams from '@/views/resource/setting/comps/request-params.vue';
import ResponseParams from '@/views/resource/setting/comps/response-params.vue';

const props = defineProps<{
  info: any;
}>();
const emit = defineEmits(['hidden']);
const { t } = useI18n();
const route = useRoute();
// 网关id
const apigwId = computed(() => +route.params.id);
const localLanguage =  cookie.parse(document.cookie).blueking_language || 'zh-cn';

const isShow = ref(false);
const currentSource = ref<any>({});

// 获取详情数据
const getInfo = () => {
  if (!props.info) return;

  try {
    currentSource.value = props.info || {};
    if (currentSource.value?.proxy?.config) {
      if (typeof currentSource.value?.proxy?.config === 'string') {
        currentSource.value.proxy.config = JSON.parse(currentSource.value?.proxy?.config);
      } else {
        currentSource.value.proxy.config = {};
      }
    }
  } catch (e) {
    console.log(e);
  }
};
getInfo();

const getResourceAuth = (authStr: string) => {
  if (!authStr) return '';

  const auth = JSON.parse(authStr);
  const tmpArr: string[] = [];

  if (auth?.auth_verified_required) {
    tmpArr.push(`${t('用户认证')}`);
  }
  if (auth?.app_verified_required) {
    tmpArr.push(`${t('蓝鲸应用认证')}`);
  }
  return tmpArr.join(', ');
};

const getPermRequired = (authStr: string) => {
  if (!authStr) return '';

  const auth = JSON.parse(authStr);
  if (auth?.resource_perm_required) {
    return `${t('校验')}`;
  }
  return `${t('不校验')}`;
};

// 显示侧边栏
const showSideslider = () => {
  isShow.value = true;
};

// 网关标签
const labels = ref<any[]>([]);
const getLabels = async () => {
  try {
    const res = await getGatewayLabels(apigwId.value);
    labels.value = res;
  } catch (e) {
    console.log(e);
  }
};
getLabels();

watch(
  () => props.info,
  () => {
    getInfo();
  },
);

defineExpose({
  showSideslider,
});
</script>

<style lang="scss" scoped>
.mb8 {
  margin-bottom: 8px;
}
.mb12 {
  margin-bottom: 12px;
}
.sideslider-content {
  width: 100%;
  padding: 24px 24px 12px;
  box-sizing: border-box;
  overflow-y: auto;
  .log-name {
    font-size: 12px;
    color: #63656e;
    font-weight: 700;
  }
  .title {
    font-size: 13px;
    color: #63656e;
    font-weight: bold;
    padding-bottom: 10px;
    border-bottom: 1px solid #dcdee5;
    margin-bottom: 17px;

    &.plugin-display {
      margin-top: 36px;
      margin-bottom: 6px;
      padding-bottom: 0;
      border-bottom: none;
    }
  }
  .ag-kv-box {
    .bk-grid-row {
      margin-bottom: 12px;
    }
    .ag-key {
      font-size: 14px;
      color: #63656e;
      display: block;
      text-align: right;
      padding-right: 0;
    }
    .ag-value {
      font-size: 14px;
      color: #313238;
    }
  }
}
</style>
<style lang="scss">
.sideslider-rg-version-collapse .bk-collapse-source {
  .bk-collapse-header {
    background-color: #f0f1f5;
  }
  .bk-collapse-content {
    padding: 12px 0px 24px;
  }
}
</style>
