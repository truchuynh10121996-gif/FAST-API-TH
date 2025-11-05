<template>
  <div>
    <h3 class="chart-title">
      📊 Dashboard: 14 Chỉ số Tài chính
    </h3>

    <!-- Hướng dẫn đọc biểu đồ -->
    <div class="chart-guide">
      <h4>💡 Hướng dẫn đọc biểu đồ:</h4>
      <ul>
        <li><strong>Chỉ số Sinh lời (X1-X4):</strong> Giá trị càng cao càng tốt - cho thấy khả năng tạo lợi nhuận</li>
        <li><strong>Đòn bẩy (X5-X6):</strong> Giá trị càng thấp càng tốt - cho thấy mức độ nợ an toàn</li>
        <li><strong>Thanh toán (X7-X11):</strong> X7, X8 ≥ 1 là tốt; X9, X10 càng cao càng tốt; X11 phụ thuộc chiến lược</li>
        <li><strong>Hiệu quả (X12-X14):</strong> Giá trị càng cao càng tốt - cho thấy hiệu quả vận hành</li>
      </ul>
    </div>

    <!-- Grid 2x2 -->
    <div class="charts-grid">
      <!-- Biểu đồ 1: Chỉ số Sinh lời (X1-X4) -->
      <div class="chart-wrapper">
        <h4 class="chart-subtitle">📈 Nhóm 1: Chỉ số Sinh lời (X1-X4)</h4>
        <Bar :data="chart1Data" :options="chart1Options" />
        <p class="chart-note">✅ Giá trị càng cao càng tốt</p>
      </div>

      <!-- Biểu đồ 2: Đòn bẩy tài chính (X5-X6) -->
      <div class="chart-wrapper">
        <h4 class="chart-subtitle">⚖️ Nhóm 2: Đòn bẩy Tài chính (X5-X6)</h4>
        <Bar :data="chart2Data" :options="chart2Options" />
        <p class="chart-note">✅ Giá trị càng thấp càng an toàn (tối ưu: X5 < 0.6, X6 < 1.5)</p>
      </div>

      <!-- Biểu đồ 3: Thanh toán & Tạo tiền (X7-X11) -->
      <div class="chart-wrapper">
        <h4 class="chart-subtitle">💰 Nhóm 3: Thanh toán & Tạo tiền (X7-X11)</h4>
        <Bar :data="chart3Data" :options="chart3Options" />
        <p class="chart-note">✅ X7, X8 ≥ 1; X9, X10, X11 càng cao càng tốt</p>
      </div>

      <!-- Biểu đồ 4: Hiệu quả hoạt động (X12-X14) -->
      <div class="chart-wrapper">
        <h4 class="chart-subtitle">🎯 Nhóm 4: Hiệu quả Hoạt động (X12-X14)</h4>
        <Bar :data="chart4Data" :options="chart4Options" />
        <p class="chart-note">✅ Giá trị càng cao càng hiệu quả</p>
      </div>
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
  name: 'IndicatorsChart',
  components: {
    Bar
  },
  props: {
    indicators: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    // Màu pastel ngọt ngào cho các biểu đồ
    const colors = {
      profit: ['#FFB3D9', '#FFC4E5', '#FFD1EC', '#FFE0F5'],
      leverage: ['#FFD1EC', '#FFC4E5'],
      liquidity: ['#C8E6C9', '#A5D6A7', '#81C784', '#66BB6A', '#4CAF50'],
      efficiency: ['#B39DDB', '#9575CD', '#7E57C2']
    }

    const borderColors = {
      profit: ['#FF6B9D', '#FF8AB5', '#FFA8D3', '#FFC4E5'],
      leverage: ['#FF8AB5', '#FF6B9D'],
      liquidity: ['#66BB6A', '#4CAF50', '#388E3C', '#2E7D32', '#1B5E20'],
      efficiency: ['#7E57C2', '#673AB7', '#5E35B1']
    }

    // Biểu đồ 1: X1-X4 (Sinh lời)
    const chart1Data = computed(() => {
      const values = [1, 2, 3, 4].map(i => props.indicators[`X_${i}`] || 0)
      return {
        labels: ['X1: Biên LN gộp', 'X2: Biên LN trước thuế', 'X3: ROA', 'X4: ROE'],
        datasets: [{
          label: 'Giá trị',
          data: values,
          backgroundColor: colors.profit,
          borderColor: borderColors.profit,
          borderWidth: 2,
          borderRadius: 8
        }]
      }
    })

    const chart1Options = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            label: (context) => `Giá trị: ${context.parsed.y.toFixed(4)}`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { font: { size: 11, weight: 'bold' }, color: '#4A4A4A' },
          grid: { color: 'rgba(255, 182, 193, 0.2)' }
        },
        x: {
          ticks: { font: { size: 10 }, color: '#4A4A4A' },
          grid: { display: false }
        }
      }
    }

    // Biểu đồ 2: X5-X6 (Đòn bẩy)
    const chart2Data = computed(() => {
      const values = [5, 6].map(i => props.indicators[`X_${i}`] || 0)
      return {
        labels: ['X5: Nợ/Tài sản', 'X6: Nợ/VCSH'],
        datasets: [{
          label: 'Giá trị',
          data: values,
          backgroundColor: colors.leverage,
          borderColor: borderColors.leverage,
          borderWidth: 2,
          borderRadius: 8
        }]
      }
    })

    const chart2Options = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            label: (context) => `Giá trị: ${context.parsed.y.toFixed(4)}`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { font: { size: 11, weight: 'bold' }, color: '#4A4A4A' },
          grid: { color: 'rgba(255, 182, 193, 0.2)' }
        },
        x: {
          ticks: { font: { size: 10 }, color: '#4A4A4A' },
          grid: { display: false }
        }
      }
    }

    // Biểu đồ 3: X7-X11 (Thanh toán & Tạo tiền)
    const chart3Data = computed(() => {
      const values = [7, 8, 9, 10, 11].map(i => props.indicators[`X_${i}`] || 0)
      return {
        labels: ['X7: TT hiện hành', 'X8: TT nhanh', 'X9: KN trả lãi', 'X10: KN trả nợ', 'X11: Tiền/VCSH'],
        datasets: [{
          label: 'Giá trị',
          data: values,
          backgroundColor: colors.liquidity,
          borderColor: borderColors.liquidity,
          borderWidth: 2,
          borderRadius: 8
        }]
      }
    })

    const chart3Options = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            label: (context) => `Giá trị: ${context.parsed.y.toFixed(4)}`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { font: { size: 11, weight: 'bold' }, color: '#4A4A4A' },
          grid: { color: 'rgba(200, 230, 201, 0.3)' }
        },
        x: {
          ticks: { font: { size: 9.5 }, color: '#4A4A4A' },
          grid: { display: false }
        }
      }
    }

    // Biểu đồ 4: X12-X14 (Hiệu quả)
    const chart4Data = computed(() => {
      const values = [12, 13, 14].map(i => props.indicators[`X_${i}`] || 0)
      return {
        labels: ['X12: Vòng quay HTK', 'X13: Kỳ thu tiền (ngày)', 'X14: Hiệu suất TS'],
        datasets: [{
          label: 'Giá trị',
          data: values,
          backgroundColor: colors.efficiency,
          borderColor: borderColors.efficiency,
          borderWidth: 2,
          borderRadius: 8
        }]
      }
    })

    const chart4Options = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            label: (context) => `Giá trị: ${context.parsed.y.toFixed(4)}`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { font: { size: 11, weight: 'bold' }, color: '#4A4A4A' },
          grid: { color: 'rgba(179, 157, 219, 0.2)' }
        },
        x: {
          ticks: { font: { size: 10 }, color: '#4A4A4A' },
          grid: { display: false }
        }
      }
    }

    return {
      chart1Data,
      chart1Options,
      chart2Data,
      chart2Options,
      chart3Data,
      chart3Options,
      chart4Data,
      chart4Options
    }
  }
}
</script>

<style scoped>
.chart-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #FF6B9D;
  text-align: center;
  margin-bottom: 1.5rem;
  text-shadow: 1px 1px 2px rgba(255, 182, 193, 0.3);
}

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

.chart-guide h4 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #7d1e52;
  margin-bottom: 1rem;
}

.chart-guide ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.chart-guide li {
  padding: 0.5rem 0;
  color: #4A4A4A;
  font-size: 0.9rem;
  line-height: 1.5;
  border-bottom: 1px solid rgba(255, 182, 193, 0.15);
}

.chart-guide li:last-child {
  border-bottom: none;
}

.chart-guide strong {
  color: #FF6B9D;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin: 2rem 0;
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.chart-wrapper {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 4px 16px rgba(255, 182, 193, 0.25);
  border: 2px solid rgba(255, 182, 193, 0.2);
  transition: all 0.3s ease;
}

.chart-wrapper:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(255, 182, 193, 0.35);
  border-color: rgba(255, 182, 193, 0.4);
}

.chart-subtitle {
  font-size: 1rem;
  font-weight: 600;
  color: #4A4A4A;
  margin-bottom: 1rem;
  text-align: center;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(255, 182, 193, 0.2);
}

.chart-note {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: #7A7A7A;
  font-style: italic;
  text-align: center;
  padding: 0.5rem;
  background: rgba(255, 240, 247, 0.5);
  border-radius: 8px;
}
</style>
