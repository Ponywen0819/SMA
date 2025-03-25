# HW1 Report

## Library

- csv
- json

## Adjacent Matrix

1. 初始化 Adjacent Matrix ，將所有元素設置為 0
2. 尋訪所有 link ，並將 matrix 中相應的元素設置為 1

## betweenness value

1. 對於每個起點 s，使用 BFS 計算到其他所有節點的最短路徑數量
2. 依照 Brandes 公式計算節點間的依賴關係
3. 將所有依賴值相加
