## 개요  
카카오맵 크롤링을 위해 만든 간단한 프로그램
입력값으로 카카오맵에 검색할 키워드가 필요하다.
출력은 검색 결과 모든 페이지의 정보들을 담은 csv 파일이다.
저장경로는 /data/~~.csv 이다.
column = [mac_name	address	address2	score	latitude	longitude]
mac_name : 맥도날드 지점명
address : 도로명 주소
address2 : 지번 주소
score : 평점
latitude : 경도
longitude : 위도

## 사용법
### kakaomap_crawl.py
카카오맵 검색결과를 크롤링하기 위한 코

터미널에 python kakaomap_crawl.py 를 입력한다.
input 에 원하는 검색어를 넣는다 ex) 맥드라이브

### address_convert.py
도로명/지번 주소를 경도/위도 좌표로 변환하기 위한 코드

위에 크롤링된 결과 파일의 경로를 file_path로 준다.
변환하는데 입력값으로 주어질 정보의 column명을 두번째 인자로 준다. 여기선 도로명주소

file_path = 'data/2020-06-23_12_13_맥드라이브.csv'
dataframe_loc_convert(file_path, 'address')
