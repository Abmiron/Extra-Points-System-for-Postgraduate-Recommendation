#include <stdio.h>
#include <stdlib.h>

typedef struct Node
{
    int data1;
    int data2;
    struct Node *next;
} Node;

typedef struct Stack
{
    Node *top;
    int size;
} Stack;

void initStack(Stack *s)
{
    s->top = NULL;
    s->size = 0;
}

int isEmpty(Stack *s)
{
    return s->size == 0;
}

// 入栈
void push(Stack *s, int data1, int data2)
{
    Node *newNode = (Node *)malloc(sizeof(Node));
    newNode->data1 = data1;
    newNode->data2 = data2;
    newNode->next = s->top;
    s->top = newNode;
    s->size++;
}

// 出栈
int pop(Stack *s, int *data1, int *data2)
{
    if (isEmpty(s))
        return -1;
    Node *temp = s->top;
    *data1 = temp->data1;
    *data2 = temp->data2;
    s->top = s->top->next;
    free(temp);
    s->size--;
    return 0;
}

// 获取栈顶
int peek(Stack *s, int *data1, int *data2)
{
    if (isEmpty(s))
        return -1;
    *data1 = s->top->data1;
    *data2 = s->top->data2;
    return 0;
}

void printPath(Stack *s)
{
    // 反转栈打印正向路径
    Stack tempStack;
    initStack(&tempStack);
    Node *current = s->top;
    while (current)
    {
        push(&tempStack, current->data1, current->data2);
        current = current->next;
    }

    while (!isEmpty(&tempStack))
    {
        int x, y;
        pop(&tempStack, &x, &y);
        printf("(%d,%d)", x, y);
    }
    printf("\n");
}

int main()
{
    int n;
    scanf("%d", &n);

    int **maze = (int **)malloc(n * sizeof(int *));
    for (int i = 0; i < n; i++)
        maze[i] = (int *)malloc(n * sizeof(int));

    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            scanf("%d", &maze[i][j]);
        }
    }

    Stack s;
    initStack(&s);

    int x = 1, y = 1;
    push(&s, x, y);
    maze[x][y] = 1;//记录起点并标记为已访问

    int found = 0;
    int directions[4][2] = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}}; // 右下左上

    while (!isEmpty(&s))
    {
        int currX, currY;
        peek(&s, &currX, &currY);
        if (currX == n - 2 && currY == n - 2)
        {
            found = 1;
            break;
        }

        int moved = 0;
        
        for (int i = 0; i < 4; i++)
        {
            int newX = currX + directions[i][0];
            int newY = currY + directions[i][1];

            if (newX > 0 && newX < n - 1 && newY > 0 && newY < n - 1 && maze[newX][newY] == 0)
            {
                push(&s, newX, newY);
                maze[newX][newY] = 1;
                moved = 1;
                break;
            }
        }
        if (!moved)
        {
            int discardX, discardY;
            pop(&s, &discardX, &discardY);
        }
    }

    if (found)
    {
        printPath(&s);
    }
    else
    {
        printf("NO\n");
    }

    // 释放内存
    while (!isEmpty(&s))
    {
        int discardX, discardY;
        pop(&s, &discardX, &discardY);
    }

    for (int i = 0; i < n; i++)
        free(maze[i]);
    free(maze);

    return 0;
}