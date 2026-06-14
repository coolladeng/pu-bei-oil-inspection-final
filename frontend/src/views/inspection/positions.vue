<template>
  <div class="positions-page">
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="所属班组">
          <el-tree-select v-model="searchForm.dept_id" :data="deptTree" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择班组" clearable filterable style="width: 200px" />
        </el-form-item>
        <el-form-item label="岗位类型">
          <el-select v-model="searchForm.pos_type" placeholder="全部" clearable style="width: 140px">
            <el-option label="巡检员" value="inspector" />
            <el-option label="维保员" value="maintainer" />
            <el-option label="审核员" value="reviewer" />
            <el-option label="调度员" value="dispatcher" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadPositions">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <div class="table-header">
        <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon>新增岗位</el-button>
      </div>
      <el-table :data="positions" v-loading="loading" stripe>
        <el-table-column prop="name" label="岗位名称" min-width="140" />
        <el-table-column prop="dept_name" label="所属班组" min-width="140" />
        <el-table-column label="岗位类型" width="120">
          <template #default="{ row }">
            <el-tag :type="typeTag(row.pos_type)" size="small">{{ typeLabel(row.pos_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? '正常' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="岗位名称" prop="name">
          <el-input v-model="form.name" placeholder="如 巡检一班班长" />
        </el-form-item>
        <el-form-item label="所属班组" prop="dept_id">
          <el-tree-select v-model="form.dept_id" :data="deptTree" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择班组" filterable style="width: 100%" />
        </el-form-item>
        <el-form-item label="岗位类型" prop="pos_type">
          <el-select v-model="form.pos_type" placeholder="选择类型" style="width: 100%">
            <el-option label="巡检员" value="inspector" />
            <el-option label="维保员" value="maintainer" />
            <el-option label="审核员" value="reviewer" />
            <el-option label="调度员" value="dispatcher" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/http'

interface Position {
  id: number; name: string; dept_id: number; dept_name: string; pos_type: string; status: number
}

const loading = ref(false); const submitting = ref(false)
const positions = ref<Position[]>([])
const deptTree = ref<any[]>([])
const searchForm = reactive({ dept_id: undefined as number | undefined, pos_type: '' })
const dialogVisible = ref(false); const dialogTitle = ref('新增岗位')
const editingId = ref<number | null>(null)
const formRef = ref()
const form = reactive<{ name: string; dept_id: number | null; pos_type: string }>({ name: '', dept_id: null, pos_type: '' })
const rules = {
  name: [{ required: true, message: '请输入岗位名称', trigger: 'blur' }],
  dept_id: [{ required: true, message: '请选择所属班组', trigger: 'change' }],
  pos_type: [{ required: true, message: '请选择岗位类型', trigger: 'change' }],
}

function typeLabel(t: string) { return { inspector: '巡检员', maintainer: '维保员', reviewer: '审核员', dispatcher: '调度员' }[t] || t }
function typeTag(t: string) { return { inspector: 'primary', maintainer: 'success', reviewer: 'warning', dispatcher: 'info' }[t] || '' }

async function loadDeptTree() {
  try {
    const data = await request.get('/departments')
    deptTree.value = Array.isArray(data) ? data : []
  } catch {
    deptTree.value = []
  }
}
async function loadPositions() {
  loading.value = true
  try {
    const params: any = {}
    if (searchForm.dept_id) params.dept_id = Number(searchForm.dept_id)
    if (searchForm.pos_type) params.pos_type = searchForm.pos_type
    const data = await request.get('/positions', { params })
    positions.value = data.list || data || []
  } catch {
    positions.value = []
  } finally { loading.value = false }
}
function resetSearch() { searchForm.dept_id = undefined; searchForm.pos_type = ''; loadPositions() }
function resetForm() { form.name = ''; form.dept_id = null; form.pos_type = '' }

function openDialog(row?: Position) {
  resetForm(); editingId.value = row?.id || null
  if (row) { dialogTitle.value = '编辑岗位'; form.name = row.name; form.dept_id = row.dept_id; form.pos_type = row.pos_type }
  else { dialogTitle.value = '新增岗位' }
  dialogVisible.value = true
}
async function submitForm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = { name: form.name, dept_id: Number(form.dept_id), pos_type: form.pos_type }
    if (editingId.value) {
      await request.put(`/positions/${editingId.value}`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post('/positions', payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadPositions()
  } finally { submitting.value = false }
}
async function handleDelete(row: Position) {
  await ElMessageBox.confirm(`确定删除岗位"${row.name}"吗？`, '确认', { type: 'warning' })
  await request.delete(`/positions/${row.id}`); ElMessage.success('删除成功'); loadPositions()
}

onMounted(() => { loadDeptTree(); loadPositions() })
</script>
<style scoped>
.positions-page { padding: 16px; }
.search-card { margin-bottom: 16px; }
.table-header { margin-bottom: 16px; display: flex; gap: 12px; }
</style>