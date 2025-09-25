import os
import sys
from flask import Flask, render_template
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

from config import Config
from extensions import db, login_manager, migrate
from models.user import User

def create_app(test_config=None):
    """创建Flask应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)

    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # 配置登录管理器
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import redirect, url_for, flash
        flash('请先登录以访问此页面', 'warning')
        return redirect(url_for('auth.login'))

    # 注册蓝图
    from routes.auth_routes import auth_bp
    from routes.main_routes import main_bp
    from routes.data_routes import data_bp
    from routes.assessment_routes import assessment_bp
    from routes.visualization_routes import visualization_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(data_bp, url_prefix='/data')
    app.register_blueprint(assessment_bp, url_prefix='/assessment')
    app.register_blueprint(visualization_bp, url_prefix='/visualization')

    # 错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)