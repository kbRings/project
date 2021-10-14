#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import warnings

# 取消提示警告
warnings.filterwarnings("ignore")


# ## 查看数据

# In[4]:


# 读取数据
user_data = pd.read_csv('公众号用户访问数据.csv', encoding='utf-8')
# 查看数据
user_data


# In[5]:


# 查看数据的基本信息
user_data.info()


# In[6]:


# 查看data数据中的重复行
user_data[user_data.duplicated()]


# In[7]:


# 查看data数据中是否有异常值
user_data.describe()


# In[8]:


user_data['文章类别'].value_counts()


# In[9]:


user_data['访问日期'].value_counts()


# ## 数据处理

# In[10]:


# 取出用户编号，文章类别、访问日期三列数据
analysis_data = user_data[['用户编号', '文章类别', '访问日期']]
# 查看提取的数据
analysis_data


# In[11]:


# 定义“格式转换”函数
def conversion_data(category):
    
    # 判断文章类别是否已经转成了列表格式
    if str(category)[0] == '[':
        # 直接返回文章类别
        return category
    # 返回转成列表格式后的文章类别
    return [category]

# 获取‘文章类别’列，调用agg()方法
analysis_data['文章类别'] = analysis_data['文章类别'].agg(conversion_data)
# 查看处理后的数据
analysis_data


# In[12]:


# 根据‘访问日期’和‘用户编号’进行分组，并聚合‘文章类别’列
adjusted_data = analysis_data.groupby(['访问日期', '用户编号']).sum()
# 查看整理后的数据
adjusted_data


# ## 数据分析

# ### 设置最小支持度为0.1，使用默认最小置信度

# In[14]:


# 导入apyori模块下的apriori函数
from apyori import apriori

# 提取‘文章类别’列数据，调用apriori()函数，设置最小支持度为0.1，使用默认最小置信度
results = apriori(adjusted_data['文章类别'], min_support=0.1)

# 遍历结果数据
for result in results:
    # 获取支持度，并保留3位小数
    support = round(result.support, 3)
    
    # 遍历ordered_statistics对象
    for rule in result.ordered_statistics:
        # 获取前件和后件并转成列表
        head_set = list(rule.items_base)
        tail_set = list(rule.items_add)
        
        # 跳过前件为空的数据
        if head_set == []:
            continue
            
        # 将前件、后件拼接成关联规则的形式
        related_category = str(head_set) + '→' + str(tail_set)
        
        # 提取置信度，并保留3位小数
        confidence = round(rule.confidence, 3)
        # 提取提升度，并保留3位小数
        lift = round(rule.lift, 3)
        
        # 查看强关联规则，支持度，置信度，提升度
        print(related_category, support, confidence, lift)


# ### 分析最小置信度

# In[15]:


# 设置空的置信度列表
confidence_list = []

# 调用apriori()函数，生成关联规则
results = apriori(adjusted_data['文章类别'], min_support=0.1)

# 遍历统计列表中的关联规则，提取置信度
for result in results:
    for rule in result.ordered_statistics:
        
        # 获取前件并转成列表
        head_set = list(rule.items_base)
        
        # 跳过前件为空的数据
        if head_set == []:
            continue
            
        # 提取置信度，并保留3位小数
        confidence = round(rule.confidence, 3)
        
        # 将置信度写入置信度列表
        confidence_list.append(confidence)
        
# 查看置信度列表
confidence_list


# In[16]:


# 提取关联规则的置信度，生成Series数据
s = pd.Series(confidence_list)
# 查看置信度的描述性统计信息
s.describe()


# In[17]:


# 对关联规则的置信度的Series数据进行排序
s.sort_values()


# ### 设置最小支持度为0.1，设置最小置信度为0.3

# In[18]:


# 提取‘文章类别’列数据，调用apriori()函数，设置最小支持度为0.1，设置最小置信度为0.3
results = apriori(adjusted_data['文章类别'], min_support=0.1, min_confidence=0.3)

# 创建空列表，存储关联规则列表，形成嵌套列表
extract_result = []

for result in results:
    # 获取支持度，并保留3位小数
    support = round(result.support, 3)
    
    # 遍历ordered_statistics对象
    for rule in result.ordered_statistics:
        # 获取前件和后件并转成列表
        head_set = list(rule.items_base)
        tail_set = list(rule.items_add)
        
        # 跳过前件为空的数据
        if head_set == []:
            continue
            
        # 将前件、后件拼接成关联规则的形式
        related_category = str(head_set) + '→' + str(tail_set)
        
        # 提取置信度，并保留3位小数
        confidence = round(rule.confidence, 3)
        # 提取提升度，并保留3位小数
        lift = round(rule.lift, 3)
        
        # 将提取的数据保存到提取列表中
        extract_result.append([related_category, support, confidence, lift])
        
# 将数据转成DataFrame的形式
rules_data = pd.DataFrame(extract_result, columns=['关联规则', '支持度', '置信度', '提升度'])
# 将数据按照“支持度”排序
sorted_by_support = rules_data.sort_values(by='支持度')

# 查看排序后的数据
sorted_by_support


# In[19]:


# 提取出提升度大于1的数据，并重置数据的索引
promoted_rules = sorted_by_support[sorted_by_support['提升度'] > 1].reset_index(drop=True)
promoted_rules


# In[20]:


# 提取出提升度小于1的数据，并重置数据的索引
restricted_rules = sorted_by_support[sorted_by_support['提升度'] < 1].reset_index(drop=True)

restricted_rules


# ## 数据展现

# ### 画提升度大于1的关联规则的柱状图

# In[30]:


import matplotlib.pyplot as plt
import warnings

# 关闭警告提示
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']

# 设置画布尺寸
plt.figure(figsize=(20, 8))

# 设置横纵坐标以及柱子的宽度
width = 0.2

# 画出柱状图
plt.bar(promoted_rules.index-width/2, promoted_rules['支持度'], width=width)
plt.bar(promoted_rules.index+width/2, promoted_rules['置信度'], width=width)

# 设置图例
plt.legend(['支持度', '置信度'], fontsize=25)
# 设置标题
plt.title('促进关系的关联规则的支持度、置信度', fontsize=25)
# 设置刻度名称
plt.xticks(promoted_rules.index, promoted_rules['关联规则'], fontsize=15)
# 设置坐标轴标签
plt.xlabel('关联规则', fontsize=20)
plt.ylabel('数值', fontsize=20)


# ### 画提升度小于1的关联规则的柱状图

# In[28]:


# 设置画布尺寸
plt.figure(figsize=(20, 8))

# 画出柱状图
plt.bar(restricted_rules.index-width/2, restricted_rules['支持度'], width=width)
plt.bar(restricted_rules.index+width/2, restricted_rules['置信度'], width=width)

# 设置图例
plt.legend(['支持度', '置信度'], fontsize=25)
# 设置标题
plt.title('抑制关系的关联规则的支持度、置信度', fontsize=25)
# 设置刻度名称
plt.xticks(restricted_rules.index, restricted_rules['关联规则'], fontsize=15)
# 设置坐标轴标签
plt.xlabel('关联规则', fontsize=20)
plt.ylabel('数值', fontsize=20)


# ### 所有强关联规则的提升度柱状图

# In[31]:


# 设置画布尺寸
plt.figure(figsize=(20, 8))

# 画出柱状图
plt.bar(sorted_by_support.index, sorted_by_support['提升度'], width=width)
# 设置标题
plt.title('提升度柱状图', fontsize=25)
# 设置刻度名称
plt.xticks(sorted_by_support.index, sorted_by_support['关联规则'], fontsize=15)

# 设置坐标轴标签
plt.xlabel('关联规则', fontsize=20)
plt.ylabel('提升度', fontsize=20)

# 设置数据标签
for a,b in zip(sorted_by_support.index, sorted_by_support['提升度']):
    plt.text(a, b, b, ha='center', va='bottom', fontsize=12)


# In[ ]:




