# nodes/speed_item_node.py

from nodes.item_node import ItemNode


class SpeedItemNode(ItemNode):
    """
    ไอเท็มเพิ่มความเร็ว (Speed Up)
    - สืบทอดจาก ItemNode
    - ใช้ item_type = "speed"
    - ภายใน ItemNode จะจัดการโหลดเฟรมและสุ่มตำแหน่งให้เอง
    """

    def __init__(self):
        # ItemNode จะใช้ item_type เพื่อตัดสินใจเลือกเฟรมจาก ResourceManager
        super().__init__(item_type="speed")
