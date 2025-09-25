import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.dataset import Dataset
from models.assessment import Assessment
from forms.data_forms import DatasetUploadForm, DatasetEditForm
from utils.data_processor import process_dataset_file, get_file_info

# 创建蓝图
data_bp = Blueprint('data', __name__)

@data_bp.route('/datasets')
@login_required
def list_datasets():
    """列出用户的所有数据集"""
    datasets = Dataset.query.filter_by(user_id=current_user.id).order_by(Dataset.created_at.desc()).all()
    return render_template('data/list_datasets.html', title='我的数据集', datasets=datasets)

@data_bp.route('/datasets/upload', methods=['GET', 'POST'])
@login_required
def upload_dataset():
    """上传新数据集"""
    form = DatasetUploadForm()
    
    if form.validate_on_submit():
        # 保存文件
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f'user_{current_user.id}', filename)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存文件
        file.save(file_path)
        
        # 获取文件信息
        file_info = get_file_info(file_path)
        
        # 创建数据集记录
        dataset = Dataset(
            name=form.name.data,
            description=form.description.data,
            file_path=file_path,
            file_type=file_info['file_type'],
            size_bytes=file_info['size_bytes'],
            user_id=current_user.id,
            row_count=file_info.get('row_count'),
            column_count=file_info.get('column_count'),
            schema=file_info.get('schema'),
            status='processed'  # 文件处理完成，设置为已处理状态
        )
        
        db.session.add(dataset)
        db.session.commit()
        
        flash('数据集上传成功！', 'success')
        return redirect(url_for('data.view_dataset', dataset_id=dataset.id))
    
    return render_template('data/upload_dataset.html', title='上传数据集', form=form)

@data_bp.route('/datasets/<int:dataset_id>')
@login_required
def view_dataset(dataset_id):
    """查看数据集详情"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 确保用户有权限查看此数据集
    if dataset.user_id != current_user.id and not current_user.is_admin:
        flash('您没有权限查看此数据集', 'danger')
        return redirect(url_for('data.list_datasets'))
    
    # 获取数据集的预览数据
    preview_result = process_dataset_file(dataset.file_path, preview=True)
    
    # 只传递预览数据，而不是整个结果字典
    preview_data = preview_result.get('data', [])
    
    # 获取与该数据集相关的评估
    assessments = Assessment.query.filter_by(dataset_id=dataset.id).order_by(Assessment.created_at.desc()).all()
    
    # 转换时间为中国时区
    assessments_with_local_time = []
    for assessment in assessments:
        assessments_with_local_time.append({
            'id': assessment.id,
            'name': assessment.name,
            'assessment_type': '数据质量评估',  # 默认类型
            'created_at': assessment.created_at,
            'status': assessment.status,
            'overall_score': assessment.overall_value_score
        })
    
    return render_template(
        'data/detail.html',
        title=f'数据集: {dataset.name}',
        dataset=dataset,
        preview_data=preview_data,
        assessments=assessments_with_local_time
    )

@data_bp.route('/datasets/<int:dataset_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_dataset(dataset_id):
    """编辑数据集信息"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 确保用户有权限编辑此数据集
    if dataset.user_id != current_user.id and not current_user.is_admin:
        flash('您没有权限编辑此数据集', 'danger')
        return redirect(url_for('data.list_datasets'))
    
    form = DatasetEditForm(obj=dataset)
    
    if form.validate_on_submit():
        dataset.name = form.name.data
        dataset.description = form.description.data
        
        db.session.commit()
        
        flash('数据集信息已更新', 'success')
        return redirect(url_for('data.view_dataset', dataset_id=dataset.id))
    
    return render_template('data/edit_dataset.html', title='编辑数据集', form=form, dataset=dataset)

@data_bp.route('/datasets/<int:dataset_id>/delete', methods=['POST'])
@login_required
def delete_dataset(dataset_id):
    """删除数据集"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 确保用户有权限删除此数据集
    if dataset.user_id != current_user.id and not current_user.is_admin:
        flash('您没有权限删除此数据集', 'danger')
        return redirect(url_for('data.list_datasets'))
    
    # 删除文件
    try:
        os.remove(dataset.file_path)
    except OSError:
        # 文件可能已经不存在，忽略错误
        pass
    
    # 删除数据库记录
    db.session.delete(dataset)
    db.session.commit()
    
    flash('数据集已删除', 'success')
    return redirect(url_for('data.list_datasets'))