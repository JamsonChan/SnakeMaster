class Node:
    def __init__(self, x, y):
        self.x = x        # x座標
        self.y = y        # y座標
        self.pre = None   # 指向前一個節點的指標
        self.next = None  # 指向下一個節點的指標

class Queue:
    def __init__(self):
        self.front = None # 指向佇列最前端的指標
        self.rear = None  # 指向佇列最後端的指標

    def len(self): # 計算佇列長度
        length = 0
        cur = self.front
        while cur:
            cur = cur.next
            length += 1
        return length

    def enQueue(self, x, y): # 在最後端(rear)加入新節點
        new = Node(x, y)
        if self.len() == 0: # 若佇列為空
            self.front = new
            self.rear = new
        else:
            new.pre = self.rear
            self.rear.next = new
            self.rear = new

    def deQueue(self): # 刪除最前端(front)的節點
        if self.len() <= 1: # 若佇列長度為1或0
            self.front = None
            self.rear = None
        else:
            self.front = self.front.next
            self.front.pre = None
    
    def reverse(self): # 反轉佇列
        cur = self.front
        self.rear, self.front = self.front , self.rear
        while cur:
            cur.next, cur.pre = cur.pre, cur.next
            cur = cur.pre

    def printQueue(self): # 顯示佇列
        cur = self.front
        print("front", end="  ")
        while cur:
            print(f"[{cur.x}, {cur.y}]", end="  ")
            cur = cur.next
        print("rear")

if __name__ == "__main__":
    queue = Queue()
    queue.enQueue(0, 9)
    queue.enQueue(1, 9)
    queue.enQueue(2, 9)
    queue.printQueue()
    queue.deQueue()
    queue.printQueue()
    queue.deQueue()
    queue.printQueue()
    queue.enQueue(3, 9)
    queue.printQueue()