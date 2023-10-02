import random
import time
import re
import requests
import bs4


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, compress",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "Keep-Alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0",
}


def download_page(page_url, headers):
    page_obj = requests.get(page_url, headers=headers)
    bs4_obj = bs4.BeautifulSoup(page_obj.text, "lxml")
    bs4_page_obj_list = [bs4_obj]
    url_set = set()
    paginator_eles = bs4_obj.find("div", attrs={"class": "paginator"})
    if paginator_eles:
        for a_ele in paginator_eles.find_all("a"):
            url_set.add(a_ele.attrs.get("href"))
    for url in url_set:
        print(f"下载分页{url}")
        page_obj = requests.get(url, headers=headers)
        bs4_page_obj = bs4.BeautifulSoup(page_obj.text, "lxml")
        bs4_page_obj_list.append(bs4_page_obj)

    return bs4_page_obj_list


def fetch_emails(bs4_page_obj_list):
    mail_list = []
    for bs4_obj in bs4_page_obj_list:
        comment_eles = bs4_obj.find_all("div", attrs={"class": "reply-doc"})
        for ele in comment_eles:
            comment_text = ele.find("p", attrs={"class": "reply-content"}).text
            pub_time = ele.find("span", attrs={"class": "pubtime"}).text
            re_pattern = re.compile(r"\w+@\w+\.\w+", flags=re.ASCII)
            email_addr = re.search(re_pattern, comment_text)
            if email_addr:
                print(pub_time, email_addr.group())
                mail_list.append((pub_time, email_addr.group()))
    print(f"下载了{len(mail_list)}个邮件。。。")
    return mail_list


def download_group_page_list(page_url, headers):
    total_mail_list = []
    page_obj = requests.get(page_url, headers=headers)
    bs4_obj = bs4.BeautifulSoup(page_obj.text, "lxml")

    bbs_eles = bs4_obj.find_all("td", attrs={"class": "title"})
    for td_ele in bbs_eles:
        a_ele = td_ele.find("a")
        reply_count = td_ele.find_next_sibling("td", attrs={"class": "r-count"}).text
        if reply_count:
            reply_count = int(reply_count)
            if reply_count > 3:
                random_pause = round(random.uniform(0, 5), 2)
                print(
                    f"sleep {random_pause} sec, downloading...",
                    [a_ele.attrs.get("href")],
                    a_ele.text,
                )
                time.sleep(random_pause)
                bs4_page_objs = download_page(a_ele.attrs.get("href"), headers=headers)
                total_mail_list.extend(fetch_emails(bs4_page_objs))
    return total_mail_list


if __name__ == "__main__":
    total_mail_addr = []
    time_start = time.time()
    for page_num in range(0, 1000, 25):
        try:
            mail_list = download_group_page_list(
                f"https://www.douban.com/group/python/discussion?start={page_num}",
                headers,
            )
            total_mail_addr.extend(mail_list)
            print("总地址数：", len(total_mail_addr))
        except Exception as e:
            print("Some error:", e)
    with open("python_qq_list02", "w") as f:
        for pub_time, mail in total_mail_addr:
            f.write(f"{pub_time},{mail}\n")
    print(f"cost time: {time.time() - time_start}")
