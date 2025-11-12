#include <stdio.h>
#include <stdlib.h>

#define MAX_VERTICES 10

int visited[MAX_VERTICES];
int graph[MAX_VERTICES][MAX_VERTICES];

// DFS遍历检查路径是否存在
int DFS(int n, int current, int target) {
    if (current == target) {
        return 1; // 找到目标顶点
    }
    
    visited[current] = 1;
    
    for (int i = 0; i < n; i++) {
        if (graph[current][i] == 1 && !visited[i]) {
            if (DFS(n, i, target)) {
                return 1;
            }
        }
    }
    
    return 0; // 没有找到路径
}

int main() {
    int N, E;
    
    // 读取顶点数和边数
    scanf("%d %d", &N, &E);
    
    // 初始化邻接矩阵和visited数组
    for (int i = 0; i < MAX_VERTICES; i++) {
        visited[i] = 0;
        for (int j = 0; j < MAX_VERTICES; j++) {
            graph[i][j] = 0;
        }
    }
    
    // 读取边
    for (int i = 0; i < E; i++) {
        int u, v;
        scanf("%d %d", &u, &v);
        
        // 只添加在有效范围内的边
        if (u >= 0 && u < N && v >= 0 && v < N) {
            graph[u][v] = 1;
            graph[v][u] = 1;
        }
    }
    
    // 读取要检查的顶点
    int i, j;
    scanf("%d %d", &i, &j);
    
    // 特殊情况：如果i和j是同一个顶点
    if (i == j) {
        printf("There is a path between %d and %d.\n", i, j);
        return 0;
    }
    
    // 检查顶点编号是否有效
    if (i < 0 || i >= N || j < 0 || j >= N) {
        printf("There is no path between %d and %d.\n", i, j);
        return 0;
    }
    
    // 检查路径是否存在
    int hasPath = DFS(N, i, j);
    
    if (hasPath) {
        printf("There is a path between %d and %d.\n", i, j);
    } else {
        printf("There is no path between %d and %d.\n", i, j);
    }
    
    return 0;
}