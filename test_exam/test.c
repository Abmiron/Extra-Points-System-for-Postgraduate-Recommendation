#include <stdio.h>
#include <stdlib.h>

typedef struct List
{
    int data;
    struct List *next;
} List;

List *creatList()
{
    List *head = (List *)malloc(sizeof(List));
    head->next = NULL;
    int x;
    scanf("%d", &x);
    if (x == -1)
        return head;
    List *tail = head;
    while (x != -1)
    {
        List *node = (List *)malloc(sizeof(List));
        node->data = x;
        node->next = NULL;
        tail->next = node;
        tail = node;
        scanf("%d", &x);
    }
    return head;
}

void printList(List *head)
{
    if (!head->next)
    {
        printf("NULL");
        return;
    }

    List *p = head->next;
    int i = 0;
    while (p)
    {
        if (i++ > 0)
            printf(" ");
        printf("%d", p->data);
        p = p->next;
    }
    printf("\n");
}

List *work(List *head1, List *head2)
{
    
    List *p1 = head1->next;
    List *p2 = head2->next;
    List *head3 = (List *)malloc(sizeof(List));
    head3->next = NULL;
    List *tail3 = head3;

    while (p1 && p2)
    {
        if (p1->data < p2->data)
        {
            p1 = p1->next;
        }
        else if (p1->data > p2->data)
        {
            p2 = p2->next;
        }
        else
        {
            List *node = (List *)malloc(sizeof(List));
            node->data = p1->data;
            node->next = NULL;
            tail3->next = node;
            tail3 = node;
            p1 = p1->next;
            p2 = p2->next;
        }
    }
    return head3;
}

int main()
{
    List *head1 = creatList();
    List *head2 = creatList();
    List *head3 = work(head1, head2);
    printList(head3);
    return 0;
}