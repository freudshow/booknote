import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.animation as animation
from collections import deque

# ======================================
# 1. 构建图（支持有向/无向/有权）
# ======================================
def create_graph(is_directed=False):
    if is_directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()

    # 边列表（可自定义修改）
    edges = [
        ("S", "A", 1),
        ("S", "B", 1),
        ("A", "D", 1),
        ("B", "C", 1),
        ("C", "D", 1),
        ("A", "C", 1),  # 构造环
    ]
    G.add_weighted_edges_from(edges)
    return G

# ======================================
# 2. BFS 单步执行生成器
# ======================================
def bfs_steps(G, start="S"):
    color = {node: 0 for node in G.nodes}  # 0未访问 1访问中 2已访问
    dist = {node: -1 for node in G.nodes}
    parent = {node: None for node in G.nodes}
    path = []
    q = deque([start])

    color[start] = 1
    dist[start] = 0

    while q:
        u = q.popleft()
        color[u] = 2
        path.append(u)

        # 返回到动画当前状态
        yield color, dist, parent, path, list(q)

        for v in G.neighbors(u):
            if color[v] == 0:
                color[v] = 1
                dist[v] = dist[u] + 1
                parent[v] = u
                q.append(v)

    yield color, dist, parent, path, list(q)

# ======================================
# 3. DFS 单步执行生成器（对比用）
# ======================================
def dfs_steps(G, start="S"):
    color = {node: 0 for node in G.nodes}
    dist = {node: -1 for node in G.nodes}
    parent = {node: None for node in G.nodes}
    path = []
    stack = [start]

    color[start] = 1
    dist[start] = 0

    while stack:
        u = stack.pop()
        if color[u] == 2:
            continue

        color[u] = 2
        path.append(u)
        yield color, dist, parent, path, list(stack)

        for v in reversed(list(G.neighbors(u))):
            if color[v] == 0:
                color[v] = 1
                dist[v] = dist[u] + 1
                parent[v] = u
                stack.append(v)

    yield color, dist, parent, path, list(stack)

# ======================================
# 4. 动画绘制函数
# ======================================
def animate(frame):
    color, dist, parent, path, queue = frame

    # 节点颜色
    node_colors = []
    for c in color.values():
        if c == 0:
            node_colors.append("white")
        elif c == 1:
            node_colors.append("gold")
        else:
            node_colors.append("limegreen")

    # 绘图
    ax1.clear()
    pos = {"S": (0, 2), "A": (-1, 1), "B": (1, 1), "C": (1, 0), "D": (-1, 0)}
    nx.draw(G, pos, ax=ax1, with_labels=True, node_color=node_colors,
            node_size=2000, font_size=14, font_weight="bold",
            edgecolors="black", linewidths=2)

    # 画权重
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax1)

    # 信息面板
    ax2.clear()
    ax2.axis("off")
    info = f"path: {' → '.join(path)}\n"
    info += f"queue/stack: {queue}\n"
    info += f"distance: {dist}\n"
    info += f"parent: {parent}"
    ax2.text(0.02, 0.9, info, va="top", fontsize=11, transform=ax2.transAxes)

# ======================================
# 5. 主程序：选择 BFS / DFS
# ======================================
if __name__ == "__main__":
    # 选择图类型
    use_directed = False   # 改成 True = 有向图
    use_dfs = False        # 改成 True = DFS栈模式

    G = create_graph(is_directed=use_directed)
    generator = dfs_steps(G) if use_dfs else bfs_steps(G)

    # 画布布局
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 7), height_ratios=[3, 1])
    fig.suptitle("BFS aimation" if not use_dfs else "DFS aimation", fontsize=14)

    # 启动动画
    ani = animation.FuncAnimation(
        fig, animate, frames=generator, interval=800, repeat=False
    )

    plt.tight_layout()
    plt.show()
