# 规则选择与自动分数计算功能实现方案

## 系统现状分析

### 现有模型结构

#### Rule 模型
- 核心字段：name, type, sub_type, award_level, award_grade, award_category, score, max_score, author_rank_ratio等
- 主要用途：定义加分规则，包括适用条件和分数配置

#### Application 模型
- 核心字段：student_id, application_type, academic_type, award_level, award_grade, award_category, self_score, final_score等
- 主要用途：记录学生的加分申请信息

### 现有流程
1. 学生填写申请表单并提交
2. 老师/管理员在审核时，系统根据申请信息匹配对应的规则
3. 如果找到匹配规则，自动计算最终分数；否则使用手动输入分数
4. 审核完成后更新申请状态和最终分数

## 实现方案设计

### 1. 核心需求
- 学生端：填写申请时可选择适用的规则，并查看预估分数
- 审核端：老师/管理员可查看学生选择的规则和自动计算的分数
- 系统：确保规则选择与申请信息的一致性，实现自动分数计算

### 2. 数据库设计

#### 调整 Application 模型
```python
# 在 models.py 中修改 Application 模型
class Application(db.Model):
    # 现有字段...
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=True)
    rule = db.relationship('Rule', backref=db.backref('applications', lazy=True))
    # 现有字段...
```

### 3. 后端 API 设计

#### 3.1 添加规则查询 API
```python
# 在 rule_bp.py 中添加
@rule_bp.route('/rules/match', methods=['POST'])
def match_rules():
    """根据申请信息匹配规则"""
    data = request.get_json()
    
    # 构建查询条件
    query = Rule.query.filter_by(status='active')
    
    if data.get('applicationType'):
        query = query.filter_by(type=data['applicationType'])
    
    if data.get('academicType'):
        query = query.filter_by(sub_type=data['academicType'])
    
    if data.get('awardLevel'):
        query = query.filter_by(award_level=data['awardLevel'])
    
    if data.get('awardGrade'):
        query = query.filter_by(award_grade=data['awardGrade'])
    
    if data.get('awardCategory'):
        query = query.filter_by(award_category=data['awardCategory'])
    
    # 如果是团队奖项，考虑团队角色
    if data.get('awardType') == 'team':
        if data.get('teamRole'):
            query = query.filter_by(team_role=data['teamRole'])
    
    rules = query.all()
    
    # 转换为JSON格式返回
    rule_list = []
    for rule in rules:
        rule_data = {
            'id': rule.id,
            'name': rule.name,
            'score': rule.score,
            'max_score': rule.max_score,
            'author_rank_ratio': rule.author_rank_ratio,
            # 其他必要字段...
        }
        rule_list.append(rule_data)
    
    return jsonify({'rules': rule_list}), 200
```

#### 3.2 更新申请提交 API
```python
# 在 application_bp.py 中修改 create_application 函数
def create_application():
    # 现有代码...
    
    # 添加规则关联
    if data.get('ruleId'):
        app.rule_id = data['ruleId']
    
    # 现有代码...
```

#### 3.3 更新申请审核 API
```python
# 在 application_bp.py 中修改 review_application 函数
def review_application(id):
    # 现有代码...
    
    # 如果学生选择了规则，使用该规则计算分数
    if app.rule_id:
        matched_rule = app.rule
        
        # 检查是否超过最大项目数量限制
        max_count_exceeded = False
        if matched_rule.max_count:
            # 统计该学生该类型奖项已通过的数量
            approved_count = Application.query.filter_by(
                student_id=app.student_id,
                status='approved',
                application_type=app.application_type,
                academic_type=app.academic_type
            ).count()
            
            if approved_count >= matched_rule.max_count:
                max_count_exceeded = True
        
        if max_count_exceeded:
            # 超过最大项目数量限制，不给予加分
            app.final_score = 0
        else:
            # 计算基础分数
            final_score = matched_rule.score
            
            # 应用作者排序比例（如果适用）
            if app.author_rank_type == 'ranked' and app.author_order:
                # 根据作者排序位置应用不同比例
                if app.author_order == 1:
                    # 第一作者，使用规则中的比例
                    if matched_rule.author_rank_ratio:
                        final_score *= matched_rule.author_rank_ratio
                else:
                    # 非第一作者，分数递减
                    final_score *= (1 - (app.author_order - 1) * 0.1)
                    
                    # 最低不低于原分数的30%
                    final_score = max(final_score, matched_rule.score * 0.3)
            
            # 应用最大分数限制（如果有）
            if matched_rule.max_score:
                final_score = min(final_score, matched_rule.max_score)
            
            # 设置最终分数
            app.final_score = final_score
    elif data.get('finalScore'):
        # 如果没有选择规则，使用手动输入的分数
        app.final_score = data.get('finalScore')
    
    # 现有代码...
```

### 4. 前端实现

#### 4.1 修改申请表单 (ApplicationForm.vue)

1. 添加规则选择组件
```vue
<!-- 在申请表单中添加规则选择区域 -->
<div class="form-group">
  <label for="ruleSelect">选择适用规则：</label>
  <select v-model="formData.ruleId" class="form-control" @change="calculateEstimatedScore">
    <option value="">请选择规则</option>
    <option v-for="rule in availableRules" :key="rule.id" :value="rule.id">
      {{ rule.name }} (基础分数: {{ rule.score }}分)
    </option>
  </select>
</div>

<div class="form-group" v-if="estimatedScore !== null">
  <label>预估分数：</label>
  <span class="estimated-score">{{ estimatedScore }}分</span>
</div>
```

2. 添加规则加载和分数计算逻辑
```javascript
// 在 ApplicationForm.vue 中添加
import { ref, watch, computed } from 'vue'
import api from '../../utils/api'

// 可用规则列表
const availableRules = ref([])
// 预估分数
const estimatedScore = ref(null)

// 监听申请类型、级别、等级等字段变化，动态加载匹配的规则
watch([() => formData.applicationType, () => formData.academicType, () => formData.awardLevel, () => formData.awardGrade, () => formData.awardCategory, () => formData.teamRole], async () => {
  // 只有当关键字段都填写后，才加载规则
  if (formData.applicationType && formData.awardLevel && formData.awardGrade) {
    await loadMatchingRules()
  } else {
    availableRules.value = []
    formData.ruleId = ''
    estimatedScore.value = null
  }
})

// 加载匹配的规则
const loadMatchingRules = async () => {
  try {
    const response = await api.apiRequest('/rules/match', 'POST', {
      applicationType: formData.applicationType,
      academicType: formData.academicType,
      awardLevel: formData.awardLevel,
      awardGrade: formData.awardGrade,
      awardCategory: formData.awardCategory,
      awardType: formData.awardType,
      teamRole: formData.teamRole
    })
    
    availableRules.value = response.rules
    
    // 如果之前选择的规则不在新的规则列表中，清空选择
    if (formData.ruleId && !availableRules.value.some(rule => rule.id === formData.ruleId)) {
      formData.ruleId = ''
      estimatedScore.value = null
    } else {
      // 重新计算预估分数
      calculateEstimatedScore()
    }
  } catch (error) {
    console.error('加载规则失败:', error)
    availableRules.value = []
  }
}

// 计算预估分数
const calculateEstimatedScore = () => {
  if (!formData.ruleId) {
    estimatedScore.value = null
    return
  }
  
  const selectedRule = availableRules.value.find(rule => rule.id === formData.ruleId)
  if (!selectedRule) {
    estimatedScore.value = null
    return
  }
  
  let score = selectedRule.score
  
  // 应用作者排序比例（如果适用）
  if (formData.author_rank_type === 'ranked' && formData.author_order) {
    if (formData.author_order === 1 && selectedRule.author_rank_ratio) {
      score *= selectedRule.author_rank_ratio
    } else {
      score *= (1 - (formData.author_order - 1) * 0.1)
      score = Math.max(score, selectedRule.score * 0.3)
    }
  }
  
  // 应用最大分数限制
  if (selectedRule.max_score) {
    score = Math.min(score, selectedRule.max_score)
  }
  
  estimatedScore.value = score.toFixed(2)
}

// 监听作者排序变化，重新计算预估分数
watch([() => formData.author_rank_type, () => formData.author_order], () => {
  calculateEstimatedScore()
})
```

#### 4.2 修改审核详情模态框 (TeacherEditDetailModal.vue)

1. 显示学生选择的规则信息
```vue
<!-- 在审核详情中添加规则信息显示 -->
<div class="form-group">
  <label>学生选择的规则：</label>
  <div v-if="application.rule" class="rule-info">
    <p>{{ application.rule.name }}</p>
    <p class="rule-details">基础分数: {{ application.rule.score }}分，最大分数: {{ application.rule.max_score }}分</p>
  </div>
  <div v-else class="no-rule">
    <p>未选择规则</p>
  </div>
</div>

<div class="form-group">
  <label>自动计算分数：</label>
  <div class="calculated-score">
    {{ application.final_score || 0 }}分
  </div>
</div>
```

### 5. 系统集成与测试

#### 5.1 数据迁移
```bash
# 执行数据库迁移
export FLASK_APP=app.py
export FLASK_ENV=development
flask db migrate -m "Add rule_id to application"
flask db upgrade
```

#### 5.2 前端API更新
```javascript
// 在 api.js 中添加规则匹配API
export default {
  // 现有API...
  matchRules: (data) => apiRequest('/rules/match', 'POST', data),
  // 现有API...
}
```

### 6. 功能流程

#### 学生端流程
1. 学生填写申请基本信息（申请类型、学术类型、奖项级别、奖项等级等）
2. 系统根据填写的信息动态加载匹配的规则列表
3. 学生从规则列表中选择适用的规则
4. 系统根据选择的规则和作者排序信息，自动计算并显示预估分数
5. 学生确认信息后提交申请

#### 审核端流程
1. 老师/管理员查看待审核申请列表
2. 点击查看申请详情，系统显示学生选择的规则和自动计算的分数
3. 老师/管理员可以验证规则选择是否正确，如有必要可以手动调整分数
4. 审核完成后，系统保存最终分数和审核结果

### 7. 安全与权限控制

1. **规则可见性**：确保学生只能看到与自己申请匹配的规则
2. **数据一致性**：在后端验证学生选择的规则是否与申请信息匹配
3. **审核权限**：确保只有具有审核权限的用户才能修改分数和审核结果
4. **日志记录**：记录规则选择和分数计算的过程，便于审计和排查问题

## 总结

本方案通过在学生端添加规则选择功能，实现了申请过程的透明化和自动化。学生可以清楚地看到自己的申请适用哪些规则以及预估分数，老师/管理员可以根据系统自动计算的分数进行审核，提高了审核效率和公正性。同时，通过数据库设计和API调整，确保了系统的可扩展性和数据一致性。