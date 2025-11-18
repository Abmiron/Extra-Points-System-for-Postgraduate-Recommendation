<template>
  <div class="page-content">
    <div class="page-title">
      <span>学院、系和专业管理</span>
    </div>
    
    <!-- 标签页切换 -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        :class="['tab-btn', { active: activeTab === tab.value }]"
        @click="activeTab = tab.value"
      >
        {{ tab.label }}
      </button>
    </div>
    
    <!-- 学院管理 -->
    <div v-if="activeTab === 'faculties'" class="card">
      <div class="card-title">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>学院管理</span>
          <button class="btn btn-outline" @click="showAddFacultyModal = true">
            <font-awesome-icon icon="fa-solid fa-plus" /> 添加学院
          </button>
        </div>
      </div>
      
      <!-- 搜索和筛选 -->
      <div class="filters" style="padding: 0 20px; padding-top: 20px;">
        <div class="filter-group">
          <input
            type="text"
            v-model="facultyFilter"
            placeholder="搜索学院..."
            class="form-control"
          >
        </div>
        <div class="filter-group">
          <button class="btn btn-outline" @click="resetFilters">清空筛选</button>
        </div>
      </div>
      
      <!-- 加载状态指示器 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载中...</div>
      </div>
      
      <!-- 学院列表 -->
      <div class="table-container" style="padding: 0 20px 20px;">
        <table class="application-table">
          <thead>
            <tr>
              <th>学院名称</th>
              <th>描述</th>
              <th style="text-align: center;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="faculty in filteredFaculties" :key="faculty.id">
              <td>{{ faculty.name }}</td>
              <td>{{ faculty.description || '无描述' }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-outline btn small-btn" @click="editFaculty(faculty)" title="编辑">
                    <font-awesome-icon icon="fa-solid fa-edit" />
                  </button>
                  <button class="btn-outline btn small-btn delete-btn" @click="deleteFaculty(faculty.id)" title="删除">
                    <font-awesome-icon icon="fa-solid fa-trash" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 系管理 -->
    <div v-if="activeTab === 'departments'" class="card">
      <div class="card-title">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>系管理</span>
          <button class="btn btn-outline" @click="showAddDepartmentModal = true">
            <font-awesome-icon icon="fa-solid fa-plus" /> 添加系
          </button>
        </div>
      </div>
      
      <!-- 搜索和筛选 -->
      <div class="filters" style="padding: 0 20px; padding-top: 20px;">
        <div class="filter-group">
          <input
            type="text"
            v-model="departmentFilter"
            placeholder="搜索系..."
            class="form-control"
          >
        </div>
        <div class="filter-group">
          <label class="filter-label">学院：</label>
          <select v-model="selectedFacultyId" class="form-control">
            <option value="">全部学院</option>
            <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
              {{ faculty.name }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <button class="btn btn-outline" @click="resetFilters">清空筛选</button>
        </div>
      </div>
      
      <!-- 加载状态指示器 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载中...</div>
      </div>
      
      <!-- 系列表 -->
      <div class="table-container" style="padding: 0 20px 20px;">
        <table class="application-table">
          <thead>
            <tr>
              <th>系名称</th>
              <th>所属学院</th>
              <th>描述</th>
              <th style="text-align: center;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="department in filteredDepartments" :key="department.id">
              <td>{{ department.name }}</td>
              <td>{{ getFacultyName(department.faculty_id) }}</td>
              <td>{{ department.description || '无描述' }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-outline btn small-btn" @click="editDepartment(department)" title="编辑">
                    <font-awesome-icon icon="fa-solid fa-edit" />
                  </button>
                  <button class="btn-outline btn small-btn delete-btn" @click="deleteDepartment(department.id)" title="删除">
                    <font-awesome-icon icon="fa-solid fa-trash" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 专业管理 -->
    <div v-if="activeTab === 'majors'" class="card">
      <div class="card-title">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>专业管理</span>
          <button class="btn btn-outline" @click="showAddMajorModal = true">
            <font-awesome-icon icon="fa-solid fa-plus" /> 添加专业
          </button>
        </div>
      </div>
      
      <!-- 搜索和筛选 -->
      <div class="filters" style="padding: 0 20px; padding-top: 20px;">
        <div class="filter-group">
          <input
            type="text"
            v-model="majorFilter"
            placeholder="搜索专业..."
            class="form-control"
          >
        </div>
        <div class="filter-group">
          <label class="filter-label">学院：</label>
          <select v-model="selectedFacultyId" class="form-control">
            <option value="">全部学院</option>
            <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
              {{ faculty.name }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">系：</label>
          <select v-model="selectedDepartmentId" class="form-control">
            <option value="">全部系</option>
            <option v-for="department in filteredDepartments" :key="department.id" :value="department.id">
              {{ department.name }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <button class="btn btn-outline" @click="resetFilters">清空筛选</button>
        </div>
      </div>
      
      <!-- 加载状态指示器 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载中...</div>
      </div>
      
      <!-- 专业列表 -->
      <div class="table-container" style="padding: 0 20px 20px;">
        <table class="application-table">
          <thead>
            <tr>
              <th>专业名称</th>
              <th>所属系</th>
              <th>描述</th>
              <th style="text-align: center;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="major in filteredMajors" :key="major.id">
              <td>{{ major.name }}</td>
              <td>{{ getDepartmentName(major.department_id) }}</td>
              <td>{{ major.description || '无描述' }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-outline btn small-btn" @click="editMajor(major)" title="编辑">
                    <font-awesome-icon icon="fa-solid fa-edit" />
                  </button>
                  <button class="btn-outline btn small-btn delete-btn" @click="deleteMajor(major.id)" title="删除">
                    <font-awesome-icon icon="fa-solid fa-trash" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 添加学院模态框 -->
    <div v-if="showAddFacultyModal" class="modal-overlay" @click="showAddFacultyModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>添加学院</h3>
          <button class="close-btn" @click="showAddFacultyModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addFaculty">
            <div class="form-group">
              <label for="facultyName">学院名称</label>
              <input 
                type="text" 
                id="facultyName" 
                v-model="newFaculty.name" 
                required
                placeholder="请输入学院名称"
                class="form-control"
              >
            </div>
            <div class="form-group">
              <label for="facultyDescription">描述</label>
              <textarea 
                id="facultyDescription" 
                v-model="newFaculty.description" 
                rows="3"
                placeholder="请输入学院描述（可选）"
                class="form-control"
              ></textarea>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="showAddFacultyModal = false">取消</button>
              <button type="submit" class="btn">添加</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- 编辑学院模态框 -->
    <div v-if="showEditFacultyModal" class="modal-overlay" @click="showEditFacultyModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>编辑学院</h3>
          <button class="close-btn" @click="showEditFacultyModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updateFaculty">
            <div class="form-group">
              <label for="editFacultyName">学院名称</label>
              <input 
                type="text" 
                id="editFacultyName" 
                v-model="editingFaculty.name" 
                required
                placeholder="请输入学院名称"
                class="form-control"
              >
            </div>
            <div class="form-group">
              <label for="editFacultyDescription">描述</label>
              <textarea 
                id="editFacultyDescription" 
                v-model="editingFaculty.description" 
                rows="3"
                placeholder="请输入学院描述（可选）"
                class="form-control"
              ></textarea>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="showEditFacultyModal = false">取消</button>
              <button type="submit" class="btn">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- 添加系模态框 -->
    <div v-if="showAddDepartmentModal" class="modal-overlay" @click="showAddDepartmentModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>添加系</h3>
          <button class="close-btn" @click="showAddDepartmentModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addDepartment">
            <div class="form-group">
              <label for="departmentName">系名称</label>
              <input 
                type="text" 
                id="departmentName" 
                v-model="newDepartment.name" 
                required
                placeholder="请输入系名称"
                class="form-control"
              >
            </div>
            <div class="form-group">
              <label for="departmentFaculty">所属学院</label>
              <select 
                id="departmentFaculty" 
                v-model="newDepartment.faculty_id" 
                required
                class="form-control"
              >
                <option value="">请选择学院</option>
                <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
                  {{ faculty.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="departmentDescription">描述</label>
              <textarea 
                id="departmentDescription" 
                v-model="newDepartment.description" 
                rows="3"
                placeholder="请输入系描述（可选）"
                class="form-control"
              ></textarea>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="showAddDepartmentModal = false">取消</button>
              <button type="submit" class="btn">添加</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- 编辑系模态框 -->
    <div v-if="showEditDepartmentModal" class="modal-overlay" @click="showEditDepartmentModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>编辑系</h3>
          <button class="close-btn" @click="showEditDepartmentModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updateDepartment">
            <div class="form-group">
              <label for="editDepartmentName">系名称</label>
              <input 
                type="text" 
                id="editDepartmentName" 
                v-model="editingDepartment.name" 
                required
                placeholder="请输入系名称"
                class="form-control"
              >
            </div>
            <div class="form-group">
              <label for="editDepartmentFaculty">所属学院</label>
              <select 
                id="editDepartmentFaculty" 
                v-model="editingDepartment.faculty_id" 
                required
                class="form-control"
              >
                <option value="">请选择学院</option>
                <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
                  {{ faculty.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="editDepartmentDescription">描述</label>
              <textarea 
                id="editDepartmentDescription" 
                v-model="editingDepartment.description" 
                rows="3"
                placeholder="请输入系描述（可选）"
                class="form-control"
              ></textarea>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="showEditDepartmentModal = false">取消</button>
              <button type="submit" class="btn">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- 添加专业模态框 -->
    <div v-if="showAddMajorModal" class="modal-overlay" @click="showAddMajorModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>添加专业</h3>
          <button class="close-btn" @click="showAddMajorModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addMajor">
            <div class="form-group">
              <label for="majorName">专业名称</label>
              <input 
                type="text" 
                id="majorName" 
                v-model="newMajor.name" 
                required
                placeholder="请输入专业名称"
                class="form-control"
              >
            </div>
            <div class="form-group">
              <label for="majorFaculty">所属学院</label>
              <select 
                id="majorFaculty" 
                v-model="newMajor.faculty_id" 
                required
                class="form-control"
                @change="onNewMajorFacultyChange"
              >
                <option value="">请选择学院</option>
                <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
                  {{ faculty.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="majorDepartment">所属系</label>
              <select 
                id="majorDepartment" 
                v-model="newMajor.department_id" 
                required
                class="form-control"
                :disabled="!newMajor.faculty_id"
              >
                <option value="">请选择系</option>
                <option v-for="department in filteredDepartmentsForMajor" :key="department.id" :value="department.id">
                  {{ department.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="majorDescription">描述</label>
              <textarea 
                id="majorDescription" 
                v-model="newMajor.description" 
                rows="3"
                placeholder="请输入专业描述（可选）"
                class="form-control"
              ></textarea>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="showAddMajorModal = false">取消</button>
              <button type="submit" class="btn">添加</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- 编辑专业模态框 -->
    <div v-if="showEditMajorModal" class="modal-overlay" @click="showEditMajorModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>编辑专业</h3>
          <button class="close-btn" @click="showEditMajorModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updateMajor">
            <div class="form-group">
              <label for="editMajorName">专业名称</label>
              <input 
                type="text" 
                id="editMajorName" 
                v-model="editingMajor.name" 
                required
                placeholder="请输入专业名称"
                class="form-control"
              >
            </div>
            <div class="form-group">
              <label for="editMajorFaculty">所属学院</label>
              <select 
                id="editMajorFaculty" 
                v-model="editingMajor.faculty_id" 
                required
                class="form-control"
                @change="onEditMajorFacultyChange"
              >
                <option value="">请选择学院</option>
                <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
                  {{ faculty.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="editMajorDepartment">所属系</label>
              <select 
                id="editMajorDepartment" 
                v-model="editingMajor.department_id" 
                required
                class="form-control"
                :disabled="!editingMajor.faculty_id"
              >
                <option value="">请选择系</option>
                <option v-for="department in filteredDepartmentsForEditMajor" :key="department.id" :value="department.id">
                  {{ department.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="editMajorDescription">描述</label>
              <textarea 
                id="editMajorDescription" 
                v-model="editingMajor.description" 
                rows="3"
                placeholder="请输入专业描述（可选）"
                class="form-control"
              ></textarea>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="showEditMajorModal = false">取消</button>
              <button type="submit" class="btn">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import api from '../../utils/api'

export default {
  name: 'FacultyManagement',
  setup() {
    // 标签页数据
    const tabs = [
      { value: 'faculties', label: '学院' },
      { value: 'departments', label: '系' },
      { value: 'majors', label: '专业' }
    ]
    
    // 当前激活的标签页
    const activeTab = ref('faculties')
    
    // 数据存储
    const faculties = ref([])
    const departments = ref([])
    const majors = ref([])
    const loading = ref(false)
    
    // 筛选条件
    const facultyFilter = ref('')
    const departmentFilter = ref('')
    const majorFilter = ref('')
    const selectedFacultyId = ref('')
    const selectedDepartmentId = ref('')
    
    // 模态框控制
    const showAddFacultyModal = ref(false)
    const showEditFacultyModal = ref(false)
    const showAddDepartmentModal = ref(false)
    const showEditDepartmentModal = ref(false)
    const showAddMajorModal = ref(false)
    const showEditMajorModal = ref(false)
    
    // 表单数据
    const newFaculty = ref({ name: '', description: '' })
    const editingFaculty = ref({ id: null, name: '', description: '' })
    const newDepartment = ref({ name: '', faculty_id: '', description: '' })
    const editingDepartment = ref({ id: null, name: '', faculty_id: '', description: '' })
    const newMajor = ref({ name: '', faculty_id: '', department_id: '', description: '' })
    const editingMajor = ref({ id: null, name: '', faculty_id: '', department_id: '', description: '' })
    
    // 加载数据
    const loadFaculties = async () => {
      loading.value = true
      try {
        const response = await api.getFacultiesAdmin()
        faculties.value = response.faculties  // 后端返回 {'faculties': [...]} 格式
        updateFilters() // 数据加载完成后更新筛选
      } catch (error) {
        console.error('加载学院数据失败:', error)
        alert('加载学院数据失败')
      } finally {
        loading.value = false
      }
    }
    
    const loadDepartments = async () => {
      loading.value = true
      try {
        const response = await api.getDepartmentsAdmin(selectedFacultyId.value)
        departments.value = response.departments  // 后端返回 {'departments': [...]} 格式
        updateFilters() // 数据加载完成后更新筛选
      } catch (error) {
        console.error('加载系数据失败:', error)
        alert('加载系数据失败')
      } finally {
        loading.value = false
      }
    }
    
    const loadMajors = async () => {
      loading.value = true
      try {
        const response = await api.getMajorsAdmin(selectedDepartmentId.value, selectedFacultyId.value)
        majors.value = response.majors  // 后端返回 {'majors': [...]} 格式
        updateFilters() // 数据加载完成后更新筛选
      } catch (error) {
        console.error('加载专业数据失败:', error)
        alert('加载专业数据失败')
      } finally {
        loading.value = false
      }
    }
    
    // 筛选后的数据
    const filteredFaculties = ref([])
    const filteredDepartments = ref([])
    const filteredMajors = ref([])
    
    // 用于添加和编辑专业的系筛选
    const filteredDepartmentsForMajor = ref([])
    const filteredDepartmentsForEditMajor = ref([])
    
    // 监听筛选条件变化
    const updateFilters = () => {
      // 筛选学院
      filteredFaculties.value = faculties.value ? faculties.value.filter(faculty => 
        faculty.name.toLowerCase().includes(facultyFilter.value.toLowerCase())
      ) : []
      
      // 筛选系
      filteredDepartments.value = departments.value ? departments.value.filter(department => 
        department.name.toLowerCase().includes(departmentFilter.value.toLowerCase()) &&
        (selectedFacultyId.value ? department.faculty_id === parseInt(selectedFacultyId.value) : true)
      ) : []
      
      // 筛选专业
      filteredMajors.value = majors.value ? majors.value.filter(major => 
        major.name.toLowerCase().includes(majorFilter.value.toLowerCase()) &&
        (selectedDepartmentId.value ? major.department_id === parseInt(selectedDepartmentId.value) : true)
      ) : []
    }
    
    // 监听筛选条件变化
    const unwatchFacultyFilter = watch(facultyFilter, updateFilters)
    const unwatchDepartmentFilter = watch(departmentFilter, updateFilters)
    const unwatchMajorFilter = watch(majorFilter, updateFilters)// 监听筛选条件变化
    const unwatchSelectedFacultyId = watch(selectedFacultyId, (newVal) => {
      // 当选择学院时，重置系选择
      selectedDepartmentId.value = '';
      loadDepartments().then(() => {
        loadMajors().then(() => {
          updateFilters()
        })
      })
    })
    const unwatchSelectedDepartmentId = watch(selectedDepartmentId, (newVal) => {
      loadMajors().then(() => {
        updateFilters()
      })
    })
    
    // 监听数据变化
    const unwatchFaculties = watch(faculties, updateFilters)
    const unwatchDepartments = watch(departments, updateFilters)
    const unwatchMajors = watch(majors, updateFilters)
    
    // 重置筛选条件
    const resetFilters = () => {
      facultyFilter.value = ''
      departmentFilter.value = ''
      majorFilter.value = ''
      selectedFacultyId.value = ''
      selectedDepartmentId.value = ''
      // 重新加载所有数据
      loadFaculties()
      loadDepartments()
      loadMajors()
    }
    
    // 学院相关操作
    const addFaculty = async () => {
      try {
        await api.createFacultyAdmin(newFaculty.value)
        showAddFacultyModal.value = false
        newFaculty.value = { name: '', description: '' }
        loadFaculties()
        alert('学院添加成功')
      } catch (error) {
        console.error('添加学院失败:', error)
        alert('添加学院失败')
      }
    }
    
    const editFaculty = (faculty) => {
      editingFaculty.value = { ...faculty }
      showEditFacultyModal.value = true
    }
    
    const updateFaculty = async () => {
      try {
        await api.updateFacultyAdmin(editingFaculty.value.id, editingFaculty.value)
        showEditFacultyModal.value = false
        loadFaculties()
        alert('学院更新成功')
      } catch (error) {
        console.error('更新学院失败:', error)
        alert('更新学院失败')
      }
    }
    
    const deleteFaculty = async (id) => {
      if (confirm('确定要删除这个学院吗？删除后相关的系、专业和学生也会被删除。')) {
        try {
          await api.deleteFacultyAdmin(id)
          loadFaculties()
          loadDepartments()
          loadMajors()
          alert('学院删除成功')
        } catch (error) {
          console.error('删除学院失败:', error)
          alert('删除学院失败')
        }
      }
    }
    
    // 系相关操作
    const addDepartment = async () => {
      try {
        await api.createDepartmentAdmin(newDepartment.value)
        showAddDepartmentModal.value = false
        newDepartment.value = { name: '', faculty_id: '', description: '' }
        loadDepartments()
        alert('系添加成功')
      } catch (error) {
        console.error('添加系失败:', error)
        alert('添加系失败')
      }
    }
    
    const editDepartment = (department) => {
      editingDepartment.value = { ...department }
      showEditDepartmentModal.value = true
    }
    
    const updateDepartment = async () => {
      try {
        await api.updateDepartmentAdmin(editingDepartment.value.id, editingDepartment.value)
        showEditDepartmentModal.value = false
        loadDepartments()
        loadMajors()
        alert('系更新成功')
      } catch (error) {
        console.error('更新系失败:', error)
        alert('更新系失败')
      }
    }
    
    const deleteDepartment = async (id) => {
      if (confirm('确定要删除这个系吗？删除后相关的专业和学生也会被删除。')) {
        try {
          await api.deleteDepartmentAdmin(id)
          loadDepartments()
          loadMajors()
          alert('系删除成功')
        } catch (error) {
          console.error('删除系失败:', error)
          alert('删除系失败')
        }
      }
    }
    
    // 专业相关操作
    const addMajor = async () => {
      try {
        await api.createMajorAdmin(newMajor.value)
        showAddMajorModal.value = false
        newMajor.value = { name: '', faculty_id: '', department_id: '', description: '' }
        loadMajors()
        alert('专业添加成功')
      } catch (error) {
        console.error('添加专业失败:', error)
        alert('添加专业失败')
      }
    }
    
    const editMajor = (major) => {
      // 查找专业所属的系
      const department = departments.value.find(d => d.id === major.department_id)
      // 设置学院ID
      editingMajor.value = { ...major, faculty_id: department ? department.faculty_id : '' }
      // 更新编辑专业时的系筛选
      updateEditMajorDepartments()
      showEditMajorModal.value = true
    }
    
    // 监听添加专业时学院变化
    const onNewMajorFacultyChange = () => {
      // 重置系选择
      newMajor.value.department_id = ''
      // 过滤系列表
      filteredDepartmentsForMajor.value = departments.value.filter(d => d.faculty_id === parseInt(newMajor.value.faculty_id))
    }
    
    // 监听编辑专业时学院变化
    const onEditMajorFacultyChange = () => {
      // 重置系选择
      editingMajor.value.department_id = ''
      // 过滤系列表
      updateEditMajorDepartments()
    }
    
    // 更新编辑专业时的系列表
    const updateEditMajorDepartments = () => {
      if (editingMajor.value.faculty_id) {
        filteredDepartmentsForEditMajor.value = departments.value.filter(d => d.faculty_id === parseInt(editingMajor.value.faculty_id))
      } else {
        filteredDepartmentsForEditMajor.value = []
      }
    }
    
    const updateMajor = async () => {
      try {
        await api.updateMajorAdmin(editingMajor.value.id, editingMajor.value)
        showEditMajorModal.value = false
        loadMajors()
        alert('专业更新成功')
      } catch (error) {
        console.error('更新专业失败:', error)
        alert('更新专业失败')
      }
    }
    
    const deleteMajor = async (id) => {
      if (confirm('确定要删除这个专业吗？删除后相关的学生也会被删除。')) {
        try {
          await api.deleteMajorAdmin(id)
          loadMajors()
          alert('专业删除成功')
        } catch (error) {
          console.error('删除专业失败:', error)
          alert('删除专业失败')
        }
      }
    }
    
    // 辅助函数
    const getFacultyName = (facultyId) => {
      const faculty = faculties.value.find(f => f.id === facultyId)
      return faculty ? faculty.name : '未找到'
    }
    
    const getDepartmentName = (departmentId) => {
      const department = departments.value.find(d => d.id === departmentId)
      return department ? department.name : '未找到'
    }
    
    // 初始化
    onMounted(() => {
      loadFaculties()
      loadDepartments()
      loadMajors()
    })
    
    // 清理监听器
    onUnmounted(() => {
      unwatchFacultyFilter()
      unwatchDepartmentFilter()
      unwatchMajorFilter()
      unwatchSelectedFacultyId()
      unwatchSelectedDepartmentId()
      unwatchFaculties()
      unwatchDepartments()
      unwatchMajors()
    })
    
    return {
      tabs,
      activeTab,
      faculties,
      departments,
      majors,
      loading,
      facultyFilter,
      departmentFilter,
      majorFilter,
      selectedFacultyId,
      selectedDepartmentId,
      filteredFaculties,
      filteredDepartments,
      filteredMajors,
      filteredDepartmentsForMajor,
      filteredDepartmentsForEditMajor,
      showAddFacultyModal,
      showEditFacultyModal,
      showAddDepartmentModal,
      showEditDepartmentModal,
      showAddMajorModal,
      showEditMajorModal,
      newFaculty,
      editingFaculty,
      newDepartment,
      editingDepartment,
      newMajor,
      editingMajor,
      addFaculty,
      editFaculty,
      updateFaculty,
      deleteFaculty,
      addDepartment,
      editDepartment,
      updateDepartment,
      deleteDepartment,
      addMajor,
      editMajor,
      updateMajor,
      deleteMajor,
      getFacultyName,
      getDepartmentName,
      resetFilters,
      onNewMajorFacultyChange,
      onEditMajorFacultyChange
    }
  }
}
</script>

<style scoped>
@import '../common/shared-styles.css';

/* 加载状态样式 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}
</style>