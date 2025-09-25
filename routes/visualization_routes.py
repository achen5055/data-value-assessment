import json
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models.dataset import Dataset
from models.assessment import Assessment
from utils.visualization_helper import generate_dataset_summary, generate_assessment_charts

# 创建蓝图
visualization_bp = Blueprint('visualization', __name__)

@visualization_bp.route('/visualize/dataset/<int:dataset_id>')
@login_required
def visualize_dataset(dataset_id):
    """可视化数据集"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 确保用户有权限查看此数据集
    if dataset.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': '没有权限访问此数据集'}), 403
    
    # 生成数据集摘要和可视化数据
    summary_data = generate_dataset_summary(dataset)
    
    return render_template(
        'visualization/dataset_visualization.html',
        title=f'数据集可视化: {dataset.name}',
        dataset=dataset,
        summary_data=summary_data
    )

@visualization_bp.route('/visualize/assessment/<int:assessment_id>')
@login_required
def visualize_assessment(assessment_id):
    """可视化评估结果"""
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # 确保用户有权限查看此评估
    if assessment.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': '没有权限访问此评估'}), 403
    
    # 获取关联的数据集
    dataset = Dataset.query.get(assessment.dataset_id)
    
    # 生成评估结果的可视化图表
    chart_data = generate_assessment_charts(assessment)
    
    # 将评估对象转换为字典
    assessment_dict = {
        'id': assessment.id,
        'name': assessment.name,
        'description': assessment.description,
        'completeness_score': assessment.completeness_score or 0,
        'accuracy_score': assessment.accuracy_score or 0,
        'consistency_score': assessment.consistency_score or 0,
        'timeliness_score': assessment.timeliness_score or 0,
        'business_value_score': assessment.business_value_score or 0,
        'overall_score': assessment.overall_value_score,
        'status': assessment.status,
        'status_display': '已完成' if assessment.status == 'completed' else '进行中' if assessment.status == 'processing' else '待处理'
    }
    
    return render_template(
        'visualization/assessment_visualization.html',
        title=f'评估可视化: {assessment.name}',
        assessment=assessment_dict,
        dataset=dataset,
        chart_data=chart_data
    )

@visualization_bp.route('/api/dataset/<int:dataset_id>/summary')
@login_required
def api_dataset_summary(dataset_id):
    """API: 获取数据集摘要数据"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 确保用户有权限查看此数据集
    if dataset.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': '没有权限访问此数据集'}), 403
    
    # 生成数据集摘要
    summary_data = generate_dataset_summary(dataset)
    
    return jsonify(summary_data)

@visualization_bp.route('/api/assessment/<int:assessment_id>/charts')
@login_required
def api_assessment_charts(assessment_id):
    """API: 获取评估结果的图表数据"""
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # 确保用户有权限查看此评估
    if assessment.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': '没有权限访问此评估'}), 403
    
    # 生成评估结果的图表数据
    chart_data = generate_assessment_charts(assessment)
    
    return jsonify(chart_data)

@visualization_bp.route('/dashboard/overview')
@login_required
def dashboard_overview():
    """数据价值仪表盘概览"""
    # 获取用户的所有评估
    assessments = Assessment.query.filter_by(user_id=current_user.id).all()
    
    # 计算平均分数
    avg_scores = {
        'quality': 0,
        'completeness': 0,
        'consistency': 0,
        'accuracy': 0,
        'timeliness': 0,
        'business_value': 0,
        'overall_value': 0
    }
    
    if assessments:
        for assessment in assessments:
            if assessment.quality_score:
                avg_scores['quality'] += assessment.quality_score
            if assessment.completeness_score:
                avg_scores['completeness'] += assessment.completeness_score
            if assessment.consistency_score:
                avg_scores['consistency'] += assessment.consistency_score
            if assessment.accuracy_score:
                avg_scores['accuracy'] += assessment.accuracy_score
            if assessment.timeliness_score:
                avg_scores['timeliness'] += assessment.timeliness_score
            if assessment.business_value_score:
                avg_scores['business_value'] += assessment.business_value_score
            if assessment.overall_value_score:
                avg_scores['overall_value'] += assessment.overall_value_score
        
        # 计算平均值
        count = len(assessments)
        for key in avg_scores:
            avg_scores[key] = round(avg_scores[key] / count, 2) if count > 0 else 0
    
    return render_template(
        'visualization/dashboard.html',
        title='数据价值仪表盘',
        avg_scores=avg_scores,
        assessments=assessments
    )