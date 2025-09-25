from forms.auth_forms import LoginForm, RegistrationForm
from forms.data_forms import DatasetUploadForm, DatasetEditForm
from forms.assessment_forms import AssessmentForm, DataQualityRuleForm

# 导出所有表单类
__all__ = [
    'LoginForm', 'RegistrationForm',
    'DatasetUploadForm', 'DatasetEditForm',
    'AssessmentForm', 'DataQualityRuleForm'
]