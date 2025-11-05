<template>
  <div>
    <h3 class="chart-title">
      📊 Dashboard: 14 Chỉ số Tài chính
    </h3>

    <!-- Biểu đồ 1: Nhóm chỉ số Sinh lời & Đòn bẩy -->
    <div class="chart-wrapper">
      <h4 class="chart-subtitle">Nhóm 1: Chỉ số Sinh lời & Đòn bẩy tài chính (X1-X6)</h4>
      <Bar :data="chart1Data" :options="chart1Options" />
    </div>

    <!-- Biểu đồ 2: Nhóm chỉ số Thanh toán & Hiệu quả -->
    <div class="chart-wrapper">
      <h4 class="chart-subtitle">Nhóm 2: Chỉ số Thanh toán & Hiệu quả hoạt động (X7-X14)</h4>
      <Radar :data="chart2Data" :options="chart2Options" />
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
  name: 'IndicatorsChart',
  components: {
    Bar,
    Radar
  },
  props: {
    indicators: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    // Biểu đồ 1: Bar chart cho X1-X6
    const chart1Data = computed(() => {
      const labels = ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']
      const values = labels.map(key => props.indicators[`X_${key.slice(1)}`] || 0)

      return {
        labels: [
          'X1: Biên lợi nhuận gộp',
          'X2: Biên LN trước thuế',
          'X3: ROA',
          'X4: ROE',
          'X5: Nợ/Tài sản',
          'X6: Nợ/VCSH'
        ],
        datasets: [
          {
            label: 'Giá trị chỉ số',
            data: values,
            backgroundColor: [
              'rgba(255, 99, 132, 0.7)',
              'rgba(255, 159, 64, 0.7)',
              'rgba(255, 205, 86, 0.7)',
              'rgba(75, 192, 192, 0.7)',
              'rgba(54, 162, 235, 0.7)',
              'rgba(153, 102, 255, 0.7)'
            ],
            borderColor: [
              'rgb(255, 99, 132)',
              'rgb(255, 159, 64)',
              'rgb(255, 205, 86)',
              'rgb(75, 192, 192)',
              'rgb(54, 162, 235)',
              'rgb(153, 102, 255)'
            ],
            borderWidth: 2,
            borderRadius: 8
          }
        ]
      }
    })

    const chart1Options = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
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
          cornerRadius: 8
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            font: {
              size: 12,
              weight: 'bold'
            },
            color: '#4A4A4A'
          },
          grid: {
            color: 'rgba(255, 182, 193, 0.2)'
          }
        },
        x: {
          ticks: {
            font: {
              size: 11
            },
            color: '#4A4A4A'
          },
          grid: {
            display: false
          }
        }
      }
    }

    // Biểu đồ 2: Radar chart cho X7-X14
    const chart2Data = computed(() => {
      const labels = ['X7', 'X8', 'X9', 'X10', 'X11', 'X12', 'X13', 'X14']
      const values = labels.map(key => props.indicators[`X_${key.slice(1)}`] || 0)

      // Normalize X13 vì giá trị có thể lớn (ngày)
      const normalizedValues = values.map((val, idx) => {
        if (idx === 6) { // X13
          return val > 100 ? 100 : val
        }
        return val
      })

      return {
        labels: [
          'X7: TT hiện hành',
          'X8: TT nhanh',
          'X9: KN trả lãi',
          'X10: KN trả nợ gốc',
          'X11: Tạo tiền/VCSH',
          'X12: Vòng quay HTK',
          'X13: Kỳ thu tiền',
          'X14: Hiệu suất TS'
        ],
        datasets: [
          {
            label: 'Giá trị chỉ số',
            data: normalizedValues,
            backgroundColor: 'rgba(255, 182, 193, 0.3)',
            borderColor: 'rgb(255, 107, 157)',
            borderWidth: 3,
            pointBackgroundColor: 'rgb(255, 107, 157)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgb(255, 107, 157)',
            pointRadius: 5,
            pointHoverRadius: 7
          }
        ]
      }
    })

    const chart2Options = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
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
              const index = context.dataIndex
              const labels = ['X7', 'X8', 'X9', 'X10', 'X11', 'X12', 'X13', 'X14']
              const actualValue = props.indicators[`X_${labels[index].slice(1)}`] || 0
              return `Giá trị: ${actualValue.toFixed(4)}`
            }
          }
        }
      },
      scales: {
        r: {
          beginAtZero: true,
          ticks: {
            font: {
              size: 11
            },
            color: '#4A4A4A',
            backdropColor: 'transparent'
          },
          grid: {
            color: 'rgba(255, 182, 193, 0.2)'
          },
          pointLabels: {
            font: {
              size: 11,
              weight: 'bold'
            },
            color: '#4A4A4A'
          }
        }
      }
    }

    return {
      chart1Data,
      chart1Options,
      chart2Data,
      chart2Options
    }
  }
}
</script>

<style scoped>
.chart-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #FF6B9D;
  text-align: center;
  margin-bottom: 2rem;
  text-shadow: 1px 1px 2px rgba(255, 182, 193, 0.3);
}

.chart-wrapper {
  margin: 2rem 0;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(255, 182, 193, 0.3);
  border: 2px solid rgba(255, 182, 193, 0.2);
}

.chart-subtitle {
  font-size: 1.1rem;
  font-weight: 600;
  color: #4A4A4A;
  margin-bottom: 1.5rem;
  text-align: center;
}
</style>
