import networkx as nx
import matplotlib.pyplot as plt
from database import get_db
from models import Person, Relationship
import numpy as np

def create_network_graph():
    """從資料庫創建關係網絡圖"""
    db = next(get_db())
    
    # 創建有向圖
    G = nx.DiGraph()
    
    # 獲取所有人物和關係
    persons = db.query(Person).all()
    relationships = db.query(Relationship).all()
    
    # 添加節點（創作者）
    for person in persons:
        G.add_node(
            person.person_id,
            name=person.name,
            description=person.description
        )
    
    # 添加邊（關係）
    for rel in relationships:
        G.add_edge(
            rel.source_person_id,
            rel.target_person_id,
            relation_type=rel.relation_type,
            evidence=rel.evidence
        )
    
    return G

def draw_network_graph(G, output_file='creator_network.png'):
    """繪製並保存關係網絡圖"""
    plt.figure(figsize=(15, 15))
    
    # 設置節點位置
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # 繪製節點
    nx.draw_networkx_nodes(
        G, pos,
        node_color='lightblue',
        node_size=500,
        alpha=0.9
    )
    
    # 繪製邊
    nx.draw_networkx_edges(
        G, pos,
        edge_color='gray',
        arrows=True,
        arrowsize=20
    )
    
    # 添加標籤
    labels = {node: G.nodes[node]['name'] for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    
    # 添加邊的標籤
    edge_labels = {(u, v): G.edges[u, v]['relation_type'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
    
    # 設置標題
    plt.title("Minecraft 創作者關係網絡圖", fontsize=16)
    
    # 保存圖片
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"關係網絡圖已保存為: {output_file}")

def analyze_network(G):
    """分析網絡圖的統計信息"""
    print("\n網絡分析結果:")
    print(f"總節點數: {G.number_of_nodes()}")
    print(f"總邊數: {G.number_of_edges()}")
    
    # 計算度中心性
    degree_centrality = nx.degree_centrality(G)
    print("\n度中心性最高的前5個創作者:")
    sorted_centrality = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
    for person_id, centrality in sorted_centrality[:5]:
        print(f"{G.nodes[person_id]['name']}: {centrality:.3f}")
    
    # 計算中介中心性
    betweenness_centrality = nx.betweenness_centrality(G)
    print("\n中介中心性最高的前5個創作者:")
    sorted_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)
    for person_id, betweenness in sorted_betweenness[:5]:
        print(f"{G.nodes[person_id]['name']}: {betweenness:.3f}")

def main():
    try:
        # 創建網絡圖
        G = create_network_graph()
        
        # 分析網絡
        analyze_network(G)
        
        # 繪製並保存網絡圖
        draw_network_graph(G)
        
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    main() 