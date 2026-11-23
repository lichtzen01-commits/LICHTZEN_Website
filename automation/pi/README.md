# PI 작성 도구

회사 원본 인보이스 엑셀(작성창 + PI + CI,PL)을 복사해 주문 정보를 넣고 PDF까지 만든다.
원본 양식 파일, 주문 정보(JSON), 고객별 Part# 표는 거래처 정보가 있어 이 공개 저장소에 두지 않는다.

| 파일 | 하는 일 |
|---|---|
| `fill_original.py 원본.xlsx 출력.xlsx 주문.json` | 작성창·PI·CI,PL에 주문 정보를 넣는다. 파일 내부(XML)를 직접 고쳐서 로고·서명 이미지와 서식을 그대로 둔다. 쉬핑마크 이미지를 MARKS 칸에 넣는다 |
| `make_mark.py 쉬핑마크.pptx PO번호 출력.pptx 출력.png` | 고객 쉬핑마크 PPT 1번 슬라이드에 `PO NO. : …` 줄을 넣는다(박스 부착용) |
| `make_mark_cell.py 받는곳 목적지 PO번호 출력.png 비율` | MARKS 칸(좁고 긴 칸)에 맞춘 세로형 쉬핑마크 이미지 |
| `export_pdf.py 엑셀 PI 출력.pdf` | 한 시트만 A4 PDF로(쪽번호 1부터). 원본 파일은 바꾸지 않는다 |
| `fonts.conf` | 원본의 Microsoft 글꼴(Tahoma, 돋움, 굴림, 맑은 고딕)을 무료 글꼴로 대신하는 설정. `~/.config/fontconfig/fonts.conf`에 둔다 |

PDF가 회사 PC 엑셀과 같게 나오려면 서버에 다음이 있어야 한다: LibreOffice, `fonts-dejavu-extra`, `fonts-noto-cjk`, 위 `fonts.conf`.
(나눔고딕은 LibreOffice에서 칸 안의 줄바꿈을 무시하는 경우가 있어 쓰지 않는다.)

주문.json 예시 (값은 가짜):
```json
{"invoice": "FX#999", "invoice_date": "2026-01-05", "po_no": "Order20260102", "po_date": "2026-01-02",
 "departure": "2026-01-15", "mark_png": "mark_cell.png",
 "non_commercial_note": "Item No. 3: No commercial value - free replacement",
 "items": [{"desc": "1. UV LAMP (MODEL-A)\n   PART#XXXX", "qty": 2, "price": 100},
           {"desc": "3. UV LAMP (MODEL-C)\n   PART#YYYY", "qty": 1, "price": 50, "non_commercial": true}]}
```
