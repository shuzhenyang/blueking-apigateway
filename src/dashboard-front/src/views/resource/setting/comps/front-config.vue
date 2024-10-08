
<template>
  <bk-form
    ref="frontRef"
    :model="frontConfigData"
    :rules="rules"
    class="front-config-container"
    @validate="setInvalidPropId"
  >
    <bk-form-item
      :label="t('请求方法')"
      property="method"
      id="front-config-method"
      required>
      <bk-select
        :input-search="false"
        :clearable="false"
        v-model="frontConfigData.method"
        @change="clearValidate"
        class="method">
        <bk-option v-for="item in methodData" :key="item.id" :value="item.id" :label="item.name" />
      </bk-select>
    </bk-form-item>
    <bk-form-item
      :label="t('请求路径')"
      property="path"
      required>
      <div class="flex-row aligin-items-center">
        <bk-input
          v-model="frontConfigData.path"
          :placeholder="t('斜线(/)开头的合法URL路径，不包含http(s)开头的域名')"
          clearable
          @input="clearValidate"
          class="w700"
          id="front-config-path"
        />
        <bk-checkbox class="ml12" v-model="frontConfigData.match_subpath">
          {{ t('匹配所有子路径') }}
        </bk-checkbox>
      </div>
    </bk-form-item>
    <bk-form-item
      :label="t('启用 WebSocket')"
      property="enable_websocket"
      required>
      <bk-switcher v-model="frontConfigData.enable_websocket" theme="primary" size="small"></bk-switcher>
    </bk-form-item>
  </bk-form>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCommon } from '../../../../store';
import mitt from '@/common/event-bus';

const props = defineProps({
  detail: {
    type: Object,
    default: {},
  },
  isClone: {
    type: Boolean,
    default: false,
  },
});

const frontRef = ref(null);
const { t } = useI18n();
const cloneTips = ref(t('请求方法+请求路径在网关下唯一，请至少调整其中一项'));
const common = useCommon();
const frontConfigData = ref({
  path: '',
  method: 'GET',
  match_subpath: false,
  enable_websocket: false,
});

const cloneData = ref({
  path: '',
  method: '',
});
const methodData = ref(common.methodList);

const rules = ref<any>({
  method: [
    {
      validator: (value: string) => {
        if (!value) return true;
        return value !== cloneData.value.method || frontConfigData.value.path !== cloneData.value.path;
      },
      message: cloneTips.value,
      trigger: 'blur',
    },
  ],
  path: [
    {
      validator: (value: string) => {
        console.log('value', value);
        if (!value) return true;
        return value !== cloneData.value.path || frontConfigData.value.method !== cloneData.value.method;
      },
      message: cloneTips.value,
      trigger: 'blur',
    },
    {
      required: true,
      message: t('请求路径不能为空'),
      trigger: 'blur',
    },
    {
      validator: (value: string) => /^\/[\w{}/.-]*$/.test(value),
      message: t('斜线(/)开头的合法URL路径，不包含http(s)开头的域名'),
      trigger: 'blur',
    },
  ],
});

// 错误表单项的 #id
const invalidFormElementIds = ref<string[]>([]);

watch(
  () => props.detail,
  (val: any) => {
    if (Object.keys(val).length) {
      const { path, method, match_subpath, enable_websocket } = val;
      frontConfigData.value = { path, method, match_subpath, enable_websocket };
      if (props.isClone) {
        cloneData.value = { path, method };
        setTimeout(() => {
          validate();
        }, 500);
      }
    }
  },
  { immediate: true },
);

watch(
  () => frontConfigData.value,
  (val: any) => {
    mitt.emit('front-config', val);
  },
  { deep: true },
);

// 监听表单校验时间，收集 #id
const setInvalidPropId = (property: string, result: boolean) => {
  if (!result) {
    invalidFormElementIds.value.push(`front-config-${property}`);
  }
};

const validate = async () => {
  invalidFormElementIds.value = [];
  await frontRef.value?.validate();
};

// 清除表单验证
const clearValidate = () => {
  frontRef.value?.clearValidate();
};

defineExpose({
  frontConfigData,
  invalidFormElementIds,
  validate,
});
</script>
  <style lang="scss" scoped>
  .front-config-container {
    .method {
      max-width: 700px;
    }
    .public-switch {
        height: 32px;
    }
    .w700 {
      max-width: 700px;
      width: 70%;
    }
    :deep(.bk-checkbox-label) {
      white-space: nowrap;
    }
  }
  </style>
