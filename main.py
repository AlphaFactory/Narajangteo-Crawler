import datetime
import re
from urllib.parse import quote

import requests
import xlsxwriter
from bs4 import BeautifulSoup
from tqdm import tqdm


def str2int(src: str):
    try:
        return int(re.search("[0-9,]+", src).group().replace(",", ""))
    except:
        return 0


def load_list(search_word: str, from_date: str, to_date: str):
    search_word = quote(search_word, encoding="cp949")
    from_date = quote(from_date, encoding="cp949")
    to_date = quote(to_date, encoding="cp949")
    full_url = (f"https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?bidNm={search_word}&bidSearchType=1"
                f"&fromBidDt={from_date}&toBidDt={to_date}"
                f"&regYn=Y&searchDtType=1&searchType=1&setMonth1=3&radOrgan=1"
                f"&maxPageViewNoByWshan=1&recordCountPerPage=100&currentPageNo=1"
                f"&area=&areaNm=&budgetCompare=&detailPrdnm=&detailPrdnmNo=&downBudget=&fromOpenBidDt=&industry="
                f"&industryCd=&instNm=&instSearchRangeType=&intbidYn=&orgArea=&procmntReqNo=&refNo=&strArea="
                f"&taskClCds=&toOpenBidDt=&upBudget=")
    response = requests.get(full_url, allow_redirects=True)

    soup = BeautifulSoup(response.content.decode("cp949"), "html.parser")
    rows = [row for row in soup.select("#resultForm > div.results > table > tbody > tr")]
    return rows


def load_price(url):
    price_response = requests.get(url)
    price_soup = BeautifulSoup(price_response.content.decode(encoding="cp949"), "html.parser")

    price_rows = [a for a in price_soup.select("#container table tr")]
    price_rows2 = []
    for prow in price_rows:
        ths = [h for h in prow.select("th")]
        tds = [d for d in prow.select("td")]
        for th, td in zip(ths, tds):
            price_rows2.append((th.get_text().strip(), td.get_text().strip()))
    price_rows = price_rows2

    price1 = price2 = price3 = ""
    for header, text in price_rows:
        if header.startswith("사업금액"):
            price1 = text
        if header.startswith("배정예산"):
            price2 = text
        if header.startswith("추정가격"):
            price3 = text

    return str2int(price1), str2int(price2), str2int(price3)


def save(rows, dst: str):
    book = xlsxwriter.Workbook(dst)
    sheet = book.add_worksheet("목록")

    # 헤더
    headers = [
        "업무", "공고번호", "차수", "분류", "공고명", "공고기관",
        "수요기관", "계약방법", "입력일시", "입찰마감일시", "공동수급", "투찰",
        "사업금액", "배정예산", "추정가격"
    ]

    for i, header in enumerate(headers):
        sheet.write(0, i, header)

    for i, row in enumerate(tqdm(rows), 1):
        cells = row.select("td")
        sheet.write(i, 0, cells[0].get_text())

        num1, num2 = cells[1].get_text().split("-")
        sheet.write(i, 1, num1)
        sheet.write(i, 2, num2)
        sheet.write(i, 3, cells[2].get_text())
        sheet.write(i, 4, cells[3].get_text())
        sheet.write(i, 5, cells[4].get_text())
        sheet.write(i, 6, cells[5].get_text())
        sheet.write(i, 7, cells[6].get_text())

        date1, date2 = cells[7].get_text().split("(")
        sheet.write(i, 8, date1)
        sheet.write(i, 9, date2[:-1])

        sheet.write(i, 10, cells[8].get_text())
        sheet.write(i, 11, cells[9].get_text())

        # 가격 쿼리해오기
        href = cells[1].select("a")[0].get("href")
        price1, price2, price3 = load_price(href)

        sheet.write(i, 12, price1)
        sheet.write(i, 13, price2)
        sheet.write(i, 14, price3)
    book.close()


if __name__ == '__main__':
    # 입력 변수
    to_date = datetime.datetime(2023, 11, 9)
    from_date = datetime.datetime(2021, 1, 1)
    keyword = "사업"

    date_ranges = []
    while (True):
        next_date = from_date + datetime.timedelta(days=30)
        if next_date > to_date:
            date_ranges.append((from_date, to_date))
            break
        else:
            date_ranges.append((from_date, next_date))
        from_date += datetime.timedelta(days=31)
    date_ranges = [(d1.strftime("%Y/%m/%d"), d2.strftime("%Y/%m/%d")) for d1, d2 in date_ranges]

    rows = []
    for from_date, to_date in tqdm(date_ranges):
        rows.extend(load_list(keyword, from_date, to_date))
    save(rows, "list.xlsx")
