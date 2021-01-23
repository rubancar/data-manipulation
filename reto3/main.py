from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import sys


def extract_user_url(element, locator, parser):
  try:
    user = element.find_element(*locator)
    user_text = user.get_attribute("href")
    user_text = parser.split(user_text)[0]
    print("user %s" % user_text)
    return user_text
  except NoSuchElementException:
    return None

if __name__ == "__main__":
    if len(sys.argv) is not 4:
      print("Missmatch number of arguments")
    user = sys.argv[1]
    password = sys.argv[2]
    link = sys.argv[3]

    # create driver to control Firefox window
    driver = webdriver.Firefox()
    driver.get(link)
    assert "Facebook" in driver.title
    time.sleep(3)
    textbox_username = driver.find_element_by_name('email')
    textbox_pass = driver.find_element_by_name("pass")
    login_button = driver.find_element_by_xpath("//form[@id='login_form']/div/div[3]/div/div/div/span/span")
    textbox_username.send_keys(user)
    textbox_pass.send_keys(password)
    time.sleep(3)
    login_button.click()
    WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div/div[1]'))
    )
    time.sleep(4)
    comments = driver.find_elements_by_xpath("/html/body/div[1]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[1]/div[4]/ul/li")
    print("number of comments %i" % len(comments))
    regular_expression = re.compile("[&?]comment_id=")
    for comment in comments:
      user_url = extract_user_url(comment, (By.XPATH, "./div/div/div/div/a"), regular_expression)

    # now, we have to check the reactions
    reaction_button = driver.find_element_by_xpath("//div[@class='bp9cbjyn j83agx80 buofh1pr ni8dbmo4 stjgntxs']")
    reaction_button.click()
    reactions = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, "//div[@class='q5bimw55 rpm2j7zs k7i0oixp gvuykj2m j83agx80 cbu4d94t ni8dbmo4 eg9m0zos l9j0dhe7 du4w35lb ofs802cu pohlnb88 dkue75c7 mb9wzai9 l56l04vs r57mb794 kh7kg01d c3g1iek1 otl40fxz cxgpxx05 rz4wbd8a sj5x9vvc a8nywdso']"))
    )
    print(" reaction_button %s" % reactions)
    time.sleep(3)
    users_reaction = reactions.find_elements_by_xpath("./div/div")
    print(" users %i " % len(users_reaction))

    parser_reaction = re.compile("\?__tn__")
    for user_reaction in users_reaction:
      user_url = extract_user_url(user_reaction, (By.XPATH, "./div/div/div[2]/div/div/div/div[1]/span/div/a"), parser_reaction)
    driver.quit()
