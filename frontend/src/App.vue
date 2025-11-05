<template>
  <div id="app">
    <!-- Header mới với tông màu hồng lung linh -->
    <header class="header">
      <div class="logo-container">
        <img
          src="/logo-agribank1.png"
          alt="Agribank Logo"
          class="logo"
        />
      </div>
      <h1 class="app-title">✨ Hệ thống AI Đánh giá Rủi ro Tín dụng Doanh nghiệp ✨</h1>
    </header>

    <!-- Sidebar Toggle Button -->
    <button @click="toggleSidebar" class="sidebar-toggle" title="Huấn luyện mô hình">
      {{ sidebarOpen ? '✖️' : '📚' }}
    </button>

    <!-- Sidebar cho huấn luyện mô hình -->
    <div class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-content">
        <h2 class="sidebar-title">📚 Huấn luyện Mô hình</h2>

        <div class="upload-area" @click="$refs.trainFileInput.click()">
          <div class="upload-icon">📤</div>
          <p class="upload-text">{{ trainFileName || 'Tải file CSV' }}</p>
          <p class="upload-hint">File CSV cần có 14 cột (X_1 đến X_14) và cột 'default'</p>
        </div>

        <input
          ref="trainFileInput"
          type="file"
          accept=".csv"
          @change="handleTrainFile"
          style="display: none"
        />

        <button
          @click="trainModel"
          class="btn btn-primary"
          :disabled="!trainFile || isTraining"
          style="margin-top: 1rem; width: 100%;"
        >
          {{ isTraining ? '⏳ Đang huấn luyện...' : '🚀 Huấn luyện Mô hình' }}
        </button>

        <!-- Training Results -->
        <div v-if="trainResult" style="margin-top: 2rem;">
          <h3 style="margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);">
            ✅ Kết quả Huấn luyện
          </h3>
          <div style="background: rgba(255, 255, 255, 0.9); padding: 1rem; border-radius: 12px;">
            <p><strong>Số mẫu Train:</strong> {{ trainResult.train_samples }}</p>
            <p><strong>Số mẫu Test:</strong> {{ trainResult.test_samples }}</p>
            <p><strong>Accuracy (Test):</strong> {{ (trainResult.metrics_test.accuracy * 100).toFixed(2) }}%</p>
            <p><strong>AUC (Test):</strong> {{ (trainResult.metrics_test.auc * 100).toFixed(2) }}%</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Container -->
    <div class="container">
      <!-- Dự báo Rủi ro Section -->
      <div class="card">
        <h2 class="card-title">🔮 Dự báo Rủi ro Tín dụng từ Hồ sơ Doanh nghiệp</h2>

        <!-- Upload XLSX File -->
        <div style="margin-bottom: 2rem;">
          <div class="upload-area" @click="$refs.xlsxFileInput.click()">
            <div class="upload-icon">📊</div>
            <p class="upload-text">{{ xlsxFileName || 'Tải lên file XLSX của doanh nghiệp' }}</p>
            <p class="upload-hint">
              File XLSX phải có 3 sheets: CDKT (Cân đối kế toán), BCTN (Báo cáo thu nhập), LCTT (Lưu chuyển tiền tệ)
            </p>
          </div>
          <input
            ref="xlsxFileInput"
            type="file"
            accept=".xlsx,.xls"
            @change="handleXlsxFile"
            style="display: none"
          />
          <button
            @click="predictFromXlsx"
            class="btn btn-primary"
            :disabled="!xlsxFile || isPredicting"
            style="margin-top: 1rem; width: 100%;"
          >
            {{ isPredicting ? '⏳ Đang tính toán...' : '🎯 Tính toán 14 chỉ số và Dự báo PD' }}
          </button>
        </div>

        <!-- Results Section -->
        <div v-if="predictionResult">
          <!-- 14 Chỉ số tài chính -->
          <div style="margin: 3rem 0;">
            <h3 style="margin-bottom: 1.5rem; color: #FF6B9D; text-align: center; font-size: 1.6rem;">
              📈 14 Chỉ số Tài chính đã tính toán
            </h3>
            <div class="indicators-grid">
              <div
                v-for="indicator in indicators"
                :key="indicator.code"
                class="indicator-card"
              >
                <div class="indicator-code">{{ indicator.code }}</div>
                <div class="indicator-name">{{ indicator.name }}</div>
                <div class="indicator-value">{{ indicator.value.toFixed(4) }}</div>
              </div>
            </div>
          </div>

          <!-- Dashboard Biểu đồ 14 chỉ số -->
          <div style="margin: 3rem 0;">
            <IndicatorsChart v-if="indicatorsDict" :indicators="indicatorsDict" />
          </div>

          <!-- PD Results -->
          <div style="margin: 3rem 0;">
            <h3 style="margin-bottom: 1.5rem; color: #FF6B9D; text-align: center; font-size: 1.6rem;">
              🎯 Kết quả Dự báo Xác suất Vỡ nợ (PD)
            </h3>

            <div class="pd-grid">
              <div
                class="pd-card"
                :class="getRiskClass(predictionResult.pd_stacking)"
              >
                <div class="pd-label">🎯 PD - Stacking (Kết quả chính)</div>
                <div class="pd-value">{{ (predictionResult.pd_stacking * 100).toFixed(2) }}%</div>
                <div class="pd-status">{{ getRiskLabel(predictionResult.pd_stacking) }}</div>
              </div>

              <div
                class="pd-card"
                :class="getRiskClass(predictionResult.pd_logistic)"
              >
                <div class="pd-label">📈 PD - Logistic Regression</div>
                <div class="pd-value">{{ (predictionResult.pd_logistic * 100).toFixed(2) }}%</div>
                <div class="pd-status">{{ getRiskLabel(predictionResult.pd_logistic) }}</div>
              </div>

              <div
                class="pd-card"
                :class="getRiskClass(predictionResult.pd_random_forest)"
              >
                <div class="pd-label">🌳 PD - Random Forest</div>
                <div class="pd-value">{{ (predictionResult.pd_random_forest * 100).toFixed(2) }}%</div>
                <div class="pd-status">{{ getRiskLabel(predictionResult.pd_random_forest) }}</div>
              </div>

              <div
                class="pd-card"
                :class="getRiskClass(predictionResult.pd_xgboost)"
              >
                <div class="pd-label">⚡ PD - XGBoost</div>
                <div class="pd-value">{{ (predictionResult.pd_xgboost * 100).toFixed(2) }}%</div>
                <div class="pd-status">{{ getRiskLabel(predictionResult.pd_xgboost) }}</div>
              </div>
            </div>

            <!-- Chart so sánh PD -->
            <div class="chart-container">
              <RiskChart :prediction="predictionResult" />
            </div>
          </div>

          <!-- Gemini Analysis Section -->
          <div style="margin: 3rem 0;">
            <button
              @click="analyzeWithGemini"
              class="btn btn-primary"
              :disabled="isAnalyzing"
              style="width: 100%;"
            >
              {{ isAnalyzing ? '⏳ Đang phân tích...' : '🤖 Phân tích chuyên sâu bằng Gemini AI' }}
            </button>

            <div v-if="geminiAnalysis" class="analysis-box">
              <h3 style="margin-bottom: 1rem; color: #FF6B9D; font-size: 1.4rem;">
                🧠 Phân tích & Khuyến nghị từ Gemini AI
              </h3>
              <div style="white-space: pre-wrap; line-height: 1.8;">{{ geminiAnalysis }}</div>
            </div>
          </div>

          <!-- Export Report Button -->
          <div v-if="geminiAnalysis" style="margin: 2rem 0; text-align: center;">
            <button
              @click="exportReport"
              class="btn btn-secondary"
              :disabled="isExporting"
              style="padding: 1rem 3rem; font-size: 1.1rem;"
            >
              {{ isExporting ? '⏳ Đang xuất báo cáo...' : '📄 Xuất Báo cáo Word' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import RiskChart from './components/RiskChart.vue'
import IndicatorsChart from './components/IndicatorsChart.vue'

export default {
  name: 'App',
  components: {
    RiskChart,
    IndicatorsChart
  },
  setup() {
    // State
    const sidebarOpen = ref(false)

    // Training
    const trainFile = ref(null)
    const trainFileName = ref('')
    const isTraining = ref(false)
    const trainResult = ref(null)

    // Prediction
    const xlsxFile = ref(null)
    const xlsxFileName = ref('')
    const isPredicting = ref(false)
    const indicators = ref([])
    const indicatorsDict = ref(null)
    const predictionResult = ref(null)

    // Gemini Analysis
    const isAnalyzing = ref(false)
    const geminiAnalysis = ref('')

    // Export
    const isExporting = ref(false)

    // API Base URL
    const API_BASE = 'http://localhost:8000'

    // Methods
    const toggleSidebar = () => {
      sidebarOpen.value = !sidebarOpen.value
    }

    const handleTrainFile = (event) => {
      const file = event.target.files[0]
      if (file) {
        trainFile.value = file
        trainFileName.value = file.name
      }
    }

    const trainModel = async () => {
      if (!trainFile.value) return

      isTraining.value = true
      trainResult.value = null

      try {
        const formData = new FormData()
        formData.append('file', trainFile.value)

        const response = await axios.post(`${API_BASE}/train`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        trainResult.value = response.data
        alert('✅ Huấn luyện mô hình thành công!')
      } catch (error) {
        alert('❌ Lỗi khi huấn luyện: ' + (error.response?.data?.detail || error.message))
      } finally {
        isTraining.value = false
      }
    }

    const handleXlsxFile = (event) => {
      const file = event.target.files[0]
      if (file) {
        xlsxFile.value = file
        xlsxFileName.value = file.name
      }
    }

    const predictFromXlsx = async () => {
      if (!xlsxFile.value) return

      isPredicting.value = true
      indicators.value = []
      indicatorsDict.value = null
      predictionResult.value = null
      geminiAnalysis.value = ''

      try {
        const formData = new FormData()
        formData.append('file', xlsxFile.value)

        const response = await axios.post(`${API_BASE}/predict-from-xlsx`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.data.status === 'success') {
          indicators.value = response.data.indicators
          indicatorsDict.value = response.data.indicators_dict
          predictionResult.value = response.data.prediction

          alert('✅ Tính toán 14 chỉ số và dự báo PD thành công!')

          // Scroll to results
          setTimeout(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
          }, 100)
        }
      } catch (error) {
        alert('❌ Lỗi khi xử lý file XLSX: ' + (error.response?.data?.detail || error.message))
      } finally {
        isPredicting.value = false
      }
    }

    const analyzeWithGemini = async () => {
      if (!predictionResult.value || !indicatorsDict.value) return

      isAnalyzing.value = true
      geminiAnalysis.value = ''

      try {
        const requestData = {
          prediction: predictionResult.value,
          indicators_dict: indicatorsDict.value,
          indicators: indicators.value
        }

        const response = await axios.post(`${API_BASE}/analyze`, requestData)

        if (response.data.status === 'success') {
          geminiAnalysis.value = response.data.analysis

          // Scroll to analysis
          setTimeout(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
          }, 100)
        }
      } catch (error) {
        alert('❌ Lỗi khi phân tích bằng Gemini: ' + (error.response?.data?.detail || error.message))
      } finally {
        isAnalyzing.value = false
      }
    }

    const exportReport = async () => {
      if (!predictionResult.value || !geminiAnalysis.value) return

      isExporting.value = true

      try {
        const reportData = {
          prediction: predictionResult.value,
          indicators: indicators.value,
          indicators_dict: indicatorsDict.value,
          analysis: geminiAnalysis.value
        }

        const response = await axios.post(`${API_BASE}/export-report`, reportData, {
          responseType: 'blob'
        })

        // Tạo URL để download
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `bao_cao_tin_dung_${new Date().getTime()}.docx`)
        document.body.appendChild(link)
        link.click()
        link.remove()

        alert('✅ Xuất báo cáo thành công!')
      } catch (error) {
        alert('❌ Lỗi khi xuất báo cáo: ' + (error.response?.data?.detail || error.message))
      } finally {
        isExporting.value = false
      }
    }

    const getRiskClass = (pd) => {
      const pdPercent = pd * 100
      if (pdPercent < 2) return 'risk-very-low'
      if (pdPercent < 5) return 'risk-low'
      if (pdPercent < 10) return 'risk-medium'
      if (pdPercent < 20) return 'risk-high'
      return 'risk-very-high'
    }

    const getRiskLabel = (pd) => {
      const pdPercent = pd * 100
      if (pdPercent < 2) return '🟢 Rất thấp (AAA-AA) - Doanh nghiệp xuất sắc'
      if (pdPercent < 5) return '🟢 Thấp (A-BBB) - Doanh nghiệp tốt'
      if (pdPercent < 10) return '🟡 Trung bình (BB) - Cần theo dõi'
      if (pdPercent < 20) return '🟠 Cao (B) - Rủi ro đáng kể'
      return '🔴 Rất cao (CCC-D) - Nguy cơ vỡ nợ cao'
    }

    return {
      sidebarOpen,
      trainFile,
      trainFileName,
      isTraining,
      trainResult,
      xlsxFile,
      xlsxFileName,
      isPredicting,
      indicators,
      indicatorsDict,
      predictionResult,
      isAnalyzing,
      geminiAnalysis,
      isExporting,
      toggleSidebar,
      handleTrainFile,
      trainModel,
      handleXlsxFile,
      predictFromXlsx,
      analyzeWithGemini,
      exportReport,
      getRiskClass,
      getRiskLabel
    }
  }
}
</script>
