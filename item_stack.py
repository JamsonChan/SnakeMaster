class Node:
    def __init__(self, item):
        self.item = item  # 道具名稱
        self.next = None  # 指向下一個節點的指標

class Stack:
    def __init__(self, size):
        self.size = size # 堆疊最高容量
        self.top = None  # 指向堆疊頂端的指標
        
    def isFull(self): # 確認堆疊是否滿
        return self.len() == self.size

    def isEmpty(self): # 確認堆疊是否空
        return self.len() == 0

    def len(self): # 計算堆疊高度
        length = 0
        cur = self.top
        while cur:
            cur = cur.next
            length += 1
        return length

    def push(self, item): # 新增一個節點到堆疊的頂端
        if not self.isFull(): # 若堆疊不是滿的
            new = Node(item)
            new.next = self.top
            self.top = new

    def pop(self): # 刪除堆疊頂端的節點
        if not self.isEmpty(): # 若堆疊不是空的
            self.top = self.top.next

    def printStack(self): # 顯示堆疊
        cur = self.top
        print("=== top ===")
        while cur:
            print(f"{cur.item}")
            cur = cur.next
        print(f"=== bottom ===\n")

if __name__ == "__main__":
    stack = Stack(3)
    stack.push("BlackHole")
    stack.push("Gamble")
    stack.push("FruitGift")
    stack.printStack()
    stack.pop()
    stack.printStack()