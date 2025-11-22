# nodes/laser_item_node.py

from nodes.item_node import ItemNode


class LaserItemNode(ItemNode):
    """
    ไอเท็มเปลี่ยนอาวุธเป็นโหมดเลเซอร์ชั่วคราว
    - สืบทอดจาก ItemNode
    - ใช้ item_type = "laser"
    """

    def __init__(self):
        super().__init__(item_type="laser")
