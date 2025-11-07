<template>
  <div id="app">
    <!-- Khoảng trống 1cm trước header -->
    <div class="header-spacer"></div>

    <!-- Header mới với tông màu hồng lung linh - Chỉ thanh hồng -->
    <header class="header"></header>

    <!-- Logo và Tiêu đề nằm dưới header, canh giữa -->
    <div class="logo-title-section">
      <div class="logo-container-center">
        <img
          src="/logo-agribank1.png"
          alt="Agribank Logo"
          class="logo-center"
        />
      </div>
      <div class="title-section-center">
        <h1 class="main-title-center">CHƯƠNG TRÌNH ĐÁNH GIÁ RỦI RO TÍN DỤNG</h1>
        <h2 class="sub-title-center">Dự báo xác suất Vỡ nợ KHDN (PD) & Phân tích AI chuyên sâu</h2>
      </div>
    </div>

    <!-- Divider sau logo và tiêu đề -->
    <div class="title-divider"></div>

    <!-- ✅ TAB SYSTEM - Thay thế Sidebar -->
    <div class="tabs-container">
      <button
        @click="activeTab = 'predict'"
        class="tab-button"
        :class="{ active: activeTab === 'predict' }"
      >
        🔮 Dự Báo PD
      </button>
      <button
        @click="activeTab = 'dashboard'"
        class="tab-button"
        :class="{ active: activeTab === 'dashboard' }"
      >
        📊 Dashboard Tài Chính
      </button>
      <button
        @click="activeTab = 'train'"
        class="tab-button"
        :class="{ active: activeTab === 'train' }"
      >
        📚 Huấn luyện mô hình
      </button>
    </div>

    <!-- Main Container -->
    <div class="container">
      <!-- ✅ TAB CONTENT: Dự Báo PD -->
      <div v-if="activeTab === 'predict'" class="tab-content">
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
          <!-- 14 Chỉ số tài chính - 2 bảng nằm ngang -->
          <div style="margin: 3rem 0;">
            <h3 style="margin-bottom: 1.5rem; color: #FF6B9D; text-align: center; font-size: 1.6rem;">
              📈 14 Chỉ số Tài chính đã tính toán
            </h3>
            <div class="indicators-tables-container">
              <!-- Bảng 1: X1-X7 -->
              <div class="indicators-table-wrapper">
                <h4 class="table-subtitle">Nhóm 1: Sinh lời & Thanh toán (X1-X7)</h4>
                <table class="indicators-table">
                  <thead>
                    <tr>
                      <th>Chỉ số</th>
                      <th>Giá trị</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="indicator in indicators.slice(0, 7)" :key="indicator.code">
                      <td>
                        <div class="indicator-code-cell">{{ indicator.code }}</div>
                        <div class="indicator-name-cell">{{ indicator.name }}</div>
                      </td>
                      <td class="indicator-value-cell">{{ indicator.value.toFixed(4) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Bảng 2: X8-X14 -->
              <div class="indicators-table-wrapper">
                <h4 class="table-subtitle">Nhóm 2: Hiệu quả hoạt động (X8-X14)</h4>
                <table class="indicators-table">
                  <thead>
                    <tr>
                      <th>Chỉ số</th>
                      <th>Giá trị</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="indicator in indicators.slice(7, 14)" :key="indicator.code">
                      <td>
                        <div class="indicator-code-cell">{{ indicator.code }}</div>
                        <div class="indicator-name-cell">{{ indicator.name }}</div>
                      </td>
                      <td class="indicator-value-cell">{{ indicator.value.toFixed(4) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Dashboard Biểu đồ 14 chỉ số -->
          <div style="margin: 3rem 0;">
            <IndicatorsChart v-if="indicatorsDict" :indicators="indicatorsDict" />
          </div>

          <!-- PD Results - 3 mô hình con trước, Stacking nổi bật ở dưới -->
          <div style="margin: 3rem 0;">
            <h3 style="margin-bottom: 1.5rem; color: #FF6B9D; text-align: center; font-size: 1.6rem;">
              🎯 Kết quả Dự báo Xác suất Vỡ nợ (PD)
            </h3>

            <!-- 3 mô hình con -->
            <div style="margin-bottom: 1rem;">
              <h4 style="color: #7A7A7A; font-size: 1.1rem; margin-bottom: 1rem; text-align: center;">
                📊 Kết quả từ 3 Mô hình Cơ sở
              </h4>
              <div class="pd-grid-base-models">
                <div
                  class="pd-card pd-card-base"
                  :class="getRiskClass(predictionResult.pd_logistic)"
                >
                  <div class="pd-label">📈 Logistic Regression</div>
                  <div class="pd-value">{{ (predictionResult.pd_logistic * 100).toFixed(2) }}%</div>
                  <div class="pd-status">{{ getRiskLabel(predictionResult.pd_logistic) }}</div>
                </div>

                <div
                  class="pd-card pd-card-base"
                  :class="getRiskClass(predictionResult.pd_random_forest)"
                >
                  <div class="pd-label">🌳 Random Forest</div>
                  <div class="pd-value">{{ (predictionResult.pd_random_forest * 100).toFixed(2) }}%</div>
                  <div class="pd-status">{{ getRiskLabel(predictionResult.pd_random_forest) }}</div>
                </div>

                <div
                  class="pd-card pd-card-base"
                  :class="getRiskClass(predictionResult.pd_xgboost)"
                >
                  <div class="pd-label">⚡ XGBoost</div>
                  <div class="pd-value">{{ (predictionResult.pd_xgboost * 100).toFixed(2) }}%</div>
                  <div class="pd-status">{{ getRiskLabel(predictionResult.pd_xgboost) }}</div>
                </div>
              </div>
            </div>

            <!-- Stacking - Kết quả chính nổi bật -->
            <div style="margin-top: 2.5rem;">
              <h4 style="color: #FF6B9D; font-size: 1.3rem; margin-bottom: 1rem; text-align: center; font-weight: 700;">
                ⭐ KẾT QUẢ CUỐI CÙNG - Mô hình Stacking Ensemble ⭐
              </h4>
              <div class="pd-stacking-container">
                <div
                  class="pd-card pd-card-stacking"
                  :class="getRiskClass(predictionResult.pd_stacking)"
                >
                  <div class="pd-label-stacking">🎯 PD - Stacking</div>
                  <div class="pd-value-stacking">{{ (predictionResult.pd_stacking * 100).toFixed(2) }}%</div>
                  <div class="pd-status-stacking">{{ getRiskLabel(predictionResult.pd_stacking) }}</div>
                </div>
              </div>
            </div>

            <!-- Chart so sánh PD -->
            <div class="chart-container" style="margin-top: 2rem;">
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
              {{ isAnalyzing ? '⏳ Đang phân tích...' : '🤖 Phân tích chuyên sâu bằng AI' }}
            </button>

            <div v-if="geminiAnalysis" class="analysis-box">
              <h3 style="margin-bottom: 1rem; color: #FF6B9D; font-size: 1.4rem;">
                🧠 Phân tích & Khuyến nghị từ AI
              </h3>

              <!-- Quyết định cuối cùng CHO VAY / KHÔNG CHO VAY -->
              <div class="lending-decision" :class="getLendingDecisionClass()">
                <div class="decision-icon">{{ getLendingDecisionIcon() }}</div>
                <div class="decision-text">{{ getLendingDecisionText() }}</div>
              </div>

              <div class="analysis-content">{{ geminiAnalysis }}</div>
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

      <!-- ✅ TAB CONTENT: Dashboard Tài Chính -->
      <div v-if="activeTab === 'dashboard'" class="tab-content">
        <div class="card">
          <h2 class="card-title">📊 Dashboard Tài Chính - Phân tích Ngành nghề</h2>

          <!-- Bảng mô tả và hướng dẫn sử dụng -->
          <div class="dashboard-guide">
            <h3 style="color: #FF6B9D; font-size: 1.1rem; margin-bottom: 0.8rem;">
              📋 Giới thiệu Dashboard
            </h3>
            <p style="margin-bottom: 0.5rem; line-height: 1.6;">
              Dashboard Tài Chính giúp bạn phân tích xu hướng và dữ liệu kinh tế theo từng ngành nghề tại Việt Nam.
              Hệ thống sử dụng AI (Gemini) để thu thập, phân tích dữ liệu mới nhất và đưa ra khuyến nghị cho quyết định tín dụng.
            </p>
            <div class="guide-steps">
              <div class="guide-step">
                <span class="step-number">1</span>
                <span class="step-text">Chọn ngành nghề muốn phân tích</span>
              </div>
              <div class="guide-step">
                <span class="step-number">2</span>
                <span class="step-text">Nhấn "🔄 AI Lấy dữ liệu" để thu thập thông tin mới nhất</span>
              </div>
              <div class="guide-step">
                <span class="step-number">3</span>
                <span class="step-text">Nhấn "📊 Xem biểu đồ" để hiển thị dữ liệu trực quan + phân tích sơ bộ</span>
              </div>
              <div class="guide-step">
                <span class="step-number">4</span>
                <span class="step-text">Nhấn "🔍 Phân tích sâu" để AI đánh giá ảnh hưởng đến quyết định cho vay</span>
              </div>
            </div>
          </div>

          <!-- Dropdown chọn ngành - TÁCH RIÊNG TỪNG NGÀNH -->
          <div style="margin: 2rem 0;">
            <label class="input-label" style="font-size: 1rem; margin-bottom: 0.8rem;">
              🏢 Chọn ngành nghề để phân tích:
            </label>
            <select
              v-model="selectedIndustry"
              class="input-field"
              style="font-size: 1rem; padding: 0.8rem;"
            >
              <option value="">-- Chọn ngành nghề --</option>
              <option value="overview">📈 Tổng quan Kinh tế Việt Nam</option>
              <option value="agriculture">🌾 Nông nghiệp</option>
              <option value="forestry">🌲 Lâm nghiệp</option>
              <option value="fishing">🐟 Thủy sản</option>
              <option value="manufacturing">🏭 Sản xuất công nghiệp</option>
              <option value="processing">⚙️ Chế biến</option>
              <option value="construction">🏗️ Xây dựng</option>
              <option value="realestate">🏘️ Bất động sản</option>
              <option value="retail">🛒 Bán lẻ</option>
              <option value="wholesale">📦 Bán sỉ</option>
              <option value="trading">💼 Thương mại</option>
              <option value="finance">🏦 Tài chính</option>
              <option value="banking">🏧 Ngân hàng</option>
              <option value="insurance">🛡️ Bảo hiểm</option>
              <option value="technology">💻 Công nghệ Thông tin</option>
              <option value="software">📱 Phần mềm</option>
              <option value="transportation">🚚 Vận tải</option>
              <option value="logistics">📮 Logistics</option>
              <option value="tourism">✈️ Du lịch</option>
              <option value="hospitality">🏨 Khách sạn - Nhà hàng</option>
              <option value="services">🎯 Dịch vụ</option>
              <option value="healthcare">🏥 Y tế</option>
              <option value="pharmaceutical">💊 Dược phẩm</option>
              <option value="energy">⚡ Năng lượng</option>
              <option value="electricity">🔌 Điện lực</option>
              <option value="mining">⛏️ Khai khoáng</option>
              <option value="education">🎓 Giáo dục</option>
              <option value="media">📺 Truyền thông</option>
              <option value="textile">👔 Dệt may</option>
              <option value="food">🍔 Thực phẩm & Đồ uống</option>
            </select>
          </div>

          <!-- Các nút chức năng theo luồng -->
          <div v-if="selectedIndustry" class="dashboard-actions">
            <!-- Bước 1: AI Lấy dữ liệu -->
            <button
              @click="fetchIndustryData"
              class="btn btn-primary"
              :disabled="isFetchingData"
              style="width: 100%; margin-bottom: 1rem;"
            >
              {{ isFetchingData ? '⏳ Đang lấy dữ liệu...' : '🔄 AI Lấy dữ liệu tự động' }}
            </button>

            <!-- Bước 2: Xem biểu đồ -->
            <button
              @click="showCharts"
              class="btn btn-secondary"
              :disabled="!industryData || isShowingCharts"
              style="width: 100%; margin-bottom: 1rem;"
            >
              {{ isShowingCharts ? '⏳ Đang tạo biểu đồ...' : '📊 Xem biểu đồ & Phân tích sơ bộ' }}
            </button>

            <!-- Bước 3: Phân tích sâu -->
            <button
              @click="deepAnalyze"
              class="btn btn-accent"
              :disabled="!chartsData || isDeepAnalyzing"
              style="width: 100%;"
            >
              {{ isDeepAnalyzing ? '⏳ Đang phân tích sâu...' : '🔍 Phân tích sâu - Đánh giá tín dụng' }}
            </button>
          </div>

          <!-- Kết quả: Hiển thị biểu đồ -->
          <div v-if="chartsData" class="charts-section" style="margin-top: 2rem;">
            <h3 style="color: #FF6B9D; font-size: 1.3rem; margin-bottom: 1rem; text-align: center;">
              📊 Biểu đồ dữ liệu: {{ getIndustryName(selectedIndustry) }}
            </h3>
            <div id="industry-charts-container" style="width: 100%; min-height: 400px;"></div>

            <!-- Phân tích sơ bộ từ AI -->
            <div v-if="briefAnalysis" class="analysis-box" style="margin-top: 1.5rem;">
              <h4 style="color: #FF6B9D; font-size: 1.1rem; margin-bottom: 1rem;">
                🤖 Phân tích sơ bộ từ AI
              </h4>
              <div class="analysis-content" style="font-size: 0.95rem; line-height: 1.7;">
                {{ briefAnalysis }}
              </div>
            </div>
          </div>

          <!-- Kết quả: Phân tích sâu -->
          <div v-if="deepAnalysisResult" class="deep-analysis-section" style="margin-top: 2rem;">
            <div class="analysis-box" style="border: 3px solid #FF6B9D;">
              <h3 style="color: #FF1493; font-size: 1.4rem; margin-bottom: 1.5rem; text-align: center; font-weight: 900;">
                🎯 Phân tích sâu - Đánh giá tín dụng
              </h3>
              <div class="analysis-content" style="font-size: 1rem; line-height: 1.8; font-weight: 600;">
                {{ deepAnalysisResult }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ✅ TAB CONTENT: Huấn luyện Mô hình -->
      <div v-if="activeTab === 'train'" class="tab-content">
        <div class="card">
          <h2 class="card-title">📚 Huấn luyện Mô hình Machine Learning</h2>

          <div style="margin-bottom: 2rem;">
            <div class="upload-area" @click="$refs.trainFileInput.click()">
              <div class="upload-icon">📤</div>
              <p class="upload-text">{{ trainFileName || 'Tải lên file CSV để huấn luyện' }}</p>
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
          </div>

          <!-- Training Results -->
          <div v-if="trainResult" style="margin-top: 2rem;">
            <h3 style="margin-bottom: 1rem; color: #FF6B9D; font-size: 1.2rem;">
              ✅ Kết quả Huấn luyện
            </h3>
            <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 240, 247, 0.95) 100%); padding: 1.5rem; border-radius: 14px; border: 2px solid rgba(255, 182, 193, 0.3);">
              <p style="margin-bottom: 0.5rem;"><strong>Số mẫu Train:</strong> {{ trainResult.train_samples }}</p>
              <p style="margin-bottom: 0.5rem;"><strong>Số mẫu Test:</strong> {{ trainResult.test_samples }}</p>
              <p style="margin-bottom: 0.5rem;"><strong>Accuracy (Test):</strong> {{ (trainResult.metrics_test.accuracy * 100).toFixed(2) }}%</p>
              <p style="margin-bottom: 0;"><strong>AUC (Test):</strong> {{ (trainResult.metrics_test.auc * 100).toFixed(2) }}%</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import RiskChart from './components/RiskChart.vue'
import IndicatorsChart from './components/IndicatorsChart.vue'

export default {
  name: 'App',
  components: {
    RiskChart,
    IndicatorsChart
  },
  setup() {
    // ✅ TAB STATE - Mặc định là 'predict'
    const activeTab = ref('predict')

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

    // Dashboard Industry Analysis - OLD (giữ lại cho tương thích)
    const selectedIndustry = ref('')
    const isAnalyzingIndustry = ref(false)
    const industryAnalysis = ref('')
    const industryCharts = ref([])

    // Dashboard Industry Analysis - NEW
    const isFetchingData = ref(false)
    const industryData = ref(null)
    const isShowingCharts = ref(false)
    const chartsData = ref(null)
    const briefAnalysis = ref('')
    const isDeepAnalyzing = ref(false)
    const deepAnalysisResult = ref('')

    // API Base URL
    const API_BASE = 'http://localhost:8000'

    // Methods
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

    const getLendingDecisionClass = () => {
      if (!predictionResult.value) return ''
      const pdPercent = predictionResult.value.pd_stacking * 100
      return pdPercent < 10 ? 'decision-approve' : 'decision-reject'
    }

    const getLendingDecisionIcon = () => {
      if (!predictionResult.value) return ''
      const pdPercent = predictionResult.value.pd_stacking * 100
      return pdPercent < 10 ? '✅' : '❌'
    }

    const getLendingDecisionText = () => {
      if (!predictionResult.value) return ''
      const pdPercent = predictionResult.value.pd_stacking * 100
      return pdPercent < 10 ? 'CHO VAY' : 'KHÔNG CHO VAY'
    }

    // Dashboard Industry Analysis
    const getIndustryName = (industry) => {
      const names = {
        'overview': 'Tổng quan Kinh tế Việt Nam',
        'agriculture': 'Nông nghiệp',
        'forestry': 'Lâm nghiệp',
        'fishing': 'Thủy sản',
        'manufacturing': 'Sản xuất công nghiệp',
        'processing': 'Chế biến',
        'construction': 'Xây dựng',
        'realestate': 'Bất động sản',
        'retail': 'Bán lẻ',
        'wholesale': 'Bán sỉ',
        'trading': 'Thương mại',
        'finance': 'Tài chính',
        'banking': 'Ngân hàng',
        'insurance': 'Bảo hiểm',
        'technology': 'Công nghệ Thông tin',
        'software': 'Phần mềm',
        'transportation': 'Vận tải',
        'logistics': 'Logistics',
        'tourism': 'Du lịch',
        'hospitality': 'Khách sạn - Nhà hàng',
        'services': 'Dịch vụ',
        'healthcare': 'Y tế',
        'pharmaceutical': 'Dược phẩm',
        'energy': 'Năng lượng',
        'electricity': 'Điện lực',
        'mining': 'Khai khoáng',
        'education': 'Giáo dục',
        'media': 'Truyền thông',
        'textile': 'Dệt may',
        'food': 'Thực phẩm & Đồ uống'
      }
      return names[industry] || industry
    }

    const analyzeIndustry = async () => {
      if (!selectedIndustry.value) return

      isAnalyzingIndustry.value = true
      industryAnalysis.value = ''
      industryCharts.value = []

      try {
        const requestData = {
          industry: selectedIndustry.value,
          industry_name: getIndustryName(selectedIndustry.value)
        }

        const response = await axios.post(`${API_BASE}/analyze-industry`, requestData)

        if (response.data.status === 'success') {
          industryAnalysis.value = response.data.analysis
          industryCharts.value = response.data.charts || []

          // Scroll to results
          setTimeout(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
          }, 100)
        }
      } catch (error) {
        alert('❌ Lỗi khi phân tích ngành: ' + (error.response?.data?.detail || error.message))
      } finally {
        isAnalyzingIndustry.value = false
      }
    }

    // NEW Dashboard Methods
    const fetchIndustryData = async () => {
      if (!selectedIndustry.value) return

      isFetchingData.value = true
      industryData.value = null
      chartsData.value = null
      briefAnalysis.value = ''
      deepAnalysisResult.value = ''

      try {
        const requestData = {
          industry: selectedIndustry.value,
          industry_name: getIndustryName(selectedIndustry.value)
        }

        const response = await axios.post(`${API_BASE}/fetch-industry-data`, requestData)

        if (response.data.status === 'success') {
          industryData.value = response.data.data
          alert('✅ Đã lấy dữ liệu thành công! Nhấn "Xem biểu đồ" để tiếp tục.')
        }
      } catch (error) {
        alert('❌ Lỗi khi lấy dữ liệu: ' + (error.response?.data?.detail || error.message))
      } finally {
        isFetchingData.value = false
      }
    }

    const showCharts = async () => {
      if (!industryData.value) return

      isShowingCharts.value = true
      chartsData.value = null
      briefAnalysis.value = ''

      try {
        const requestData = {
          industry: selectedIndustry.value,
          industry_name: getIndustryName(selectedIndustry.value),
          data: industryData.value
        }

        const response = await axios.post(`${API_BASE}/generate-charts`, requestData)

        if (response.data.status === 'success') {
          chartsData.value = response.data.charts_data
          briefAnalysis.value = response.data.brief_analysis

          // Render charts using ECharts
          await nextTick()
          renderCharts(response.data.charts_data)

          // Scroll to charts
          setTimeout(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
          }, 100)
        }
      } catch (error) {
        alert('❌ Lỗi khi tạo biểu đồ: ' + (error.response?.data?.detail || error.message))
      } finally {
        isShowingCharts.value = false
      }
    }

    const renderCharts = (chartsDataArray) => {
      const container = document.getElementById('industry-charts-container')
      if (!container) return

      // Clear container
      container.innerHTML = ''

      // Tạo nhiều biểu đồ ECharts
      chartsDataArray.forEach((chartConfig, index) => {
        const chartDiv = document.createElement('div')
        chartDiv.id = `chart-${index}`
        chartDiv.style.width = '100%'
        chartDiv.style.height = '400px'
        chartDiv.style.marginBottom = '2rem'
        container.appendChild(chartDiv)

        const chartInstance = echarts.init(chartDiv)
        chartInstance.setOption(chartConfig)
      })
    }

    const deepAnalyze = async () => {
      if (!chartsData.value) return

      isDeepAnalyzing.value = true
      deepAnalysisResult.value = ''

      try {
        const requestData = {
          industry: selectedIndustry.value,
          industry_name: getIndustryName(selectedIndustry.value),
          data: industryData.value,
          brief_analysis: briefAnalysis.value
        }

        const response = await axios.post(`${API_BASE}/deep-analyze-industry`, requestData)

        if (response.data.status === 'success') {
          deepAnalysisResult.value = response.data.deep_analysis

          // Scroll to deep analysis
          setTimeout(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
          }, 100)
        }
      } catch (error) {
        alert('❌ Lỗi khi phân tích sâu: ' + (error.response?.data?.detail || error.message))
      } finally {
        isDeepAnalyzing.value = false
      }
    }

    return {
      // ✅ TAB STATE
      activeTab,
      // Training
      trainFile,
      trainFileName,
      isTraining,
      trainResult,
      // Prediction
      xlsxFile,
      xlsxFileName,
      isPredicting,
      indicators,
      indicatorsDict,
      predictionResult,
      // Gemini Analysis
      isAnalyzing,
      geminiAnalysis,
      // Export
      isExporting,
      // Dashboard - OLD
      selectedIndustry,
      isAnalyzingIndustry,
      industryAnalysis,
      industryCharts,
      // Dashboard - NEW
      isFetchingData,
      industryData,
      isShowingCharts,
      chartsData,
      briefAnalysis,
      isDeepAnalyzing,
      deepAnalysisResult,
      // Methods
      handleTrainFile,
      trainModel,
      handleXlsxFile,
      predictFromXlsx,
      analyzeWithGemini,
      exportReport,
      getRiskClass,
      getRiskLabel,
      getLendingDecisionClass,
      getLendingDecisionIcon,
      getLendingDecisionText,
      getIndustryName,
      analyzeIndustry,
      // Dashboard - NEW Methods
      fetchIndustryData,
      showCharts,
      deepAnalyze
    }
  }
}
</script>
