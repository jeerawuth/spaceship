# nodes/buckshot_item_node.py

from nodes.item_node import ItemNode


class BuckshotItemNode(ItemNode):
    """
    ไอเท็มเปลี่ยนอาวุธเป็นโหมด buckshot (ยิงกระสุนกระจาย) ชั่วคราว
    - สืบทอดจาก ItemNode
    - ใช้ item_type = "buckshot"
    """

    def __init__(self):
        # ItemNode จะใช้ item_type เพื่อตัดสินใจเลือกเฟรมจาก ResourceManager
        super().__init__(item_type="buckshot")
