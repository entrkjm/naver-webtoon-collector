"""
모바일 HTML 구조 분석 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bs4 import BeautifulSoup

html_file = Path('data/raw/2025-12-19/webtoon_chart.html')
if not html_file.exists():
    print(f"HTML 파일을 찾을 수 없습니다: {html_file}")
    sys.exit(1)

html = html_file.read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'lxml')

print("=== 모바일 HTML 구조 분석 ===\n")

# 1. 웹툰 리스트를 포함하는 컨테이너 찾기
containers = soup.find_all(['ul', 'div', 'section'], class_=lambda x: x and ('list' in str(x).lower() or 'webtoon' in str(x).lower() or 'item' in str(x).lower()))
print(f"1. 웹툰 관련 컨테이너: {len(containers)}개")
for i, container in enumerate(containers[:5]):
    classes = container.get('class', [])
    print(f"   {i+1}. {container.name}.{classes}")

# 2. 링크에서 titleId 찾기
links = soup.find_all('a', href=lambda x: x and 'titleId' in str(x))
print(f"\n2. titleId가 있는 링크: {len(links)}개")
if links:
    for link in links[:10]:
        href = link.get('href', '')
        title = link.get_text(strip=True)
        # titleId 추출
        if 'titleId=' in href:
            title_id = href.split('titleId=')[1].split('&')[0]
        else:
            title_id = "N/A"
        print(f"   - 제목: {title[:40]}, ID: {title_id}, href: {href[:60]}")

# 3. li 태그 찾기 (리스트 아이템)
list_items = soup.find_all('li')
print(f"\n3. li 태그: {len(list_items)}개")
webtoon_items = []
for item in list_items:
    # titleId가 있는 링크를 포함하는 li
    link = item.find('a', href=lambda x: x and 'titleId' in str(x))
    if link:
        text = item.get_text(strip=True)
        if len(text) > 5:
            webtoon_items.append(item)
            if len(webtoon_items) <= 5:
                print(f"   - {text[:50]}")

print(f"\n4. 웹툰 아이템으로 보이는 li: {len(webtoon_items)}개")

# 4. 특정 클래스나 ID 찾기
webtoon_elements = soup.find_all(attrs={'class': lambda x: x and any(keyword in str(x).lower() for keyword in ['webtoon', 'toon', 'item', 'list', 'rank'])})
print(f"\n5. 웹툰 관련 클래스: {len(webtoon_elements)}개")
if webtoon_elements:
    for elem in webtoon_elements[:10]:
        classes = elem.get('class', [])
        text = elem.get_text(strip=True)
        if len(text) > 3 and len(text) < 100:
            print(f"   - {elem.name}.{classes}: {text[:50]}")

# 5. 가장 유망한 선택자 추천
print("\n=== 추천 선택자 ===")
if webtoon_items:
    first_item = webtoon_items[0]
    print(f"li 태그 내부 구조:")
    print(f"  - {first_item}")
    print(f"\n추천 선택자:")
    print(f"  - 'li a[href*=\"titleId\"]' (링크 기반)")
    if first_item.get('class'):
        class_name = first_item.get('class')[0]
        print(f"  - 'li.{class_name}' (클래스 기반)")

