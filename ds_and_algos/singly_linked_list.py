#!/usr/bin/env python
"""This module contains a singly linked list implementation"""
__author__ = "Malhar Vora"
__license__ = "GPL"
__email__ = "mlvora.2010@gmail.com"

class MyList(object):
    """Singly linke list implementation"""

    class _Node(object):
        """Internal class that represents a node in linked list"""
        def __init__(self, data=None):
            self._data = data
            self._next_node = None

        @property
        def data(self):
            """Returns data contained in Node"""
            return self._data

        @data.setter
        def data(self, data=None):
            """Sets data
                :param data: Data to be set in Node
            """
            self._data = data

        @property
        def next_node(self):
            """Returns reference to the next node"""
            return self._next_node

        @next_node.setter
        def next_node(self, next_node):
            """Sets next node for Node
               :param next_node: Reference to the next node
            """
            self._next_node = next_node       

    def __init__(self):
        self._size = 0
        self._head = None
        self._node_class = self._Node

    def __len__(self):
        return self._size

    def prepend(self, data=None):
        """Prepends the data to the list.
           Similar to insert_at_beginning 
           method if linked list
           :param data: Data to be inserted
           :type data: object
        """ 
        new_node = self._node_class(data)
        # First check if list is empty
        if self._head is None:
            self._head = new_node
        else:
            new_node.next_node = self._head
            self._head = new_node
        self._size += 1

    def __str__(self):
        """Overriden method to print linked list
           :returns: Newline separated string of
                     list items
           :rtype: str
        """
        current_node = self._head
        return_value = "" 
        while current_node != None:
            return_value += str(current_node.data) + "\n"
            current_node = current_node.next_node
        return return_value.strip() 
            
    def append(self, data):
        """Prepends the data to the list.
           Similar to insert_at_end 
           method if linked list
           :param data: Data to be inserted
           :type data: object
        """
        if self._head is None:
            self._head = self._node_class(data)
        else:
            current_node = self._head
            previous_node = current_node
            while current_node is not None:
                previous_node = current_node
                current_node = current_node.next_node
            previous_node.next_node = self._node_class(data) 
        self._size += 1     
    
    def __getitem__(self, index):
        """Magic method to implement retrieval for item 
           using index. i.e list[1]
           :param index: Index of item to be retrieved
           :type index: int
           :returns: Item at <index> position  
           :rtype: type of returned item 
        """
        if index + 1 > self._size:
            raise IndexError("list index out of range")
        position = 0
        return_node = None
        current_node = self._head
        previous_node = current_node
        while current_node is not None:
            if position == index:
                return_node = current_node
                break
            current_node = current_node.next_node
            position += 1
        return return_node.data 

    def remove(self, data):
        """Removes first occurrence of data from list
        :param data: Data to remove
        :type data: object
        """ 
        current_node = self._head
        found = False
        previous_node = current_node
        while current_node is not None:
            previous_node = current_node
            if current_node.data == data:
                previous_node.next_node = current_node.next_node
                del current_node
                found = True
                self._size -= 1 
                break
            current_node = current_node.next_node   
        if found == False:
            raise ValueError("list.remove(x): x not in list")
 
    def count(self, data):
        """Returns the no of occurences of data in list
           :param data: Data to check occurrence of
           :type data: object
           :returns: Occurance count of data 
           :rtype: int
        """
        current_node = self._head
        count = 0
        while current_node is not None:
            if current_node.data == data:
                 count += 1
            current_node = current_node.next_node
        return count       


    def reverse(self):
        """Returns the reversed linked list"""
        prev = None
        current = self._head
        while(current is not None):
            next_node = current.next_node
            current.next_node = prev
            prev = current
            current = next_node
        self._head = prev 
            




m = MyList()
m.append(10)
m.append(20)
m.append(30)
m.append(40)
m.append(50)
print len(m)
print "---------"
m.reverse()
print m
