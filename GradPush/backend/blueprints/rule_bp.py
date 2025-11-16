# -*- coding: utf-8 -*-
"""
规则管理蓝图

该文件负责处理规则管理相关的API端点，包括：
- 获取所有规则
- 获取单个规则
- 创建规则
- 更新规则
- 删除规则
- 切换规则状态（启用/禁用）
"""

from flask import Blueprint, request, jsonify, abort
from models import Rule
from datetime import datetime
from extensions import db
import traceback
import sys
import os

# 设置默认编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 创建蓝图实例
rule_bp = Blueprint('rule', __name__, url_prefix='/api')

# 获取所有规则
@rule_bp.route('/rules', methods=['GET'])
def get_rules():
    # 获取查询参数
    rule_type = request.args.get('type')
    status = request.args.get('status')
    level = request.args.get('level')
    
    # 构建查询
    query = Rule.query
    
    if rule_type:
        query = query.filter_by(type=rule_type)
    
    if status:
        query = query.filter_by(status=status)
    
    if level:
        query = query.filter_by(level=level)
    
    rules = query.all()
    rule_list = []
    
    for rule in rules:
        rule_data = {
            'id': rule.id,
            'name': rule.name,
            'type': rule.type,
            'sub_type': rule.sub_type,
            'level': rule.level,
            'grade': rule.grade,
            'category': rule.category,
            'participation_type': rule.participation_type,
            'team_role': rule.team_role,
            'author_rank_type': rule.author_rank_type,
            'author_rank': rule.author_rank,
            'author_rank_ratio': rule.author_rank_ratio,
            'research_type': rule.research_type,
            'score': rule.score,
            'max_score': rule.max_score,
            'max_count': rule.max_count,
            'is_special': rule.is_special,
            'status': rule.status,
            'description': rule.description,
            'createdAt': rule.created_at.isoformat() if rule.created_at else None,
            'updatedAt': rule.updated_at.isoformat() if rule.updated_at else None
        }
        rule_list.append(rule_data)
    
    return jsonify({'rules': rule_list}), 200

# 获取单个规则
@rule_bp.route('/rules/<int:rule_id>', methods=['GET'])
def get_rule(rule_id):
    rule = Rule.query.get_or_404(rule_id)
    
    rule_data = {
        'id': rule.id,
        'name': rule.name,
        'type': rule.type,
        'sub_type': rule.sub_type,
        'level': rule.level,
        'grade': rule.grade,
        'category': rule.category,
        'participation_type': rule.participation_type,
        'team_role': rule.team_role,
        'author_rank_type': rule.author_rank_type,
        'author_rank': rule.author_rank,
        'author_rank_ratio': rule.author_rank_ratio,
        'research_type': rule.research_type,
        'score': rule.score,
        'max_score': rule.max_score,
        'max_count': rule.max_count,
        'is_special': rule.is_special,
        'status': rule.status,
        'description': rule.description,
        'createdAt': rule.created_at.isoformat() if rule.created_at else None,
        'updatedAt': rule.updated_at.isoformat() if rule.updated_at else None
    }
    
    return jsonify(rule_data), 200

# 创建规则
@rule_bp.route('/rules', methods=['POST'])
def create_rule():
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'type', 'score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 创建新规则
        new_rule = Rule(
            name=data['name'],
            type=data['type'],
            sub_type=data.get('sub_type'),
            level=data.get('level'),
            grade=data.get('grade'),
            category=data.get('category'),
            participation_type=data.get('participation_type', 'individual'),
            team_role=data.get('team_role'),
            author_rank_type=data.get('author_rank_type', 'unranked'),
            author_rank=data.get('author_rank'),
            author_rank_ratio=data.get('author_rank_ratio'),
            research_type=data.get('research_type'),
            score=data['score'],
            max_score=data.get('max_score'),
            max_count=data.get('max_count'),
            is_special=data.get('is_special', False),
            status=data.get('status', 'active'),
            description=data.get('description')
        )
        
        db.session.add(new_rule)
        db.session.commit()
        
        return jsonify({
            'id': new_rule.id,
            'name': new_rule.name,
            'type': new_rule.type,
            'sub_type': new_rule.sub_type,
            'level': new_rule.level,
            'grade': new_rule.grade,
            'category': new_rule.category,
            'participation_type': new_rule.participation_type,
            'team_role': new_rule.team_role,
            'author_rank_type': new_rule.author_rank_type,
            'author_rank': new_rule.author_rank,
            'author_rank_ratio': new_rule.author_rank_ratio,
            'score': new_rule.score,
            'max_score': new_rule.max_score,
            'max_count': new_rule.max_count,
            'is_special': new_rule.is_special,
            'status': new_rule.status,
            'description': new_rule.description,
            'createdAt': new_rule.created_at.isoformat() if new_rule.created_at else None,
            'updatedAt': new_rule.updated_at.isoformat() if new_rule.updated_at else None
        }), 201
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Failed to create rule'}), 500

# 更新规则
@rule_bp.route('/rules/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    try:
        rule = Rule.query.get_or_404(rule_id)
        data = request.get_json()
        
        # 更新规则字段
        if 'name' in data:
            rule.name = data['name']
        if 'type' in data:
            rule.type = data['type']
        if 'sub_type' in data:
            rule.sub_type = data['sub_type']
        if 'level' in data:
            rule.level = data['level']
        if 'grade' in data:
            rule.grade = data['grade']
        if 'category' in data:
            rule.category = data['category']
        if 'participation_type' in data:
            rule.participation_type = data['participation_type']
        if 'team_role' in data:
            rule.team_role = data['team_role']
        if 'author_rank_type' in data:
            rule.author_rank_type = data['author_rank_type']
        if 'author_rank' in data:
            rule.author_rank = data['author_rank']
        if 'author_rank_ratio' in data:
            rule.author_rank_ratio = data['author_rank_ratio']
        if 'research_type' in data:
            rule.research_type = data['research_type']
        if 'score' in data:
            rule.score = data['score']
        if 'max_score' in data:
            rule.max_score = data['max_score']
        if 'max_count' in data:
            rule.max_count = data['max_count']
        if 'is_special' in data:
            rule.is_special = data['is_special']
        if 'status' in data:
            rule.status = data['status']
        if 'description' in data:
            rule.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'id': rule.id,
            'name': rule.name,
            'type': rule.type,
            'sub_type': rule.sub_type,
            'level': rule.level,
            'grade': rule.grade,
            'category': rule.category,
            'participation_type': rule.participation_type,
            'team_role': rule.team_role,
            'author_rank_type': rule.author_rank_type,
            'author_rank': rule.author_rank,
            'author_rank_ratio': rule.author_rank_ratio,
            'score': rule.score,
            'max_score': rule.max_score,
            'max_count': rule.max_count,
            'is_special': rule.is_special,
            'status': rule.status,
            'description': rule.description,
            'createdAt': rule.created_at.isoformat() if rule.created_at else None,
            'updatedAt': rule.updated_at.isoformat() if rule.updated_at else None
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Failed to update rule'}), 500

# 删除规则
@rule_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    try:
        rule = Rule.query.get_or_404(rule_id)
        
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({'message': 'Rule deleted successfully'}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Failed to delete rule'}), 500

# 切换规则状态
@rule_bp.route('/rules/<int:rule_id>/toggle-status', methods=['PATCH'])
def toggle_rule_status(rule_id):
    try:
        rule = Rule.query.get_or_404(rule_id)
        
        # 切换状态
        new_status = 'active' if rule.status == 'disabled' else 'disabled'
        rule.status = new_status
        
        db.session.commit()
        
        return jsonify({
            'id': rule.id,
            'status': rule.status,
            'message': f'Rule {new_status}d successfully'
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Failed to toggle rule status'}), 500

# 根据申请信息匹配规则
@rule_bp.route('/rules/match', methods=['POST'])
def match_rules():
    """根据申请信息匹配规则"""
    try:
        data = request.get_json()
        
        # 构建查询条件
        query = Rule.query.filter_by(status='active')
        
        # 支持前端传递的参数格式（下划线命名法）
        if data.get('application_type'):
            query = query.filter_by(type=data['application_type'])
        elif data.get('applicationType'):
            query = query.filter_by(type=data['applicationType'])
        
        if data.get('academic_type'):
            query = query.filter_by(sub_type=data['academic_type'])
        elif data.get('academicType'):
            query = query.filter_by(sub_type=data['academicType'])
        
        # 学术专长相关字段匹配
        if data.get('award_level'):
            query = query.filter_by(level=data['award_level'])
        elif data.get('awardLevel'):
            query = query.filter_by(level=data['awardLevel'])
        
        if data.get('award_grade'):
            query = query.filter_by(grade=data['award_grade'])
        elif data.get('awardGrade'):
            query = query.filter_by(grade=data['awardGrade'])
        
        if data.get('award_category'):
            query = query.filter_by(category=data['award_category'])
        elif data.get('awardCategory'):
            query = query.filter_by(category=data['awardCategory'])
        
        # 团队相关字段匹配
        if data.get('award_type') == 'team' or data.get('awardType') == 'team':
            if data.get('team_role'):
                query = query.filter_by(team_role=data['team_role'])
            elif data.get('teamRole'):
                query = query.filter_by(team_role=data['teamRole'])
        
        # 综合表现相关字段匹配
        if data.get('performance_type'):
            query = query.filter_by(sub_type=data['performance_type'])
        
        if data.get('performance_level'):
            query = query.filter_by(level=data['performance_level'])
        
        if data.get('performance_participation'):
            query = query.filter_by(participation_type=data['performance_participation'])
        
        rules = query.all()
        
        # 转换为JSON格式返回
        rule_list = []
        for rule in rules:
            rule_data = {
                'id': rule.id,
                'name': rule.name,
                'type': rule.type,
                'sub_type': rule.sub_type,
                'level': rule.level,
                'grade': rule.grade,
                'category': rule.category,
                'participation_type': rule.participation_type,
                'team_role': rule.team_role,
                'author_rank_type': rule.author_rank_type,
                'author_rank': rule.author_rank,
                'author_rank_ratio': rule.author_rank_ratio,
                'research_type': rule.research_type,
                'score': rule.score,
                'max_score': rule.max_score,
                'max_count': rule.max_count,
                'is_special': rule.is_special,
                'status': rule.status,
                'description': rule.description,
                'createdAt': rule.created_at.isoformat() if rule.created_at else None,
                'updatedAt': rule.updated_at.isoformat() if rule.updated_at else None
            }
            rule_list.append(rule_data)
        
        return jsonify({'rules': rule_list}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Failed to match rules'}), 500