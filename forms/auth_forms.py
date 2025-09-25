from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    """用户登录表单"""
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    """用户注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=3, max=64, message='用户名长度必须在3到64个字符之间')
    ])
    email = StringField('电子邮箱', validators=[
        DataRequired(message='请输入电子邮箱'),
        Email(message='请输入有效的电子邮箱地址'),
        Length(max=120, message='电子邮箱长度不能超过120个字符')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码'),
        Length(min=8, message='密码长度不能少于8个字符')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    agree_terms = BooleanField('我同意服务条款', validators=[DataRequired(message='请同意服务条款')])
    submit = SubmitField('注册')
    
    def validate_username(self, username):
        """验证用户名是否已存在"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名')
    
    def validate_email(self, email):
        """验证电子邮箱是否已存在"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该电子邮箱已被注册，请使用其他电子邮箱')