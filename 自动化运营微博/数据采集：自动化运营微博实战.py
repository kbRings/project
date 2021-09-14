#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
import time
browser = webdriver.Chrome()
# 登录微博
def weibo_login(username, password):
        # 打开微博登录页
        browser.get('https://passport.weibo.cn/signin/login')
        browser.implicitly_wait(5)
        time.sleep(1)
        # 填写登录信息：用户名、密码
        browser.find_element_by_id("loginName").send_keys(username)
        browser.find_element_by_id("loginPassword").send_keys(password)
        time.sleep(1)
        # 点击登录
        browser.find_element_by_id("loginAction").click()
        time.sleep(1)
        browser.find_element_by_xpath('//div[@class="my-btn-box"]').click()
        time.sleep(1)
# 设置用户名、密码
username = '13060969205'
password = 'lkb130125'
weibo_login(username, password)


# In[4]:


def add_follow(uid):
        browser.get('https://m.weibo.com/u/' + str(uid))
        time.sleep(1)
        # browser.find_element_by_id("follow").click()
        follow_button = browser.find_element_by_xpath('//div[@class="btn_bed W_fl"]')
        follow_button.click()
        time.sleep(1)
# 每天学点心理学UID
uid = '1890826225'
add_follow(uid)


# In[9]:


# 给指定某条微博添加内容
def add_comment(weibo_url, content):
        browser.get(weibo_url)
        browser.implicitly_wait(5)
        content_textarea = browser.find_element_by_css_selector("textarea.W_input").clear()
        content_textarea = browser.find_element_by_css_selector("textarea.W_input").send_keys(content)
        time.sleep(2)
        comment_button = browser.find_element_by_css_selector(".W_btn_a").click()
        time.sleep(1)

# 发文字微博
def post_weibo(content):
        # 跳转到用户的首页
        browser.get('https://weibo.com')
        browser.implicitly_wait(5)
        # 点击右上角的发布按钮
        post_button = browser.find_element_by_css_selector("[node-type='publish']").click()
        # 在弹出的文本框中输入内容
        content_textarea = browser.find_element_by_css_selector("textarea.W_input").send_keys(content)
        time.sleep(2)
        # 点击发布按钮
        post_button = browser.find_element_by_css_selector("[node-type='submit']").click()
        time.sleep(1)
# 给指定的微博写评论
weibo_url = 'https://weibo.com/1890826225/HjjqSahwl'
content = 'Gook Luck!好运已上路!'
# 自动发微博
content = '每天学点心理学'
post_weibo(content)


# In[5]:


# 进行多个关注
uids = ['5489243430', '2028810631']
for uid in uids:
    add_follow(uid)
    time.sleep(2)


# In[ ]:




