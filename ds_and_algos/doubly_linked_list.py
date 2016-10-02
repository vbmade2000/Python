class LinkedList(object):
    """Implements doubly linked list data structure"""
 
    class Node(object):
        """Represents a Doubly linkedlist node"""
        def __init__(self, data, next_node=None, prev_node=None):
            self._data = data
            self._next_node = next_node
            self._prev_node = prev_node
        
        @property 
        def data(self): 
            return self._data
 
        @data.setter
        def data(self, value):
            self._data = value

        @property
        def next_node(self):
            return self._next_node
 
        @next_node.setter
        def next_node(self,  value):
            self._next_node = value
 
        @property
        def prev_node(self):
            return self._prev_node

        @prev_node.setter
        def prev_node(self, value):
            self._prev_node = value

    def __init__(self):
        self._head = None
        self._size = 0 

    def prepend(self, value):
        """Prepends new node"""
        new_node = self.Node(value)
        if self._head is None:
            self._head = new_node
        else:
            current_node = self._head
            new_node.next_node = current_node
            self._head = new_node
        self._size += 1  

    def append(self, value):
        """Appends new node"""
        new_node = self.Node(value)
        if self._head is None:
            self._head = new_node
        else:
            prev_node = None
            current_node = self._head
            while current_node is not None:
                prev_node = current_node
                current_node = current_node.next_node
            prev_node.next_node = new_node
            new_node.prev_node = prev_node  
        self._size += 1

    def print_list(self):
        """Prints list"""
        current_node = self._head
        while current_node is not None:
            print current_node.data
            current_node = current_node.next_node

    def __len__(self):
        """Returns length of list"""
        return self._size

    def pop(self):
        """Removes node from top"""
        if self._head is None:
            return None
        else:
            first_node = self._head
            self._head = first_node.next_node
            self._size -= 1 
            return first_node.data

    def deque(self):
        """Deque node from list"""
        if self._head is None:
            return None
        else:
           current_node = self._head
           prev_node = None
           while current_node is not None:
               prev_node = current_node
               current_node = current_node.next_node
           last_node = prev_node.prev_node
           last_node.next_node = None
           del prev_node           
           self._size -= 1

l = LinkedList()
l.prepend(1) 
l.prepend(2)
l.prepend(3)
l.prepend(4)
l.append(10)
l.append(20)

l.print_list()
print str(len(l))
print str(l.pop())
print "-----------------------"
print str(len(l))
print "--------------------------"
l.deque()
l.print_list()
print str(len(l))
