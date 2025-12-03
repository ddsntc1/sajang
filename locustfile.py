from locust import HttpUser, task, between
import os, random, urllib.parse, re

csrf_re = re.compile(r'name="csrfmiddlewaretoken" value="([^"]+)"')

class WebsiteTest(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # 로그인 페이지에서 CSRF 토큰을 얻은 뒤 로그인 POST
        login_page = self.client.get("/common/login/", name="login_form")
        match = csrf_re.search(login_page.text)
        if not match:
            # 페이지에 토큰이 없으면 로그인 못 하므로 바로 반환
            return

        token = match.group(1)
        self.client.post(
            "/common/login/",
            data={
                "username": "test01",
                "password": "test01",
                "csrfmiddlewaretoken": token,
            },
            headers={"Referer": "/common/login/"},
            name="login",
        )
    
    @task(2)
    def search(self):
        keyword = random.choice(["안녕", "하이", "카페"])
        q = urllib.parse.quote(keyword)
        self.client.get(f"/board/search/?q={q}", name="search")
    
    @task(1)
    def all_question_list(self):
        self.client.get("/board/category/all/")
    
    @task(1)
    def free_question_list(self):
        self.client.get("/board/category/hot/")
    
    @task(1)
    def message_list(self):
        self.client.get("/board/messages/")
        
    @task(1)
    def send_message(self):
        # 메시지 작성 폼에서 CSRF 토큰 확보
        res = self.client.get("/board/messages/send/")
        match = csrf_re.search(res.text)
        if not match:
            return

        token = match.group(1)
        content = f"hello from locust #{random.randint(1, 9999)}"
        self.client.post(
            "/board/messages/send/",
            data={"receiver": "카페", "content": content, "csrfmiddlewaretoken": token},
            headers={"Referer": "/board/messages/send/"},
            name="send_message",
        )
