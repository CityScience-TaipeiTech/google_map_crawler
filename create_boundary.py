import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

def create_grid_and_centroids(polygon: Polygon, grid_size: int):
    """
    切割多邊形為正方形並取得中心點。
    
    Args:
        polygon (Polygon): 要切割的多邊形。
        grid_size (int): 正方形的邊長大小。單位是 meter

    Returns:
        grid_gdf (GeoDataFrame): 包含正方形的 GeoDataFrame。
        centroid_gdf (GeoDataFrame): 包含正方形中心點的 GeoDataFrame。
    """
    # Get the bounds of the polygon
    minx, miny, maxx, maxy = polygon.bounds
    
    # Generate grid of squares
    x_coords = list(range(int(minx), int(maxx) + grid_size, grid_size))
    y_coords = list(range(int(miny), int(maxy) + grid_size, grid_size))
    
    squares = []
    centroids = []
    
    for x in x_coords:
        for y in y_coords:
            # Create square
            square = Polygon([
                (x, y),
                (x + grid_size, y),
                (x + grid_size, y + grid_size),
                (x, y + grid_size),
                (x, y)
            ])
            
            # Check intersection with polygon
            if polygon.intersects(square):
                # Add the square
                # 以防萬一可能會用到
                clipped_square = polygon.intersection(square)
                squares.append(clipped_square)
                
                # Add the centroid
                centroids.append(clipped_square.centroid)
    
    # Create GeoDataFrames for squares and centroids
    # 保存為 GeoJSON 或 SHP 文件
    # grid_gdf = gpd.GeoDataFrame(geometry=squares, crs="EPSG:4326")
    centroid_gdf = gpd.GeoDataFrame(geometry=centroids, crs="EPSG:3826")
    centroid_gdf = centroid_gdf.to_crs(4326)
    
    # 創建 GeoDataFrame 保存結果
    centroid_gdf.to_file("./data/target.geojson", driver="GeoJSON")
    
    
    # return grid_gdf, centroid_gdf


if __name__ == "__main__":
    gdf = gpd.read_file("./data/area.geojson")
    gdf = gdf.to_crs(epsg=3826) # 轉換成公尺單位
    print("==========================================================================")
    print(gdf.head())
    print(gdf.crs)
    print("==========================================================================")
    # 過濾出 Polygon 或 MultiPolygon 類型的幾何
    polygons = gdf[gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])]

    # 將 MultiPolygon 分解為單獨的 Polygon（如果需要）
    single_polygons = []
    for geom in polygons.geometry:
        if isinstance(geom, Polygon):
            single_polygons.append(geom)
        elif isinstance(geom, MultiPolygon):
            single_polygons.extend(geom.geoms)

    # print(single_polygons[0])

    create_grid_and_centroids(single_polygons[0], 100)