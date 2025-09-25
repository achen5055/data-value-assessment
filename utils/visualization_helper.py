import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

def generate_dataset_summary(dataset):
    """
    生成数据集摘要和可视化数据
    
    Args:
        dataset: 数据集模型实例
        
    Returns:
        dict: 包含摘要和可视化数据的字典
    """
    summary = {
        'dataset_id': dataset.id,
        'dataset_name': dataset.name,
        'file_type': dataset.file_type,
        'row_count': dataset.row_count,
        'column_count': dataset.column_count,
        'size_bytes': dataset.size_bytes,
        'size_formatted': format_file_size(dataset.size_bytes),
        'charts': []
    }
    
    try:
        # 读取数据集文件
        file_path = dataset.file_path
        
        if dataset.file_type == 'csv':
            df = pd.read_csv(file_path)
        elif dataset.file_type in ['xlsx', 'xls']:
            df = pd.read_excel(file_path)
        elif dataset.file_type == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                df = pd.DataFrame(data)
            else:
                raise ValueError("JSON文件格式不支持，需要包含对象列表")
        else:
            raise ValueError(f"不支持的文件类型: {dataset.file_type}")
        
        # 生成列类型分布图
        column_types = get_column_types(df)
        summary['column_types'] = column_types
        summary['charts'].append({
            'type': 'pie',
            'title': '列类型分布',
            'data': [{'name': k, 'value': v} for k, v in column_types.items()]
        })
        
        # 生成缺失值分布图
        missing_data = get_missing_data(df)
        summary['missing_data'] = missing_data
        if missing_data['columns']:
            summary['charts'].append({
                'type': 'bar',
                'title': '缺失值比例 (前10列)',
                'categories': [col for col, _ in missing_data['columns'][:10]],
                'series': [{
                    'name': '缺失值比例 (%)',
                    'data': [pct for _, pct in missing_data['columns'][:10]]
                }]
            })
        
        # 生成数值列分布图 (最多5个)
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        for i, col in enumerate(numeric_columns[:5]):
            try:
                # 计算基本统计信息
                stats = {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'median': float(df[col].median()),
                    'std': float(df[col].std())
                }
                
                # 生成直方图数据
                hist_data = generate_histogram_data(df[col])
                
                summary['charts'].append({
                    'type': 'histogram',
                    'title': f'{col} 分布',
                    'categories': hist_data['bins'],
                    'series': [{
                        'name': col,
                        'data': hist_data['counts']
                    }],
                    'stats': stats
                })
            except:
                pass
        
        # 生成分类列分布图 (最多5个)
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        for i, col in enumerate(categorical_columns[:5]):
            try:
                # 获取前10个类别及其计数
                value_counts = df[col].value_counts().head(10)
                
                summary['charts'].append({
                    'type': 'bar',
                    'title': f'{col} 分布 (前10类)',
                    'categories': value_counts.index.tolist(),
                    'series': [{
                        'name': col,
                        'data': value_counts.values.tolist()
                    }]
                })
            except:
                pass
        
    except Exception as e:
        summary['error'] = str(e)
    
    return summary

def generate_assessment_charts(assessment):
    """
    生成评估结果的可视化图表
    
    Args:
        assessment: 评估模型实例
        
    Returns:
        dict: 包含图表数据的字典
    """
    charts = {
        'assessment_id': assessment.id,
        'assessment_name': assessment.name,
        'charts': []
    }
    
    # 1. 生成评分雷达图数据
    scores = {
        '数据质量': assessment.quality_score or 0,
        '完整性': assessment.completeness_score or 0,
        '一致性': assessment.consistency_score or 0,
        '准确性': assessment.accuracy_score or 0,
        '时效性': assessment.timeliness_score or 0,
        '业务价值': assessment.business_value_score or 0
    }
    
    charts['charts'].append({
        'type': 'radar',
        'title': '数据价值评分',
        'categories': list(scores.keys()),
        'series': [{
            'name': '评分',
            'data': list(scores.values())
        }]
    })
    
    # 2. 生成总体评分仪表盘
    charts['charts'].append({
        'type': 'gauge',
        'title': '综合价值评分',
        'value': assessment.overall_value_score or 0,
        'min': 0,
        'max': 100,
        'levels': [
            {'color': '#FF4500', 'range': [0, 40]},
            {'color': '#FFA500', 'range': [40, 70]},
            {'color': '#32CD32', 'range': [70, 100]}
        ]
    })
    
    # 3. 如果有详细结果，添加更多图表
    detailed_results = assessment.get_detailed_results()
    if detailed_results and 'quality' in detailed_results:
        quality = detailed_results['quality']
        
        # 完整性得分柱状图
        if 'completeness' in quality and 'column_scores' in quality['completeness']:
            completeness_scores = quality['completeness']['column_scores']
            # 选择前10个列
            items = list(completeness_scores.items())
            if items:
                columns = [col for col, _ in items[:10]]
                scores = [score for _, score in items[:10]]
                
                charts['charts'].append({
                    'type': 'bar',
                    'title': '列完整性得分',
                    'categories': columns,
                    'series': [{
                        'name': '完整性得分',
                        'data': scores
                    }]
                })
        
        # 一致性得分柱状图
        if 'consistency' in quality and 'column_scores' in quality['consistency']:
            consistency_scores = quality['consistency']['column_scores']
            # 选择前10个列
            items = list(consistency_scores.items())
            if items:
                columns = [col for col, _ in items[:10]]
                scores = [score for _, score in items[:10]]
                
                charts['charts'].append({
                    'type': 'bar',
                    'title': '列一致性得分',
                    'categories': columns,
                    'series': [{
                        'name': '一致性得分',
                        'data': scores
                    }]
                })
    
    return charts

def get_column_types(df):
    """
    获取DataFrame的列类型分布
    
    Args:
        df: pandas DataFrame
        
    Returns:
        dict: 列类型及其计数
    """
    type_counts = {}
    
    for dtype in df.dtypes:
        dtype_name = str(dtype)
        
        if 'int' in dtype_name:
            key = '整数'
        elif 'float' in dtype_name:
            key = '浮点数'
        elif 'datetime' in dtype_name:
            key = '日期时间'
        elif 'bool' in dtype_name:
            key = '布尔值'
        elif 'object' in dtype_name:
            key = '字符串'
        elif 'category' in dtype_name:
            key = '分类'
        else:
            key = '其他'
        
        type_counts[key] = type_counts.get(key, 0) + 1
    
    return type_counts

def get_missing_data(df):
    """
    获取DataFrame的缺失值信息
    
    Args:
        df: pandas DataFrame
        
    Returns:
        dict: 缺失值信息
    """
    missing_data = {
        'total_cells': df.size,
        'missing_cells': df.isna().sum().sum(),
        'missing_percentage': round((df.isna().sum().sum() / df.size) * 100, 2),
        'columns': []
    }
    
    # 计算每列的缺失值
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            missing_pct = round((missing_count / len(df)) * 100, 2)
            missing_data['columns'].append((col, missing_pct))
    
    # 按缺失比例降序排序
    missing_data['columns'].sort(key=lambda x: x[1], reverse=True)
    
    return missing_data

def generate_histogram_data(series, bins=10):
    """
    生成直方图数据
    
    Args:
        series: pandas Series
        bins: 分箱数量
        
    Returns:
        dict: 包含分箱和计数的字典
    """
    hist, bin_edges = np.histogram(series.dropna(), bins=bins)
    
    # 将分箱边界转换为标签
    bin_labels = []
    for i in range(len(bin_edges) - 1):
        bin_labels.append(f"{bin_edges[i]:.2f} - {bin_edges[i+1]:.2f}")
    
    return {
        'bins': bin_labels,
        'counts': hist.tolist()
    }

def format_file_size(size_bytes):
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化后的文件大小
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def plot_to_base64(plt_figure):
    """
    将matplotlib图形转换为base64编码的字符串
    
    Args:
        plt_figure: matplotlib图形
        
    Returns:
        str: base64编码的图形
    """
    buf = BytesIO()
    plt_figure.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_str