<template>
  <div>
    <h3 class="chart-title">
      📊 Biểu đồ Phân tích 14 Chỉ số Tài chính
    </h3>

    <!-- Hướng dẫn chuyên nghiệp -->
    <div class="chart-guide">
      <h4>📖 Hướng dẫn Đọc & Phân tích Biểu đồ</h4>

      <div class="guide-section">
        <h5>🎯 1. Biểu đồ Radar (Tổng quan toàn diện)</h5>
        <p class="guide-description">Biểu đồ radar giúp nhìn nhận tổng thể 14 chỉ số cùng lúc. Hình dạng đều và rộng = doanh nghiệp cân bằng, các góc nhọn = điểm mạnh/yếu cần lưu ý.</p>
      </div>

      <div class="guide-section">
        <h5>📈 2. Biểu đồ Cột (Chi tiết từng nhóm)</h5>
        <ul class="guide-list">
          <li>
            <span class="guide-icon">💰</span>
            <strong>Sinh lời (X1-X4):</strong>
            <span class="guide-good">Càng cao càng tốt</span> - Đo lường khả năng tạo lợi nhuận. Tham khảo: X1 > 0.2, X2 > 0.1, X3 > 0.05, X4 > 0.1
          </li>
          <li>
            <span class="guide-icon">⚖️</span>
            <strong>Đòn bẩy (X5-X6):</strong>
            <span class="guide-caution">Càng thấp càng an toàn</span> - Đo lường mức độ nợ. Tốt: X5 < 0.6, X6 < 1.5
          </li>
          <li>
            <span class="guide-icon">💧</span>
            <strong>Thanh toán (X7-X11):</strong>
            <span class="guide-mixed">Phụ thuộc chỉ số</span> - X7, X8 ≥ 1 là tốt; X9, X10 > 2 là tốt; X11 phụ thuộc ngành
          </li>
          <li>
            <span class="guide-icon">⚡</span>
            <strong>Hiệu quả (X12-X14):</strong>
            <span class="guide-good">Càng cao càng tốt</span> - Đo lường hiệu quả vận hành. X12 > 5, X13 < 60 ngày, X14 > 1
          </li>
        </ul>
      </div>

      <div class="guide-note">
        <strong>⚠️ Lưu ý:</strong> Các giá trị tham khảo trên phụ thuộc ngành nghề. So sánh với trung bình ngành để có đánh giá chính xác nhất.
      </div>
    </div>

    <!-- Biểu đồ Radar tổng hợp 14 chỉ số -->
    <div class="radar-chart-container">
      <h4 class="chart-section-title">🎯 Biểu đồ Radar - Tổng quan 14 Chỉ số</h4>
      <div class="radar-wrapper">
        <Radar :data="radarAllData" :options="radarAllOptions" />
      </div>
      <p class="chart-description">
        Biểu đồ radar hiển thị toàn bộ 14 chỉ số tài chính trên cùng một đồ thị.
        Hình dạng <strong>đều và rộng</strong> cho thấy doanh nghiệp phát triển cân bằng.
        Các <strong>góc nhọn hoặc lõm</strong> chỉ ra điểm mạnh hoặc điểm yếu cần quan tâm.
      </p>
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

    // Biểu đồ Radar cho tất cả 14 chỉ số
    const radarAllData = computed(() => {
      const labels = [
        'X1: Biên LN gộp',
        'X2: Biên LN trước thuế',
        'X3: ROA',
        'X4: ROE',
        'X5: Nợ/TS',
        'X6: Nợ/VCSH',
        'X7: TT hiện hành',
        'X8: TT nhanh',
        'X9: KN trả lãi',
        'X10: KN trả nợ',
        'X11: Tiền/VCSH',
        'X12: Vòng quay HTK',
        'X13: Kỳ thu tiền',
        'X14: Hiệu suất TS'
      ]

      const values = []
      for (let i = 1; i <= 14; i++) {
        values.push(props.indicators[`X_${i}`] || 0)
      }

      return {
        labels: labels,
        datasets: [{
          label: '14 Chỉ số Tài chính',
          data: values,
          backgroundColor: 'rgba(255, 107, 157, 0.25)',
          borderColor: '#FF6B9D',
          borderWidth: 3,
          pointBackgroundColor: '#FF6B9D',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#FF6B9D',
          pointRadius: 5,
          pointHoverRadius: 7
        }]
      }
    })

    const radarAllOptions = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            font: { size: 14, weight: 'bold' },
            color: '#FF6B9D',
            padding: 15
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.85)',
          titleFont: { size: 14, weight: 'bold' },
          bodyFont: { size: 13 },
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            label: (context) => {
              const value = context.parsed.r
              return `Giá trị: ${value.toFixed(4)}`
            }
          }
        }
      },
      scales: {
        r: {
          beginAtZero: true,
          ticks: {
            stepSize: 0.2,
            font: { size: 11, weight: 'bold' },
            color: '#4A4A4A',
            backdropColor: 'rgba(255, 255, 255, 0.8)',
            backdropPadding: 3
          },
          grid: {
            color: 'rgba(255, 182, 193, 0.4)',
            lineWidth: 2
          },
          angleLines: {
            color: 'rgba(255, 182, 193, 0.4)',
            lineWidth: 2
          },
          pointLabels: {
            font: { size: 11, weight: 'bold' },
            color: '#2c3e50',
            padding: 8
          }
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
      chart4Options,
      radarAllData,
      radarAllOptions
    }
  }
}
</script>

<style scoped>
.chart-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #FF6B9D;
  text-align: center;
  margin-bottom: 2rem;
  text-shadow: 2px 2px 3px rgba(255, 182, 193, 0.3);
}

/* Hướng dẫn chuyên nghiệp */
.chart-guide {
  background: linear-gradient(135deg,
    rgba(255, 240, 247, 0.98) 0%,
    rgba(255, 255, 255, 0.98) 100%);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2.5rem;
  border: 3px solid rgba(255, 182, 193, 0.4);
  box-shadow: 0 6px 16px rgba(255, 182, 193, 0.3);
}

.chart-guide h4 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #7d1e52;
  margin-bottom: 1.5rem;
  text-align: center;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(255, 182, 193, 0.3);
}

.guide-section {
  margin-bottom: 1.5rem;
}

.guide-section h5 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #FF6B9D;
  margin-bottom: 0.8rem;
}

.guide-description {
  color: #4A4A4A;
  font-size: 0.95rem;
  line-height: 1.7;
  margin-bottom: 0.5rem;
}

.guide-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.guide-list li {
  padding: 0.8rem;
  color: #4A4A4A;
  font-size: 0.92rem;
  line-height: 1.6;
  border-bottom: 1px solid rgba(255, 182, 193, 0.2);
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.guide-list li:last-child {
  border-bottom: none;
}

.guide-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.guide-good {
  color: #00a651;
  font-weight: 600;
  background: rgba(0, 166, 81, 0.1);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.guide-caution {
  color: #ff9800;
  font-weight: 600;
  background: rgba(255, 152, 0, 0.1);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.guide-mixed {
  color: #2196F3;
  font-weight: 600;
  background: rgba(33, 150, 243, 0.1);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.guide-note {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(255, 235, 59, 0.2);
  border-left: 4px solid #FFC107;
  border-radius: 8px;
  color: #4A4A4A;
  font-size: 0.9rem;
}

/* Biểu đồ Radar */
.radar-chart-container {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2.5rem;
  box-shadow: 0 6px 20px rgba(255, 182, 193, 0.3);
  border: 2px solid rgba(255, 182, 193, 0.3);
}

.chart-section-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #FF6B9D;
  text-align: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.8rem;
  border-bottom: 2px solid rgba(255, 182, 193, 0.3);
}

.radar-wrapper {
  max-width: 650px;
  margin: 0 auto;
  padding: 1rem;
}

.chart-description {
  text-align: center;
  color: #4A4A4A;
  font-size: 0.95rem;
  line-height: 1.7;
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(255, 240, 247, 0.5);
  border-radius: 12px;
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
