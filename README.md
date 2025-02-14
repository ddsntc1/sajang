# 나도사장 커뮤니티 개발

<div align="center">
  <img src="https://github.com/user-attachments/assets/98a957ce-f7ce-4fb8-9f06-5c0ade52e98a" width="500px">
</div>

## 📌 프로젝트 개요
- **프로젝트 인원**: 1명
- **개발 기간**: 2024.11 ~ 2025.01
- **웹사이트**: [나도사장 커뮤니티 바로가기](https://www.nadosajang.com)

## 🛠 스택
- **OS**: Ubuntu 22.04
- **Backend**: Python, Django
- ~**Frontend**: Javascript, HTML/CSS~ 
- **Database**: MariaDB(MySQL)

## Directory

###  Directory Structure
<details>
  <summary>디렉토리 구조</summary>

  ```Linux
  .
  └── sajang
      ├── README.md
      └── sosang
          ├── board # 커뮤니티 이용 기능 // 게시글, 답변, 카테고리, 메세지, 북마크 등
          ├── common # 유저 신고, 검색, 프로필, 회원가입, 로그인 등에 관한 기능
          ├── config
  
          ├── media  # media와 static은 별도 hdd 마운트 폴더에 저장
          ├── static
  
          ├── manage.py
          ├── requirements.txt
          └── templates
              ├── base.html # 기본 틀
              ├── board # 광고, 게시글, 문의기능 등 관련 페이지
              ├── common # 로그인, 회원가입, 유저관리 기능 관련 페이지
              ├── form_errors.html
              ├── navbar.html # 네비게이션 바
              └── _sidebar.html # 사이드 바
  
  ```
</details>


## 📓 시스템 아키텍처
<div align="center">
  <img src="https://github.com/user-attachments/assets/475f59db-9208-4adb-95c4-c5b684143ba9" width="500px">
</div>

## 📜 ERD 
<div align="center">
  <img src="https://github.com/user-attachments/assets/fefefd19-9827-47bf-9a43-9dba6eef709c" width="500px">
</div>

