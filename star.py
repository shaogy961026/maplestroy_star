import random
import numpy as np

# 定義每個星級的強化機率
rates = {
    17: {'success': 0.3, 'maintain': 0.21, 'down': 0.49},
    18: {'success': 0.3, 'maintain': 0.28, 'down': 0.42},
    19: {'success': 0.3, 'maintain': 0.28, 'down': 0.42},
    20: {'success': 0.3, 'maintain': 0.7, 'down': 0.0},
    21: {'success': 0.3, 'maintain': 0.35, 'down': 0.35},
    22: {'success': 0.03, 'maintain': 0.582, 'down': 0.388},
    23: {'success': 0.02, 'maintain': 0.588, 'down': 0.392},
    24: {'success': 0.01, 'maintain': 0.594, 'down': 0.396}
}
end=23

def simulate_enhancement():
    star = 1  # 初始星級
    total_maple_points = 0  # 總楓點花費
    total_s = 0  # 總17星卷使用量
    process = []  # 記錄過程
    while star < end:
        if star < 17:
            # 使用17星卷升回17星
            total_s += 1
            star = 17
            process.append(f"星級低於17，使用17星卷升回17星。當前星級：{star}")
        else:
            # 進行強化
            total_maple_points += 50
            rand = random.random()
            if rand < rates[star]['success']:
                star += 1
                process.append(f"使用50楓點強化成功，星級+1。當前星級：{star}")
            elif rand < rates[star]['success'] + rates[star]['maintain']:
                process.append(f"使用50楓點強化失敗，星級維持。當前星級：{star}")
            else:
                star -= 1
                process.append(f"使用50楓點強化失敗，星級-1。當前星級：{star}")

    return total_maple_points, total_s, process

# 運行100,000次模擬
num_simulations = 100000
maple_points_list = []
s_list = []

for _ in range(num_simulations):
    mp, s, _ = simulate_enhancement()
    maple_points_list.append(mp)
    s_list.append(s)

# 計算平均值
avg_maple_points = np.mean(maple_points_list)
avg_s = np.mean(s_list)

# 顯示一次模擬的詳細過程
_, _, example_process = simulate_enhancement()

# 輸出結果
print("=== 一次模擬的詳細過程 ===")
for step in example_process:
    print(step)
print("\t")
print(f'至{end}星')
print(f"100,000次模擬的平均楓點花費：{avg_maple_points:.2f}")
print(f"100,000次模擬的平均17星卷使用量：{avg_s:.2f}")
