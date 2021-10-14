#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests


# In[9]:


def search():
    while True:
        # 输入关键词
        data_list = []
        code_name = input('请输入股票名称（q为退出）：')
        if code_name == 'q':
            print('已退出')
            break
        url = 'http://www.cninfo.com.cn/new/information/topSearch/query'
        # 向搜索接口发起请求，获取数据
        params = {
            'keyWord': code_name,
            'maxNum': 10
        }
        res = requests.post(url, params=params)
        # 过滤A股
        for i in res.json():
            if i['category'] == 'A股':
                data_list.append(i)
        # 判断是否无搜索结果，如果无搜索结果就重新循环
        if len(res.json()) == 0:
            print('无搜索结果')
            continue
        # 将序号与股票绑定，方便后续取出股票信息
        index = 1
        result_dict = {}
        for row in data_list:
            result_dict[str(index)] = row
            # 顺便打印股票名称和对应序号
            print("【序号-{}】 名称 - {} 代码 - {} ".format(index, row['zwjc'], row['code']))
            index += 1
        while True:
            choice = input('请选择序号(q为退出)：')
            # 如果选择的序号存在股票字典里，则返回结果
            if choice in result_dict:
                result = result_dict[choice]
                break
            # 如果是0则中止这个循环
            elif choice == 'q':
                break
            # 否则，打印提示
            else:
                print('输入了不存在的序号，请重新输入!')
        if result != None or len(result) != 0:
            break
    return result


# In[12]:


def select(code, orgid):

    # 获取报告类型
    while True:
        # 初始化一个类型字典
        category_dict = {
            "1": "category_ndbg_szsh;",
            "2": "category_bndbg_szsh;",
            "3": "category_rcjy_szsh;"
        }

        # 让用户选择需要下载的报告类型
        numbers = input('请输入搜索类型序号：1、年报 2、半年报 3、日常经营：（输入序号，如：1）')
        
        # 判断用户选择的类型是否存在，如果存在，则返回类型
        if category_dict.get(numbers) != None:
            category = category_dict[numbers]
            break
        # 否则，打印提示
        else:
            print('请输入提示内的搜索类型序号')
    # 获取时间
    start = input('请输入搜索范围起始时间(例如 2021-01-01)：')
    end = input('请输入搜索范围结束时间(例如 2021-07-01)：')

    # 根据股票代码的头文字，判断股票交易所信息
    if code[0] == '6':
        column = 'sse'
        plate = 'sh'
    else:
        column = 'szse'
        plate = 'sz'

    # 筛选报告
    # 设置初始页码
    page_num = 1    
    pdf_dict = {}
    while True:    
        
        # 设置报告筛选参数
        params = {
            'stock': '{},{}'.format(code, orgid),
            'tabName': 'fulltext',
            'pageSize': '30',
            'pageNum': str(page_num),
            'category': category,
            'seDate': '{}~{}'.format(start, end),
            'column': column,
            'plate': plate,
            'searchkey': '',
            'secid': '',
            'sortName': '',
            'sortType': '',
            'isHLtitle': ''
        }

        # 发起报告搜索请求
        r = requests.post('http://www.cninfo.com.cn/new/hisAnnouncement/query', params=params)
        r_json = r.json()

        # 判断是否搜索失败、或者无搜索结果，如果无结果则结束
        if r_json['announcements'] == None or len(r_json['announcements']) == 0:
            print('无搜索结果')
            break

        # 遍历搜索结果
        for i in r_json['announcements']:
            pdf_dict[i['announcementTitle']] = i['adjunctUrl']
        # 判断是否还有下一页数据，没有的话就结束循环
        if r_json['hasMore'] == False:
            print('没有下一页了')
            break
        # 让页数加一，开始下一轮循环
        else:
            page_num += 1
    return pdf_dict


# In[13]:


def download(pdf_dict):
    
    # 循环遍历筛选结果字典中的键
    for key in pdf_dict:

        # 拼接完整 url
        pdf_r = requests.get('http://static.cninfo.com.cn/' + pdf_dict[key])

        # 拼接文件后缀
        file_path = key + '.pdf'

        # 将报告内容写入文件，保存文件
        with open(file_path, 'wb') as f:
            f.write(pdf_r.content)

        # 打印下载提示
        print('{}打印成功'.format(file_path))


# In[ ]:


# 功能整合
def main():
    # 搜索股票，获取股票id信息等
    result = search()
    # 输入各个参数，筛选报告
    pdf_dict = select(result['code'], result['orgId'])
    # 下载报告
    download(pdf_dict)
main()

