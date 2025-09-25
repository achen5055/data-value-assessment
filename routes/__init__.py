from routes.auth_routes import auth_bp
from routes.main_routes import main_bp
from routes.data_routes import data_bp
from routes.assessment_routes import assessment_bp
from routes.visualization_routes import visualization_bp

# 导出所有蓝图
__all__ = ['auth_bp', 'main_bp', 'data_bp', 'assessment_bp', 'visualization_bp']