import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
import click


def extract_single_polygons(gdf):
    """
    從 GeoDataFrame 中提取單獨的 Polygon。

    Args:
        gdf (GeoDataFrame): 包含 Polygon 或 MultiPolygon 的 GeoDataFrame。

    Returns:
        list: 單獨的 Polygon 列表。
    """
    single_polygons = []
    for geom in gdf.geometry:
        if isinstance(geom, Polygon):
            single_polygons.append(geom)
        elif isinstance(geom, MultiPolygon):
            single_polygons.extend(geom.geoms)
    return single_polygons

@click.command()
@click.option('--size', '-s', 'grid_size', type=int, help='the size of grid', required=True)
@click.option('--input-file', '-i', 'input_file', type=click.Path(exists=True), help='the input file', required=True)
@click.option('--output-file', '-o', 'output_file', type=click.Path(), help='the output file', required=True)
def create_grid_and_centroids(grid_size: int, input_file: str, output_file: str)->None:
    """
    切割多邊形為正方形並取得中心點。
    
    Args:
        grid_size (int): 正方形的邊長大小。單位是 meter
        input_file (str): 輸入的 GeoJSON 文件路徑
        output_file (str): 輸出的 GeoJSON 文件路徑
    """
    
    gdf = gpd.read_file(input_file)
    gdf = gdf.set_crs(epsg=4326, allow_override=True) # 強置轉換以防萬一
    gdf = gdf.to_crs(epsg=3826) # 轉換成公尺單位

    # 提取單獨的 Polygon
    polygons = extract_single_polygons(gdf)

    squares = []
    centroids = []
    # Get the bounds of the polygon
    for polygon in polygons:
        minx, miny, maxx, maxy = polygon.bounds
    
        # Generate grid of squares
        x_coords = list(range(int(minx), int(maxx) + grid_size, grid_size))
        y_coords = list(range(int(miny), int(maxy) + grid_size, grid_size))
        
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
    centroid_gdf.to_file(output_file, driver="GeoJSON")
    
    
    # return grid_gdf, centroid_gdf


if __name__ == "__main__":

    # 過濾出 Polygon 或 MultiPolygon 類型的幾何
    # polygons = gdf[gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])]

    create_grid_and_centroids()