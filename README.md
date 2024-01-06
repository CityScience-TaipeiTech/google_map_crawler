# Google Map Crawler

## 環境

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 執行

1. 一次抓取一個類別的所有地點

```shell
python3 taipei_v1.py
```

2. 一次抓取多個類別的所有地點（平行處理：一次處理 CPU 個數的類別）

```shell
python3 taipei_v2.py
```

3. 一次抓取所有類別的所有地點（平行處理）

```shell
python3 taipei_v2.py
```

> ⚠️ 會一次開啟 96 個瀏覽器

## 資料儲存

1. 儲存位置

```shell
./taipei/<type>.json
```

2. JSON 格式

```json
{
  "library": [
    {
      "name": "財團法人中華經濟研究院圖書館",
      "a": "https://www.google.com/maps/place/%E8%B2%A1%E5%9C%98%E6%B3%95%E4%BA%BA%E4%B8%AD%E8%8F%AF%E7%B6%93%E6%BF%9F%E7%A0%94%E7%A9%B6%E9%99%A2%E5%9C%96%E6%9B%B8%E9%A4%A8/data=!4m7!3m6!1s0x3442aa2495fbd017:0xa448a87f238e4a0d!8m2!3d25.0159201!4d121.5469296!16s%2Fg%2F1q62kbc9d!19sChIJF9D7lSSqQjQRDUqOI3-oSKQ?authuser=0&hl=zh-TW&rclk=1",
      "keyword": "library",
      "category": "圖書館",
      "lat": 25.0159201,
      "lon": 121.5469296
    },
    ...
  ]
}
```
