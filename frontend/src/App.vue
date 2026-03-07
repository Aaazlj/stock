<script setup lang="ts">
import { ref, onMounted, shallowRef } from 'vue'
import * as echarts from 'echarts'

const stockCode = ref('000001')
const chartContainer = ref<HTMLElement | null>(null)
const chartInstance = shallowRef<echarts.ECharts | null>(null)
const loading = ref(false)
const errorMsg = ref('')

const fetchStockData = async () => {
  if (!stockCode.value) {
    errorMsg.value = '请输入股票代码'
    return
  }
  
  errorMsg.value = ''
  loading.value = true
  
  try {
    const response = await fetch(`/api/stock/${stockCode.value}/history`)
    const result = await response.json()
    
    if (result.status === 'success' && result.data && result.data.length > 0) {
      renderChart(result.data)
    } else {
      errorMsg.value = result.message || '获取数据失败，可能无此股票记录或未拉取到。'
      chartInstance.value?.clear()
    }
  } catch (err: any) {
    errorMsg.value = `请求发生错误: ${err.message}`
    chartInstance.value?.clear()
  } finally {
    loading.value = false
  }
}

const renderChart = (data: any[]) => {
  if (!chartInstance.value && chartContainer.value) {
    chartInstance.value = echarts.init(chartContainer.value)
  }
  
  if (!chartInstance.value) return

  const dates = data.map(item => item.date)
  const lineData = data.map(item => item.values) // [open, close, low, high]
  const volumes = data.map((item, index) => [index, item.volume, item.values[0] > item.values[1] ? -1 : 1])

  const option = {
    title: {
      text: `${stockCode.value} 走势概览`,
      left: 0
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    grid: [
      { left: '10%', right: '8%', height: '50%' },
      { left: '10%', right: '8%', top: '65%', height: '20%' }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        axisLabel: { show: false }
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: { show: true }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
      { show: true, xAxisIndex: [0, 1], type: 'slider', bottom: '5%', start: 50, end: 100 }
    ],
    series: [
      {
        name: '日K',
        type: 'candlestick',
        data: lineData,
        itemStyle: {
          color: '#ef232a', // 阳线颜色
          color0: '#14b143', // 阴线颜色
          borderColor: '#ef232a',
          borderColor0: '#14b143'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes.map(item => {
          return {
            value: item[1],
            itemStyle: { color: item[2] === 1 ? '#ef232a' : '#14b143' }
          }
        })
      }
    ]
  }
  
  chartInstance.value.setOption(option, true)
}

onMounted(() => {
  window.addEventListener('resize', () => {
    chartInstance.value?.resize()
  })
})
</script>

<template>
  <div class="app-container">
    <header class="header">
      <h1>日线行情检查器</h1>
      <div class="search-bar">
        <input 
          v-model="stockCode" 
          @keyup.enter="fetchStockData"
          placeholder="输入A股代码，如 000001" 
          type="text" 
        />
        <button @click="fetchStockData" :disabled="loading">查询</button>
      </div>
    </header>
    
    <main class="main-content">
      <div v-if="loading" class="loading">正在获取数据，如果初次调用可能涉及重跑 akshare，耗时较久...</div>
      <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
      
      <div 
        ref="chartContainer" 
        class="chart-container" 
        v-show="!loading && !errorMsg"
      ></div>
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background-color: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #333;
}

.header {
  padding: 20px 40px;
  background-color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  color: #1f2f3d;
}

.search-bar {
  display: flex;
  gap: 10px;
}

.search-bar input {
  padding: 8px 16px;
  font-size: 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  outline: none;
  width: 250px;
  transition: border-color 0.2s;
}

.search-bar input:focus {
  border-color: #409eff;
}

.search-bar button {
  padding: 8px 24px;
  font-size: 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-bar button:hover:not(:disabled) {
  background-color: #66b1ff;
}

.search-bar button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.main-content {
  flex: 1;
  padding: 20px 40px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  overflow: hidden;
}

.loading {
  font-size: 16px;
  color: #909399;
  text-align: center;
  margin-top: 50px;
}

.error {
  font-size: 16px;
  color: #f56c6c;
  text-align: center;
  margin-top: 50px;
  background-color: #fef0f0;
  padding: 20px;
  border-radius: 4px;
}

.chart-container {
  flex: 1;
  min-height: 400px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 20px;
}
</style>
