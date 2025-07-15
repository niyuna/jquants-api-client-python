---
description: 四半期の財務諸表情報が取得できます
---

# 財務諸表(BS/PL)(/fins/fs\_details)

### APIの概要

上場企業の四半期毎の財務情報における、貸借対照表、損益計算書に記載の項目を取得することができます。

### 本APIの留意点

{% hint style="info" %}
**FinancialStatement（財務諸表の各種項目）について**

* EDINET XBRLタクソノミ本体（label情報）を用いてコンテンツを作成しています。
* FinancialStatementに含まれる冗長ラベル（英語）については、下記サイトよりご確認ください。\
  [https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html)\
  年度別に公表されているEDINETタクソノミページに、「勘定科目リスト」（会計基準：日本基準）及び「国際会計基準タクソノミ要素リスト」（会計基準：IFRS） が掲載されています。会計基準別に以下のとおりデータを提供しています。
  * 会計基準が日本基準の場合、「勘定科目リスト」の各シートのE列「冗長ラベル（英語）」をキーとし、その値とセットで提供しています。
  * 会計基準がIFRSの場合、「国際会計基準タクソノミ要素リスト」の各シートのD列「冗長ラベル（英語）」をキーとし、その値とセットで提供しています。

**提出者別タクソノミについて**

* EDINETタクソノミには存在しない提出者別タクソノミで定義される企業独自の項目は、本APIの提供対象外となります。
{% endhint %}

{% hint style="warning" %}
* 三井海洋開発（銘柄コード62690）は、2022年2月以降の決算短信の連結財務諸表及び連結財務諸表注記を米ドルにより表示されています。そのため、本サービスの当該銘柄の対象の財務諸表情報についても米ドルでの提供となります。
{% endhint %}

### パラメータ及びレスポンス

## 四半期の財務諸表情報を取得することができます

<mark style="color:blue;">`GET`</mark> `https://api.jquants.com/v1/fins/fs_details`

リクエストパラメータにcode（銘柄コード）またはdate（開示日）を入力する必要があります。

\*は必須項目

#### Query Parameters

| Name            | Type   | Description                                                          |
| --------------- | ------ | -------------------------------------------------------------------- |
| code            | String | <p>4桁もしくは5桁の銘柄コード</p><p>ex.86970 or 8697</p>                         |
| date            | String | ex.2022-01-05 or 20220105                                            |
| pagination\_key | String | <p>検索の先頭を指定する文字列</p><p>過去の検索で返却された<code>pagination_key</code>を設定</p> |

#### Headers

| Name                                            | Type   | Description |
| ----------------------------------------------- | ------ | ----------- |
| Authorization<mark style="color:red;">\*</mark> | String | アクセスキー      |

{% tabs %}
{% tab title="200: OK " %}
```json
{
    "fs_details": [
        {
              "DisclosedDate": "2023-01-30",
              "DisclosedTime": "12:00:00",
              "LocalCode": "86970",
              "DisclosureNumber": "20230127594871",
              "TypeOfDocument": "3QFinancialStatements_Consolidated_IFRS",
              "FinancialStatement": {
                    "Goodwill (IFRS)": "67374000000",
                    "Retained earnings (IFRS)": "263894000000",
                    "Operating profit (loss) (IFRS)": "51765000000.0",
                    "Previous fiscal year end date, DEI": "2022-03-31",
                    "Basic earnings (loss) per share (IFRS)": "66.76",
                    "Document type, DEI": "四半期第３号参考様式　[IFRS]（連結）",
                    "Current period end date, DEI": "2022-12-31",
                    "Revenue - 2 (IFRS)": "100987000000.0",
                    "Industry code when consolidated financial statements are prepared in accordance with industry specific regulations, DEI": "CTE",
                    "Profit (loss) attributable to owners of parent (IFRS)": "35175000000.0",
                    "Other current liabilities - CL (IFRS)": "8904000000",
                    "Share of profit (loss) of investments accounted for using equity method (IFRS)": "1042000000.0",
                    "Current liabilities (IFRS)": "78852363000000",
                    "Equity attributable to owners of parent (IFRS)": "311103000000",
                    "Whether consolidated financial statements are prepared, DEI": "true",
                    "Non-current liabilities (IFRS)": "33476000000",
                    "Other expenses (IFRS)": "58000000.0",
                    "Income taxes payable - CL (IFRS)": "5245000000",
                    "Filer name in English, DEI": "Japan Exchange Group, Inc.",
                    "Non-controlling interests (IFRS)": "8918000000",
                    "Capital surplus (IFRS)": "38844000000",
                    "Finance costs (IFRS)": "71000000.0",
                    "Other current assets - CA (IFRS)": "4217000000",
                    "Property, plant and equipment (IFRS)": "11277000000",
                    "Deferred tax liabilities (IFRS)": "419000000",
                    "Other components of equity (IFRS)": "422000000",
                    "Current fiscal year start date, DEI": "2022-04-01",
                    "Type of current period, DEI": "Q3",
                    "Cash and cash equivalents (IFRS)": "91135000000",
                    "Share capital (IFRS)": "11500000000",
                    "Retirement benefit asset - NCA (IFRS)": "9028000000",
                    "Number of submission, DEI": "1",
                    "Trade and other receivables - CA (IFRS)": "18837000000",
                    "Liabilities and equity (IFRS)": "79205861000000",
                    "EDINET code, DEI": "E03814",
                    "Equity (IFRS)": "320021000000",
                    "Security code, DEI": "86970",
                    "Other financial assets - CA (IFRS)": "112400000000",
                    "Other financial assets - NCA (IFRS)": "2898000000",
                    "Income taxes receivable - CA (IFRS)": "5529000000",
                    "Investments accounted for using equity method (IFRS)": "18362000000",
                    "Other non-current assets - NCA (IFRS)": "6240000000",
                    "Previous fiscal year start date, DEI": "2021-04-01",
                    "Filer name in Japanese, DEI": "株式会社日本取引所グループ",
                    "Deferred tax assets (IFRS)": "2862000000",
                    "Trade and other payables - CL (IFRS)": "5037000000",
                    "Bonds and borrowings - CL (IFRS)": "33000000000",
                    "Current fiscal year end date, DEI": "2023-03-31",
                    "XBRL amendment flag, DEI": "false",
                    "Non-current assets (IFRS)": "182317000000",
                    "Retirement benefit liability - NCL (IFRS)": "9214000000",
                    "Amendment flag, DEI": "false",
                    "Assets (IFRS)": "79205861000000",
                    "Income tax expense (IFRS)": "15841000000.0",
                    "Report amendment flag, DEI": "false",
                    "Profit (loss) (IFRS)": "35894000000.0",
                    "Operating expenses (IFRS)": "50206000000.0",
                    "Intangible assets (IFRS)": "36324000000",
                    "Profit (loss) before tax from continuing operations (IFRS)": "51736000000.0",
                    "Liabilities (IFRS)": "78885839000000",
                    "Accounting standards, DEI": "IFRS",
                    "Bonds and borrowings - NCL (IFRS)": "19972000000",
                    "Finance income (IFRS)": "43000000.0",
                    "Profit (loss) attributable to non-controlling interests (IFRS)": "719000000.0",
                    "Comparative period end date, DEI": "2021-12-31",
                    "Current assets (IFRS)": "79023543000000",
                    "Other non-current liabilities - NCL (IFRS)": "3870000000",
                    "Other income (IFRS)": "458000000.0",
                    "Treasury shares (IFRS)": "-3556000000"
              }
        }
    ],
    "pagination_key": "value1.value2."
}
```
{% endtab %}

{% tab title="400: Bad Request " %}
```json
{
　　　　　　　　"message": "This API requires at least 1 parameter as follows; 'date','code'."
}
```
{% endtab %}

{% tab title="401: Unauthorized " %}
```json
{
　　　　　　　　"message": "The incoming token is invalid or expired."
}
```
{% endtab %}

{% tab title="403: Forbidden " %}
```json
{
　　　　　　　　"message": <Error Message>
}
```
{% endtab %}

{% tab title="500: Internal Server Error " %}
```json
{
　　　　　　　　"message": "Unexpected error. Please try again later."
}
```
{% endtab %}

{% tab title="413: Payload Too Large " %}
```json
{
    "message": "Response data is too large. Specify parameters to reduce the acquired data range."
}
```
{% endtab %}
{% endtabs %}

### データ項目概要

<table><thead><tr><th width="196">変数名</th><th width="118">変数名2</th><th width="137">説明</th><th width="91">型</th><th>備考</th></tr></thead><tbody><tr><td>DisclosedDate</td><td></td><td>開示日</td><td>String</td><td></td></tr><tr><td>DisclosedTime</td><td></td><td>開示時刻</td><td>String</td><td></td></tr><tr><td>LocalCode</td><td></td><td>銘柄コード（5桁）</td><td>String</td><td></td></tr><tr><td>DisclosureNumber</td><td></td><td>開示番号</td><td>String</td><td>APIから出力されるjsonは開示番号で昇順に並んでいます。</td></tr><tr><td>TypeOfDocument</td><td></td><td>開示書類種別</td><td>String</td><td><a href="statements/typeofdocument">開示書類種別一覧</a></td></tr><tr><td>FinancialStatement</td><td></td><td>財務諸表の各種項目</td><td>Map</td><td></td></tr><tr><td></td><td>冗長ラベル（英語）</td><td>財務諸表の値</td><td>String</td><td>XBRLタグと紐づく冗長ラベル（英語）とその値</td></tr></tbody></table>

### APIコールサンプルコード

{% tabs %}
{% tab title="Curl" %}
{% code overflow="wrap" %}
```bash
idToken=<YOUR idToken> && curl https://api.jquants.com/v1/fins/fs_details?code=86970&date=20230130 -H "Authorization: Bearer $idToken" 
```
{% endcode %}
{% endtab %}

{% tab title="Python" %}
{% code overflow="wrap" %}
```python
import requests
import json

idToken = "YOUR idToken"
headers = {'Authorization': 'Bearer {}'.format(idToken)}
r = requests.get("https://api.jquants.com/v1/fins/fs_details?code=86970&date=20230130", headers=headers)
r.json()
```
{% endcode %}
{% endtab %}
{% endtabs %}
