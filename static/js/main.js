/**
 * 数据价值评估系统 - 主要JavaScript文件
 */

// 当DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initTooltips();
    
    // 初始化警告消息自动关闭
    initAlertDismiss();
    
    // 初始化文件上传预览
    initFileUploadPreview();
    
    // 初始化数据表格
    initDataTables();
});

/**
 * 初始化Bootstrap工具提示
 */
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * 初始化警告消息自动关闭
 */
function initAlertDismiss() {
    // 3秒后自动关闭警告消息
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-important)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 3000);
}

/**
 * 初始化文件上传预览
 */
function initFileUploadPreview() {
    var fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            var fileName = e.target.files[0] ? e.target.files[0].name : '未选择文件';
            var fileLabel = document.querySelector('.custom-file-label');
            if (fileLabel) {
                fileLabel.textContent = fileName;
            }
            
            // 显示文件类型图标
            var fileTypeIcon = document.getElementById('fileTypeIcon');
            if (fileTypeIcon && e.target.files[0]) {
                var fileType = e.target.files[0].name.split('.').pop().toLowerCase();
                var iconClass = 'fas fa-file';
                
                if (fileType === 'csv') {
                    iconClass = 'fas fa-file-csv';
                } else if (['xls', 'xlsx'].includes(fileType)) {
                    iconClass = 'fas fa-file-excel';
                } else if (fileType === 'json') {
                    iconClass = 'fas fa-file-code';
                }
                
                fileTypeIcon.className = iconClass;
                fileTypeIcon.style.display = 'inline-block';
            }
        });
    }
}

/**
 * 初始化数据表格
 */
function initDataTables() {
    var dataTables = document.querySelectorAll('.datatable');
    if (dataTables.length > 0) {
        dataTables.forEach(function(table) {
            $(table).DataTable({
                language: {
                    "sProcessing": "处理中...",
                    "sLengthMenu": "显示 _MENU_ 条",
                    "sZeroRecords": "没有匹配结果",
                    "sInfo": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
                    "sInfoEmpty": "显示第 0 至 0 项结果，共 0 项",
                    "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
                    "sInfoPostFix": "",
                    "sSearch": "搜索:",
                    "sUrl": "",
                    "sEmptyTable": "表中数据为空",
                    "sLoadingRecords": "载入中...",
                    "sInfoThousands": ",",
                    "oPaginate": {
                        "sFirst": "首页",
                        "sPrevious": "上页",
                        "sNext": "下页",
                        "sLast": "末页"
                    },
                    "oAria": {
                        "sSortAscending": ": 以升序排列此列",
                        "sSortDescending": ": 以降序排列此列"
                    }
                },
                responsive: true
            });
        });
    }
}

/**
 * 创建评分图表
 * @param {string} elementId - 图表容器元素ID
 * @param {Object} scores - 评分数据对象
 */
function createScoreChart(elementId, scores) {
    var chartDom = document.getElementById(elementId);
    if (!chartDom) return;
    
    var myChart = echarts.init(chartDom);
    var option = {
        radar: {
            indicator: [
                { name: '数据质量', max: 100 },
                { name: '完整性', max: 100 },
                { name: '一致性', max: 100 },
                { name: '准确性', max: 100 },
                { name: '时效性', max: 100 },
                { name: '业务价值', max: 100 }
            ]
        },
        series: [{
            type: 'radar',
            data: [{
                value: [
                    scores.quality || 0,
                    scores.completeness || 0,
                    scores.consistency || 0,
                    scores.accuracy || 0,
                    scores.timeliness || 0,
                    scores.business_value || 0
                ],
                name: '评分',
                areaStyle: {
                    color: 'rgba(78, 115, 223, 0.3)'
                },
                lineStyle: {
                    color: '#4e73df',
                    width: 2
                },
                itemStyle: {
                    color: '#4e73df'
                }
            }]
        }]
    };
    
    myChart.setOption(option);
    
    // 响应式调整
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}

/**
 * 创建仪表盘图表
 * @param {string} elementId - 图表容器元素ID
 * @param {number} value - 仪表盘值
 * @param {string} title - 图表标题
 */
function createGaugeChart(elementId, value, title) {
    var chartDom = document.getElementById(elementId);
    if (!chartDom) return;
    
    var myChart = echarts.init(chartDom);
    var option = {
        title: {
            text: title,
            left: 'center'
        },
        series: [{
            type: 'gauge',
            progress: {
                show: true,
                width: 18
            },
            axisLine: {
                lineStyle: {
                    width: 18,
                    color: [
                        [0.4, '#e74a3b'],
                        [0.7, '#f6c23e'],
                        [1, '#1cc88a']
                    ]
                }
            },
            axisTick: { show: false },
            splitLine: { show: false },
            axisLabel: { show: false },
            anchor: { show: false },
            pointer: { show: false },
            detail: {
                valueAnimation: true,
                fontSize: 30,
                offsetCenter: [0, '70%'],
                formatter: '{value}',
                color: 'inherit'
            },
            data: [{
                value: value || 0
            }]
        }]
    };
    
    myChart.setOption(option);
    
    // 响应式调整
    window.addEventListener('resize', function() {
        myChart.resize();
    });
}

/**
 * 格式化文件大小
 * @param {number} bytes - 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 确认删除操作
 * @param {string} message - 确认消息
 * @returns {boolean} 是否确认删除
 */
function confirmDelete(message) {
    return confirm(message || '确定要删除吗？此操作不可恢复。');
}

/**
 * 加载数据集预览
 * @param {number} datasetId - 数据集ID
 * @param {string} containerId - 预览容器元素ID
 */
function loadDatasetPreview(datasetId, containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;
    
    // 显示加载中
    container.innerHTML = '<div class="text-center py-5"><div class="loading-spinner"></div><p class="mt-3">加载数据预览中...</p></div>';
    
    // 发送AJAX请求获取预览数据
    fetch(`/api/dataset/${datasetId}/preview`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                return;
            }
            
            // 创建表格
            var tableHtml = '<div class="table-responsive"><table class="table table-sm table-hover"><thead><tr>';
            
            // 表头
            data.columns.forEach(column => {
                tableHtml += `<th>${column}</th>`;
            });
            
            tableHtml += '</tr></thead><tbody>';
            
            // 表格内容
            data.data.forEach(row => {
                tableHtml += '<tr>';
                data.columns.forEach(column => {
                    tableHtml += `<td>${row[column] !== null ? row[column] : '<span class="text-muted">null</span>'}</td>`;
                });
                tableHtml += '</tr>';
            });
            
            tableHtml += '</tbody></table></div>';
            
            // 添加预览信息
            var infoHtml = `<p class="text-muted">显示前 ${data.data.length} 行数据，共 ${data.total_rows} 行</p>`;
            
            container.innerHTML = infoHtml + tableHtml;
        })
        .catch(error => {
            container.innerHTML = `<div class="alert alert-danger">加载预览失败: ${error.message}</div>`;
        });
}