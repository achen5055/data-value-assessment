import os
import json
import pandas as pd
import numpy as np

def get_file_info(file_path):
    """
    获取文件的基本信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        dict: 包含文件信息的字典
    """
    file_info = {
        'file_type': os.path.splitext(file_path)[1][1:].lower(),
        'size_bytes': os.path.getsize(file_path)
    }
    
    # 根据文件类型读取更多信息
    try:
        if file_info['file_type'] in ['csv']:
            df = pd.read_csv(file_path)
            file_info.update(_get_dataframe_info(df))
        elif file_info['file_type'] in ['xlsx', 'xls']:
            df = pd.read_excel(file_path)
            file_info.update(_get_dataframe_info(df))
        elif file_info['file_type'] == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                df = pd.DataFrame(data)
                file_info.update(_get_dataframe_info(df))
            else:
                file_info['row_count'] = 1 if data else 0
                file_info['column_count'] = len(data) if isinstance(data, dict) else 0
                file_info['schema'] = {'type': 'json', 'structure': 'object'}
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
    
    return file_info

def _get_dataframe_info(df):
    """
    获取DataFrame的信息
    
    Args:
        df: pandas DataFrame
        
    Returns:
        dict: 包含DataFrame信息的字典
    """
    info = {
        'row_count': len(df),
        'column_count': len(df.columns)
    }
    
    # 获取列信息
    columns = []
    for col in df.columns:
        col_info = {
            'name': col,
            'type': str(df[col].dtype),
            'unique_count': int(df[col].nunique()),
            'missing_count': int(df[col].isna().sum()),
            'missing_percentage': float(round(df[col].isna().mean() * 100, 2))
        }
        
        # 对于数值型列，添加统计信息
        if np.issubdtype(df[col].dtype, np.number):
            col_info.update({
                'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                'std': float(df[col].std()) if not pd.isna(df[col].std()) else None
            })
        
        # 对于字符串列，添加长度信息
        elif df[col].dtype == 'object':
            try:
                str_lens = df[col].astype(str).str.len()
                col_info.update({
                    'min_length': int(str_lens.min()) if not pd.isna(str_lens.min()) else None,
                    'max_length': int(str_lens.max()) if not pd.isna(str_lens.max()) else None,
                    'mean_length': float(str_lens.mean()) if not pd.isna(str_lens.mean()) else None
                })
            except:
                pass
        
        columns.append(col_info)
    
    info['schema'] = columns
    return info

def process_dataset_file(file_path, preview=False, limit=100):
    """
    处理数据集文件，返回数据或预览
    
    Args:
        file_path: 文件路径
        preview: 是否只返回预览数据
        limit: 预览行数限制
        
    Returns:
        dict: 包含数据或预览的字典
    """
    file_type = os.path.splitext(file_path)[1][1:].lower()
    result = {'file_type': file_type}
    
    try:
        if file_type == 'csv':
            df = pd.read_csv(file_path)
            if preview:
                df = df.head(limit)
            result['data'] = df.to_dict('records')
            result['columns'] = df.columns.tolist()
        
        elif file_type in ['xlsx', 'xls']:
            df = pd.read_excel(file_path)
            if preview:
                df = df.head(limit)
            result['data'] = df.to_dict('records')
            result['columns'] = df.columns.tolist()
        
        elif file_type == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                df = pd.DataFrame(data)
                if preview:
                    df = df.head(limit)
                result['data'] = df.to_dict('records')
                result['columns'] = df.columns.tolist()
            else:
                result['data'] = data
                result['preview'] = True
        
        else:
            result['error'] = f"不支持的文件类型: {file_type}"
    
    except Exception as e:
        result['error'] = f"处理文件时出错: {str(e)}"
    
    return result

def analyze_data_quality(df):
    """
    分析数据质量
    
    Args:
        df: pandas DataFrame
        
    Returns:
        dict: 包含数据质量分析结果的字典
    """
    quality_results = {
        'completeness': {},
        'uniqueness': {},
        'consistency': {},
        'overall_score': 0
    }
    
    # 计算完整性 (非空值比例)
    completeness_scores = {}
    for col in df.columns:
        non_null_ratio = 1 - df[col].isna().mean()
        completeness_scores[col] = round(non_null_ratio * 100, 2)
    quality_results['completeness'] = {
        'column_scores': completeness_scores,
        'overall_score': round(sum(completeness_scores.values()) / len(completeness_scores), 2)
    }
    
    # 计算唯一性 (唯一值比例)
    uniqueness_scores = {}
    for col in df.columns:
        unique_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
        uniqueness_scores[col] = round(unique_ratio * 100, 2)
    quality_results['uniqueness'] = {
        'column_scores': uniqueness_scores,
        'overall_score': round(sum(uniqueness_scores.values()) / len(uniqueness_scores), 2)
    }
    
    # 计算一致性 (基于数据类型的有效值比例)
    consistency_scores = {}
    for col in df.columns:
        # 对于数值型列，检查非无穷大和非NaN的比例
        if np.issubdtype(df[col].dtype, np.number):
            valid_ratio = (~df[col].isna() & np.isfinite(df[col])).mean()
        # 对于日期列，检查可解析为日期的比例
        elif df[col].dtype == 'datetime64[ns]':
            valid_ratio = (~df[col].isna()).mean()
        # 对于字符串列，检查非空字符串的比例
        else:
            try:
                valid_ratio = (~df[col].isna() & (df[col].astype(str).str.strip() != '')).mean()
            except:
                valid_ratio = (~df[col].isna()).mean()
        
        consistency_scores[col] = round(valid_ratio * 100, 2)
    
    quality_results['consistency'] = {
        'column_scores': consistency_scores,
        'overall_score': round(sum(consistency_scores.values()) / len(consistency_scores), 2)
    }
    
    # 计算总体得分 (各项得分的平均值)
    overall_scores = [
        quality_results['completeness']['overall_score'],
        quality_results['uniqueness']['overall_score'],
        quality_results['consistency']['overall_score']
    ]
    quality_results['overall_score'] = round(sum(overall_scores) / len(overall_scores), 2)
    
    return quality_results