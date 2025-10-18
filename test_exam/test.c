#include <stdio.h>

int get_h(int m)
{
    if (m == 0)
        return 0;
    int h = 0;
    int total = 0;
    while (total < m)
    {
        h++;
        total += (1 << (h - 1)); // 累加第h层节点数（2^(h-1)）
    }
    return h;
}

// 计算节点数为m的完全二叉树中左子树的节点数
int get_left_count(int m)
{
    if (m <= 1)
        return 0;
    int h = get_h(m);
    int s = (1 << (h - 1)) - 1;       // 前h-1层的总节点数（完美二叉树）
    int t = m - s;                    // 最后一层的节点数
    int max_left_last = 1 << (h - 2); // 最后一层左子树最多节点数（2^(h-2)）

    if (t <= max_left_last)
    {
        // 最后一层节点均在左子树
        return ((1 << (h - 2)) - 1) + t;
    }
    else
    {
        // 左子树为完美二叉树（h-1层）
        return (1 << (h - 1)) - 1;
    }
}

// 递归构建层序序列
// post后序，res层序，start后序索引，index当前层序位置
void build_level(int post[], int res[], int start, int end, int index)
{
    if (start > end)
        return; //递归终止

    // 根节点是后序序列的最后一个元素，放入层序对应位置
    res[index] = post[end];
    int m = end - start + 1; // 当前子树的节点数
    if (m == 1)
        return; //递归终止

    int k = get_left_count(m); // 左子树节点数
    // 递归处理左子树：后序[start, start+k-1]，层序位置2*index+1
    build_level(post, res, start, start + k - 1, 2 * index + 1);
    // 递归处理右子树：后序[start+k, end-1]，层序位置2*index+2
    build_level(post, res, start + k, end - 1, 2 * index + 2);
}

int main()
{
    int N;
    scanf("%d", &N);
    int post[30];
    for (int i = 0; i < N; i++)
    {
        scanf("%d", &post[i]);
    }

    int res[30];
    build_level(post, res, 0, N - 1, 0);

    for (int i = 0; i < N; i++)
    {
        if (i != 0)
            printf(" ");
        printf("%d", res[i]);
    }
    printf("\n");

    return 0;
}