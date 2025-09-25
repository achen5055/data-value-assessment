from datetime import datetime
import json
from extensions import db

class Assessment(db.Model):
    """数据价值评估模型"""
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    
    # 评估结果
    quality_score = db.Column(db.Float, nullable=True)  # 数据质量得分
    completeness_score = db.Column(db.Float, nullable=True)  # 完整性得分
    consistency_score = db.Column(db.Float, nullable=True)  # 一致性得分
    accuracy_score = db.Column(db.Float, nullable=True)  # 准确性得分
    timeliness_score = db.Column(db.Float, nullable=True)  # 时效性得分
    business_value_score = db.Column(db.Float, nullable=True)  # 业务价值得分
    overall_value_score = db.Column(db.Float, nullable=True)  # 综合价值得分
    
    # 详细评估结果，存储为JSON
    detailed_results = db.Column(db.Text, nullable=True)
    
    # 外键
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, name, description, dataset_id, user_id):
        self.name = name
        self.description = description
        self.dataset_id = dataset_id
        self.user_id = user_id
    
    def set_results(self, results_dict):
        """设置评估结果"""
        # 设置各项得分
        self.quality_score = results_dict.get('quality_score')
        self.completeness_score = results_dict.get('completeness_score')
        self.consistency_score = results_dict.get('consistency_score')
        self.accuracy_score = results_dict.get('accuracy_score')
        self.timeliness_score = results_dict.get('timeliness_score')
        self.business_value_score = results_dict.get('business_value_score')
        self.overall_value_score = results_dict.get('overall_value_score')
        
        # 存储详细结果
        self.detailed_results = json.dumps(results_dict)
        
        # 更新状态
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
    
    def get_detailed_results(self):
        """获取详细评估结果"""
        if self.detailed_results:
            return json.loads(self.detailed_results)
        return None
    
    def __repr__(self):
        return f'<Assessment {self.name} for Dataset {self.dataset_id}>'


class DataQualityRule(db.Model):
    """数据质量规则模型"""
    __tablename__ = 'data_quality_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    rule_type = db.Column(db.String(50), nullable=False)  # 规则类型：completeness, consistency, accuracy, etc.
    rule_definition = db.Column(db.Text, nullable=False)  # 规则定义，存储为JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, name, description, rule_type, rule_definition, user_id):
        self.name = name
        self.description = description
        self.rule_type = rule_type
        self.rule_definition = json.dumps(rule_definition)
        self.user_id = user_id
    
    def get_rule_definition(self):
        """获取规则定义"""
        return json.loads(self.rule_definition)
    
    def __repr__(self):
        return f'<DataQualityRule {self.name}>'