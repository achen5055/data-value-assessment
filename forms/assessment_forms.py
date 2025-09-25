from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length

class AssessmentForm(FlaskForm):
    """评估创建表单"""
    name = StringField('评估名称', validators=[
        DataRequired(message='请输入评估名称'),
        Length(max=100, message='名称长度不能超过100个字符')
    ])
    description = TextAreaField('评估描述', validators=[
        Length(max=500, message='描述长度不能超过500个字符')
    ])
    rules = SelectMultipleField('应用的数据质量规则', 
                               validators=[DataRequired(message='请至少选择一个规则')],
                               coerce=str)
    submit = SubmitField('开始评估')

class DataQualityRuleForm(FlaskForm):
    """数据质量规则表单"""
    name = StringField('规则名称', validators=[
        DataRequired(message='请输入规则名称'),
        Length(max=100, message='名称长度不能超过100个字符')
    ])
    description = TextAreaField('规则描述', validators=[
        Length(max=500, message='描述长度不能超过500个字符')
    ])
    rule_type = SelectField('规则类型', choices=[
        ('completeness', '完整性'),
        ('consistency', '一致性'),
        ('accuracy', '准确性'),
        ('timeliness', '时效性'),
        ('uniqueness', '唯一性'),
        ('validity', '有效性')
    ], validators=[DataRequired(message='请选择规则类型')])
    column = StringField('列名', validators=[
        DataRequired(message='请输入列名')
    ])
    condition = SelectField('条件', choices=[
        ('not_null', '不为空'),
        ('unique', '唯一值'),
        ('range', '范围内'),
        ('pattern', '匹配模式'),
        ('equals', '等于'),
        ('not_equals', '不等于'),
        ('greater_than', '大于'),
        ('less_than', '小于'),
        ('in_list', '在列表中'),
        ('not_in_list', '不在列表中')
    ], validators=[DataRequired(message='请选择条件')])
    value = StringField('值', validators=[
        DataRequired(message='请输入条件值')
    ])
    submit = SubmitField('保存规则')