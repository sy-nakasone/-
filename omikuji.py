import random

def draw_omikuji():
    omikuji_data = {
        "ドラえもん": "大吉",
        "のび太": "中吉",
        "しずか": "吉",
        "スネ夫": "小吉",
        "ジャイアン": "凶",
        "先生": "大凶"
    }

    character, fortune = random.choice(list(omikuji_data.items()))
    
    print("=== ドラえもんおみくじ ===")
    print(f"キャラクター: {character}")
    print(f"運勢: {fortune}")

if __name__ == "__main__":
    draw_omikuji()
