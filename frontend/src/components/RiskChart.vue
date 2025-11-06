<template>
  <div>
    <h3 style="margin-bottom: 1.5rem; color: #FF6B9D; text-align: center; font-size: 1.4rem; font-weight: 700;">
      📊 Biểu đồ So sánh PD từ 4 Models
    </h3>

    <!-- Grid 2 cột: Bar chart và Radar chart -->
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 2rem; margin-top: 1.5rem;">
      <!-- Biểu đồ cột -->
      <div style="background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(255, 182, 193, 0.25);">
        <h4 style="text-align: center; color: #4A4A4A; font-size: 1rem; margin-bottom: 1rem;">📊 Biểu đồ Cột</h4>
        <Bar :data="chartData" :options="chartOptions" />
      </div>

      <!-- Biểu đồ Radar -->
      <div style="background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(255, 182, 193, 0.25);">
        <h4 style="text-align: center; color: #4A4A4A; font-size: 1rem; margin-bottom: 1rem;">🎯 Biểu đồ Radar</h4>
        <Radar :data="radarData" :options="radarOptions" />
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { Bar, Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
)

export default {
  name: 'RiskChart',
  components: {
    Bar,
    Radar
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
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            font: {
              size: 14,
              weight: 'bold'
            },
            color: '#2c3e50'
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleFont: {
            size: 14,
            weight: 'bold'
          },
          bodyFont: {
            size: 13
          },
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            label: function(context) {
              const value = context.parsed.y
              let risk = ''
              if (value < 5) risk = '🟢 Rủi ro Thấp'
              else if (value < 15) risk = '🟡 Rủi ro Trung bình'
              else risk = '🔴 Rủi ro Cao'
              return `PD: ${value}% - ${risk}`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function(value) {
              return value + '%'
            },
            font: {
              size: 12,
              weight: 'bold'
            },
            color: '#2c3e50'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          ticks: {
            font: {
              size: 13,
              weight: 'bold'
            },
            color: '#2c3e50'
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

    // Radar Chart Data
    const radarData = computed(() => {
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
            backgroundColor: 'rgba(255, 107, 157, 0.2)',
            borderColor: '#FF6B9D',
            borderWidth: 3,
            pointBackgroundColor: '#FF6B9D',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: '#FF6B9D',
            pointRadius: 5,
            pointHoverRadius: 7
          }
        ]
      }
    })

    const radarOptions = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            font: {
              size: 13,
              weight: 'bold'
            },
            color: '#2c3e50'
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleFont: {
            size: 13,
            weight: 'bold'
          },
          bodyFont: {
            size: 12
          },
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: function(context) {
              const value = context.parsed.r
              let risk = ''
              if (value < 5) risk = '🟢 Rủi ro Thấp'
              else if (value < 15) risk = '🟡 Rủi ro Trung bình'
              else risk = '🔴 Rủi ro Cao'
              return `PD: ${value}% - ${risk}`
            }
          }
        }
      },
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: {
            stepSize: 20,
            callback: function(value) {
              return value + '%'
            },
            font: {
              size: 11
            },
            color: '#4A4A4A'
          },
          grid: {
            color: 'rgba(255, 182, 193, 0.3)'
          },
          angleLines: {
            color: 'rgba(255, 182, 193, 0.3)'
          },
          pointLabels: {
            font: {
              size: 12,
              weight: 'bold'
            },
            color: '#2c3e50'
          }
        }
      }
    }

    return {
      chartData,
      chartOptions,
      radarData,
      radarOptions
    }
  }
}
</script>
