from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class DatasetUploadForm(FlaskForm):
    """数据集上传表单"""
    name = StringField('数据集名称', validators=[
        DataRequired(message='请输入数据集名称'),
        Length(max=100, message='名称长度不能超过100个字符')
    ])
    description = TextAreaField('数据集描述', validators=[
        Length(max=500, message='描述长度不能超过500个字符')
    ])
    file = FileField('数据文件', validators=[
        FileRequired(message='请选择要上传的文件'),
        FileAllowed(['csv', 'xlsx', 'xls', 'json'], '只支持CSV、Excel和JSON格式')
    ])
    submit = SubmitField('上传数据集')

class DatasetEditForm(FlaskForm):
    """数据集编辑表单"""
    name = StringField('数据集名称', validators=[
        DataRequired(message='请输入数据集名称'),
        Length(max=100, message='名称长度不能超过100个字符')
    ])
    description = TextAreaField('数据集描述', validators=[
        Length(max=500, message='描述长度不能超过500个字符')
    ])
    submit = SubmitField('保存修改')