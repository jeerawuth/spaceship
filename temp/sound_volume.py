import math
import pygame

def play_explosion_with_distance(hero, explosion_pos, sound):
    # 1) จุดของ hero
    hero_x, hero_y = hero.rect.center

    # 2) จุดระเบิด (explosion_pos เป็น tuple (x, y))
    ex_x, ex_y = explosion_pos

    # 3) คำนวณระยะห่างแบบพีทาโกรัส
    dx = ex_x - hero_x
    dy = ex_y - hero_y
    distance = math.sqrt(dx*dx + dy*dy)

    # 4) แปลงระยะเป็นความดัง (ลองปรับค่าตามเหมาะ)
    #    ยิ่งใกล้ ยิ่งดัง / ยิ่งไกล ยิ่งเบา
    MAX_HEAR_DISTANCE = 600   # ระยะที่ยังพอได้ยิน
    distance = min(distance, MAX_HEAR_DISTANCE)

    # แปลงเป็น 1.0 → 0.0 ตามระยะ
    volume = 1.0 - (distance / MAX_HEAR_DISTANCE)

    # กันไม่ให้เบาจนหาย หรือดังเกิน
    volume = max(0.1, min(1.0, volume))

    sound.set_volume(volume)
    sound.play()
