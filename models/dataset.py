from datetime import datetime
import json
from extensions import db

# 自定义JSON编码器，处理numpy数据类型
class NumpyEncoder(json.JSONEncoder):
    def default(self, o):
        # 检查是否是numpy数值类型
        try:
            import numpy as np
            if isinstance(o, (np.integer, np.int64, np.int32, np.int16, np.int8)):
                return int(o)
            elif isinstance(o, (np.floating, np.float64, np.float32, np.float16)):
                return float(o)
            elif isinstance(o, np.ndarray):
                return o.tolist()
            elif isinstance(o, np.bool_):
                return bool(o)
        except ImportError:
            pass  # 如果没有安装numpy，跳过numpy类型处理
        return super().default(o)

class Dataset(db.Model):
    """数据集模型"""
    __tablename__ = 'datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # csv, json, excel等
    size_bytes = db.Column(db.Integer, nullable=False)
    row_count = db.Column(db.Integer, nullable=True)
    column_count = db.Column(db.Integer, nullable=True)
    schema = db.Column(db.Text, nullable=True)  # 存储为JSON字符串
    status = db.Column(db.String(20), default='processing')  # processing, processed, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 关系
    assessments = db.relationship('Assessment', backref='dataset', lazy='dynamic')
    
    def __init__(self, name, description, file_path, file_type, size_bytes, user_id, 
                 row_count=None, column_count=None, schema=None, status='processing'):
        self.name = name
        self.description = description
        self.file_path = file_path
        self.file_type = file_type
        self.size_bytes = size_bytes
        self.user_id = user_id
        self.row_count = row_count
        self.column_count = column_count
        self.schema = json.dumps(schema, cls=NumpyEncoder) if schema else None
        self.status = status
    
    def get_schema(self):
        """获取数据集的结构信息"""
        if self.schema:
            return json.loads(self.schema)
        return None
    
    def __repr__(self):
        return f'<Dataset {self.name}>'