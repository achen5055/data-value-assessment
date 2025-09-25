from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.dataset import Dataset
from models.assessment import Assessment, DataQualityRule
import pytz
from forms.assessment_forms import AssessmentForm, DataQualityRuleForm
from utils.assessment_engine import run_assessment

# 创建蓝图
assessment_bp = Blueprint('assessment', __name__)

@assessment_bp.route('/assessments')
@login_required
def list_assessments():
    """列出用户的所有评估"""
    assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).all()
    
    # 获取所有相关数据集
    dataset_ids = [a.dataset_id for a in assessments]
    datasets = {d.id: d for d in Dataset.query.filter(Dataset.id.in_(dataset_ids)).all()}
    
    # 转换时间为中国时区
    assessments_with_local_time = []
    for assessment in assessments:
        assessment_dict = {
            'id': assessment.id,
            'name': assessment.name,
            'description': assessment.description,
            'created_at': (assessment.created_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
            'completed_at': (assessment.completed_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M') if assessment.completed_at else None,
            'status': assessment.status,
            'quality_score': assessment.quality_score,
            'overall_score': assessment.overall_value_score,  # 添加overall_score别名
            'overall_value_score': assessment.overall_value_score,
            'dataset': datasets.get(assessment.dataset_id)
        }
        assessments_with_local_time.append(assessment_dict)
    
    return render_template('assessment/list_assessments.html', 
                         title='我的评估', 
                         assessments=assessments_with_local_time)

@assessment_bp.route('/assessments/new/<int:dataset_id>', methods=['GET', 'POST'])
@login_required
def new_assessment(dataset_id):
    """创建新的评估"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 确保用户有权限评估此数据集
    if dataset.user_id != current_user.id and not current_user.is_admin:
        flash('您没有权限评估此数据集', 'danger')
        return redirect(url_for('data.list_datasets'))
    
    form = AssessmentForm()
    
    # 获取用户创建的数据质量规则
    user_rules = DataQualityRule.query.filter_by(user_id=current_user.id).all()
    form.rules.choices = [(str(rule.id), rule.name) for rule in user_rules]
    
    if form.validate_on_submit():
        # 创建新的评估
        assessment = Assessment(
            name=form.name.data,
            description=form.description.data,
            dataset_id=dataset.id,
            user_id=current_user.id
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        # 启动评估任务
        selected_rule_ids = [int(rule_id) for rule_id in form.rules.data]
        selected_rules = DataQualityRule.query.filter(DataQualityRule.id.in_(selected_rule_ids)).all()
        
        # 更新评估状态
        assessment.status = 'processing'
        db.session.commit()
        
        # 运行评估
        try:
            results = run_assessment(dataset, selected_rules)
            assessment.set_results(results)
            db.session.commit()
            flash('评估已完成！', 'success')
        except Exception as e:
            assessment.status = 'failed'
            db.session.commit()
            flash(f'评估失败: {str(e)}', 'danger')
        
        return redirect(url_for('assessment.view_assessment', assessment_id=assessment.id))
    
    return render_template(
        'assessment/new_assessment.html',
        title='创建评估',
        form=form,
        dataset=dataset
    )

@assessment_bp.route('/assessments/<int:assessment_id>')
@login_required
def view_assessment(assessment_id):
    """查看评估详情"""
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # 确保用户有权限查看此评估
    if assessment.user_id != current_user.id and not current_user.is_admin:
        flash('您没有权限查看此评估', 'danger')
        return redirect(url_for('assessment.list_assessments'))
    
    # 获取关联的数据集
    dataset = Dataset.query.get(assessment.dataset_id)
    
    # 获取详细评估结果
    detailed_results = assessment.get_detailed_results()
    
    # 转换时间为中国时区
    # 创建状态显示映射
    status_display_map = {
        'pending': '等待中',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '失败'
    }
    
    # 计算评估耗时
    duration = None
    if assessment.completed_at and assessment.created_at:
        duration = (assessment.completed_at - assessment.created_at).total_seconds()
    
    assessment_with_local_time = {
        'id': assessment.id,
        'name': assessment.name,
        'description': assessment.description,
        'created_at': (assessment.created_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
        'completed_at': (assessment.completed_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M') if assessment.completed_at else None,
        'status': assessment.status,
        'status_display': status_display_map.get(assessment.status, assessment.status),
        'quality_score': assessment.quality_score,
        'overall_score': assessment.overall_value_score,  # 使用overall_value_score作为overall_score
        'overall_value_score': assessment.overall_value_score,
        'duration': duration,
        'assessment_type_display': '数据质量评估',  # 默认类型
        'results': assessment.get_detailed_results().get('results', {}) if assessment.get_detailed_results() else {}
    }
    
    return render_template(
        'assessment/view_assessment.html',
        title=f'评估: {assessment.name}',
        assessment=assessment_with_local_time,
        dataset=dataset,
        detailed_results=detailed_results
    )

@assessment_bp.route('/assessments/<int:assessment_id>/delete', methods=['POST'])
@login_required
def delete_assessment(assessment_id):
    """删除评估"""
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # 确保用户有权限删除此评估
    if assessment.user_id != current_user.id and not current_user.is_admin:
        flash('您没有权限删除此评估', 'danger')
        return redirect(url_for('assessment.list_assessments'))
    
    db.session.delete(assessment)
    db.session.commit()
    
    flash('评估已删除', 'success')
    return redirect(url_for('assessment.list_assessments'))

@assessment_bp.route('/rules')
@login_required
def list_rules():
    """列出用户的所有数据质量规则"""
    rules = DataQualityRule.query.filter_by(user_id=current_user.id).all()
    return render_template('assessment/list_rules.html', title='数据质量规则', rules=rules)

@assessment_bp.route('/rules/new', methods=['GET', 'POST'])
@login_required
def new_rule():
    """创建新的数据质量规则"""
    form = DataQualityRuleForm()
    
    if form.validate_on_submit():
        # 创建规则定义
        rule_definition = {
            'column': form.column.data,
            'condition': form.condition.data,
            'value': form.value.data
        }
        
        # 创建新的规则
        rule = DataQualityRule(
            name=form.name.data,
            description=form.description.data,
            rule_type=form.rule_type.data,
            rule_definition=rule_definition,
            user_id=current_user.id
        )
        
        db.session.add(rule)
        db.session.commit()
        
        flash('数据质量规则已创建', 'success')
        return redirect(url_for('assessment.list_rules'))
    
    return render_template('assessment/new_rule.html', title='创建数据质量规则', form=form)

@assessment_bp.route('/rules/<int:rule_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_rule(rule_id):
    """编辑数据质量规则"""
    rule = DataQualityRule.query.get_or_404(rule_id)
    
    # 确保用户有权限编辑此规则
    if rule.user_id != current_user.id and not current_user.is_admin:
        flash('您没有权限编辑此规则', 'danger')
        return redirect(url_for('assessment.list_rules'))
    
    form = DataQualityRuleForm(obj=rule)
    
    # 填充规则定义
    rule_definition = rule.get_rule_definition()
    if rule_definition:
        form.column.data = rule_definition.get('column')
        form.condition.data = rule_definition.get('condition')
        form.value.data = rule_definition.get('value')
    
    if form.validate_on_submit():
        # 更新规则
        rule.name = form.name.data
        rule.description = form.description.data
        rule.rule_type = form.rule_type.data
        
        # 更新规则定义
        rule_definition = {
            'column': form.column.data,
            'condition': form.condition.data,
            'value': form.value.data
        }
        rule.rule_definition = rule_definition
        
        db.session.commit()
        
        flash('数据质量规则已更新', 'success')
        return redirect(url_for('assessment.list_rules'))
    
    return render_template('assessment/edit_rule.html', title='编辑数据质量规则', form=form, rule=rule)

@assessment_bp.route('/rules/<int:rule_id>/delete', methods=['POST'])
@login_required
def delete_rule(rule_id):
    """删除数据质量规则"""
    rule = DataQualityRule.query.get_or_404(rule_id)
    
    # 确保用户有权限删除此规则
    if rule.user_id != current_user.id and not current_user.is_admin:
        flash('您没有权限删除此规则', 'danger')
        return redirect(url_for('assessment.list_rules'))
    
    db.session.delete(rule)
    db.session.commit()
    
    flash('数据质量规则已删除', 'success')
    return redirect(url_for('assessment.list_rules'))