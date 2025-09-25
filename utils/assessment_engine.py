import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from utils.data_processor import process_dataset_file, analyze_data_quality

def run_assessment(dataset, rules=None):
    """
    运行数据价值评估
    
    Args:
        dataset: 数据集模型实例
        rules: 数据质量规则列表（可选）
        
    Returns:
        dict: 包含评估结果的字典
    """
    # 初始化结果字典
    results = {
        'dataset_id': dataset.id,
        'dataset_name': dataset.name,
        'assessment_time': datetime.utcnow().isoformat(),
        'quality_score': 0,
        'completeness_score': 0,
        'consistency_score': 0,
        'accuracy_score': 0,
        'timeliness_score': 0,
        'business_value_score': 0,
        'overall_value_score': 0,
        'details': {}
    }
    
    try:
        # 读取数据集文件
        file_path = dataset.file_path
        file_type = dataset.file_type
        
        # 根据文件类型读取数据
        if file_type == 'csv':
            df = pd.read_csv(file_path)
        elif file_type in ['xlsx', 'xls']:
            df = pd.read_excel(file_path)
        elif file_type == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                df = pd.DataFrame(data)
            else:
                raise ValueError("JSON文件格式不支持，需要包含对象列表")
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
        
        # 1. 数据质量评估
        quality_results = analyze_data_quality(df)
        results['quality_score'] = quality_results['overall_score']
        results['completeness_score'] = quality_results['completeness']['overall_score']
        results['consistency_score'] = quality_results['consistency']['overall_score']
        
        # 重构详细结果结构，使其与模板匹配
        results['details'] = {
            '数据质量': {
                '完整性': {
                    'score': quality_results['completeness']['overall_score'],
                    'description': '数据完整性评估，检查缺失值比例'
                },
                '一致性': {
                    'score': quality_results['consistency']['overall_score'],
                    'description': '数据一致性评估，检查数据类型和格式一致性'
                },
                '唯一性': {
                    'score': quality_results['uniqueness']['overall_score'],
                    'description': '数据唯一性评估，检查重复值比例'
                }
            }
        }
        
        # 2. 应用数据质量规则（如果提供）
        if rules:
            rule_results = apply_quality_rules(df, rules)
            results['details']['规则评估'] = {
                '规则通过率': {
                    'score': rule_results['pass_percentage'],
                    'description': f'应用了{rule_results["rule_count"]}条规则，{rule_results["passed_rules"]}条通过'
                }
            }
            results['accuracy_score'] = rule_results['pass_percentage']
        else:
            # 如果没有自定义规则，使用默认的准确性评估
            accuracy_score = evaluate_default_accuracy(df)
            results['details']['准确性评估'] = {
                '数据准确性': {
                    'score': accuracy_score,
                    'description': '基于数据类型和值范围的准确性评估'
                }
            }
            results['accuracy_score'] = accuracy_score
        
        # 3. 时效性评估
        timeliness_score = evaluate_timeliness(df)
        results['timeliness_score'] = timeliness_score
        results['details']['时效性评估'] = {
            '数据时效性': {
                'score': timeliness_score,
                'description': '基于数据最新更新时间的时效性评估'
            }
        }
        
        # 4. 数据价值维度评估
        value_dimensions = evaluate_value_dimensions(df)
        results['details']['价值维度'] = value_dimensions
        
        # 5. 业务价值评估
        business_value_score = calculate_business_value(
            results['quality_score'],
            results['completeness_score'],
            results['consistency_score'],
            results['accuracy_score'],
            results['timeliness_score']
        )
        results['business_value_score'] = business_value_score
        
        # 6. 计算综合价值得分
        results['overall_value_score'] = calculate_overall_value(results)
        
        # 添加综合评估结果
        results['details']['综合评估'] = {
            '数据质量得分': {
                'score': results['quality_score'],
                'description': '数据质量综合得分'
            },
            '业务价值得分': {
                'score': results['business_value_score'],
                'description': '数据业务价值综合得分'
            },
            '综合价值得分': {
                'score': results['overall_value_score'],
                'description': '数据综合价值得分'
            }
        }
        
    except Exception as e:
        results['error'] = str(e)
    
    return results

def apply_quality_rules(df, rules):
    """
    应用数据质量规则
    
    Args:
        df: pandas DataFrame
        rules: 数据质量规则列表
        
    Returns:
        dict: 包含规则应用结果的字典
    """
    rule_results = {
        'rule_count': len(rules),
        'passed_rules': 0,
        'failed_rules': 0,
        'pass_percentage': 0,
        'details': []
    }
    
    for rule in rules:
        rule_def = rule.get_rule_definition()
        column = rule_def.get('column')
        condition = rule_def.get('condition')
        value = rule_def.get('value')
        
        # 跳过不适用的规则
        if column not in df.columns:
            rule_result = {
                'rule_id': rule.id,
                'rule_name': rule.name,
                'status': 'skipped',
                'reason': f"列 '{column}' 不存在"
            }
            rule_results['details'].append(rule_result)
            continue
        
        # 应用规则
        result = apply_rule_condition(df, column, condition, value)
        
        # 记录结果
        if result['passed']:
            rule_results['passed_rules'] += 1
        else:
            rule_results['failed_rules'] += 1
        
        rule_result = {
            'rule_id': rule.id,
            'rule_name': rule.name,
            'rule_type': rule.rule_type,
            'status': 'passed' if result['passed'] else 'failed',
            'pass_rate': result['pass_rate'],
            'details': result['details']
        }
        rule_results['details'].append(rule_result)
    
    # 计算通过率
    if rule_results['rule_count'] > 0:
        rule_results['pass_percentage'] = round(
            (rule_results['passed_rules'] / rule_results['rule_count']) * 100, 2
        )
    
    return rule_results

def apply_rule_condition(df, column, condition, value):
    """
    应用规则条件
    
    Args:
        df: pandas DataFrame
        column: 列名
        condition: 条件类型
        value: 条件值
        
    Returns:
        dict: 包含规则应用结果的字典
    """
    result = {
        'passed': False,
        'pass_rate': 0,
        'details': {}
    }
    
    try:
        if condition == 'not_null':
            # 检查非空值
            valid_count = (~df[column].isna()).sum()
            total_count = len(df)
            pass_rate = (valid_count / total_count) * 100 if total_count > 0 else 0
            result['passed'] = pass_rate >= float(value)
            result['pass_rate'] = round(pass_rate, 2)
            result['details'] = {
                'valid_count': int(valid_count),
                'total_count': total_count,
                'threshold': float(value)
            }
        
        elif condition == 'unique':
            # 检查唯一值
            unique_count = df[column].nunique()
            total_count = len(df)
            pass_rate = (unique_count / total_count) * 100 if total_count > 0 else 0
            result['passed'] = pass_rate >= float(value)
            result['pass_rate'] = round(pass_rate, 2)
            result['details'] = {
                'unique_count': int(unique_count),
                'total_count': total_count,
                'threshold': float(value)
            }
        
        elif condition == 'range':
            # 检查值范围
            try:
                min_val, max_val = value.split(',')
                min_val = float(min_val.strip())
                max_val = float(max_val.strip())
                
                valid_count = ((df[column] >= min_val) & (df[column] <= max_val)).sum()
                total_count = len(df)
                pass_rate = (valid_count / total_count) * 100 if total_count > 0 else 0
                result['passed'] = pass_rate >= 95  # 默认95%符合率为通过
                result['pass_rate'] = round(pass_rate, 2)
                result['details'] = {
                    'valid_count': int(valid_count),
                    'total_count': total_count,
                    'min_value': min_val,
                    'max_value': max_val
                }
            except:
                result['details'] = {'error': '范围格式无效，应为"最小值,最大值"'}
        
        elif condition == 'pattern':
            # 检查模式匹配
            try:
                pattern = value
                valid_count = df[column].astype(str).str.match(pattern).sum()
                total_count = len(df)
                pass_rate = (valid_count / total_count) * 100 if total_count > 0 else 0
                result['passed'] = pass_rate >= 95  # 默认95%符合率为通过
                result['pass_rate'] = round(pass_rate, 2)
                result['details'] = {
                    'valid_count': int(valid_count),
                    'total_count': total_count,
                    'pattern': pattern
                }
            except:
                result['details'] = {'error': '正则表达式无效'}
        
        elif condition in ['equals', 'not_equals', 'greater_than', 'less_than']:
            # 比较操作
            try:
                compare_value = float(value) if df[column].dtype.kind in 'ifc' else value
                
                if condition == 'equals':
                    valid_count = (df[column] == compare_value).sum()
                elif condition == 'not_equals':
                    valid_count = (df[column] != compare_value).sum()
                elif condition == 'greater_than':
                    valid_count = (df[column] > compare_value).sum()
                elif condition == 'less_than':
                    valid_count = (df[column] < compare_value).sum()
                
                total_count = len(df)
                pass_rate = (valid_count / total_count) * 100 if total_count > 0 else 0
                result['passed'] = pass_rate >= 95  # 默认95%符合率为通过
                result['pass_rate'] = round(pass_rate, 2)
                result['details'] = {
                    'valid_count': int(valid_count),
                    'total_count': total_count,
                    'compare_value': compare_value,
                    'condition': condition
                }
            except:
                result['details'] = {'error': '比较值格式无效'}
        
        elif condition in ['in_list', 'not_in_list']:
            # 列表检查
            try:
                value_list = [v.strip() for v in value.split(',')]
                
                if condition == 'in_list':
                    valid_count = df[column].isin(value_list).sum()
                else:  # not_in_list
                    valid_count = (~df[column].isin(value_list)).sum()
                
                total_count = len(df)
                pass_rate = (valid_count / total_count) * 100 if total_count > 0 else 0
                result['passed'] = pass_rate >= 95  # 默认95%符合率为通过
                result['pass_rate'] = round(pass_rate, 2)
                result['details'] = {
                    'valid_count': int(valid_count),
                    'total_count': total_count,
                    'value_list': value_list,
                    'condition': condition
                }
            except:
                result['details'] = {'error': '列表格式无效'}
        
        else:
            result['details'] = {'error': f'不支持的条件类型: {condition}'}
    
    except Exception as e:
        result['details'] = {'error': str(e)}
    
    return result

def evaluate_timeliness(df):
    """
    评估数据的时效性
    
    Args:
        df: pandas DataFrame
        
    Returns:
        float: 时效性得分 (0-100)
    """
    # 查找可能的日期列
    date_columns = []
    for col in df.columns:
        # 检查列名是否包含日期相关关键词
        if any(keyword in col.lower() for keyword in ['date', 'time', 'day', 'month', 'year', '日期', '时间']):
            date_columns.append(col)
        
        # 检查是否为日期类型
        if df[col].dtype == 'datetime64[ns]':
            date_columns.append(col)
        
        # 尝试转换为日期类型
        if df[col].dtype == 'object':
            try:
                pd.to_datetime(df[col], errors='raise')
                date_columns.append(col)
            except:
                pass
    
    # 如果没有找到日期列，返回默认分数
    if not date_columns:
        return 50.0  # 默认中等分数
    
    # 分析最新的日期列
    latest_dates = []
    for col in date_columns:
        try:
            dates = pd.to_datetime(df[col], errors='coerce')
            if not dates.isna().all():
                latest = dates.max()
                latest_dates.append(latest)
        except:
            pass
    
    if not latest_dates:
        return 50.0  # 默认中等分数
    
    # 计算最新日期与当前日期的差距
    most_recent = max(latest_dates)
    days_diff = (datetime.now() - most_recent).days
    
    # 根据差距计算时效性得分
    if days_diff <= 1:  # 1天内
        return 100.0
    elif days_diff <= 7:  # 1周内
        return 90.0
    elif days_diff <= 30:  # 1个月内
        return 80.0
    elif days_diff <= 90:  # 3个月内
        return 70.0
    elif days_diff <= 180:  # 6个月内
        return 60.0
    elif days_diff <= 365:  # 1年内
        return 50.0
    else:  # 超过1年
        return max(10.0, 50.0 - (days_diff - 365) / 100)  # 随时间递减，但不低于10分

def calculate_business_value(quality_score, completeness_score, consistency_score, accuracy_score, timeliness_score):
    """
    计算业务价值得分
    
    Args:
        quality_score: 质量得分
        completeness_score: 完整性得分
        consistency_score: 一致性得分
        accuracy_score: 准确性得分
        timeliness_score: 时效性得分
        
    Returns:
        float: 业务价值得分 (0-100)
    """
    # 权重设置
    weights = {
        'quality': 0.2,
        'completeness': 0.2,
        'consistency': 0.15,
        'accuracy': 0.25,
        'timeliness': 0.2
    }
    
    # 计算加权得分
    business_value = (
        weights['quality'] * quality_score +
        weights['completeness'] * completeness_score +
        weights['consistency'] * consistency_score +
        weights['accuracy'] * (accuracy_score or 50) +  # 如果没有准确性得分，使用默认值50
        weights['timeliness'] * timeliness_score
    )
    
    return round(business_value, 2)

def evaluate_default_accuracy(df):
    """
    默认的准确性评估（当没有自定义规则时使用）
    
    Args:
        df: pandas DataFrame
        
    Returns:
        float: 准确性得分 (0-100)
    """
    accuracy_scores = []
    
    for col in df.columns:
        col_score = 0
        
        # 数值型列的准确性评估
        if np.issubdtype(df[col].dtype, np.number):
            # 检查异常值（超出3倍标准差）
            if df[col].std() > 0:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outlier_ratio = (z_scores > 3).mean()
                col_score = max(0, 100 - outlier_ratio * 100)
            else:
                col_score = 100  # 如果标准差为0，所有值相同，准确性高
        
        # 字符串列的准确性评估
        elif df[col].dtype == 'object':
            # 检查空字符串和无效值
            valid_ratio = (~df[col].isna() & (df[col].astype(str).str.strip() != '')).mean()
            col_score = valid_ratio * 100
        
        # 日期列的准确性评估
        elif df[col].dtype == 'datetime64[ns]':
            # 检查有效日期
            valid_ratio = (~df[col].isna()).mean()
            col_score = valid_ratio * 100
        
        accuracy_scores.append(col_score)
    
    # 返回平均准确性得分
    return round(sum(accuracy_scores) / len(accuracy_scores), 2) if accuracy_scores else 50.0

def evaluate_value_dimensions(df):
    """
    评估数据价值维度
    
    Args:
        df: pandas DataFrame
        
    Returns:
        dict: 包含各价值维度评估结果的字典
    """
    dimensions = {
        '数据完整性': {
            'score': 0,
            'description': '数据完整性和覆盖率评估'
        },
        '数据准确性': {
            'score': 0,
            'description': '数据准确性和可靠性评估'
        },
        '数据时效性': {
            'score': 0,
            'description': '数据时效性和新鲜度评估'
        },
        '数据一致性': {
            'score': 0,
            'description': '数据一致性和标准化评估'
        },
        '数据可用性': {
            'score': 0,
            'description': '数据可用性和易用性评估'
        }
    }
    
    # 计算数据完整性得分
    completeness_score = (1 - df.isna().mean().mean()) * 100
    dimensions['数据完整性']['score'] = round(completeness_score, 2)
    
    # 计算数据准确性得分（基于数据类型和值范围）
    accuracy_scores = []
    for col in df.columns:
        if np.issubdtype(df[col].dtype, np.number):
            # 数值型列：检查异常值
            if df[col].std() > 0:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outlier_ratio = (z_scores > 3).mean()
                accuracy_scores.append(100 - outlier_ratio * 100)
            else:
                accuracy_scores.append(100)
        else:
            # 非数值型列：检查有效值比例
            valid_ratio = (~df[col].isna()).mean()
            accuracy_scores.append(valid_ratio * 100)
    
    dimensions['数据准确性']['score'] = round(sum(accuracy_scores) / len(accuracy_scores), 2) if accuracy_scores else 50.0
    
    # 计算数据一致性得分
    consistency_scores = []
    for col in df.columns:
        if df[col].dtype == 'object':
            # 字符串列：检查格式一致性（例如长度分布）
            str_lens = df[col].astype(str).str.len()
            if str_lens.std() > 0:
                # 长度标准差越小，一致性越高
                consistency_score = max(0, 100 - (str_lens.std() / str_lens.mean()) * 100)
                consistency_scores.append(consistency_score)
            else:
                consistency_scores.append(100)
        else:
            consistency_scores.append(100)  # 数值型列默认一致性高
    
    dimensions['数据一致性']['score'] = round(sum(consistency_scores) / len(consistency_scores), 2) if consistency_scores else 100.0
    
    # 计算数据可用性得分
    usability_score = (
        dimensions['数据完整性']['score'] * 0.3 +
        dimensions['数据准确性']['score'] * 0.3 +
        dimensions['数据一致性']['score'] * 0.2 +
        (100 if len(df) > 0 else 0) * 0.2  # 数据量得分
    )
    dimensions['数据可用性']['score'] = round(usability_score, 2)
    
    return dimensions

def calculate_overall_value(results):
    """
    计算综合价值得分
    
    Args:
        results: 评估结果字典
        
    Returns:
        float: 综合价值得分 (0-100)
    """
    # 权重设置
    weights = {
        'quality': 0.3,
        'business_value': 0.7
    }
    
    # 计算加权得分
    overall_value = (
        weights['quality'] * results['quality_score'] +
        weights['business_value'] * results['business_value_score']
    )
    
    return round(overall_value, 2)