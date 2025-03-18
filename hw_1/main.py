import json
import csv
import collections
import heapq
import matplotlib.pyplot as plt
import pandas as pd

def load_data(file_path):
    """讀取JSON檔案並返回數據"""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def build_adjacency_matrix(data):
    """從數據建立鄰接矩陣"""
    nodes = data['nodes']
    links = data['links']
    
    # 建立節點索引映射
    node_names = [node['name'] for node in nodes]
    node_indices = {name: i for i, name in enumerate(node_names)}
    
    # 創建空的鄰接矩陣
    n = len(nodes)
    adj_matrix = [[0 for _ in range(n)] for _ in range(n)]
    
    # 根據links填充鄰接矩陣
    for link in links:
        source = link['source']
        target = link['target']
        value = link['value']
        adj_matrix[source][target] = value
        adj_matrix[target][source] = value  # 無向圖需要對稱
    
    return adj_matrix, node_names


def save_matrix_to_csv(adj_matrix, node_names, file_path):
    """使用原生方法將鄰接矩陣儲存成CSV檔案，不包含標頭"""
    
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in adj_matrix:
            csv_writer.writerow([1 if i!=0 else 0 for i in row])
    print(f"鄰接矩陣已成功儲存至 {file_path}")

def shortest_path(graph, start):
    """使用Dijkstra算法計算從一個節點到其他所有節點的最短路徑"""
    # 初始化距離、前驅節點和路徑數量
    dist = {node: float('infinity') for node in range(len(graph))}
    pred = {node: [] for node in range(len(graph))}
    paths = {node: 0 for node in range(len(graph))}
    
    dist[start] = 0
    paths[start] = 1
    
    # 優先隊列
    pq = [(0, start)]
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        # 如果已經找到更短的路徑，則跳過
        if current_dist > dist[current]:
            continue
        
        # 探索相鄰節點
        for neighbor in range(len(graph)):
            if graph[current][neighbor] > 0:  # 存在邊
                weight = graph[current][neighbor]
                distance = current_dist + 1/weight  # 權重越大，距離越短
                
                # 如果找到更短的路徑
                if distance < dist[neighbor]:
                    dist[neighbor] = distance
                    pred[neighbor] = [current]
                    paths[neighbor] = paths[current]
                    heapq.heappush(pq, (distance, neighbor))
                # 如果找到相同長度的路徑
                elif distance == dist[neighbor]:
                    pred[neighbor].append(current)
                    paths[neighbor] += paths[current]
    
    return dist, pred, paths

def calculate_dependency(graph, source, distances, predecessors, path_counts):
    """計算一個節點對其他節點對的依賴性"""
    # 初始化依賴值
    dependency = {node: 0 for node in range(len(graph))}
    
    # 按距離從遠到近的順序處理節點
    nodes = sorted([(distances[node], node) for node in range(len(graph)) if node != source], reverse=True)
    
    for _, node in nodes:
        # 計算節點的依賴性
        for pred in predecessors[node]:
            dependency[pred] += (path_counts[pred] / path_counts[node]) * (1 + dependency[node])
    
    return dependency

def calculate_betweenness_centrality(adj_matrix):
    """計算 betweenness centrality"""
    n = len(adj_matrix)
    betweenness = {node: 0 for node in range(n)}
    
    # 對每個節點
    for s in range(n):
        # 計算最短路徑
        distances, predecessors, path_counts = shortest_path(adj_matrix, s)
        # 計算依賴值
        dependency = calculate_dependency(adj_matrix, s, distances, predecessors, path_counts)
        
        # 累加betweenness
        for v in range(n):
            if v != s:
                betweenness[v] += dependency[v]
    
    # 歸一化 (對於無向圖除以2)
    for node in betweenness:
        betweenness[node] /= 2
    
    # 歸一化為[0,1]的範圍
    if n > 2:
        normalization_factor = (n-1) * (n-2)
        for node in betweenness:
            betweenness[node] /= normalization_factor
    
    return betweenness

def get_top_k_betweenness(adj_matrix,k = 10):
    """計算中介中心性並返回前k名的節點"""
    # 默認k為10，如果需要其他數量可以通過參數傳入
    
    # 計算betweenness中心性
    betweenness = calculate_betweenness_centrality(adj_matrix)
    
    # 將結果與節點名稱關聯
    result = [(node, value) for node, value in betweenness.items()]
    
    # 根據中介中心性排序
    result.sort(key=lambda x: x[1], reverse=True)
    
    # 返回前k個結果
    return result[:k]
    

def main():
    # 讀取資料
    file_path = "/Users/ponywen/Documents/projects/SMA/hw_1/starwars-full-interactions-allCharacters-1.json"
    data = load_data(file_path)
    
    # 建立鄰接矩陣
    adj_matrix, node_names = build_adjacency_matrix(data)
    
    # 將鄰接矩陣儲存為CSV
    save_matrix_to_csv(adj_matrix, node_names, "/Users/ponywen/Documents/projects/SMA/hw_1/matrix.csv")

    top_10 = get_top_k_betweenness(adj_matrix)
    
    # 顯示結果
    print("角色中介中心性 (Betweenness Centrality):")
    for name, value in top_10:
        print(f"{name}: {value:.6f}")
    
    # 視覺化前10名角色的中介中心性
    plt.figure(figsize=(12, 6))
    plt.barh(top_10[1][::-1], top_10[0][::-1])
    plt.xlabel('中介中心性 (Betweenness Centrality)')
    plt.title('Top 10')
    plt.tight_layout()
    plt.savefig('betweenness_centrality.png')
    plt.show()

if __name__ == "__main__":
    main()

