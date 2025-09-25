from flask import Blueprint, render_template, json
from flask_login import login_required, current_user
from models import Dataset, Assessment
from datetime import datetime, timedelta
import pytz

# 创建蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页"""
    return render_template('main/index.html', title='数据价值评估系统')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """用户仪表盘"""
    # 获取用户的数据集和评估
    user_datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    user_assessments = Assessment.query.filter_by(user_id=current_user.id).all()
    
    # 统计信息
    dataset_count = len(user_datasets)
    assessment_count = len(user_assessments)
    
    # 最近的数据集和评估
    recent_datasets = Dataset.query.filter_by(user_id=current_user.id).order_by(Dataset.created_at.desc()).limit(5).all()
    recent_assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).limit(5).all()
    
    # 将Assessment对象转换为可序列化的字典
    serializable_assessments = []
    # 设置中国时区
    china_tz = pytz.timezone('Asia/Shanghai')
    
    for assessment in recent_assessments:
        # 直接添加8小时补偿UTC到中国时区的差异
        created_at_local = assessment.created_at + timedelta(hours=8)
        completed_at_local = (assessment.completed_at + timedelta(hours=8)) if assessment.completed_at else None
        
        # 格式化为本地时间字符串
        print(f"原始数据库时间: {assessment.created_at}")
        print(f"调整后中国时间: {created_at_local.strftime('%Y-%m-%d %H:%M')}")
        
        assessment_dict = {
            'id': assessment.id,
            'name': assessment.name,
            'description': assessment.description,
            'created_at': created_at_local.strftime('%Y-%m-%d %H:%M'),
            'completed_at': completed_at_local.strftime('%Y-%m-%d %H:%M') if completed_at_local else None,
            'status': assessment.status,
            'quality_score': assessment.quality_score,
            'completeness_score': assessment.completeness_score,
            'consistency_score': assessment.consistency_score,
            'accuracy_score': assessment.accuracy_score,
            'timeliness_score': assessment.timeliness_score,
            'business_value_score': assessment.business_value_score,
            'overall_value_score': assessment.overall_value_score,
            'dataset': {
                'id': assessment.dataset_id,
                'name': assessment.dataset.name if hasattr(assessment, 'dataset') else "未知数据集"
            }
        }
        serializable_assessments.append(assessment_dict)
    
    return render_template(
        'main/dashboard.html',
        title='仪表盘',
        dataset_count=dataset_count,
        assessment_count=assessment_count,
        recent_datasets=recent_datasets,
        recent_assessments=recent_assessments,
        serializable_assessments=serializable_assessments
    )

@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('main/about.html', title='关于系统')

@main_bp.route('/help')
def help():
    """帮助页面"""
    return render_template('main/help.html', title='帮助文档')