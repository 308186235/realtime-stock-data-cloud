# 市场数据获取说明

本系统利用多个数据源获取股票市场数据,目前支持通达信和同花顺两种数据源,可以单独使用或组合使用以获取更全面的数据。

## 支持的数据源

### 1. 通达信数据源

通达信数据源支持从本地通达信安装路径或网络API获取数据。

#### 本地通达信数据

如果您本地安装了通达信软件,系统会自动尝试在以下位置查找通达信安装目录:

- C:/Program Files/通达信
- C:/通达信
- D:/通达信
- E:/通达信

如果通达信安装在其他位置,您可以在启动系统时指定通达信路径:

```python
# 在代码中指定
from services.market_data_service import MarketDataService
market_data_service = MarketDataService(tdx_path="您的通达信安装路径")

# 或在配置文件中设置
TDX_PATH = "您的通达信安装路径"
```

### 2. 同花顺数据源

同花顺数据源通过同花顺网站API获取数据,不需要本地安装同花顺软件。系统会自动从同花顺网站和接口获取数据,如果同花顺接口不可用,会自动切换到备用数据源。

## 数据源管理

系统提供了三种模式来使用数据源:

1. **单一数据源模式**:仅使用通达信或同花顺数据源
2. **自动选择模式**:系统自动选择最佳数据源(默认模式)
3. **数据合并模式**:合并多个数据源的数据,获取更完整的数据集

### 使用示例

```python
# 使用通达信数据源
data_tdx = market_data_service.get_k_data(code="600000", data_source="tdx")

# 使用同花顺数据源
data_ths = market_data_service.get_k_data(code="600000", data_source="ths")

# 自动选择最佳数据源
data_auto = market_data_service.get_k_data(code="600000", data_source="auto")

# 合并多个数据源的数据
data_merged = market_data_service.merge_data_sources(code="600000")
```

## 数据缓存

为提高性能,系统对获取的数据进行缓存:

- 内存缓存:频繁使用的数据(如股票列表,指数数据)会保存在内存中
- 文件缓存:所有请求的数据都会缓存到硬盘,默认缓存路径为 `data/cache`

默认缓存时间为1天,可以通过API参数修改缓存行为:

```python
# 不使用缓存,强制刷新数据
data = market_data_service.get_stock_list(use_cache=False)

# 使用缓存,但缓存时间缩短为半天(0.5天)
data = market_data_service.get_k_data(code="600000", use_cache=True, cache_days=0.5)

# 清除指定数据源的缓存
market_data_service.clear_cache(data_source="ths")
```

## API接口说明

### 获取股票列表

```python
# 获取所有股票 (自动选择数据源)
stocks = market_data_service.get_stock_list()

# 使用通达信获取所有股票
stocks_tdx = market_data_service.get_stock_list(data_source="tdx")

# 使用同花顺获取所有股票
stocks_ths = market_data_service.get_stock_list(data_source="ths")

# 获取特定行业的股票
bank_stocks = market_data_service.get_industry_stocks("银行")
```

### 获取K线数据

```python
# 获取日K线数据(默认过去一年),自动选择数据源
daily_data = market_data_service.get_k_data(code="600000")

# 使用通达信获取指定时间段的周K线数据
weekly_data = market_data_service.get_k_data(
    code="600000",
    start_date="2022-01-01",
    end_date="2023-01-01",
    freq="weekly",
    data_source="tdx"
)

# 合并多个数据源的数据,获取更完整的数据集
merged_data = market_data_service.merge_data_sources(
    code="600000",
    start_date="2022-01-01",
    end_date="2023-01-01"
)
```

### 获取实时行情

```python
# 获取单只股票实时行情 (自动选择数据源)
quote = market_data_service.get_realtime_quotes("600000")

# 使用同花顺获取多只股票实时行情
quotes = market_data_service.get_realtime_quotes(
    ["600000", "000001"], 
    data_source="ths"
)
```

### 获取指数数据

```python
# 获取上证指数数据 (自动选择数据源)
sh_index = market_data_service.get_index_data("000001")

# 使用通达信获取深证成指数据
sz_index = market_data_service.get_index_data(
    "399001",
    data_source="tdx"
)
```

### 比较数据源

系统还提供了比较不同数据源数据差异的功能:

```python
# 比较通达信和同花顺的数据差异
comparison = market_data_service.compare_data_sources("600000")
```

## 前端使用说明

在前端,可以通过 `marketDataService` 服务访问所有数据接口,并可以指定数据源:

```javascript
import marketDataService from '@/services/marketDataService';

// 获取股票列表 (自动选择数据源)
async function getStocks() {
  const response = await marketDataService.getStockList();
  if (response.success) {
    const stocks = response.data;
    // 处理数据...
  }
}

// 使用同花顺获取K线数据
async function getStockData(code) {
  const params = {
    start_date: '2022-01-01',
    end_date: '2023-01-01',
    freq: 'daily',
    data_source: 'ths'
  };
  
  const response = await marketDataService.getKData(code, params);
  if (response.success) {
    const kData = response.data;
    // 处理K线数据...
  }
}

// 合并多个数据源获取数据
async function getMergedData(code) {
  const params = {
    merge_sources: true
  };
  
  const response = await marketDataService.getKData(code, params);
  if (response.success) {
    const kData = response.data;
    // 处理K线数据...
  }
}

// 比较不同数据源的数据差异
async function compareDataSources(code) {
  const response = await marketDataService.compareDataSources(code);
  if (response.success) {
    const tdxData = response.data.tdx.data;
    const thsData = response.data.ths.data;
    // 比较数据差异...
  }
}
```

### 数据源选择UI组件

系统提供了方便的UI组件来选择数据源,这些组件位于 `components` 目录下:

1. **DataSourceSelector** - 通用数据源选择器组件,可在任何页面使用:

```html
<template>
  <DataSourceSelector :defaultSource="dataSource" @change="onDataSourceChange" />
</template>

<script>
import DataSourceSelector from '@/components/DataSourceSelector.vue';

export default {
  components: { DataSourceSelector },
  data() {
    return {
      dataSource: 'auto'  // 默认为自动选择
    }
  },
  methods: {
    onDataSourceChange(source) {
      this.dataSource = source;  // 可能是 'auto', 'tdx', 'ths', 或 'merge'
      this.fetchData();  // 使用新选择的数据源重新获取数据
    }
  }
}
</script>
```

2. **StockChart** - 集成了数据源选择的股票K线图表组件:

```html
<template>
  <StockChart :code="stockCode" :title="stockName" :showCompare="true" />
</template>

<script>
import StockChart from '@/components/StockChart.vue';

export default {
  components: { StockChart },
  data() {
    return {
      stockCode: '600000',
      stockName: '浦发银行'
    }
  }
}
</script>
```

这些组件可以在市场概览,股票详情,投资组合等多个页面中复用,以提供一致的数据源选择功能。

### 数据源对比功能

在StockChart组件中,如果启用了showCompare属性,还会显示一个"对比数据源"按钮,点击后可以直观地比较不同数据源(通达信和同花顺)提供的数据差异,帮助用户选择最可靠的数据。

## 注意事项

1. **请求频率限制**:通过网络接口获取数据时,请控制请求频率,避免被服务器限制
2. **数据源选择**:不同的数据源可能有不同的优势,例如:
   - 通达信本地数据速度快,但可能不是最新
   - 同花顺网络数据更新及时,但可能有访问限制
3. **数据一致性**:不同数据源可能存在微小差异,关键计算时建议使用合并后的数据
4. **缓存管理**:长期运行系统可能需要定期清理缓存,可通过API或服务执行清理:

```python
# 清理所有缓存
market_data_service.clear_cache()

# 清理7天前的缓存
market_data_service.clear_cache(older_than_days=7)

# 清理特定类型的缓存
market_data_service.clear_cache(pattern="index_*")

# 清理特定数据源的缓存
market_data_service.clear_cache(data_source="ths")
```

## 故障排除

1. **无法找到通达信安装路径**
   
   如果系统无法自动找到通达信安装路径,会输出警告并切换到网络数据获取。请检查通达信安装路径是否正确,或手动指定路径。

2. **同花顺数据获取失败**

   如果同花顺数据获取失败,系统会自动切换到备用接口。如果两个数据源都失败,请检查网络连接和接口可用性。

3. **数据异常**

   如发现数据异常(如价格,成交量等不符合预期),可以尝试:
   - 清除缓存强制刷新数据
   - 比对多个数据源结果(使用 compareDataSources 功能)
   - 尝试合并数据源(使用 merge_sources 功能)

4. **数据源比较**

   使用系统提供的数据源比较功能,可以帮助您了解不同数据源的差异,选择最适合您需求的数据源或合并策略。 
