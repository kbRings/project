#!/usr/bin/env python
# coding: utf-8

# In[32]:


import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import cufflinks as cf
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = 'all'
cf.set_config_file(offline=True) # 离线模式绘图


# ### 加载数据

# In[33]:


data = pd.read_csv('./电子产品销售分析.csv')
data.head()


# ### 数据预处理

# In[34]:


"""
字段介绍：
Unnamed:行号 event_time:下单时间 order_id:订单编号 product_id:产品标号 category_id:类别编号
category_code:类别 brand:品牌 price:价格 user_id:用户编号 age:年龄 sex:性别 local:省份
"""
data.info()


# In[35]:


# 提取日期列（年月日）和月份列（年月）
data['event_time'] = pd.to_datetime(data['event_time'])
data['event_dates'] = data['event_time'].dt.date.astype('datetime64[ns]')
data['event_month'] = data['event_time'].values.astype('datetime64[M]')


# In[36]:


# 删除行号列
data = data.drop(['Unnamed: 0'], axis=1)
data


# In[37]:


# user_id列格式设置为str
data['user_id'] = data['user_id'].values.astype('str')
data
data.info()


# In[38]:


# 查看这两列的数据缺失比重
print('category_code缺失比例', data['category_code'].isnull().sum()/data.shape[0], 'brand缺失比例为',
     data['brand'].isnull().sum()/data.shape[0])


# In[39]:


# category_code缺失比例为22.9%，比重较大，不建议删除，这里我们选择用"R"来填充缺失值
# brand缺失值比例为4.8%，比重较小，可以直接删除
data.dropna(subset=['brand'], axis=0, inplace=True)
data.info()


# In[40]:


data['category_code'] = data['category_code'].fillna('R')
data.info()


# In[41]:


# 查看重复值
data[data.duplicated()]
data[['order_id', 'product_id']].duplicated().sum()


# In[42]:


# 由于这个数据表只有订单号，没有订单下的商品销售数量，所以这里的重复值是同笔订单下了多个数量的订单
# 所以不删除重复值，进而增加一列购买数量的列和总价的列
# 添加新列：buy_cnt
df = data.groupby(['order_id', 'product_id']).agg(buy_cnt=('user_id', 'count'))
data = pd.merge(data, df, on=['order_id', 'product_id'], how='inner')


# In[47]:


data[data.duplicated()]
data = data.drop_duplicates().reset_index(drop=True)


# In[48]:


data.info()


# In[49]:


# 添加新列：购买总金额
data['amount'] = data['price'] * data['buy_cnt']
data


# In[51]:


# 查看其他数据是否有异常
data[['event_time', 'price', 'age', 'sex']].describe(include='all')


# In[52]:


# 年龄的范围是16-50，正常。价格最小的是0（可能是免费的赠品），最大的一个是11574.05（一台电视机），正常
data[data['price'] == max(data['price'])]


# In[53]:


# event_time中有一个1970年的要删除
data = data.drop(index=data[data['event_time']=='1970-01-01 00:33:40+00:00'].index)
# 恢复索引
data.index = range(data.shape[0])


# In[54]:


min(data['event_time'])


# ### 数据分析

# In[55]:


data


# #### 总指标

# In[57]:


# 总GMV(网站的成交金额，主要包括付款金额和未付款的)约为1.15亿元
round(data['amount'].sum(), ndigits=2)


# In[58]:


# 每月的GMV
# GMV8月之前都基本是处于上升状态，在7月8月的上升更是非常大，8月达到峰值，然后就开始下降了
data.groupby(by='event_month', as_index=True).agg({'amount':sum}).iplot(kind='line')


# In[60]:


# 客单价（总销售额/总消费人数）
round(data['amount'].sum() / data['user_id'].nunique(), 0)


# In[61]:


# 笔单价（总销售额/总订单笔数）
round(data['amount'].sum() / data['order_id'].nunique(), 0)


# #### 用户分析

# In[62]:


# 用户年龄结构
# 先划分一下年龄
data['age_cut'] = pd.cut(data['age'], bins=[data.age.min(), 20, 30, 40, data.age.max()], labels=['16-20','20-30','30-40','40-50'])
data[['age', 'age_cut']]


# In[65]:


# age_unique:年龄非重复计数
data.groupby(by=data['age_cut']).agg(age_unique=('user_id', 'nunique')).reset_index().iplot(kind='pie', labels='age_cut', values='age_unique')


# In[69]:


# 购买用户中，年龄在【20-50】范围内的人群占多数，且20-30、30-40、40-50、三类群体占比都在28%以上，16-20岁的人群还没经济独立，消费占比较小
a = data.groupby(by=data['age_cut'], as_index=False).agg({'order_id':len, 'amount':sum})
a


# In[70]:


# 20岁以上的客户中，下单数/消费额的占比都比较接近，差异不明显，40-50岁这个年龄段的消费水平更高些
import plotly.offline as py
import plotly.graph_objs as go
pyplt = py.offline.plot
py.init_notebook_mode(connected=True)

fig = {
    "data":[
        {
            'values':a['order_id'],
            'labels':a['age_cut'],
            'domain':{'x':[0,0.8], 'y':[0,0.6]},
            'name':"不同年龄段的订单占比",
            'hoverinfo':"label+percent+name",
            'hole':.3,
            'type':'pie'
        },
        {
            'values':a['amount'],
            'labels':a['age_cut'],
            'domain':{'x':[.6,1],'y':[0,.6]},
            'name':"不同年龄段的销售额占比",
            'hoverinfo':'label+percent+name',
            'hole':.3,
            'type':'pie'
        }
    ],
    'layout':{
        'title':'不同年龄段订单/销售额占比分布图',
        'annotations':[
            {
                'font':{'size':18},
                'showarrow':False,
                'text':'订单占比',
                'x':0.4,
                'y':0.255
            },
            {
                'font':{'size':18},
                'showarrow':False,
                'text':'销售额占比',
                'x':0.86,
                'y':0.255
            }
        ]
    }
}
py.iplot(fig)


# In[71]:


# 用户性别比例
# 男女各占一半，购买用户中没有明显的性别差异
data.groupby(by='sex', as_index=False).agg({'age':len}).iplot(kind='pie', labels='sex', values='age')


# In[72]:


b = data.groupby(by=data['sex'], as_index=False).agg({'order_id':len, 'amount':sum})
b


# In[73]:


# 在下单数/销售额层面，不同性别之间也没有明显差异
fig = {
    'data':[
        {
            'values':b['order_id'],
            'labels':b['sex'],
            'domain':{'x':[0,0.8], 'y':[0,0.6]},
            'name':"不同性别的订单占比",
            'hoverinfo':'label+percent+name',
            'hole':.3,
            'type':'pie'
        },
        {
            'values':b['amount'],
            'labels':b['sex'],
            'domain':{'x':[.6,1], 'y':[0,.6]},
            'name':'不同性别的销售额占比',
            'hoverinfo':'label+percent+name',
            'hole':.3,
            'type':'pie'
        }
    ],
    'layout':{
        'title':'不同性别订单/销售额占比分布图',
        'annotations':[
            {
                'font':{'size':18},
                'showarrow':False,
                'text':'订单占比',
                'x':0.4,
                'y':0.255
            },
            {
                'font':{'size':18},
                'showarrow':False,
                'text':'销售额占比',
                'x':0.86,
                'y':0.255
            }
        ]
    }
}
py.iplot(fig)


# In[74]:


# 用户的地区分布
# 这里要排下序
# 用户所在地区前三的分别是广东、上海、北京
data.groupby(by='local', as_index=True).agg({'age':len}).sort_values(by='age', ascending=True).iplot(kind='bar', orientation='h')


# In[75]:


# 新老用户每月的销售额与销量对比
# 划分每个用户的首次购买月份（用来确认用户在几月份是属于新客户）
data_user = data.groupby('user_id').agg(首次购买时间 = ('event_time', 'min')).reset_index()
user_all = pd.merge(data, data_user, on='user_id')
user_all['新老用户'] = np.where(user_all['event_time']==user_all['首次购买时间'], '新客户', '老客户')


# In[76]:


user_all


# In[77]:


# 2020年5月之前，新老客户的贡献度相差不大（老客户贡献度略多于新客户）；2020年5月以后，差异逐渐变大，老客户的贡献度远超新客户
pd.pivot_table(user_all, index='event_month', columns='新老用户', values='buy_cnt', aggfunc='sum').iplot(kind='line', title='新老客户每月销量')


# In[79]:


pd.pivot_table(user_all, index='event_month', columns='新老用户', values='amount', aggfunc='sum').iplot(kind='line', title='新老客户每月销售额')


# In[80]:


# 七月、八月的新增客户数最多
user_all[user_all['新老用户']=='新客户'].groupby('event_month')['order_id'].count().iplot(kind='line')
# pd.pivot_table(user_all, index='event_month', columns='新老用户', values='order_id', aggfunc='count')


# ### 获取RFM各项值

# In[81]:


# 做透视表，求出RFMP
RFM_df = pd.pivot_table(user_all, index='user_id', values=['event_dates', 'order_id', 'amount', 'product_id'],
                       aggfunc=({'event_dates':max, 'order_id':len, 'amount':sum}))
RFM_df


# In[83]:


# 求出R值
RFM_df['event_dates'] = RFM_df['event_dates'].max() - RFM_df['event_dates']
RFM_df


# In[85]:


# 去除event_dates列中的"days"字段，以30天为周期
RFM_df['event_dates'] = RFM_df['event_dates'].map(lambda x:x/np.timedelta64(30,'D'))
RFM_df


# In[86]:


# 将列（column）排序
RFM_df = RFM_df[['event_dates', 'order_id', 'amount']]
# 重命名列
RFM_df.rename(columns={'event_dates':'R', 'order_id':'F', 'amount':'M'}, inplace=True)
# 重设索引
RFM_df.reset_index(inplace=True)
RFM_df


# In[87]:


# 打分
RFM_df_score = RFM_df.copy()


# In[88]:


for i,j in enumerate(RFM_df_score['R']):
    if j <= 1:
        RFM_df_score['R'][i] = 5
    elif j <= 2:
        RFM_df_score['R'][i] = 4
    elif j <= 3:
        RFM_df_score['R'][i] = 3
    elif j <= 4:
        RFM_df_score['R'][i] = 2
    else:
        RFM_df_score['R'][i] = 1


# In[89]:


for i,j in enumerate(RFM_df_score['F']):
    if j <= 1:
        RFM_df_score['F'][i] = 1
    elif j <= 2:
        RFM_df_score['F'][i] = 2
    elif j <= 3:
        RFM_df_score['F'][i] = 3
    elif j <= 4:
        RFM_df_score['F'][i] = 4
    else :
        RFM_df_score['F'][i] = 5


# In[90]:


for i,j in enumerate(RFM_df_score['M']):
    if j <= 200:
        RFM_df_score['M'][i] = 1
    elif j <= 500:
        RFM_df_score['M'][i] = 2
    elif j <= 1000:
        RFM_df_score['M'][i] = 3
    elif j <= 2000:
        RFM_df_score['M'][i] = 4
    else :
        RFM_df_score['M'][i] = 5


# In[91]:


RFM_df_score


# ### KMeans人群分类

# In[92]:


from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score # 轮廓系数
from sklearn.preprocessing import StandardScaler, MinMaxScaler # 归一化处理的模块


# In[93]:


# 获取数据
df0 = RFM_df_score.iloc[:,1:]
# 标准化数据
res_std = StandardScaler().fit_transform(df0)
res_std


# In[94]:


# 使用轮廓系数法确定k值
score = []
for i in range(2, 9):
    # 训练模型
    clf = KMeans(n_clusters=i, random_state=0).fit(res_std)
    # 获取评分（轮廓系数）
    score.append(silhouette_score(res_std, clf.labels_))
    
pd.DataFrame({'n_clusters':np.arange(2,9), 'score':score}).set_index('n_clusters').iplot(kind='line', xTitle='n_clusters', yTitle='score')


# In[95]:


# 使用手肘法确定k值
inertia = []
for k in range(2, 9):
    kmeans = KMeans(n_clusters=k, random_state=0).fit(res_std)
    inertia.append(np.sqrt(kmeans.inertia_))

plt.plot(range(2, 9), inertia)
plt.xlabel('k')
plt.show()


# In[96]:


# 获取最佳分簇数模型，这里我们取6
clf = KMeans(n_clusters=6, random_state=20).fit(res_std)
# 添加label
df0['labels'] = clf.labels_
df0


# In[97]:


# 统计一下各类用户之间的差异
df0['labels'].value_counts(normalize=True)  # normalize=True显示占比


# In[98]:


# 提取质心
clf.cluster_centers_


# In[99]:


rfm_data_centers = pd.DataFrame(clf.cluster_centers_, columns=['R', 'F', 'M'])
rfm_data_centers


# In[100]:


# 这里划分类别用的是归一化后的数据，因为质心就是从归一化数据里建模得出的
# R、F、M的中位值都偏下，我们这里选用均值来判断每个质心分别时属于什么类型的客户
res_std_tb = pd.DataFrame(res_std)
res_std_tb.rename(columns={0:'R', 1:'F', 2:'M'}, inplace=True)
res_std_tb.iplot('box', mean=True)


# In[101]:


R_label = np.where(rfm_data_centers['R']>rfm_data_centers['R'].mean(),1,0)
F_label = np.where(rfm_data_centers['F']>rfm_data_centers['F'].mean(),1,0)     
M_label = np.where(rfm_data_centers['M']>rfm_data_centers['M'].mean(),1,0)

rfm_data_centers_label = pd.DataFrame([R_label, F_label, M_label]).T
rfm_data_centers_label.rename(columns={0:'R', 1:'F', 2:'M'}, inplace=True)
rfm_data_centers_label


# In[103]:


RFM_labels = pd.read_excel('./RFM_labels.xlsx', engine='openpyxl')
RFM_labels = RFM_labels.iloc[:,:-1]
RFM_labels


# In[104]:


cc = pd.merge(rfm_data_centers_label, RFM_labels, on=['R','F','M'], how='left')
cc['labels'] = cc.index
cc


# In[105]:


RFM_df['labels'] = clf.labels_
RFM_df


# In[106]:


# 在RFM_df后面添加客户类别列
RFM_df = pd.merge(RFM_df, cc[['labels', '客户级别']], on='labels', how='left')
RFM_df


# In[107]:


RFM_df.groupby('客户级别')['user_id'].count().iplot(kind='bar')


# In[ ]:




