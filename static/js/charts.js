/**
 * 数据价值评估系统 - 图表工具函数
 */

// 初始化ECharts图表
function initCharts() {
    // 检查ECharts是否已加载
    if (typeof echarts === 'undefined') {
        console.error('ECharts未加载，请检查CDN链接');
        return;
    }
    
    // 初始化所有图表容器
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        const chartType = container.dataset.chartType;
        if (chartType) {
            initChart(container, chartType);
        }
    });
}

// 初始化单个图表
function initChart(container, chartType) {
    const chart = echarts.init(container);
    
    // 根据图表类型设置不同的配置
    let option = {};
    
    switch (chartType) {
        case 'radar':
            option = getRadarOption();
            break;
        case 'bar':
            option = getBarOption();
            break;
        case 'pie':
            option = getPieOption();
            break;
        case 'line':
            option = getLineOption();
            break;
        default:
            console.warn('未知的图表类型:', chartType);
            return;
    }
    
    chart.setOption(option);
    
    // 响应式调整
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    return chart;
}

// 获取雷达图配置
function getRadarOption(data = null) {
    return {
        title: {
            text: '数据质量评估',
            left: 'center'
        },
        tooltip: {
            trigger: 'item'
        },
        legend: {
            data: ['当前评估'],
            bottom: 10
        },
        radar: {
            indicator: [
                { name: '完整性', max: 100 },
                { name: '准确性', max: 100 },
                { name: '一致性', max: 100 },
                { name: '时效性', max: 100 },
                { name: '可用性', max: 100 }
            ]
        },
        series: [{
            name: '数据质量',
            type: 'radar',
            data: data || [{
                value: [85, 90, 78, 92, 88],
                name: '当前评估'
            }]
        }]
    };
}

// 获取柱状图配置
function getBarOption(data = null) {
    return {
        title: {
            text: '各项指标得分',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: data ? data.categories : ['完整性', '准确性', '一致性', '时效性', '可用性']
        },
        yAxis: {
            type: 'value',
            max: 100
        },
        series: [{
            name: '得分',
            type: 'bar',
            data: data ? data.values : [85, 90, 78, 92, 88],
            itemStyle: {
                color: function(params) {
                    const value = params.data;
                    if (value >= 90) return '#1cc88a'; // 绿色
                    if (value >= 80) return '#36b9cc'; // 蓝色
                    if (value >= 70) return '#f6c23e'; // 黄色
                    return '#e74a3b'; // 红色
                }
            },
            label: {
                show: true,
                position: 'top',
                formatter: '{c}'
            }
        }]
    };
}

// 获取饼图配置
function getPieOption(data = null) {
    return {
        title: {
            text: '质量等级分布',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
            orient: 'vertical',
            left: 'left'
        },
        series: [{
            name: '质量等级',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: false,
                position: 'center'
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: '18',
                    fontWeight: 'bold'
                }
            },
            labelLine: {
                show: false
            },
            data: data || [
                { value: 35, name: '优秀 (90-100)' },
                { value: 40, name: '良好 (80-89)' },
                { value: 20, name: '一般 (70-79)' },
                { value: 5, name: '需改进 (<70)' }
            ]
        }]
    };
}

// 获取折线图配置
function getLineOption(data = null) {
    return {
        title: {
            text: '历史评估趋势',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: data ? data.legend : ['完整性', '准确性', '一致性'],
            bottom: 10
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: data ? data.categories : ['评估1', '评估2', '评估3', '评估4', '当前评估']
        },
        yAxis: {
            type: 'value',
            max: 100
        },
        series: data ? data.series : [
            {
                name: '完整性',
                type: 'line',
                smooth: true,
                data: [78, 82, 85, 83, 85]
            },
            {
                name: '准确性',
                type: 'line',
                smooth: true,
                data: [85, 88, 90, 87, 90]
            },
            {
                name: '一致性',
                type: 'line',
                smooth: true,
                data: [72, 75, 78, 76, 78]
            }
        ]
    };
}

// 从API获取数据并更新图表
function loadChartData(chart, apiUrl) {
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const option = chart.getOption();
            // 根据API返回的数据更新图表配置
            // 这里需要根据具体的API响应格式进行调整
            chart.setOption(updateChartOption(option, data));
        })
        .catch(error => {
            console.error('加载图表数据失败:', error);
        });
}

// 更新图表配置（需要根据具体需求实现）
function updateChartOption(option, data) {
    // 根据数据更新图表配置
    // 这里是一个示例实现，需要根据实际数据结构调整
    if (data.type === 'radar') {
        option.series[0].data = data.values;
    } else if (data.type === 'bar') {
        option.xAxis.data = data.categories;
        option.series[0].data = data.values;
    }
    // 其他图表类型的更新逻辑...
    
    return option;
}

// 导出图表为图片
function exportChart(chart, filename = 'chart') {
    const imgData = chart.getDataURL({
        pixelRatio: 2,
        backgroundColor: '#fff'
    });
    
    const link = document.createElement('a');
    link.download = `${filename}.png`;
    link.href = imgData;
    link.click();
}

// 页面加载完成后初始化图表
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
});

// 导出函数供其他模块使用
window.ChartUtils = {
    initCharts,
    initChart,
    getRadarOption,
    getBarOption,
    getPieOption,
    getLineOption,
    loadChartData,
    exportChart
};