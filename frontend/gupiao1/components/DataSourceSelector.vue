<template>
    <view class="data-source-selector" style="background-color: #2a2a2a; padding: 4px 8px; border-radius: 15px; display: flex; align-items: center;">
        <picker mode="selector" :range="dataSources" @change="onPickerChange" :value="currentSourceIndex" style="width: 100%; height: 100%;">
            <view class="picker-view" style="display: flex; align-items: center; height: 100%;">
                <text class="source-label" style="font-size: 14px; color: #bbb;">数据源:</text>
                <text class="source-value" style="font-size: 14px; color: #4c8dff; margin-left: 4px;">{{ dataSourceNames[dataSources[currentSourceIndex]] }}</text>
                <text class="source-icon" style="font-size: 12px; color: #999; margin-left: 4px;">▼</text>
            </view>
        </picker>
    </view>
</template>

<script>
export default {
    props: {
        defaultSource: {
            type: String,
            default: 'auto'
        }
    },
    data() {
        return {
            dataSources: ['auto', 'tdx', 'ths', 'compare'],
            dataSourceNames: {
                'auto': '自动',
                'tdx': '通达信',
                'ths': '同花顺',
                'compare': '对比模式'
            },
            currentSourceIndex: 0
        }
    },
    created() {
        // 根据默认数据源设置初始选中索引
        this.currentSourceIndex = this.dataSources.indexOf(this.defaultSource);
        if (this.currentSourceIndex === -1) {
            this.currentSourceIndex = 0;
        }
    },
    methods: {
        onPickerChange(e) {
            const index = e.detail.value;
            this.currentSourceIndex = index;
            const source = this.dataSources[index];
            this.$emit('change', source);
        }
    }
}
</script>

<style>
.data-source-selector {
    display: flex;
    align-items: center;
    background-color: #2a2a2a !important;
    padding: 4px 8px;
    border-radius: 15px;
}

.picker-view {
    display: flex;
    align-items: center;
    height: 100%;
}

.source-label {
    font-size: 14px;
    color: #bbb !important;
}

.source-value {
    font-size: 14px;
    color: #4c8dff !important;
    margin-left: 4px;
}

.source-icon {
    font-size: 12px;
    color: #999 !important;
    margin-left: 4px;
}
</style> 
