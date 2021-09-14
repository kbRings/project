#!/usr/bin/env python
# coding: utf-8

# # 封装元素定位函数

# Selenium中，经常需要复用某些元素获取的方法，毕竟每次都find_element_by_xxx有点太繁琐了。
# 
# 我们可以将一些常用的方法进行二次封装，在弄一个简单的函数出来。

# In[1]:


from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains

# 通过ID获取元素
def id(element):
    return driver.find_element_by_id(element)

# 通过CSS获取元素
def css(element):
    return driver.find_element_by_css_selector(element)

# 通过name获取
def name(element):
    return driver.find_element_by_name(element)


# In[8]:


from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains
driver = webdriver.Chrome('/Users/kbring/Documents/work/chromedriver')
driver.maximize_window()
driver.get('https://flight.tuniu.com/')

# 定义好出发和到达的城市
from_city = "SJZ"
to_city = "SY"
from_date = "2021-02-01"
id("J_FormDepartCity").clear()
id("J_FormDepartCity").send_keys(from_city)
time.sleep(2)
driver.find_element_by_xpath("//div[@class='autocomplete-suggestions'][1]/div[1]").click()
id("J_FormDestCity").send_keys(to_city)
time.sleep(2)
driver.find_element_by_xpath("//div[@class='autocomplete-suggestions'][2]/div[2]").click()

# 删除时间控件的只读属性
driver.execute_script("document.getElementById('J_FormDepartDate').removeAttribute('readonly')")
# 设置时间
id("J_FormDepartDate").clear()
id("J_FormDepartDate").send_keys(from_date)

# 点击一下其他位置，清除浮窗
ActionChains(driver).move_by_offset(0, 10).click().perform()

# 点击搜索按钮
time.sleep(1)
id("J_Search").click()


# ## 提炼函数到单独的文件中

# 函数写完之后，但是还是与所有的Python代码混合在一起，可以通过代码分层，将一些函数提炼到一个单独的文件中。
# 例如可以将上文写的几个函数提炼到一个function.py文件中。
# 
# 在pycharm中实现。

# ## Selenium代码异常

# 项目除了结构设计得合理以外，还需要较高的异常处理能力，在Selenium中，常见的异常都可以在下述网址直接查询到。
# 
# https://www.selenium.dev/selenium/docs/api/py/common/selenium.common.exceptions.html#module-selenium.common.exceptions

# 最常出现的还是NoSuchElementException，找不到元素，其它错误异常在代码编写过程中，碰到就去官网查询一下即可，
# 要记住编程是离不开手册的，工作多少年都一样。

# ## 补充知识点implicitly_wait()方法

# 在使用Selenium进行网页元素定位的时候，有时页面加载会慢，可能是受网速影响，也可能其它原因，
# 这时需要一个获取元素的等待时间，之前都是采用time模块的sleep方法实现的，
# 其实Selenium也给我们提供了一个自带的方法，即implicitly_wait智能等待，
# 设置一个全局智能等待的时间，那获取元素的时候，就会按照这个时间进行等待，例如设置了10秒，如果5秒元素获取到了，
# 那智能等待就等于5秒，反之，等待10秒还没有获取到，就会进行下一步计算或者报错。
# 
# 具体的代码格式如下：

# In[ ]:


# 设置全局等待时间为10秒
driver.implicitly_wait(10)
driver.get('https://flight.tuniu.com/')

