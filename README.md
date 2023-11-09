# Narajangteo-Crawler

간단한 나라장터 크롤링 스크립트입니다. 입찰 공고에 대한 간단한 정보와 비용을 쿼리하여 엑셀파일로 저장합니다.

## 필요 라이브러리

- requests == 2.31.0
- BeautifulSoup4 == 4.12.2
- tqdm == 4.66.1
- XlsxWriter == 3.1.9

## 사용방법

`if __name__ == "__main__":` 아래의 다음의 코드들을 수정하고 `python main.py`로 실행하십시오.
실행하기 전 `requirements.txt`의 라이브러리들은 모두 설치되어 있어야 합니다.

```python
if __name__ == '__main__':
    to_date = datetime.datetime(2023, 11, 9)  # 검색 끝 날짜
    from_date = datetime.datetime(2021, 1, 1)  # 검색 시작 날짜
    keyword = "사업"  # 검색어
```

결과물로는 `list.xlsx` 파일이 루트경로에 저장될 것입니다.

## 라이센스

The Unlicense.