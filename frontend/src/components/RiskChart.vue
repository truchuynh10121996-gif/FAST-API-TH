<template>
  <div>
    <h3 style="margin-bottom: 1.5rem; color: #FF6B9D; text-align: center; font-size: 1.5rem; font-weight: 700;">
      📊 Biểu đồ So sánh Xác suất Vỡ nợ (PD) từ 4 Models
    </h3>

    <!-- Hướng dẫn đọc -->
    <div class="chart-guide">
      <p class="guide-text">
        📖 <strong>Cách đọc biểu đồ:</strong> Biểu đồ cột so sánh xác suất vỡ nợ (PD) dự báo bởi 4 mô hình AI khác nhau.
        Màu sắc thể hiện mức độ rủi ro: <span class="color-tag green">🟢 Xanh = Thấp</span>,
        <span class="color-tag yellow">🟡 Vàng = Trung bình</span>,
        <span class="color-tag red">🔴 Đỏ = Cao</span>.
        <strong>Stacking Model</strong> là kết quả tổng hợp từ 3 mô hình còn lại và được tin cậy nhất.
      </p>
    </div>

    <!-- Biểu đồ cột duy nhất -->
    <div class="chart-container">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
)

export default {
  name: 'RiskChart',
  components: {
    Bar
  },
  props: {
    prediction: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const chartData = computed(() => {
      const pdStacking = (props.prediction.pd_stacking * 100).toFixed(2)
      const pdLogistic = (props.prediction.pd_logistic * 100).toFixed(2)
      const pdRF = (props.prediction.pd_random_forest * 100).toFixed(2)
      const pdXGB = (props.prediction.pd_xgboost * 100).toFixed(2)

      return {
        labels: ['Stacking', 'Logistic', 'Random Forest', 'XGBoost'],
        datasets: [
          {
            label: 'Xác suất Vỡ nợ (%)',
            data: [pdStacking, pdLogistic, pdRF, pdXGB],
            backgroundColor: [
              getBarColor(pdStacking / 100),
              getBarColor(pdLogistic / 100),
              getBarColor(pdRF / 100),
              getBarColor(pdXGB / 100)
            ],
            borderColor: [
              getBarBorderColor(pdStacking / 100),
              getBarBorderColor(pdLogistic / 100),
              getBarBorderColor(pdRF / 100),
              getBarBorderColor(pdXGB / 100)
            ],
            borderWidth: 3,
            borderRadius: 10
          }
        ]
      }
    })

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            font: {
              size: 15,
              weight: 'bold'
            },
            color: '#FF6B9D',
            padding: 20
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.85)',
          titleFont: {
            size: 15,
            weight: 'bold'
          },
          bodyFont: {
            size: 14
          },
          padding: 15,
          cornerRadius: 10,
          callbacks: {
            label: function(context) {
              const value = context.parsed.y
              let risk = ''
              if (value < 2) risk = '🟢 Rủi ro Rất Thấp (AAA-AA)'
              else if (value < 5) risk = '🟢 Rủi ro Thấp (A-BBB)'
              else if (value < 10) risk = '🟡 Rủi ro Trung bình (BB)'
              else if (value < 20) risk = '🟠 Rủi ro Cao (B)'
              else risk = '🔴 Rủi ro Rất Cao (CCC-D)'
              return `PD: ${value}% - ${risk}`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: 'Xác suất Vỡ nợ (%)',
            font: {
              size: 14,
              weight: 'bold'
            },
            color: '#FF6B9D'
          },
          ticks: {
            callback: function(value) {
              return value + '%'
            },
            font: {
              size: 13,
              weight: 'bold'
            },
            color: '#4A4A4A'
          },
          grid: {
            color: 'rgba(255, 182, 193, 0.2)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Mô hình Dự báo',
            font: {
              size: 14,
              weight: 'bold'
            },
            color: '#FF6B9D'
          },
          ticks: {
            font: {
              size: 13,
              weight: 'bold'
            },
            color: '#4A4A4A'
          },
          grid: {
            display: false
          }
        }
      }
    }

    const getBarColor = (pd) => {
      if (pd < 0.05) return 'rgba(143, 227, 207, 0.8)' // Xanh nhạt
      if (pd < 0.15) return 'rgba(255, 224, 138, 0.8)' // Vàng nhạt
      return 'rgba(255, 138, 138, 0.8)' // Đỏ nhạt
    }

    const getBarBorderColor = (pd) => {
      if (pd < 0.05) return '#00a651' // Xanh đậm
      if (pd < 0.15) return '#ff9800' // Vàng đậm
      return '#e53935' // Đỏ đậm
    }

    return {
      chartData,
      chartOptions
    }
  }
}
</script>

<style scoped>
.chart-guide {
  background: linear-gradient(135deg,
    rgba(255, 240, 247, 0.95) 0%,
    rgba(255, 255, 255, 0.95) 100%);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 2px solid rgba(255, 182, 193, 0.3);
  box-shadow: 0 4px 12px rgba(255, 182, 193, 0.2);
}

.guide-text {
  color: #4A4A4A;
  font-size: 0.95rem;
  line-height: 1.8;
  margin: 0;
}

.color-tag {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
  white-space: nowrap;
}

.color-tag.green {
  color: #00a651;
  background: rgba(0, 166, 81, 0.1);
}

.color-tag.yellow {
  color: #ff9800;
  background: rgba(255, 152, 0, 0.1);
}

.color-tag.red {
  color: #e53935;
  background: rgba(229, 57, 53, 0.1);
}

.chart-container {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 6px 20px rgba(255, 182, 193, 0.3);
  border: 2px solid rgba(255, 182, 193, 0.3);
}
</style>
