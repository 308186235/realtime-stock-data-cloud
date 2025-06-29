<template>
  <view class="container">
    <u-navbar title="交易指南" :autoBack="true"></u-navbar>
    
    <scroll-view scroll-y class="content-scroll">
      <view class="guideline-container">
        <u-tabs :list="tabsList" :current="currentTab" @change="tabChange"></u-tabs>
        
        <!-- 风险控制 -->
        <view v-if="currentTab === 0" class="tab-content">
          <view class="section">
            <view class="section-header">
              <text class="section-title">交易前必做的3件事</text>
              <text class="section-subtitle">降低踩雷概率</text>
            </view>
            
            <view class="sub-section">
              <u-subsection title="1. 基本面排雷:3个核心指标+2个快速排除法" type="warning">
                <view class="item-block">
                  <view class="item-title">财务三剑客(规避垃圾股):</view>
                  <view class="item-content">
                    <view class="item-point">
                      <text class="bullet">•</text>
                      <text>净利润增长率:近1年＞0,且季度环比增速＞10%(避免业绩下滑股)</text>
                    </view>
                    <view class="item-point">
                      <text class="bullet">•</text>
                      <text>资产负债率:制造业＜60%,科技/消费＜40%(负债过高易暴雷,如房企＞80%慎碰)</text>
                    </view>
                    <view class="item-point">
                      <text class="bullet">•</text>
                      <text>商誉/市值比:＜10%(商誉占比高,如某股商誉50亿,市值200亿,减值风险大)</text>
                    </view>
                  </view>
                </view>
                
                <view class="item-block">
                  <view class="item-title">快速排除法:</view>
                  <view class="item-content">
                    <view class="item-point">
                      <text class="bullet">✅</text>
                      <text>打开F10,看"股东研究":若前十大股东有"信托计划,个人投资者扎堆",且机构持仓＜10%,慎选(可能是庄股)</text>
                    </view>
                    <view class="item-point">
                      <text class="bullet">✅</text>
                      <text>查"监管问询函":近1年被交易所发函问询财务问题的公司,直接拉黑(如康美药业类造假前兆)</text>
                    </view>
                  </view>
                </view>
              </u-subsection>
            </view>
            
            <view class="sub-section">
              <u-subsection title="2. 技术面定趋势:3要素判断多空强弱" type="primary">
                <view class="item-block">
                  <view class="item-title">均线系统:</view>
                  <view class="item-content">
                    <view class="item-point">
                      <text>日线级别,5/10/20日均线呈多头排列(5日均线上穿10日均线,10日均线上穿20日均线),且股价站稳20日均线(中期趋势向上)</text>
                    </view>
                    <view class="item-point">
                      <text>反例:若股价在60日均线下方,且均线空头排列,坚决不抄底(下跌趋势不言底)</text>
                    </view>
                  </view>
                </view>
                
                <view class="item-block">
                  <view class="item-title">成交量:</view>
                  <view class="item-content">
                    <view class="item-point">
                      <text>上涨时成交量需温和放大(较前5日平均量增20%-50%),缩量上涨不可持续;下跌时缩量(较前5日缩量30%以上),说明抛压减轻</text>
                    </view>
                  </view>
                </view>
                
                <view class="item-block">
                  <view class="item-title">MACD背离信号:</view>
                  <view class="item-content">
                    <view class="item-point">
                      <text>股价创新高,但MACD红柱长度缩短(顶背离,见顶信号);股价创新低,MACD绿柱缩短(底背离,见底信号),背离次数越多,反转概率越高(至少出现1次才关注)</text>
                    </view>
                  </view>
                </view>
              </u-subsection>
            </view>
            
            <view class="sub-section">
              <u-subsection title="3. 仓位规划:金字塔建仓法(散户保命关键)" type="success">
                <view class="item-block">
                  <view class="item-content">
                    <view class="item-point">
                      <text class="bullet">•</text>
                      <text>首次建仓:不超过总资金的20%(例:10万元本金,首仓≤2万),用于试错</text>
                    </view>
                    <view class="item-point">
                      <text class="bullet">•</text>
                      <text>加仓条件:买入后股价上涨5%,且回踩5日均线不破,再加20%仓位(避免追高)</text>
                    </view>
                    <view class="item-point">
                      <text class="bullet">•</text>
                      <text>极限仓位:单只个股不超过50%仓位(分散风险,避免单票暴雷腰斩)</text>
                    </view>
                    <view class="item-point warning-text">
                      <text class="bullet">⚠️</text>
                      <text>严禁"一把梭哈":曾有散户满仓某ST股,退市后本金仅剩10%</text>
                    </view>
                  </view>
                </view>
              </u-subsection>
            </view>
          </view>
          
          <view class="section">
            <view class="section-header">
              <text class="section-title">高风险操作警示</text>
              <text class="section-subtitle">杜绝4类高风险操作</text>
            </view>
            
            <view class="table-container">
              <view class="table-header">
                <view class="table-cell">危险行为</view>
                <view class="table-cell">具体表现</view>
                <view class="table-cell">案例(散户常犯)</view>
                <view class="table-cell">后果</view>
              </view>
              
              <view class="table-row">
                <view class="table-cell">追涨杀跌</view>
                <view class="table-cell">看到某股涨5%后追入,跌3%后恐慌割肉</view>
                <view class="table-cell">2023年AI概念股波动时,频繁换股者半年亏损40%</view>
                <view class="table-cell">手续费+价差双重亏损</view>
              </view>
              
              <view class="table-row">
                <view class="table-cell">抄底接刀</view>
                <view class="table-cell">股价暴跌30%后"捡便宜",未等止跌信号</view>
                <view class="table-cell">某新能源股连续跌停,散户越跌越买,最终退市</view>
                <view class="table-cell">本金腰斩</view>
              </view>
              
              <view class="table-row">
                <view class="table-cell">满仓赌单票</view>
                <view class="table-cell">认为"某股必涨",押上所有资金</view>
                <view class="table-cell">2021年某白酒股暴跌,满仓者被迫扛单2年</view>
                <view class="table-cell">资金利用率归零</view>
              </view>
              
              <view class="table-row">
                <view class="table-cell">过度交易</view>
                <view class="table-cell">每周交易＞5次,频繁换股</view>
                <view class="table-cell">统计显示:月交易超20次的散户,80%最终亏损</view>
                <view class="table-cell">手续费吃掉10%本金</view>
              </view>
            </view>
          </view>
        </view>
        
        <!-- 分析方法 -->
        <view v-if="currentTab === 1" class="tab-content">
          <view class="section">
            <view class="section-header">
              <text class="section-title">热点选股:3步锁定主线板块</text>
            </view>
            <view class="item-block">
              <view class="item-content">
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>看政策:中央会议/行业规划出台后,3天内持续有个股涨停(如2023年"新能源汽车下乡"政策后,相关产业链涨3个月)</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>看资金:连续5个交易日,板块成交额占全市场15%以上(用通达信"板块指数"看成交额排名)</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>看龙头:板块内有3只以上个股连板(如智能Agent板块,科大讯飞,拓尔思等多股齐涨,说明资金共识强)</text>
                </view>
                <view class="item-point tip-text">
                  <text class="bullet">💡</text>
                  <text>技巧:每天10:00前看"昨日涨停表现"指数,若该指数涨幅＞2%,且连涨3天,可参与热点接力</text>
                </view>
              </view>
            </view>
          </view>
          
          <view class="section">
            <view class="section-header">
              <text class="section-title">分时图抓拐点:3个经典信号</text>
            </view>
            <view class="item-block">
              <view class="item-content">
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>早盘急跌买点:9:45-10:00,股价快速下跌5%以上,但成交量未放大(量价背离),随后15分钟内收复失地,视为洗盘,可低吸</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>尾盘抢筹信号:14:50后,股价直线拉抬,且分时成交量柱持续放大(每笔成交＞100手),同时量比＞2,次日高开概率70%</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>高位跳水止损:13:30后,股价从涨3%快速跌至-1%,且跌破当天均价线,无论盈亏,立刻卖出(防止尾盘暴跌)</text>
                </view>
              </view>
            </view>
          </view>
          
          <view class="section">
            <view class="section-header">
              <text class="section-title">周末深度分析:5步打造交易系统</text>
            </view>
            <view class="item-block">
              <view class="item-content">
                <view class="item-point">
                  <text class="number">1.</text>
                  <text>板块轮动表:整理本周领涨板块,标注驱动因素(政策/业绩/事件),预判下周持续性</text>
                </view>
                <view class="item-point">
                  <text class="number">2.</text>
                  <text>个股K线库:收集3-5只典型股(如本周龙头股,暴跌股),分析其上涨/下跌时的指标共振信号(如"均线多头+MACD金叉+量比放大")</text>
                </view>
                <view class="item-point">
                  <text class="number">3.</text>
                  <text>风险案例集:记录本周踩的坑(如追高被套,没止损导致大亏),用红笔标注"下次遇到XX情况,必须XX"(例:"股价跌破20日均线,30分钟内必卖")</text>
                </view>
                <view class="item-point">
                  <text class="number">4.</text>
                  <text>消息日历:标注下周重要事件(如财报披露日,美联储加息节点),提前规划仓位应对</text>
                </view>
                <view class="item-point">
                  <text class="number">5.</text>
                  <text>指标优化:对比自己常用的MACD,KDJ参数,是否需要调整(如短线改为MACD(5,10,5),提高灵敏度)</text>
                </view>
              </view>
            </view>
          </view>
        </view>
        
        <!-- 操作策略 -->
        <view v-if="currentTab === 2" class="tab-content">
          <view class="section">
            <view class="section-header">
              <text class="section-title">买卖点设定:精准到价格和时间</text>
            </view>
            
            <view class="sub-section">
              <view class="item-title">买入点:</view>
              <view class="item-content">
                <view class="item-point">
                  <text class="bullet">✅</text>
                  <text>技术支撑位:股价回踩前低/缺口/60日均线且缩量,分时图出现"W底"或"三重底"形态,尾盘14:45后买入(避免早盘诱多)</text>
                </view>
                <view class="item-point">
                  <text class="bullet">✅</text>
                  <text>突破确认点:股价放量突破前高(近3个月高点),且10:30前封涨停,打板买入(仅限牛市或热点板块)</text>
                </view>
              </view>
            </view>
            
            <view class="sub-section">
              <view class="item-title">卖出点:</view>
              <view class="item-content">
                <view class="item-point">
                  <text class="bullet">✅</text>
                  <text>止损:跌破买入价的7%(或跌破关键支撑位,如20日均线),无条件止损(例:10元买入,跌到9.3元必须卖,不抱幻想)</text>
                </view>
                <view class="item-point">
                  <text class="bullet">✅</text>
                  <text>止盈:达到目标涨幅(如15%-20%),或出现顶背离信号,分批次卖出(先卖50%,剩50%设移动止损(成本价上移5%))</text>
                </view>
              </view>
            </view>
          </view>
          
          <view class="section">
            <view class="section-header">
              <text class="section-title">仓位动态调整:跟紧大盘节奏</text>
            </view>
            <view class="item-block">
              <view class="item-content">
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>大盘MACD金叉(日线):仓位可提升至60%-80%,重点买强势股</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>大盘跌破60日均线:仓位降至30%以下,仅留现金+防守型板块(如医药,消费)</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>震荡市(布林带收口):采用"高抛低吸",股价碰布林上轨卖30%,碰下轨买30%</text>
                </view>
              </view>
            </view>
          </view>
          
          <view class="section">
            <view class="section-header">
              <text class="section-title">每日15分钟复盘:3个核心问题</text>
            </view>
            <view class="item-block">
              <view class="item-content">
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>买对了吗?:买入逻辑是否成立(如因"业绩预增"买入,是否有公告支撑)</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>卖错了吗?:卖出后股价继续涨,是因为指标背离没看懂,还是情绪恐慌?记录原因</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>仓位合理吗?:本次操作仓位是否符合"金字塔法则",若满仓导致被动,下次如何调整?</text>
                </view>
                <view class="item-point tip-text">
                  <text class="bullet">📒</text>
                  <text>工具:用Excel记录每笔交易(时间,股票,买卖价,仓位,理由,结果),每月统计胜率(＞50%可优化,＜40%需停手反思)</text>
                </view>
              </view>
            </view>
          </view>
          
          <view class="section">
            <view class="section-header">
              <text class="section-title">工具运用:3个免费高效软件</text>
            </view>
            <view class="item-block">
              <view class="item-content">
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>通达信:用"自定义选股"设置条件(如"MACD金叉+量比＞1.5+股价在20日均线上"),每天14:30一键筛选潜力股</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>东方财富:看"资金流向"板块,选"超大单净流入占比＞3%"且"股价在5日均线上"的个股(资金持续流入是上涨动力)</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>同花顺iFinD(免费版):查个股"机构持仓变化",若近3个月社保基金/QFII增持超1%,加入自选股(机构背书安全性高)</text>
                </view>
              </view>
            </view>
          </view>
        </view>
        
        <!-- 心态管理 -->
        <view v-if="currentTab === 3" class="tab-content">
          <view class="section">
            <view class="section-header">
              <text class="section-title">心态管理:3个反人性操作</text>
            </view>
            <view class="item-block">
              <view class="item-content">
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>暴跌日敢买:大盘暴跌2%以上时,筛选"逆市红盘+缩量"的个股(主力护盘迹象),次日反弹概率超60%(例:2022年4月27日暴跌后,抄底新能源的投资者1个月赚30%)</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>暴涨日慎追:板块集体涨停次日,不追后排跟风股(如2024年AI第一天爆发时,追第二梯队的散户多数被套)</text>
                </view>
                <view class="item-point">
                  <text class="bullet">•</text>
                  <text>盈利后减仓:当某只个股盈利超20%,卖出一半仓位,剩余仓位设"成本价止损"(既锁定利润,又保留复利机会)</text>
                </view>
              </view>
            </view>
          </view>
          
          <view class="section">
            <view class="section-header">
              <text class="section-title">长期主义:拒绝3类"快速致富"陷阱</text>
            </view>
            <view class="item-block">
              <view class="item-content warning-list">
                <view class="item-point">
                  <text class="bullet">⚠️</text>
                  <text>荐股群/直播间:99%是杀猪盘(先免费推票吸引信任,再让接盘庄股,如2023年某财经大V带人接盘某退市股,散户集体维权)</text>
                </view>
                <view class="item-point">
                  <text class="bullet">⚠️</text>
                  <text>杠杆/配资:10倍杠杆看似暴利,实际股价跌10%就爆仓(2015年股灾中,无数散户因配资血本无归)</text>
                </view>
                <view class="item-point">
                  <text class="bullet">⚠️</text>
                  <text>短线频繁博弈:统计显示,A股散户年化交易成本占本金8%-15%,过度交易相当于"给券商打工"</text>
                </view>
              </view>
            </view>
          </view>
          
          <view class="section">
            <view class="section-header">
              <text class="section-title">从亏损到盈利的3个阶段</text>
            </view>
            <view class="item-block">
              <view class="item-content">
                <view class="item-point">
                  <text class="number">1.</text>
                  <text>新手期(0-1年):专注"不亏钱",用10%资金练手,重点学止损,仓位管理,允许自己试错,但每笔错误必须记录原因</text>
                </view>
                <view class="item-point">
                  <text class="number">2.</text>
                  <text>成长期(1-3年):建立"单一策略"(如只做尾盘均线回踩股,或只做财报预增股),把一种方法练到精通(胜率＞55%即可稳定盈利)</text>
                </view>
                <view class="item-point">
                  <text class="number">3.</text>
                  <text>成熟期(3年+):根据市场风格切换策略(牛市追涨龙头,熊市潜伏低PE股),但核心纪律不变(止损,分散仓位,不情绪化)</text>
                </view>
              </view>
            </view>
          </view>
          
          <view class="conclusion">
            <view class="conclusion-title">最终目标</view>
            <view class="conclusion-text">
              通过3-6个月的刻意练习,形成自己的"交易 checklist"(如买入前必查5个指标,卖出时必看3个信号),用规则代替感觉,让盈利成为"大概率事件"而非运气。
            </view>
            <view class="conclusion-quote">
              记住:股票交易不是"猜涨跌",而是"用小亏损试错,用大盈利兑现"—— 严格执行纪律,比短期赚多少钱更重要。
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      tabsList: [
        { name: '风险控制' },
        { name: '分析方法' },
        { name: '操作策略' },
        { name: '心态管理' }
      ],
      currentTab: 0
    }
  },
  methods: {
    tabChange(index) {
      this.currentTab = index;
    }
  }
}
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f7fa;
}

.content-scroll {
  flex: 1;
  height: 100%;
}

.guideline-container {
  padding: 15px;
}

.section {
  margin-bottom: 20px;
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.sub-section {
  margin-top: 15px;
  border-left: 3px solid #2979ff;
  padding-left: 10px;
}

.item-block {
  margin-top: 10px;
  margin-bottom: 15px;
}

.item-title {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 5px;
  color: #303133;
}

.item-content {
  padding-left: 5px;
}

.item-point {
  margin-bottom: 10px;
  display: flex;
  align-items: flex-start;
  line-height: 1.5;
}

.bullet {
  display: inline-block;
  margin-right: 8px;
  color: #2979ff;
  font-weight: bold;
}

.number {
  display: inline-block;
  margin-right: 8px;
  color: #2979ff;
  font-weight: bold;
}

.warning-text {
  color: #fa3534;
}

.tip-text {
  color: #19be6b;
}

.table-container {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.table-header {
  display: flex;
  background-color: #f8f8f9;
  font-weight: bold;
}

.table-row {
  display: flex;
  border-top: 1px solid #ebeef5;
}

.table-cell {
  flex: 1;
  padding: 12px 8px;
  font-size: 14px;
  border-right: 1px solid #ebeef5;
  word-break: break-all;
}

.table-cell:last-child {
  border-right: none;
}

.warning-list .item-point {
  color: #fa3534;
}

.conclusion {
  background-color: #ecf5ff;
  padding: 15px;
  border-radius: 8px;
  margin-top: 20px;
}

.conclusion-title {
  font-size: 18px;
  font-weight: bold;
  color: #2979ff;
  margin-bottom: 10px;
}

.conclusion-text {
  line-height: 1.6;
  margin-bottom: 15px;
}

.conclusion-quote {
  font-style: italic;
  color: #606266;
  padding-left: 10px;
  border-left: 3px solid #2979ff;
  line-height: 1.6;
}

.section-header {
  margin-bottom: 15px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #2979ff;
  display: block;
}

.section-subtitle {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
  display: block;
}
</style> 
 
