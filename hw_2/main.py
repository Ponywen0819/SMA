import numpy as np

def read_adjacency_matrix(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        adjacency_matrix = []

        node_id = list(map(int, lines[0].split(",")[1:]))
        for line in lines[1:]:
            adjacency_row = list(map(float, line.split(",")))[1:]
            adjacency_matrix.append(adjacency_row)

    return adjacency_matrix, node_id

def get_diagonal_degree_matrix(adjacency_matrix):
    diagonal_matrix = []
    for i in range(len(adjacency_matrix)):
        diagonal_matrix.append([0 for _ in range(len(adjacency_matrix))])
        diagonal_matrix[i][i] = sum(adjacency_matrix[i])
    return diagonal_matrix

def get_laplacian_matrix(adjacency_matrix, diagonal_matrix):
    laplacian_matrix = []
    for i in range(len(adjacency_matrix)):
        
        laplacian_matrix.append([0 for _ in range(len(adjacency_matrix))])
        for j in range(len(adjacency_matrix)):
            laplacian_matrix[i][j] = diagonal_matrix[i][j] - adjacency_matrix[i][j]
    return laplacian_matrix

def smallest_k_eigenvector(eigenvalues, eigenvectors, k):
    # 将特征值和特征向量转换为列表，方便操作
    eigenvalues = eigenvalues.tolist()
    eigenvectors = eigenvectors.T  # 转置使得每行对应一个特征向量
    
    # 过滤掉接近0的特征值（使用一个小的阈值）
    threshold = 1e-10
    non_zero_indices = [i for i, val in enumerate(eigenvalues) if abs(val) > threshold]
    
    # 获取非零特征值及其索引
    non_zero_eigenvalues = [eigenvalues[i] for i in non_zero_indices]
    
    # 找出k个最小特征值的索引
    smallest_k_indices = []
    while len(smallest_k_indices) < k and len(non_zero_eigenvalues) > 0:
        min_val = min(non_zero_eigenvalues)
        min_idx = non_zero_eigenvalues.index(min_val)
        smallest_k_indices.append(non_zero_indices[min_idx])
        non_zero_eigenvalues.pop(min_idx)
        non_zero_indices.pop(min_idx)
    
    # 获取对应的特征向量
    smallest_k_vectors = [eigenvectors[i] for i in smallest_k_indices]
    smallest_k_values = [eigenvalues[i] for i in smallest_k_indices]
    
    return smallest_k_values, np.array(smallest_k_vectors)

def kmeans(X, k, max_iter=100, random_state=42):
    np.random.seed(random_state)
    n_samples, n_features = X.shape
    
    centers = X[np.random.choice(n_samples, k, replace=False)]
    
    for _ in range(max_iter):
        distances = np.zeros((n_samples, k))
        for i, center in enumerate(centers):
            distances[:, i] = np.linalg.norm(X - center, axis=1)
        
        labels = np.argmin(distances, axis=1)
        
        new_centers = np.array([X[labels == i].mean(axis=0) for i in range(k)])
        
        if np.all(centers == new_centers):
            break
            
        centers = new_centers
    
    cluster_matrix = np.zeros((n_samples, k))
    for i in range(n_samples):
        cluster_matrix[i, labels[i]] = 1
    
    return labels, centers


def save_eigenvector(eigenvectors, file_path):
    with open(file_path, 'w') as file:
        for eigenvector in eigenvectors:
            eigenvector_list = eigenvector.tolist()

            file.write(f"{str(eigenvector_list)[1:-1]}\n")

def save_cluster(cluster, node_id, file_path):
    with open(file_path, 'w') as file:
        for i in range(len(cluster)):
            file.write(f"{cluster[i]} ")

def main():
    K = 3

    adjacency_matrix, node_id = read_adjacency_matrix("/Users/ponywen/Documents/projects/SMA/hw_2/adjacent_matrix-1-1.csv")
    diagonal_matrix = get_diagonal_degree_matrix(adjacency_matrix)
    laplacian_matrix = get_laplacian_matrix(adjacency_matrix, diagonal_matrix)

    eigenvalues, eigenvectors = np.linalg.eig(laplacian_matrix)

    smallest_values, smallest_vectors = smallest_k_eigenvector(eigenvalues, eigenvectors, K)
    
    cluster, centers = kmeans(smallest_vectors.T, K, random_state=42)
    print(cluster)
    
    save_eigenvector(smallest_vectors, "./hw_2/eigenvector.csv")
    save_cluster(cluster, node_id, "./hw_2/cluster.csv")
    

if __name__ == "__main__":
    main()
