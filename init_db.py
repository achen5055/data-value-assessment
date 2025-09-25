#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表和初始数据
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.user import User
from models.dataset import Dataset
from models.assessment import Assessment

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✓ 数据库表创建成功")
        
        # 创建管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_admin=True,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            db.session.add(admin)
            print("✓ 管理员用户创建成功")
        
        # 创建测试用户
        test_user = User.query.filter_by(username='test').first()
        if not test_user:
            test = User(
                username='test',
                email='test@example.com',
                password='test123',
                is_admin=False,
                created_at=datetime.utcnow()
            )
            db.session.add(test)
            print("✓ 测试用户创建成功")
        
        # 创建示例数据集
        if Dataset.query.count() == 0:
            datasets = [
                Dataset(
                    name='销售数据2024',
                    filename='sales_data_2024.csv',
                    file_type='csv',
                    file_size=1024000,
                    row_count=10000,
                    column_count=15,
                    description='2024年销售数据，包含产品、客户、销售额等信息',
                    user_id=1,
                    created_at=datetime.utcnow()
                ),
                Dataset(
                    name='用户行为数据',
                    filename='user_behavior.json',
                    file_type='json',
                    file_size=512000,
                    row_count=5000,
                    column_count=8,
                    description='用户行为分析数据，包含点击、浏览、购买等行为',
                    user_id=1,
                    created_at=datetime.utcnow()
                ),
                Dataset(
                    name='产品质量数据',
                    filename='quality_data.xlsx',
                    file_type='excel',
                    file_size=2048000,
                    row_count=15000,
                    column_count=12,
                    description='产品质量检测数据，包含各项质量指标',
                    user_id=2,
                    created_at=datetime.utcnow()
                )
            ]
            db.session.add_all(datasets)
            print("✓ 示例数据集创建成功")
        
        # 创建示例评估
        if Assessment.query.count() == 0:
            assessments = [
                Assessment(
                    name='销售数据质量评估',
                    description='对2024年销售数据进行全面的质量评估',
                    assessment_type='quality',
                    dataset_id=1,
                    user_id=1,
                    status='completed',
                    overall_score=85.5,
                    results={
                        '完整性': 92.0,
                        '准确性': 88.5,
                        '一致性': 79.0,
                        '时效性': 95.0
                    },
                    created_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration=120
                ),
                Assessment(
                    name='用户行为数据价值评估',
                    description='评估用户行为数据的业务价值',
                    assessment_type='value',
                    dataset_id=2,
                    user_id=1,
                    status='completed',
                    overall_score=78.0,
                    results={
                        '业务价值': 82.0,
                        '经济价值': 75.0,
                        '潜在价值': 70.0
                    },
                    created_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration=180
                )
            ]
            db.session.add_all(assessments)
            print("✓ 示例评估创建成功")
        
        # 提交所有更改
        db.session.commit()
        print("✓ 数据库初始化完成！")

def check_database():
    """检查数据库状态"""
    print("检查数据库状态...")
    
    with app.app_context():
        try:
            # 检查表是否存在
            db.engine.execute('SELECT 1 FROM user LIMIT 1')
            print("✓ 数据库连接正常")
            
            # 统计数据
            user_count = User.query.count()
            dataset_count = Dataset.query.count()
            assessment_count = Assessment.query.count()
            
            print(f"✓ 用户数量: {user_count}")
            print(f"✓ 数据集数量: {dataset_count}")
            print(f"✓ 评估数量: {assessment_count}")
            
            return True
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
            return False

def reset_database():
    """重置数据库（危险操作）"""
    confirm = input("确定要重置数据库吗？所有数据将被删除！(y/N): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return
    
    with app.app_context():
        # 删除所有表
        db.drop_all()
        print("✓ 数据库表已删除")
        
        # 重新创建表
        db.create_all()
        print("✓ 数据库表重新创建")
        
        print("✓ 数据库重置完成")

if __name__ == '__main__':
    print("=" * 50)
    print("数据价值评估系统 - 数据库管理工具")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'init':
            init_database()
        elif command == 'check':
            check_database()
        elif command == 'reset':
            reset_database()
        elif command == 'help':
            print("可用命令:")
            print("  init    - 初始化数据库")
            print("  check   - 检查数据库状态")
            print("  reset   - 重置数据库（危险）")
            print("  help    - 显示帮助信息")
        else:
            print(f"未知命令: {command}")
            print("使用 'help' 查看可用命令")
    else:
        # 交互式模式
        while True:
            print("\n请选择操作:")
            print("1. 初始化数据库")
            print("2. 检查数据库状态")
            print("3. 重置数据库")
            print("4. 退出")
            
            choice = input("请输入选项 (1-4): ").strip()
            
            if choice == '1':
                init_database()
            elif choice == '2':
                check_database()
            elif choice == '3':
                reset_database()
            elif choice == '4':
                print("再见！")
                break
            else:
                print("无效选项，请重新选择")