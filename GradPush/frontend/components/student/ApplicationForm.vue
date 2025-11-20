<template>
  <div class="page-content">
    <div class="page-title">
      <span>加分申请</span>
    </div>

    <div class="card application-card">
      <form @submit.prevent="submitForm" class="application-form">
        <!-- 基本信息（通用） -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'info-circle']" />
            <span>基本信息</span>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">项目全称</label>
              <div class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'signature']" />
                <input type="text" class="form-control" v-model="formData.projectName" placeholder="请输入项目全称"
                  maxlength="100" required>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">获得时间</label>
              <div class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'calendar']" />
                <input type="date" class="form-control" v-model="formData.awardDate" required>
              </div>
            </div>
          </div>
        </div>

        <!-- 规则选择 -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'scroll']" />
            <span>规则选择</span>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">选择适用规则 <span class="required">*</span></label>
              <div class="select-with-button">
                <div class="select-with-icon">
                  <font-awesome-icon :icon="['fas', 'list-check']" />
                  <select class="form-control" v-model="formData.ruleId" required @change="calculateEstimatedScore">
                    <option value="">请选择规则</option>
                    <option v-for="rule in availableRules" :key="rule.id" :value="rule.id">
                      {{ rule.name }} (基础分数: {{ rule.score }})
                    </option>
                  </select>
                </div>
                <button type="button" class="btn btn-outline btn-small" @click="refreshRules">
                  <font-awesome-icon :icon="['fas', 'sync-alt']" />
                  刷新
                </button>
              </div>
              
              <!-- 规则说明显示区域 -->
              <div v-if="formData.ruleId" class="rule-description">
                <label class="form-label">规则说明</label>
                <div class="description-content">
                  {{ availableRules.find(rule => rule.id === formData.ruleId)?.description || '暂无规则说明' }}
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- 申请类型 -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'tag']" />
            <span>申请类型</span>
          </div>
          <div class="radio-cards compact">
            <div class="radio-card horizontal" :class="{ active: formData.applicationType === 'academic' }"
              @click.stop="toggleRadioCard('applicationType', 'academic')">
              <div class="radio-icon">
                <font-awesome-icon :icon="['fas', 'book']" />
              </div>
              <span>学术专长</span>
            </div>
            <div class="radio-card horizontal" :class="{ active: formData.applicationType === 'comprehensive' }"
              @click.stop="toggleRadioCard('applicationType', 'comprehensive')">
              <div class="radio-icon">
                <font-awesome-icon :icon="['fas', 'trophy']" />
              </div>
              <span>综合表现</span>
            </div>
          </div>
        </div>

        <!-- 学术专长特有信息 -->
        <div class="form-section" v-if="formData.applicationType === 'academic'">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'award']" />
            <span>学术奖项信息</span>
          </div>

          <!-- 新增：学术类型选择（放在现有内容最前面） -->
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">学术类型 <span class="required">*</span></label>
              <div class="radio-cards">
              <div class="radio-card horizontal" :class="{ active: formData.academicType === 'research' }"
                  @click.stop="toggleRadioCard('academicType', 'research')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'flask']" />
                  </div>
                  <span>科研成果</span>
                </div>
                <div class="radio-card horizontal" :class="{ active: formData.academicType === 'competition' }"
                  @click.stop="toggleRadioCard('academicType', 'competition')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'trophy']" />
                  </div>
                  <span>学业竞赛</span>
                </div>
                <div class="radio-card horizontal" :class="{ active: formData.academicType === 'innovation' }"
                  @click.stop="toggleRadioCard('academicType', 'innovation')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'lightbulb']" />
                  </div>
                  <span>创新创业训练</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 原有学业竞赛字段需要用v-if包裹 -->
          <div v-if="formData.academicType === 'competition'">
            <!-- 这里放原有的奖项级别、等级等学业竞赛字段 -->
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">奖项级别 <span class="required">*</span></label>
                <div class="radio-cards">
              <div class="radio-card horizontal" :class="{ active: formData.awardLevel === 'national' }" 
                       @click.stop="toggleRadioCard('awardLevel', 'national'); if (formData.awardLevel === 'national') handleLevelChange()">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'globe']" />
                    </div>
                    <span>国家级</span>
                  </div>
                  <div class="radio-card horizontal" :class="{ active: formData.awardLevel === 'provincial' }" 
                       @click.stop="toggleRadioCard('awardLevel', 'provincial'); if (formData.awardLevel === 'provincial') handleLevelChange()">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'map-marker-alt']" />
                    </div>
                    <span>省级</span>
                  </div>
                </div>
              </div>
              <!-- 其他学业竞赛字段... -->
              <div class="form-group">
                <label class="form-label">奖项等级 <span class="required">*</span></label>
                <div class="radio-cards">
                  <!-- 国家级奖项等级 -->
                  <template v-if="formData.awardLevel === 'national'">
                    <div class="radio-card horizontal" :class="{ active: formData.awardGrade === 'firstOrHigher' }" @click.stop="toggleRadioCard('awardGrade', 'firstOrHigher')">
                      <div class="radio-icon">
                        <font-awesome-icon :icon="['fas', 'medal']" />
                      </div>
                      <span>一等奖及以上</span>
                    </div>
                    <div class="radio-card horizontal" :class="{ active: formData.awardGrade === 'second' }" @click.stop="toggleRadioCard('awardGrade', 'second')">
                      <div class="radio-icon">
                        <font-awesome-icon :icon="['fas', 'medal']" />
                      </div>
                      <span>二等奖</span>
                    </div>
                    <div class="radio-card horizontal" :class="{ active: formData.awardGrade === 'third' }" @click.stop="toggleRadioCard('awardGrade', 'third')">
                      <div class="radio-icon">
                        <font-awesome-icon :icon="['fas', 'medal']" />
                      </div>
                      <span>三等奖</span>
                    </div>
                  </template>
                  <!-- 省级奖项等级 -->
                  <template v-if="formData.awardLevel === 'provincial'">
                    <div class="radio-card horizontal" :class="{ active: formData.awardGrade === 'firstOrHigher' }" @click.stop="toggleRadioCard('awardGrade', 'firstOrHigher')">
                      <div class="radio-icon">
                        <font-awesome-icon :icon="['fas', 'medal']" />
                      </div>
                      <span>一等奖及以上</span>
                    </div>
                    <div class="radio-card horizontal" :class="{ active: formData.awardGrade === 'second' }" @click.stop="toggleRadioCard('awardGrade', 'second')">
                      <div class="radio-icon">
                        <font-awesome-icon :icon="['fas', 'medal']" />
                      </div>
                      <span>二等奖</span>
                    </div>
                  </template>
                  <!-- 未选择奖项级别时的提示 -->
                  <div class="radio-card horizontal" v-if="!formData.awardLevel" :class="{ disabled: true }">
                    <span>请先选择奖项级别</span>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">奖项类别 <span class="required">*</span></label>
                <div class="radio-cards">
              <div class="radio-card horizontal" :class="{ active: formData.awardCategory === 'A+类' }" @click.stop="toggleRadioCard('awardCategory', 'A+类')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'star']" />
                    </div>
                    <span>A+类</span>
                  </div>
                  <div class="radio-card horizontal" :class="{ active: formData.awardCategory === 'A类' }" @click.stop="toggleRadioCard('awardCategory', 'A类')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'star']" />
                    </div>
                    <span>A类</span>
                  </div>
                  <div class="radio-card horizontal" :class="{ active: formData.awardCategory === 'A-类' }" @click.stop="toggleRadioCard('awardCategory', 'A-类')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'star']" />
                    </div>
                    <span>A-类</span>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">参与类型</label>
                <div class="radio-cards compact">
              <div class="radio-card horizontal small" :class="{ active: formData.awardType === 'individual' }"
                    @click.stop="toggleRadioCard('awardType', 'individual')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'user']" />
                    </div>
                    <span>个人</span>
                  </div>
                  <div class="radio-card horizontal small" :class="{ active: formData.awardType === 'team' }"
                    @click.stop="toggleRadioCard('awardType', 'team')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'users']" />
                    </div>
                    <span>集体</span>
                  </div>
                </div>
              </div>

              <div class="form-grid" v-if="formData.awardType === 'team'">
                <div class="form-group">
                  <label class="form-label">作者排序类型</label>
                  <div class="radio-cards compact">
              <div class="radio-card horizontal small" :class="{ active: formData.authorRankType === 'ranked' }"
                      @click.stop="toggleRadioCard('authorRankType', 'ranked')">
                      <div class="radio-icon">
                        <font-awesome-icon :icon="['fas', 'list-ol']" />
                      </div>
                      <span>区分排名</span>
                    </div>
                    <div class="radio-card horizontal small" :class="{ active: formData.authorRankType === 'unranked' }"
                      @click.stop="toggleRadioCard('authorRankType', 'unranked')">
                      <div class="radio-icon">
                        <font-awesome-icon :icon="['fas', 'users']" />
                      </div>
                      <span>不区分排名</span>
                    </div>
                  </div>
                </div>
              </div>
              <!-- 修改：仅当选择"有排名"时显示作者排序输入框 -->
              <div class="form-grid" v-if="formData.awardType === 'team' && formData.authorRankType === 'ranked'">
                <div class="form-group">
                  <label class="form-label">作者排序</label>
                  <div class="input-with-icon">
                    <font-awesome-icon :icon="['fas', 'hashtag']" />
                    <input type="number" class="form-control" v-model="formData.authorOrder" min="1"
                      placeholder="请输入作者排序">
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 新增：科研成果特有字段 -->
          <div v-if="formData.academicType === 'research'">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">成果类型 <span class="required">*</span></label>
                <div class="radio-cards">
              <div class="radio-card horizontal" :class="{ active: formData.researchType === 'thesis' }" @click.stop="toggleRadioCard('researchType', 'thesis')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'file-alt']" />
                    </div>
                    <span>学术论文</span>
                  </div>
                  <div class="radio-card horizontal" :class="{ active: formData.researchType === 'patent' }" @click.stop="toggleRadioCard('researchType', 'patent')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'file-invoice']" />
                    </div>
                    <span>发明专利</span>
                  </div>
                </div>
              </div>

              <!-- 其他科研成果字段... -->
            </div>
          </div>


          <!-- 新增：创新创业训练特有字段 -->
          <div v-if="formData.academicType === 'innovation'">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">项目级别 <span class="required">*</span></label>
                <div class="radio-cards">
              <div class="radio-card horizontal" :class="{ active: formData.innovationLevel === 'national' }" @click.stop="toggleRadioCard('innovationLevel', 'national')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'globe']" />
                    </div>
                    <span>国家级</span>
                  </div>
                  <div class="radio-card horizontal" :class="{ active: formData.innovationLevel === 'provincial' }" @click.stop="toggleRadioCard('innovationLevel', 'provincial')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'map-marker-alt']" />
                    </div>
                    <span>省级</span>
                  </div>
                  <div class="radio-card horizontal" :class="{ active: formData.innovationLevel === 'school' }" @click.stop="toggleRadioCard('innovationLevel', 'school')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'university']" />
                    </div>
                    <span>校级</span>
                  </div>
                </div>
              </div>

              <!-- 团队角色选择 -->
              <div class="form-group">
                <label class="form-label">角色 <span class="required">*</span></label>
                <div class="radio-cards compact">
              <div class="radio-card horizontal small" :class="{ active: formData.innovationRole === 'leader' }"
                    @click.stop="toggleRadioCard('innovationRole', 'leader')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'flag']" />
                    </div>
                    <span>组长</span>
                  </div>
                  <div class="radio-card horizontal small" :class="{ active: formData.innovationRole === 'member' }"
                    @click.stop="toggleRadioCard('innovationRole', 'member')">
                    <div class="radio-icon">
                      <font-awesome-icon :icon="['fas', 'user-friends']" />
                    </div>
                    <span>组员</span>
                  </div>
                </div>
              </div>
              <!-- 其他创新创业字段... -->
            </div>
          </div>

        </div>


        <!-- 综合表现特有信息 -->
        <div class="form-section" v-if="formData.applicationType === 'comprehensive'">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'hands-helping']" />
            <span>综合表现信息</span>
          </div>
          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">表现类型 <span class="required">*</span></label>
              <div class="radio-cards">
              <div class="radio-card horizontal" :class="{ active: formData.performanceType === 'international_internship' }" @click.stop="toggleRadioCard('performanceType', 'international_internship')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'globe']" />
                  </div>
                  <span>国际组织实习</span>
                </div>
                <div class="radio-card horizontal" :class="{ active: formData.performanceType === 'military_service' }" @click.stop="toggleRadioCard('performanceType', 'military_service')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'shield-alt']" />
                  </div>
                  <span>参军入伍服兵役</span>
                </div>
                <div class="radio-card horizontal" :class="{ active: formData.performanceType === 'volunteer' }" @click.stop="toggleRadioCard('performanceType', 'volunteer')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'hands-helping']" />
                  </div>
                  <span>志愿服务</span>
                </div>
                <div class="radio-card horizontal" :class="{ active: formData.performanceType === 'social_work' }" @click.stop="toggleRadioCard('performanceType', 'social_work')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'user-tie']" />
                  </div>
                  <span>社会工作</span>
                </div>
                <div class="radio-card horizontal" :class="{ active: formData.performanceType === 'sports' }" @click.stop="toggleRadioCard('performanceType', 'sports')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'football-ball']" />
                  </div>
                  <span>体育比赛</span>
                </div>
                <div class="radio-card horizontal" :class="{ active: formData.performanceType === 'honor_title' }" @click.stop="toggleRadioCard('performanceType', 'honor_title')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'medal']" />
                  </div>
                  <span>荣誉称号</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">奖项级别 <span class="required">*</span></label>
              <div class="radio-cards">
              <div class="radio-card horizontal" :class="{ active: formData.performanceLevel === 'provincial' }" @click.stop="toggleRadioCard('performanceLevel', 'provincial')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'map-marker-alt']" />
                  </div>
                  <span>省级</span>
                </div>
                <div class="radio-card horizontal" :class="{ active: formData.performanceLevel === 'school' }" @click.stop="toggleRadioCard('performanceLevel', 'school')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'university']" />
                  </div>
                  <span>校级</span>
                </div>
                <div class="radio-card horizontal" :class="{ active: formData.performanceLevel === 'college' }" @click.stop="toggleRadioCard('performanceLevel', 'college')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'building']" />
                  </div>
                  <span>院级</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">参与类型 <span class="required">*</span></label>
              <div class="radio-cards compact">
              <div class="radio-card horizontal small" :class="{ active: formData.performanceParticipation === 'individual' }"
                  @click.stop="toggleRadioCard('performanceParticipation', 'individual')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'user']" />
                  </div>
                  <span>个人</span>
                </div>
                <div class="radio-card horizontal small" :class="{ active: formData.performanceParticipation === 'team' }"
                  @click.stop="toggleRadioCard('performanceParticipation', 'team')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'users']" />
                  </div>
                  <span>集体</span>
                </div>
              </div>
            </div>

            <div class="form-group" v-if="formData.performanceParticipation === 'team'">
              <label class="form-label">角色 <span class="required">*</span></label>
              <div class="radio-cards compact">
              <div class="radio-card horizontal small" :class="{ active: formData.teamRole === 'leader' }"
                  @click.stop="toggleRadioCard('teamRole', 'leader')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'flag']" />
                  </div>
                  <span>队长</span>
                </div>
                <div class="radio-card horizontal small" :class="{ active: formData.teamRole === 'member' }"
                  @click.stop="toggleRadioCard('teamRole', 'member')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'user-friends']" />
                  </div>
                  <span>队员</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        

        <!-- 加分详情（通用） -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'star']" />
            <span>加分详情</span>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">自评加分</label>
              <div class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'calculator']" />
                <input type="number" class="form-control" v-model="formData.selfScore" step="0.1" min="0"
                  placeholder="请输入自评加分" required>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">预估分数</label>
              <div class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'chart-line']" />
                <input type="number" class="form-control" v-model="estimatedScore" step="0.1" min="0" readonly>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">加分依据说明</label>
            <textarea class="form-control" v-model="formData.description" rows="3" maxlength="300"
              placeholder="请详细说明加分依据..." required></textarea>
            <div class="char-counter">{{ formData.description.length }}/300</div>
          </div>
        </div>

        <!-- 证明材料（通用） -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'paperclip']" />
            <span>证明材料</span>
          </div>
          <div class="file-upload-area" @click="triggerFileInput" @drop="handleDrop" @dragover.prevent
            @dragenter.prevent>
            <div class="upload-icon">
              <font-awesome-icon :icon="['fas', 'cloud-upload-alt']" />
            </div>
            <div class="upload-text">
              <p>点击或拖拽文件到此处上传</p>
              <p class="help-text">支持 {{ systemSettings.allowedFileTypes.join(', ') }} 格式，单个文件不超过{{ systemSettings.singleFileSizeLimit }}MB，总文件大小不超过{{ systemSettings.totalFileSizeLimit }}MB</p>
            </div>
          </div>
          <input type="file" ref="fileInput" style="display: none;" accept=".pdf,.jpg,.jpeg,.png"
            @change="handleFileSelect" multiple>

          <div class="file-list" v-if="formData.files.length > 0">
            <div class="file-list-header">
              <span>已上传文件 ({{ formData.files.length }})</span>
            </div>
            <div v-for="(file, index) in formData.files" :key="file.name + index" class="file-item">
              <div class="file-icon">
                <font-awesome-icon :icon="getFileIcon(file.name)" />
              </div>
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">{{ formatFileSize(file.size) }}</div>
              </div>
              <div class="file-actions">
                <button type="button" class="file-action-btn" @click.stop="previewFile(file)" title="预览">
                  <font-awesome-icon :icon="['fas', 'eye']" />
                </button>
                <button type="button" class="file-action-btn" @click.stop="removeFile(index)" title="删除">
                  <font-awesome-icon :icon="['fas', 'times']" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <button type="button" class="btn btn-outline" @click="saveDraft">
            <font-awesome-icon :icon="['fas', 'save']" />
            保存草稿
          </button>
          <button type="submit" class="btn btn-primary">
            <font-awesome-icon :icon="['fas', 'paper-plane']" />
            提交审核
          </button>
        </div>
      </form>
    </div>

    <!-- 文件预览模态框 -->
    <div v-if="previewFileData" class="modal-overlay" @click="closePreview">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>
            <font-awesome-icon :icon="getFileIcon(previewFileData.name)" />
            文件预览
          </h3>
          <button class="close-btn" @click="closePreview">
            <font-awesome-icon :icon="['fas', 'times']" />
          </button>
        </div>
        <div class="modal-body">
          <div v-if="isImageFile(previewFileData.name)" class="image-preview">
            <img :src="previewFileData.url" :alt="previewFileData.name" />
          </div>
          <div v-else class="file-preview">
            <div class="file-preview-icon">
              <font-awesome-icon :icon="getFileIcon(previewFileData.name)" size="4x" />
            </div>
            <h4>{{ previewFileData.name }}</h4>
            <p class="help-text">该文件类型不支持在线预览，请下载后查看</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useApplicationsStore } from '../../stores/applications'

// 定义事件，用于通知父组件切换页面
const emit = defineEmits(['switch-page'])

// 接收编辑申请ID
const props = defineProps(['editApplicationId'])

const authStore = useAuthStore()
const applicationsStore = useApplicationsStore()
const fileInput = ref(null)
const previewFileData = ref(null)

// 表单数据
const formData = reactive({
  // 添加用户信息
  id: null, // 用于存储申请ID，编辑时使用
  studentId: authStore.user?.studentId || '',
  name: authStore.userName,
  departmentId: authStore.user?.departmentId || '',
  majorId: authStore.user?.majorId || '',
  
  // 原有表单数据
  applicationType: 'academic',
  projectName: '',
  awardDate: '',
  // 新增：学术类型（科研/竞赛/创新）
  academicType: '',
  // 科研成果特有字段
  researchType: '',       // 成果类型
  // 创新特有字段
  innovationLevel: '',    // 项目级别
  innovationRole: '', // 存储组长(leader)/组员(member)
  // 学术专长特有字段
  awardLevel: '',
  awardGrade: '', // 新增：奖项等级
  awardCategory: '', // 新增：奖项类别（A+/A/A-）
  awardType: 'individual',
  authorRankType: 'ranked', // 新增：排序类型（默认有排名）
  authorOrder: '',
  // 综合表现特有字段
  performanceType: '',
  performanceLevel: '', // 奖项级别
  performanceParticipation: 'individual', // 参与类型（个人/集体）
  teamRole: '', // 团队角色（队长/队员）
  // 规则选择字段
  ruleId: '', // 选择的规则ID
  // 通用字段
  selfScore: '',
  description: '',
  files: []
})


// 级别变更时重置等级
const handleLevelChange = () => {
  formData.awardGrade = ''
}

// 处理radio-card的点击事件，支持取消选择
const toggleRadioCard = (fieldName, value) => {
  if (formData[fieldName] === value) {
    formData[fieldName] = ''
  } else {
    formData[fieldName] = value
  }
}

// 规则选择和预估分数计算相关
import api from '../../utils/api'

const availableRules = ref([])
const estimatedScore = ref(0)

// 系统设置
const systemSettings = ref({
  singleFileSizeLimit: 10, // 默认10MB
  totalFileSizeLimit: 50, // 默认50MB
  allowedFileTypes: ['.pdf', '.jpg', '.jpeg', '.png']
})

// 加载编辑数据
const loadEditData = async (applicationId) => {
  // 如果没有ID或ID为空，重置为新表单
  if (!applicationId) {
    // 清空表单
    Object.assign(formData, {
      id: null,
      studentId: authStore.user?.studentId || '',
      name: authStore.userName,
      departmentId: authStore.user?.departmentId || '',
      majorId: authStore.user?.majorId || '',
      applicationType: 'academic',
      projectName: '',
      awardDate: '',
      academicType: '',
      researchType: '',
      innovationLevel: '',
      innovationRole: '',
      awardLevel: '',
      awardGrade: '',
      awardCategory: '',
      awardType: 'individual',
      authorRankType: 'ranked',
      authorOrder: '',
      performanceType: '',
      performanceLevel: '',
      performanceParticipation: 'individual',
      teamRole: '',
      ruleId: '',
      selfScore: '',
      description: '',
      files: []
    })
    return
  }
  
  try {
    const application = await applicationsStore.fetchApplicationById(applicationId)
    
    // 将后端返回的下划线命名转换为前端的驼峰命名
    const fieldMapping = {
      'student_id': 'studentId',
      'student_name': 'name',
      'department_id': 'departmentId',
      'major_id': 'majorId',
      'application_type': 'applicationType',
      'self_score': 'selfScore',
      'project_name': 'projectName',
      'award_date': 'awardDate',
      'award_level': 'awardLevel',
      'award_type': 'awardType',
      'academic_type': 'academicType',
      'research_type': 'researchType',
      'innovation_level': 'innovationLevel',
      'innovation_role': 'innovationRole',
      'award_grade': 'awardGrade',
      'award_category': 'awardCategory',
      'author_rank_type': 'authorRankType',
      'author_order': 'authorOrder',
      'performance_type': 'performanceType',
      'performance_level': 'performanceLevel',
      'performance_participation': 'performanceParticipation',
      'team_role': 'teamRole',
      'rule_id': 'ruleId'
    }
    
    // 清空表单
    Object.assign(formData, {
      id: null,
      studentId: authStore.user?.studentId || '',
      name: authStore.userName,
      departmentId: authStore.user?.departmentId || '',
      majorId: authStore.user?.majorId || '',
      applicationType: 'academic',
      projectName: '',
      awardDate: '',
      academicType: '',
      researchType: '',
      innovationLevel: '',
      innovationRole: '',
      awardLevel: '',
      awardGrade: '',
      awardCategory: '',
      awardType: 'individual',
      authorRankType: 'ranked',
      authorOrder: '',
      performanceType: '',
      performanceLevel: '',
      performanceParticipation: 'individual',
      teamRole: '',
      ruleId: '',
      selfScore: '',
      description: '',
      files: []
    })
    
    // 填充表单数据
    for (const [key, value] of Object.entries(application)) {
      const newKey = fieldMapping[key] || key
      if (newKey in formData) {
        formData[newKey] = value
      }
    }
    
    // 处理文件（如果有）
    if (application.files && Array.isArray(application.files)) {
      // 将后端返回的文件数据转换为前端可用的格式
      formData.files = application.files.map(file => {
        // 后端返回的文件通常包含id、name、path等字段
        // 直接使用这些字段创建一个文件对象表示
        return {
          id: file.id,
          name: file.name,
          path: file.path,
          size: file.size || 0,
          // 标记这是后端返回的文件，不是浏览器File对象
          isBackendFile: true
        }
      })
    } else {
      formData.files = []
    }
    
  } catch (error) {
    console.error('加载编辑数据失败:', error)
    // 当加载失败（如404），重置为新表单
    Object.assign(formData, {
      id: null,
      studentId: authStore.user?.studentId || '',
      name: authStore.userName,
      departmentId: authStore.user?.departmentId || '',
      majorId: authStore.user?.majorId || '',
      applicationType: 'academic',
      projectName: '',
      awardDate: '',
      academicType: '',
      researchType: '',
      innovationLevel: '',
      innovationRole: '',
      awardLevel: '',
      awardGrade: '',
      awardCategory: '',
      awardType: 'individual',
      authorRankType: 'ranked',
      authorOrder: '',
      performanceType: '',
      performanceLevel: '',
      performanceParticipation: 'individual',
      teamRole: '',
      ruleId: '',
      selfScore: '',
      description: '',
      files: []
    })
  }
}

// 监听编辑申请ID变化
watch(() => props.editApplicationId, (newId) => {
  if (newId) {
    loadEditData(newId)
  }
}, { immediate: true })

// 监听表单关键字段变化，自动匹配规则
watch([
  () => formData.applicationType,
  () => formData.academicType,
  () => formData.awardLevel,
  () => formData.awardGrade,
  () => formData.awardCategory,
  () => formData.awardType,
  () => formData.teamRole,
  () => formData.performanceType,
  () => formData.performanceLevel,
  () => formData.performanceParticipation,
  () => formData.projectName
], () => {
  fetchMatchingRules()
}, { deep: true })

// 获取匹配的规则
const fetchMatchingRules = async () => {
  try {
    // 始终获取所有规则，不进行类型过滤
    const response = await api.getRules()
    // 过滤掉禁用的规则，只显示状态为'active'的规则
    availableRules.value = response.rules.filter(rule => rule.status === 'active')
    
    // 如果当前选择的规则不在列表中，清除选择
    if (formData.ruleId && !availableRules.value.some(rule => rule.id === formData.ruleId)) {
      formData.ruleId = ''
    }
    
    // 如果只有一个规则，自动选择
    if (availableRules.value.length === 1 && !formData.ruleId) {
      formData.ruleId = availableRules.value[0].id
    }
    
    // 重新计算预估分数
    calculateEstimatedScore()
  } catch (error) {
    console.error('获取规则失败:', error)
  }
}

// 计算预估分数
const calculateEstimatedScore = () => {
  if (!formData.ruleId) {
    estimatedScore.value = 0
    return
  }
  
  const selectedRule = availableRules.value.find(rule => rule.id === formData.ruleId)
  if (!selectedRule) {
    estimatedScore.value = 0
    return
  }
  
  let score = selectedRule.score
  
  // 根据作者排序调整分数
  if (formData.awardType === 'team' && formData.authorRankType === 'ranked' && formData.authorOrder) {
    const order = parseInt(formData.authorOrder)
    if (order === 1) {
      // 第一作者使用规则中定义的比例
      score = score * (selectedRule.author_rank_ratio || 1)
    } else {
      // 非第一作者分数递减，最低不低于30%
      const reductionFactor = Math.max(0.3, 1 - (order - 1) * 0.1)
      score = score * reductionFactor
    }
  }
  
  // 应用最大分数限制
  if (selectedRule.max_score && score > selectedRule.max_score) {
    score = selectedRule.max_score
  }
  
  estimatedScore.value = parseFloat(score.toFixed(1))
}

// 监听规则选择变化，自动填充表单信息
watch(() => formData.ruleId, async (newRuleId) => {
  if (!newRuleId) return
  
  // 先尝试从availableRules中查找规则
  let selectedRule = availableRules.value.find(rule => rule.id === newRuleId)
  
  // 如果在availableRules中找不到，尝试单独获取该规则的详细信息
  if (!selectedRule) {
    try {
      selectedRule = await api.getRule(newRuleId)
    } catch (error) {
      console.error('获取规则详情失败:', error)
      return
    }
  }
  
  if (!selectedRule) return
  
  // 根据选择的规则自动填充表单信息
  formData.applicationType = selectedRule.type
  
  if (selectedRule.type === 'academic') {
    formData.academicType = selectedRule.sub_type
    
    // 根据不同学术子类型设置相应字段
    if (selectedRule.sub_type === 'research' || selectedRule.sub_type === 'competition') {
      formData.awardLevel = selectedRule.level
      formData.awardGrade = selectedRule.grade
      formData.awardCategory = selectedRule.category
    } else if (selectedRule.sub_type === 'innovation') {
      formData.innovationLevel = selectedRule.level
    }
    
    // 根据规则设置参与类型（团队或个人）
    formData.awardType = selectedRule.participation_type
    
    // 设置团队角色
    if (selectedRule.participation_type === 'team') {
      if (selectedRule.sub_type === 'innovation') {
        formData.innovationRole = selectedRule.team_role
      } else {
        formData.teamRole = selectedRule.team_role
      }
    }
    
    // 设置科研成果类型
    if (selectedRule.sub_type === 'research') {
      // 将'research_type'映射为UI中使用的'papers'值
      if (selectedRule.research_type === 'paper') {
        formData.researchType = 'thesis' // 学术论文对应到'thesis'选项
      } else {
        formData.researchType = selectedRule.research_type
      }
    }
    
    // 设置作者排序相关
    formData.authorRankType = selectedRule.author_rank_type
    if (selectedRule.author_rank) {
      formData.authorOrder = selectedRule.author_rank
    }
  } else if (selectedRule.type === 'comprehensive') {
    formData.performanceType = selectedRule.sub_type
    formData.performanceLevel = selectedRule.level
    formData.performanceParticipation = selectedRule.participation_type
    if (selectedRule.participation_type === 'team') {
      formData.teamRole = selectedRule.team_role
    }
  }
  
  // 重新计算预估分数
  calculateEstimatedScore()
}, { immediate: true })

// 刷新规则列表
const refreshRules = () => {
  fetchMatchingRules()
}

// 在组件挂载时自动刷新规则选择栏并加载系统设置
onMounted(() => {
  refreshRules()
  loadSystemSettings()
})

// 加载系统设置
const loadSystemSettings = async () => {
  try {
    const settings = await api.getSystemSettings()
    systemSettings.value = {
      singleFileSizeLimit: settings.singleFileSizeLimit || 10,
      totalFileSizeLimit: settings.totalFileSizeLimit || 50,
      allowedFileTypes: settings.allowedFileTypes || ['.pdf', '.jpg', '.jpeg', '.png']
    }
  } catch (error) {
    console.error('获取系统设置失败:', error)
  }
}

// 原有方法保持不变...
const getFileIcon = (fileName) => {
  if (!fileName) {
    return ['fas', 'file-question']
  }
  const ext = fileName.split('.').pop().toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) {
    return ['fas', 'file-image']
  } else if (ext === 'pdf') {
    return ['fas', 'file-pdf']
  } else {
    return ['fas', 'file']
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const isImageFile = (fileName) => {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
  const ext = fileName.split('.').pop().toLowerCase()
  return imageExtensions.includes(ext)
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  
  // 检查总文件大小
  const currentTotalSize = formData.files.reduce((total, file) => total + file.size, 0)
  let totalSizeWithNewFiles = currentTotalSize
  
  for (const file of files) {
    totalSizeWithNewFiles += file.size
  }
  
  if (totalSizeWithNewFiles > systemSettings.value.totalFileSizeLimit * 1024 * 1024) {
    alert(`总文件大小超过${systemSettings.value.totalFileSizeLimit}MB限制`)
    event.target.value = ''
    return
  }
  
  // 检查单个文件大小和类型
  files.forEach(file => {
    if (file.size > systemSettings.value.singleFileSizeLimit * 1024 * 1024) {
      alert(`文件 ${file.name} 大小超过${systemSettings.value.singleFileSizeLimit}MB限制`)
      return
    }
    
    const fileExt = `.${file.name.split('.').pop().toLowerCase()}`
    if (!systemSettings.value.allowedFileTypes.includes(fileExt)) {
      alert(`文件 ${file.name} 类型不支持，仅支持${systemSettings.value.allowedFileTypes.join(', ')}格式`)
      return
    }
    
    // 使用展开运算符创建新数组，确保响应式更新
    formData.files = [...formData.files, file]
  })
  event.target.value = ''
}

const handleDrop = (event) => {
  event.preventDefault()
  const files = Array.from(event.dataTransfer.files)
  
  // 检查总文件大小
  const currentTotalSize = formData.files.reduce((total, file) => total + file.size, 0)
  let totalSizeWithNewFiles = currentTotalSize
  
  for (const file of files) {
    totalSizeWithNewFiles += file.size
  }
  
  if (totalSizeWithNewFiles > systemSettings.value.totalFileSizeLimit * 1024 * 1024) {
    alert(`总文件大小超过${systemSettings.value.totalFileSizeLimit}MB限制`)
    return
  }
  
  // 检查单个文件大小和类型
  files.forEach(file => {
    if (file.size > systemSettings.value.singleFileSizeLimit * 1024 * 1024) {
      alert(`文件 ${file.name} 大小超过${systemSettings.value.singleFileSizeLimit}MB限制`)
      return
    }
    
    const fileExt = `.${file.name.split('.').pop().toLowerCase()}`
    if (!systemSettings.value.allowedFileTypes.includes(fileExt)) {
      alert(`文件 ${file.name} 类型不支持，仅支持${systemSettings.value.allowedFileTypes.join(', ')}格式`)
      return
    }
    
    // 使用展开运算符创建新数组，确保响应式更新
    formData.files = [...formData.files, file]
  })
}

const removeFile = (index) => {
  // 使用展开运算符创建新数组，确保响应式更新
  formData.files = formData.files.filter((_, i) => i !== index)
}

const previewFile = (file) => {
  // 检查是否是浏览器File对象（用于新上传的文件）
  if (file instanceof File) {
    if (isImageFile(file.name)) {
      const url = URL.createObjectURL(file)
      previewFileData.value = {
        name: file.name,
        url: url,
        file: file,
        size: file.size
      }
    } else {
      previewFileData.value = {
        name: file.name,
        file: file,
        size: file.size
      }
    }
  } else {
    // 从后端获取的文件对象，通常包含id、name、path等字段
    // 对于后端图片文件，构建正确的预览URL
    let url = null
    if (isImageFile(file.name)) {
      if (file.path) {
        // 检查path是否已经是完整URL
        if (file.path.startsWith('http://') || file.path.startsWith('https://')) {
          url = file.path
        } else {
          // 添加服务器地址前缀
          url = `http://localhost:5001${file.path}`
        }
      } else if (file.id) {
        // 如果没有path字段，使用文件ID构建URL
        url = `http://localhost:5001/uploads/files/${file.id}`
      }
    }
    previewFileData.value = {
      name: file.name,
      url: url,
      file: file,
      size: file.size || 0
    }
  }
}

const closePreview = () => {
  if (previewFileData.value && previewFileData.value.url) {
    URL.revokeObjectURL(previewFileData.value.url)
  }
  previewFileData.value = null
}

const downloadFile = (fileData) => {
  const file = fileData.file
  
  // 检查是否是浏览器File对象（用于新上传的文件）
  if (file instanceof File) {
    const url = URL.createObjectURL(file)
    const a = document.createElement('a')
    a.href = url
    a.download = fileData.name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } else {
    // 从后端获取的文件对象，构建正确的下载URL
    let downloadUrl = null
    
    if (file.path) {
      // 检查path是否已经是完整URL
      if (file.path.startsWith('http://') || file.path.startsWith('https://')) {
        downloadUrl = file.path
      } else {
        // 添加服务器地址前缀
        downloadUrl = `http://localhost:5001${file.path}`
      }
    } else if (file.id) {
      // 如果没有path字段，使用文件ID构建URL
      downloadUrl = `http://localhost:5001/uploads/files/${file.id}`
    }
    
    // 创建一个隐藏的<a>标签来触发下载
    if (downloadUrl) {
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = fileData.name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
  }
}

// 修改保存草稿和提交表单的验证逻辑
const saveDraft = async () => {
  try {
    // 从authStore获取实际的学生信息
    const studentName = authStore.user?.name || authStore.userName || '未知学生'
    const studentId = authStore.user?.studentId || '未知学号'
    
    // 准备草稿数据
    const draftData = {
      ...formData,
      // 确保使用正确的字段名，与显示组件保持一致
      studentName,
      studentId,
      departmentId: authStore.user?.departmentId || '',
      majorId: authStore.user?.majorId || '',
      status: 'draft',
      appliedAt: new Date().toISOString()
    }
    
    let success
    if (formData.id) {
      // 更新现有申请
      success = await applicationsStore.updateApplication(formData.id, draftData)
    } else {
      // 创建新申请
      success = await applicationsStore.addApplication(draftData)
    }
    
    if (success) {
      alert('草稿已保存')
      // 保存成功后继续留在当前页面
    } else {
      alert('保存草稿失败，请稍后重试')
    }
  } catch (error) {
    console.error('保存草稿失败:', error)
    alert('保存草稿失败，请稍后重试')
  }
}

const submitForm = async () => {
    // 通用验证
    if (!formData.projectName) {
      alert('请输入项目全称')
      return
    }

    if (!formData.awardDate) {
      alert('请输入获得时间')
      return
    }

    if (!formData.description) {
      alert('请输入项目描述')
      return
    }

    // 学术专长特有验证增强
    if (formData.applicationType === 'academic') {
      // 新增：验证学术类型已选择
      if (!formData.academicType) {
        alert('请选择学术类型（科研成果/学业竞赛/创新创业训练）')
        return
      }

      // 学业竞赛特有验证
      if (formData.academicType === 'competition') {
        if (!formData.awardLevel) {
          alert('请选择奖项级别')
          return
        }
        if (!formData.awardGrade) { // 新增：验证奖项等级
          alert('请选择奖项等级')
          return
        }
        if (!formData.awardCategory) {
          alert('请选择奖项类别')
          return
        }
        // 新增：团队奖项的排序验证
        if (formData.awardType === 'team') {
          // 当选择"有排名"时必须填写作者排序
          if (formData.authorRankType === 'ranked' && !formData.authorOrder) {
            alert('请输入作者排序')
            return
          }
        }
      }

      // 新增：科研成果验证
      if (formData.academicType === 'research') {
        if (!formData.researchType) {
          alert('请选择成果类型')
          return
        }
      }

      // 新增：创新创业验证
      if (formData.academicType === 'innovation') {
        if (!formData.innovationLevel) {
          alert('请选择项目级别')
          return
        }

        if (!formData.innovationRole) {
          alert('请选择您的角色（组长/组员）')
          return
        }
      }
    }

    // 综合表现特有验证
    if (formData.applicationType === 'comprehensive') {
      if (!formData.performanceType) {
        alert('请选择表现类型')
        return
      }
      if (!formData.performanceLevel) {
        alert('请选择奖项级别')
        return
      }
    }

    // 通用字段验证
    if (!formData.selfScore) {
      alert('请输入自评加分')
      return
    }

    if (formData.files.length === 0) {
      alert('请上传证明文件')
      return
    }

    // 从authStore获取实际的学生信息
    const studentName = authStore.user?.name || authStore.userName || '未知学生'
    const studentId = authStore.user?.studentId || '未知学号'
    
    console.log('=== 提交申请时的学生信息 ===')
    console.log('studentName:', studentName)
    console.log('studentId:', studentId)

    // 确保studentName字段存在（兼容后端期望）
    formData.studentName = formData.name || authStore.userName

    // 准备申请数据
    const applicationData = {
      ...formData,
      // 确保使用正确的字段名，与显示组件保持一致
      studentName,
      studentId,
      facultyId: authStore.user?.facultyId || '',
      departmentId: authStore.user?.departmentId || '',
      majorId: authStore.user?.majorId || '',
      status: 'pending',
      appliedAt: new Date().toISOString()
    }
  
    console.log('=== 最终发送的申请数据 ===')

    try {
      let success
      if (formData.id) {
        // 更新现有申请
        success = await applicationsStore.updateApplication(formData.id, applicationData)
      } else {
        // 创建新申请
        success = await applicationsStore.addApplication(applicationData)
      }

      if (success) {
        alert('申请已提交，等待审核中...')

        // 重置表单，但保持默认的加分申请类型
        Object.assign(formData, {
          id: null,
          studentId: authStore.user?.studentId || '',
          name: authStore.userName,
          departmentId: authStore.user?.departmentId || '',
          majorId: authStore.user?.majorId || '',
          applicationType: 'academic', // 默认选择学术专长
          projectName: '',
          awardDate: '',
          academicType: 'competition', // 默认选择学业竞赛
          researchType: '',
          innovationLevel: '',
          innovationRole: '',
          awardLevel: '',
          awardGrade: '',
          awardCategory: '',
          awardType: 'individual',
          authorRankType: 'ranked',
          authorOrder: '',
          performanceType: '',
          performanceLevel: '',
          performanceParticipation: 'individual',
          teamRole: '',
          ruleId: '',
          selfScore: '',
          description: '',
          files: []
        })
        
        // 重置规则列表和预估分数
        availableRules.value = []
        estimatedScore.value = 0
        
        // 不再自动切换到申请历史页面，保持在加分申请页面
      } else {
        alert('提交失败，请稍后重试')
      }
    } catch (error) {
      console.error('提交申请失败:', error)
      alert('提交失败，请稍后重试')
    }
}
</script>

<style scoped>
/* 引入共享样式 */
@import '../common/shared-styles.css';

/* 必填项红色星号 */
.required {
  color: #ff4d4f;
}

/* 应用表单特有样式 */
.application-form {
  padding: 0;
}

/* 表单部分样式 */
.form-section {
  padding: 10px 15px;
  border-bottom: 1px solid #f0f4f8;
}

.form-section:last-child {
  border-bottom: none;
}

/* 表单组微调 */
.form-group {
  margin-bottom: 3px;
}

/* 表单标签微调 */
.form-label {
  margin-bottom: 6px;
  font-size: 0.95rem;
}

/* 激活状态的单选卡片样式 */

/* 激活状态的单选卡片样式 */
.radio-card.active {
  border-color: #003366;
  background-color: #f0f7ff;
  color: #003366;
}

/* 激活状态的单选卡片图标样式 */
.radio-card.active .radio-icon {
  color: #003366;
}

/* 文件上传文本样式 */
.upload-text p {
  margin: 0;
  color: #333;
}

/* 表单操作按钮样式 */
.form-actions {
  padding: 15px 20px;
  background: #ffffff;
  border-top: 1px solid #ffffff;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 模态框特有样式（覆盖共享样式） */
.modal-overlay {
  background-color: rgba(0, 0, 0, 0.7);
}

.modal-content {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  width: 90vw;
  height: 90vh;
  max-width: 1200px;
  max-height: 800px;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f4f8;
}

.modal-header h3 {
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-body {
  flex: 1;
  overflow: auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 图片预览区域 */
.image-preview {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 4px;
}

/* 文件预览区域 */
.file-preview {
  text-align: center;
  padding: 40px 20px;
  width: 100%;
}

.file-preview-icon {
  margin-bottom: 20px;
  color: #666;
}

.file-preview h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1.2rem;
}

/* 规则说明区域样式 */
.rule-description {
  margin-top: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
}

.rule-description .form-label {
  font-weight: 600;
  margin-bottom: 8px;
  display: block;
  color: #495057;
}

.rule-description .description-content {
  font-size: 14px;
  line-height: 1.6;
  color: #6c757d;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
    padding: 12px 15px;
  }

  .btn {
    justify-content: center;
  }

  .modal-content {
    width: 95vw;
    height: 95vh;
    max-width: none;
    max-height: none;
  }

  .modal-header {
    padding: 12px 15px;
  }

  .modal-body {
    padding: 15px;
  }

  .file-preview {
    .rule-description {
      margin-top: 12px;
      padding: 12px;
    }

    .rule-description .description-content {
      font-size: 13px;
    }
    padding: 30px 15px;
  }

  .file-preview h4 {
    font-size: 1.1rem;
  }
}
</style>