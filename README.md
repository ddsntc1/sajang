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


## 추후 개선점

- 웹 소켓 기능을 통한 실시간 채팅 기능구현 // 현재는 DB 입출력 방식으로 소통 확인을 위해 새로고침 필요
- Prometheus로 로그 수집 예정 // 현재 Datadog 체험판을 적용, 로그 확인은 터미널에서 확인가능
- 디자인 개선
- 커뮤니티 활성화 이후 서비스 유지보수 작업

- 추가 기능 확장 : 자영업에 필요한 세금, 지원 정책에 관한 뉴스 크롤링 // 세무사 소개 서비스

