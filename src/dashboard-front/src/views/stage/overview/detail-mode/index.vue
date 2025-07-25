<template>
  <div>
    <!-- 自定义头部 -->
    <stage-top-bar ref="stageTopBarRef" />
    <div class="detail-mode">
      <bk-alert
        v-if="!stageStore.realStageMainLoading && stageData.status === 0 && stageData.release.status !== 'unreleased'"
        theme="warning"
        :title="t('当前环境已下架，所有内容的更新均不会生效，如需重新启用，需要重新发布')" style="margin-bottom: 16px;" />
      <bk-alert
        v-if="common.isProgrammableGateway"
        :title="t('可编程网关的环境由平台内置，不能修改和新增')"
        class="mb24"
        closable
      />
      <bk-loading :loading="stageStore.realStageMainLoading">
        <section class="stage-info">
          <div :class="['stage-name', stageData.release.status === 'unreleased' ? 'no-release' : '']">
            <template v-if="stageData.release.status === 'unreleased'">
              <span class="no-release-label">{{ t('未发布') }}</span>
              <span class="no-release-label">{{ t('未发布') }}</span>
              <span class="no-release-dot"></span>
              <!-- <span class="no-release-icon apigateway-icon icon-ag-edit-line" @click="handleEditStage">
              </span> -->
            </template>
            <span class="name">
              {{ stageData.name }}
            </span>
          </div>
          <div class="info">
            <div class="column">
              <div class="apigw-form-item">
                <div class="label">{{ `${t('访问地址')}：` }}</div>
                <div class="value url">
                  <p
                    class="link"
                    v-bk-tooltips="{ content: getStageAddress(stageData.name) }"
                  >
                    {{ getStageAddress(stageData.name) || '--' }}
                  </p>
                  <i
                    class="apigateway-icon icon-ag-copy-info"
                    v-if="getStageAddress(stageData.name)"
                    @click.self.stop="copy(getStageAddress(stageData.name))"
                  ></i>
                </div>
              </div>
              <div class="apigw-form-item">
                <div class="label">{{ `${t('当前资源版本')}：` }}</div>
                <div class="value">
                  <span
                    class="unrelease"
                    v-if="stageData.release.status === 'unreleased'"
                  >
                    --
                  </span>
                  <span v-else>{{ stageData.resource_version.version || '--' }}</span>
                  <bk-tag
                    v-if="getStatus(stageData) === 'doing'" class="ml8" style="height: 16px;font-size: 10px;"
                    theme="info"
                  >
                    {{ stageData.publish_version }} {{ t('发布中') }}
                  </bk-tag>
                </div>
              </div>
              <div class="apigw-form-item">
                <div class="label">{{ `${t('描述')}：` }}</div>
                <div class="value">
                  {{ stageData.description || '--' }}
                </div>
              </div>
            </div>
            <div class="column">
              <div class="apigw-form-item">
                <div class="label">{{ `${t('发布人')}：` }}</div>
                <div class="value">
                  <bk-user-display-name :user-id="stageData.release.created_by" />
                </div>
              </div>
              <div class="apigw-form-item">
                <div class="label">{{ `${t('发布时间')}：` }}</div>
                <div class="value">
                  {{ stageData.release.created_time || '--' }}
                </div>
              </div>
              <div class="apigw-form-item">
                <div class="label">{{ `${t('创建时间')}：` }}</div>
                <div class="value">
                  {{ stageData.created_time || '--' }}
                </div>
              </div>
            </div>
          </div>
          <div class="operate">
            <div class="line"></div>
            <bk-button
              v-if="!basicInfoData.status"
              v-bk-tooltips="{ content: t('当前网关已停用，如需使用，请先启用'), delay: 300 }"
              class="mr10"
              disabled
              theme="primary"
            >
              {{ t('发布资源') }}
            </bk-button>
            <bk-button
              v-else
              theme="primary"
              class="mr10"
              v-bk-tooltips="{
                content: getStatus(stageData) === 'doing'
                  ? t('当前有版本正在发布，请稍后再操作')
                  : (stageData?.publish_validate_msg || '--'),
                disabled: getStatus(stageData) !== 'doing' && !stageData?.publish_validate_msg
              }"
              :disabled="!!stageData?.publish_validate_msg || getStatus(stageData) === 'doing'"
              @click="handleRelease">
              {{ t('发布资源') }}
            </bk-button>
            <bk-button
              v-if="common.curApigwData?.kind !== 1"
              v-bk-tooltips="{
                content: t('当前有版本正在发布，请稍后再操作'),
                disabled: getStatus(stageData) !== 'doing'
              }"
              class="mr10"
              @click="handleEditStage"
              :disabled="getStatus(stageData) === 'doing'"
            >
              {{ t('编辑') }}
            </bk-button>
            <bk-dropdown v-model:is-show="showDropdown" trigger="click">
              <bk-button class="more-cls" @click="showDropdown = true">
                <i class="apigateway-icon icon-ag-gengduo" />
              </bk-button>
              <template #content>
                <bk-dropdown-menu ext-cls="stage-more-actions">
                  <bk-dropdown-item
                    :ext-cls="stageData.status !== 1 ? 'disabled' : ''"
                    v-bk-tooltips="
                      stageData.release.status === 'unreleased' ?
                        t('尚未发布，不可下架') :
                        stageData.status === 0 && stageData.release.status !== 'unreleased' ?
                          t('已下架') :
                          t('下架环境')"
                    @click="stageData.status === 1 ? handleStageUnlist() : void 0"
                  >
                    {{ t('下架') }}
                  </bk-dropdown-item>
                  <bk-dropdown-item
                    v-if="common.curApigwData?.kind !== 1"
                    :ext-cls="stageData.status !== 0 ? 'disabled' : ''"
                    v-bk-tooltips="stageData.status === 1 ? t('环境下架后，才能删除') : t('删除环境')"
                    @click="stageData.status === 0 ? handleStageDelete() : void 0"
                  >
                    {{ t('删除') }}
                  </bk-dropdown-item>
                </bk-dropdown-menu>
              </template>
            </bk-dropdown>
          </div>
        </section>
      </bk-loading>
      <div class="mt15">
        <bk-alert
          v-if="common.isProgrammableGateway"
          class="mb15"
        >
          <template #title>
            <div>
              <span>{{ t('可编程网关的配置信息（如后端服务、插件配置、变量配置等）均在代码仓库中声明。') }}</span>
              <bk-button text theme="primary" @click="handleDevGuideClick">{{ t('查看开发指南') }}</bk-button>
            </div>
          </template>
        </bk-alert>
        <bk-alert
          v-else
          class="mb15"
          theme="warning"
        >
          <template #title>
            <div>
              {{ t('修改环境的配置信息（含后端服务配置、插件配置、变量配置）后，会') }}<span
                class="stress"
              >{{ t('立即在线上环境生效，请谨慎操作') }}</span>
            </div>
          </template>
        </bk-alert>
      </div>
      <div class="tab-wrapper">
        <bk-tab
          v-model:active="active"
          type="card-tab"
          @change="handleTabChange"
        >
          <bk-tab-panel
            v-for="item in panels"
            :key="item.name"
            :name="item.name"
            :label="item.label"
            render-directive="if"
          >
            <component
              :is="curTabComponent"
              :stage-id="stageData.id"
              :stage-address="getStageAddress(stageData.name)"
              :version-id="stageData.resource_version.id">
            </component>
          </bk-tab-panel>
        </bk-tab>
      </div>

      <!-- 环境侧边栏 -->
      <edit-stage-sideslider ref="stageSidesliderRef" />

      <!-- 发布资源至环境 -->
      <release-sideslider
        :current-assets="stageData"
        ref="releaseSidesliderRef"
        @closed-on-publishing="handleClosedOnPublishing"
        @release-success="handleReleaseSuccess"
      />

      <!-- 发布可编程网关的资源至环境 -->
      <release-programmable-slider
        ref="releaseProgrammableSliderRef"
        :current-stage="stageData"
        @hidden="handleReleaseSuccess"
        @release-success="handleReleaseSuccess"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  computed,
  onMounted,
  ref,
  shallowRef,
  watch,
} from 'vue';
import { useI18n } from 'vue-i18n';
import {
  useRoute,
  useRouter,
} from 'vue-router';
import {
  InfoBox,
  Message,
} from 'bkui-vue';
import {
  copy,
  getStatus,
} from '@/common/util';
import {
  useCommon,
  useStage,
} from '@/store';
import releaseSideslider from '../comps/release-sideslider.vue';
import releaseProgrammableSlider from '../comps/release-programmable-slider.vue';
import editStageSideslider from '../comps/edit-stage-sideslider.vue';
import stageTopBar from '@/components/stage-top-bar.vue';
import { useGetGlobalProperties } from '@/hooks';
import {
  deleteStage,
  getGateWaysInfo,
  removalStage,
} from '@/http';
import mitt from '@/common/event-bus';
import { BasicInfoParams } from '@/views/basic-info/common/type';

import resourceInfo from './resource-info.vue';
import pluginManage from './plugin-manage.vue';
import variableManage from './variable-manage.vue';

type TabComponents = typeof resourceInfo | typeof pluginManage | typeof variableManage;

const { t } = useI18n();
const stageStore = useStage();
const route = useRoute();
const router = useRouter();
const common = useCommon();

// 全局变量
const globalProperties = useGetGlobalProperties();
const { GLOBAL_CONFIG } = globalProperties;

const releaseSidesliderRef = ref(null);
const releaseProgrammableSliderRef = ref(null);
const stageSidesliderRef = ref(null);
const stageTopBarRef = ref(null);

const showDropdown = ref<boolean>(false);

// 当前tab
const curTabComponent = shallowRef<TabComponents>(resourceInfo);

// 当前环境信息
const stageData: any = computed(() => {
  if (stageStore.curStageData.id !== null) {
    return stageStore.curStageData;
  }
  return {
    name: '',
    description: '',
    description_en: '',
    status: 1,
    created_time: '',
    release: {
      status: '',
      created_time: null,
      created_by: '',
    },
    resource_version: '',
    new_resource_version: '',
    publish_validate_msg: '',
  };
});

// 当前激活name
const active = ref('resourceInfo');
// tab 选项卡
const panels = [
  { name: 'resourceInfo', label: t('资源信息'), component: resourceInfo },
  { name: 'pluginManage', label: t('插件管理'), component: pluginManage },
  { name: 'variableManage', label: t('变量管理'), component: variableManage },
];

// 是否正在删除
const isDeleteLoading = ref(false);

// 网关id
const apigwId = computed(() => common.apigwId);

// 设置动态组件
const setDynamicComponents = (name: string) => {
  const curPanel = panels.find(item => item.name === name) || panels[0];
  curTabComponent.value = curPanel.component;
};

// 发布成功，重新请求环境详情
const handleReleaseSuccess = async () => {
  // stageTopBarRef.value?.getStageDetailFun(stageData.value?.id);
  await mitt.emit('rerun-init');
};

// 处理在版本还在发布时关闭抽屉的情况（刷新 stage 状态）
const handleClosedOnPublishing = () => {
  mitt.emit('rerun-init');
};

// 重新加载子组件
const routeIndex = ref(0);
watch(
  () => route.query,
  () => {
    routeIndex.value += 1;
  },
);

// 选项卡切换
const handleTabChange = (name: string) => {
  setDynamicComponents(name);
  active.value = name;
  // 更新query参数
  router.push({
    query: {
      stage: stageData.value?.name,
      tab: name,
    },
  });
};

// 发布资源
const handleRelease = () => {
  // 普通网关
  if (common.curApigwData?.kind !== 1) {
    releaseSidesliderRef.value?.showReleaseSideslider();
  } else {
    // 可编程网关
    releaseProgrammableSliderRef.value?.showReleaseSideslider();
  }
};

// 下架环境
const handleStageUnlist = async () => {
  showDropdown.value = false;
  InfoBox({
    title: t('确认下架环境？'),
    subTitle: t('可能会导致正在使用该接口的服务异常，请确认'),
    confirmText: t('确认下架'),
    onConfirm: async () => {
      if (isDeleteLoading.value) {
        return;
      }
      isDeleteLoading.value = true;
      const data = {
        status: 0,
      };
      try {
        await removalStage(apigwId.value, stageData.value.id, data);
        Message({
          message: t('下架成功'),
          theme: 'success',
        });
        // 获取网关列表
        await mitt.emit('rerun-init');
        // 开启loading
      } catch (error) {
        console.error(error);
      } finally {
        showDropdown.value = false;
      }
    },
  });
};

// 删除环境
const handleStageDelete = async () => {
  showDropdown.value = false;
  if (stageData.value.name === 'prod') {
    return Message({
      message: t('prod环境不可删除'),
      theme: 'warning',
    });
  }

  InfoBox({
    title: t('确认删除吗？'),
    onConfirm: async () => {
      try {
        await deleteStage(apigwId.value, stageData.value.id);
        Message({
          message: t('删除成功'),
          theme: 'success',
        });
        // 获取网关列表
        await mitt.emit('rerun-init', { isUpdate: false, isDelete: true });
        // 切换前一个环境, 并且不需要获取当前环境详情
        await mitt.emit('switch-stage', true);
        // 开启loading
      } catch (error) {
        console.error(error);
      }
    },
  });
};

// 编辑环境
const handleEditStage = () => {
  stageSidesliderRef.value.handleShowSideslider('edit');
};

// 访问地址
const getStageAddress = (name: string) => {
  const keys: any = {
    api_name: common.apigwName,
    stage_name: name,
    resource_path: '',
  };

  let url = GLOBAL_CONFIG.STAGE_DOMAIN;
  for (const name of Object.keys(keys)) {
    const reg = new RegExp(`{${name}}`);
    url = url?.replace(reg, keys[name]);
  }
  return url;
};

// 当前基本信息
const basicInfoData = ref<BasicInfoParams>({
  status: 1,
  name: '',
  url: '',
  description: '',
  description_en: '',
  public_key_fingerprint: '',
  bk_app_codes: '',
  docs_url: '',
  api_domain: '',
  created_by: '',
  created_time: '',
  public_key: '',
  maintainers: [],
  developers: [],
  is_public: true,
  is_official: false,
  related_app_codes: [],
});

// 获取网关基本信息
const getBasicInfo = async (apigwId: number) => {
  try {
    const res = await getGateWaysInfo(apigwId);
    basicInfoData.value = Object.assign({}, res);
  } catch (e) {
    console.error(e);
  }
};

const handleDevGuideClick = () => {
  const lang = common.curApigwData?.extra_info?.language || 'python';
  if (lang === 'python') {
    window.open('https://github.com/TencentBlueKing/bk-apigateway-framework/blob/master/docs/python.md');
  } else {
    window.open('https://github.com/TencentBlueKing/bk-apigateway-framework/blob/master/docs/golang.md');
  }
};

onMounted(async () => {
  if (route.query.tab !== 'resourceInfo') {
    active.value = (route.query.tab || 'resourceInfo') as string;
    setDynamicComponents(active.value);
  }
  await getBasicInfo(common.apigwId);
});
</script>

<style lang="scss" scoped>
.detail-mode {
  min-width: calc(1280px - 260px);
  padding: 20px 24px;
  font-size: 12px;
  .stage-info {
    display: flex;
    // height: 128px;
    min-height: 128px;
    padding: 24px;
    background: #ffffff;
    box-shadow: 0 2px 4px 0 #1919290d;

    .stage-name {
      width: 120px;
      height: 80px;
      margin-right: 35px;
      background-color: #f0f5ff;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      &.no-release {
        background-color: #f0f1f5;
        .name {
          color: #979ba5;
        }
      }
      .no-release-dot {
        border: 1px solid #c4c6cc;
        background: #f0f1f5;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 2px;
      }
      .no-release-label {
        position: absolute;
        background-color: #fafbfd;
        top: 3px;
        left: 3px;
        border-radius: 2px;
        color: #63656e;
        font-size: 12px;
        padding: 2px 6px;
      }
      .no-release-icon {
        color: #979ba5;
        background-color: #fff;
        border-radius: 4px;
        font-size: 14px;
        position: absolute;
        right: 3px;
        top: 3px;
        padding: 4px;
        cursor: pointer;
      }
    }

    .name {
      padding: 0 3px;
      font-weight: 700;
      font-size: 16px;
      color: #3a84ff;
      display: inline-block;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .info {
    display: flex;
    .column {
      transform: translateY(-8px);
      &:first-child {
        margin-right: 80px;
      }
    }
    .apigw-form-item {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      line-height: 32px;
      color: #63656e;

      .value {
        max-width: 220px;
        color: #313238;

        &.url {
          max-width: 200px;
          display: flex;
          align-items: center;

          .link {
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
          }

          i {
            cursor: pointer;
            color: #3a84ff;
            margin-left: 3px;
            font-size: 12px;
            padding: 3px;
          }
        }
      }
      .unrelease {
        display: inline-block;
        font-size: 10px;
        // color: #fe9c00;
        // background: #fff1db;
        border-radius: 2px;
        padding: 2px 5px;
        line-height: 1;
      }
    }
  }

  .operate {
    display: flex;
    margin-left: 40px;
    .line {
      height: 32px;
      width: 1px;
      background: #dcdee5;
      margin-right: 20px;
    }
  }
}

.tab-wrapper {
  background: #ffffff;
  box-shadow: 0 2px 4px 0 #1919290d;
  border-radius: 0 0 2px 2px;
  font-size: 14px;

  :deep(.bk-tab-panel) {
    min-height: 420px;
  }
  :deep(.bk-tab-content) {
    padding: 24px;
  }
}

.stage-more-actions {
  :deep(.disabled) {
    color: #c4c6cc !important;
    background-color: #fff !important;
    border-color: #dcdee5 !important;
    cursor: not-allowed;
  }
}

.more-cls {
  padding: 5px 7px;
  i {
    transform: rotate(90deg);
    font-size: 16px;
  }
}
.stress {
  color: red;
}
</style>
