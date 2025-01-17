# Google Map Crawler

## 環境

```shell
pyenv local 3.12.5
poetry install
poetry env activate
source ./venv/activate/bin
```
## .env 檔案內容
```shell 
DB_PASSWORD=
```

## Polygon 轉換為 point
```shell
sh get_points_from_polygon.sh
```
> 要先將想轉化的區域存成 area.geojson 並放到 data folder 中
> 最後會產出 target.geojson 這是給下一步驟使用的


## 執行 Google map crawler
一次抓取所有類別的所有地點（平行處理）
```shell
sh start_fetch_poi.sh
```

> ⚠️ 會一次開啟 96 個瀏覽器

## 資料儲存

1. 儲存位置

```shell
./output/<type>.json
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
