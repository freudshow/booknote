import numpy as np
import matplotlib.pyplot as plt

# 生成随机数据点
def generate_data(num_points, num_clusters):
    centroids = np.random.rand(num_clusters, 2) * 10
    labels = np.random.randint(0, num_clusters, size=num_points)
    data = centroids[labels] + 0.5 * np.random.randn(num_points, 2)
    return data, centroids

# 初始化质心
def initialize_centroids(data, k):
    indices = np.random.choice(data.shape[0], k, replace=False)
    return data[indices]

# 分配簇
def assign_clusters(data, centroids):
    distances = np.linalg.norm(data[:, np.newaxis] - centroids, axis=2)
    return np.argmin(distances, axis=1)

# 更新质心
def update_centroids(data, labels, k):
    new_centroids = np.array([data[labels == i].mean(axis=0) for i in range(k)])
    return new_centroids

# K-means算法
def kmeans(data, k, max_iters=100):
    centroids = initialize_centroids(data, k)
    for _ in range(max_iters):
        old_centroids = centroids
        labels = assign_clusters(data, centroids)
        centroids = update_centroids(data, labels, k)
        if np.all(old_centroids == centroids):
            break
    return labels, centroids

# 主函数
if __name__ == "__main__":
    num_points = 300
    num_clusters = 3
    data, true_centroids = generate_data(num_points, num_clusters)
    
    labels, centroids = kmeans(data, num_clusters)
    
    # 绘制结果
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(data[:, 0], data[:, 1], c=labels, cmap='viridis')
    plt.scatter(centroids[:, 0], centroids[:, 1], s=300, c='red', marker='X')
    plt.title('K-means Clustering')
    plt.xlabel('Feature 1')
    plt.ylabel('Feature 2')
    plt.colorbar(scatter, label='Cluster Label')
    plt.show()


