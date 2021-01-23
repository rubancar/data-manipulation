from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
#from selenium.webdriver import By


class Comment:
    def __init__(self, webElement, driver, writer, post, caption):
        self.element = webElement
        self.driver = driver
        self.writer = writer
        self.post = post
        self.caption = caption
        self.data = {'post':post, 'caption':caption}
    
    def extract_data(self):
        # first: position the element into the user view, to be able to perform actions over 
        # the elements
        self.driver.execute_script("arguments[0].scrollIntoView();", self.element)

        username = self.element.find_element_by_xpath("./div/li/div/div/div/a")
        username_text = username.get_attribute('href').replace("https://www.instagram.com/", "").replace("/", "")
        self.data['username'] = username_text
        self.data['idFatherComment'] = username_text
        
        datetime = self.element.find_element_by_xpath("./div/li/div/div/div[2]/div/div/a/time")
        datetime_text = datetime.get_attribute('datetime')
        self.data['date'] = datetime_text

        likes = self.element.find_element_by_xpath("./div/li/div/div/div[2]/div/div/button[1]")
        likes_text = likes.get_attribute('innerHTML')
        if likes_text.find("like") == -1:
            likes_text = '0 like'
        self.data['likesComment'] = likes_text

        comment = self.element.find_element_by_xpath("./div/li/div/div/div[2]/span")
        comment_text = comment.text

        self.writer.writerow(self.data)

        father_id = username_text
        try:
            button = self.element.find_element_by_xpath("./li/ul/li/div/button")
            print("Processing replies...")
            button.click()
            # find subcomments starting from the father element
            sub_comments = WebDriverWait(self.driver, 4).until(
                element_is_a_subcomment((By.XPATH, "./li/ul/div"), self.element)
            )
            print("Number of replies found %i" % len(sub_comments))
            self.extract_replys(sub_comments)
        except NoSuchElementException:
            pass
        except TimeoutException:
            print("There no replies to processes")
            pass

    
    def extract_replys(self, replies):
        for reply in replies:
            username = reply.find_element_by_xpath("./li/div/div/div[2]/h3/div")
            username_text = username.text

            datetime = reply.find_element_by_xpath("./li/div/div/div[2]/div/div/a/time")
            datetime_text = datetime.get_attribute('datetime')
           
            comment = reply.find_element_by_xpath("./li/div/div/div[2]/span")
            comment_text = comment.text

            likes = reply.find_element_by_xpath("./li/div/div/div[2]/div/div/button[1]")
            likes_text = likes.get_attribute('innerHTML')
            if likes_text.find("like") == -1:
                likes_text = '0 like'

            # ['post', 'caption', 'date', 'likesComment', 'idFatherComment', 'idChildComment', 'username']
            self.writer.writerow({'post':self.post, 'caption':self.caption, 'likesComment':likes_text, 'idChildComment':username_text, 'username':username_text})
            
    def write_comment_row(self):
        pass

        
        
class element_is_a_subcomment():
    def __init__(self, locator, base_element):
        self.locator = locator
        self.base_element = base_element


    def __call__(self, driver):
        subcomments = self.base_element.find_elements(*self.locator)
        return subcomments
        

driver = webdriver.Firefox()
driver.get("https://www.instagram.com/p/B166OkVBPJR/")
assert "Instagram" in driver.title

xpath_for_comments = "//ul[@class='Mr508'][position()>{}]"
commentList = driver.find_elements_by_xpath(xpath_for_comments.format(0))
print("Number of comments in current state: %i" % (len(commentList)))

button_more = driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/article/div[3]/div[1]/ul/li/div')
post = driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div/article/header/div[2]/div[1]/div[1]/a")
caption = driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span")
comments_processed = 0


with open('comments.csv', 'w', newline='') as csvfile:
    fieldnames = ['post', 'caption', 'date', 'likesComment', 'idFatherComment', 'idChildComment', 'username']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    #writer.writerow({'post': 'jdskahd', 'caption':'ksks', 'date':'satuwq', 'likesComment':'2 likes', 'idFatherComment':'asd', 'idChildComment':'asdas', 'username':'username'})

    while len(commentList) > 0:
        for element in commentList:
            comment = Comment(element, driver, writer, post.text, caption.text)
            comment.extract_data()

        try:
            driver.execute_script("arguments[0].scrollIntoView(false);", button_more)
            WebDriverWait(driver, 4).until(
                EC.visibility_of(button_more)
            )
            button_more.click()
            comments_processed = comments_processed + 12
            time.sleep(2)
            commentList = driver.find_elements_by_xpath(xpath_for_comments.format(comments_processed))
        except NoSuchElementException:
            print("No more elements to process")
            break
        
driver.close()





