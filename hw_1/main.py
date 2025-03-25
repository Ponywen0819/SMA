import json
import csv

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
        adj_matrix[source][target] = 1
        adj_matrix[target][source] = 1  # 無向圖需要對稱
    
    return adj_matrix, node_names

def save_matrix_to_csv(adj_matrix, node_names, file_path):
    """使用原生方法將鄰接矩陣儲存成CSV檔案，不包含標頭"""
    
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in adj_matrix:
            csv_writer.writerow([1 if i!=0 else 0 for i in row])
    print(f"鄰接矩陣已成功儲存至 {file_path}")

def shortest_path(graph, start):
    """使用 BFS 計算最短路徑"""
    n = len(graph)
    stack = []

    distances = [-1 for _ in range(n)]
    distances[start] = 0

    path_counts = [0 for _ in range(n)]
    path_counts[start] = 1
    
    predecessors = [[] for _ in range(n)]
    
    queue = [start]
    while queue:
        current = queue.pop(0)
        stack.append(current)

        for neighbor, connected in enumerate(graph[current]):
            if connected == 0:
                continue
            if distances[neighbor] == -1:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)
            if distances[neighbor] == distances[current] + 1:
                path_counts[neighbor] += path_counts[current]
                predecessors[neighbor].append(current)
    
    return distances, predecessors, path_counts, stack

def calculate_dependency(graph, stack, predecessors, path_counts):
    """計算一個節點對其他節點對的依賴性"""
    n = len(graph)

    dependency = [0 for _ in range(n)]
    while stack:
        current = stack.pop()
        for predecessor in predecessors[current]:
            dependency[predecessor] += path_counts[predecessor] / path_counts[current] * (1 + dependency[current])
    
    return dependency

def calculate_betweenness_centrality(adj_matrix):
    """計算 betweenness centrality"""
    n = len(adj_matrix)
    
    betweenness = [ 0 for _ in range(n)]
    
    for s in range(n):
        # 計算最短路徑
        _, predecessors, path_counts, stack = shortest_path(adj_matrix, s)
        
        # 計算依賴值
        dependency = calculate_dependency(adj_matrix, stack, predecessors, path_counts)

        # 累加依賴值
        for v in range(n):
            if v == s:
                continue
            betweenness[v] += dependency[v]

    return [i/2 for i in betweenness]

def get_top_k_betweenness(adj_matrix,k = 10):
    """計算中介中心性並返回前k名的節點"""
    # 默認k為10，如果需要其他數量可以通過參數傳入
    
    # 計算betweenness中心性
    betweenness = calculate_betweenness_centrality(adj_matrix)
    
    # 將結果與節點名稱關聯
    result = [(node, value) for node, value in enumerate(betweenness)]
    
    # 根據中介中心性排序
    result.sort(key=lambda x: x[1], reverse=True)
    
    # 返回前k個結果
    return result[:k]
    

def save_betweenness_to_csv(betweenness, file_path):
    """將中介中心性儲存為CSV檔案"""
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for node, value in betweenness:
            csv_writer.writerow([node, f"{value:.2f}"])
    print(f"中介中心性已成功儲存至 {file_path}")

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
    
    # 將中介中心性儲存為CSV
    save_betweenness_to_csv(top_10, "/Users/ponywen/Documents/projects/SMA/hw_1/rank.csv")

    # 視覺化前10名角色的中介中心性
    # a = [str(x[0]) for x in top_10[::-1]]
    # b = [x[1] for x in top_10[::-1]]
    # plt.figure(figsize=(12, 6))
    # plt.barh(a,b)
    # plt.xlabel('中介中心性 (Betweenness Centrality)')
    # plt.title('Top 10')
    # plt.tight_layout()
    # plt.savefig('betweenness_centrality.png')
    # plt.show()

if __name__ == "__main__":
    main()

