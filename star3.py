import random
import os
import numpy as np

# 定義機率表
def get_probabilities(event_active=False):
    base_probabilities = {
        15: {"success": 0.3000, "destroy": 0.1050, "drop": 0.0000, "hold": 0.5950},
        16: {"success": 0.3000, "destroy": 0.1400, "drop": 0.5600, "hold": 0.0000},
        17: {"success": 0.3000, "destroy": 0.2100, "drop": 0.4900, "hold": 0.0000},
        18: {"success": 0.3000, "destroy": 0.2800, "drop": 0.4200, "hold": 0.0000},
        19: {"success": 0.3000, "destroy": 0.2800, "drop": 0.4200, "hold": 0.0000},
    }
    if event_active:
        base_probabilities[15] = {"success": 1.0000, "destroy": 0.0000, "drop": 0.0000, "hold": 0.0000}
    return base_probabilities

# 星卷價格（楓幣）
scroll_prices = {
    15: 81555555,
    16: 244444444,
    17: 2396666666,
    18: 5466666666,
    19: 17776888888,
    20: 48888888888
}

# 基本設定
points_per_billion = 6
scroll_costs = {star: price * points_per_billion / 10**8 for star, price in scroll_prices.items()}
equip_compensation_cost = 60000000 * points_per_billion / 10**8
upgrade_cost = 9
protect_cost = 50
event_active = True
probabilities = get_probabilities(event_active)
target = 20
simulations = 100000

# 輸出初始條件
print("=== 程式輸入條件 ===")
print(f"目標星數：0星到{target}星")
print(f"活動狀態：{'啟用' if event_active else '未啟用'}（15星強化成功率100%）")
print("星卷價格（楓幣）：")
for star, price in scroll_prices.items():
    print(f"{star}星：{price:,} 楓幣")
print("\n楓點與楓幣換算：")
print(f"換算比例：1億楓幣 = {points_per_billion} 楓點")
print("\n星卷價格（轉換後，楓點）：")
for star, cost in scroll_costs.items():
    print(f"{star}星：{cost:.2f} 楓點")
print(f"\n普通強化成本：{upgrade_cost} 楓點（不防爆設定）")
print(f"防破壞強化成本：{protect_cost} 楓點（破壞改為維持）")
print(f"裝備補償成本（破壞時）：{equip_compensation_cost:.2f} 楓點")
print("成本已包含裝備破壞後拿裝備修復價格（楓幣楓點換算）")
print(f"模擬次數：每個策略{simulations:,}次")
print("=================\n")

# 模擬函數
def simulate_from_start(start_star, restart_star, protect_start=None, buy_back_threshold=None, target=target, simulations=simulations):
    total_costs = []
    total_destroys = []
    log_file = f"log_start_{start_star}{'_protect_' + str(protect_start) if protect_start is not None else ''}{'_buyback_' + str(buy_back_threshold) if buy_back_threshold is not None else ''}.txt"
    
    # 策略描述
    strategy_desc = f"模擬策略：起始買{start_star}星卷，若破壞後買{restart_star}星卷" + \
                    (f"，從{protect_start}星開始使用防破壞" if protect_start is not None else "（無防破壞）") + \
                    (f"，下降到{buy_back_threshold}星買回{start_star}星" if buy_back_threshold is not None else "")
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"{strategy_desc}\n\n")
    
    all_costs = []  # 儲存每次模擬的總成本，用於分位數計算
    for sim in range(simulations):
        total_cost = 0
        destroy_count = 0
        current_star = start_star
        total_cost += scroll_costs[start_star]
        
        path = [f"初始購買星力{start_star}強化卷 (成本: {scroll_costs[start_star]:.2f} 楓點, 目前總成本: {total_cost:.2f})"]
        
        while current_star < target:
            use_protect = protect_start is not None and current_star >= protect_start
            cost = protect_cost if use_protect else upgrade_cost
            total_cost += cost
            
            outcome = random.random()
            p_s = probabilities[current_star]["success"]
            p_d = probabilities[current_star]["destroy"]
            p_drop = probabilities[current_star]["drop"]
            
            if outcome < p_s:
                if sim == 0:
                    path.append(f"{current_star}升{current_star+1} 成功 (成本: {cost} 楓點{' [防破壞]' if use_protect else ''}, 目前總成本: {total_cost:.2f})")
                current_star += 1
            elif outcome < p_s + p_d:
                if use_protect:
                    if sim == 0:
                        path.append(f"{current_star}升{current_star+1} 失敗，維持 (成本: {cost} 楓點 [防破壞], 目前總成本: {total_cost:.2f})")
                else:
                    total_cost += equip_compensation_cost + scroll_costs[restart_star]
                    destroy_count += 1
                    if sim == 0:
                        path.append(f"{current_star}升{current_star+1} 破壞，回到12星，購買{restart_star}星 (成本: {cost} + {equip_compensation_cost:.2f} + {scroll_costs[restart_star]:.2f} 楓點, 目前總成本: {total_cost:.2f})")
                    current_star = restart_star
            elif outcome < p_s + p_d + p_drop:
                next_star = current_star - 1  # 遵循機率表
                buy_back = buy_back_threshold is not None and next_star <= buy_back_threshold
                if sim == 0:
                    if buy_back:
                        path.append(f"{current_star}升{current_star+1} 失敗，下滑至{next_star}，買回{start_star}星 (成本: {cost} + {scroll_costs[start_star]:.2f} 楓點{' [防破壞]' if use_protect else ''}, 目前總成本: {total_cost:.2f})")
                    else:
                        path.append(f"{current_star}升{current_star+1} 失敗，下滑至{next_star} (成本: {cost} 楓點{' [防破壞]' if use_protect else ''}, 目前總成本: {total_cost:.2f})")
                current_star = next_star
                if buy_back:
                    total_cost += scroll_costs[start_star]
                    current_star = start_star
            else:
                if sim == 0:
                    path.append(f"{current_star}升{current_star+1} 失敗，維持 (成本: {cost} 楓點{' [防破壞]' if use_protect else ''}, 目前總成本: {total_cost:.2f})")
        
        all_costs.append(total_cost)
        total_costs.append(total_cost)
        total_destroys.append(destroy_count)
        
        if sim == 0:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write("單次模擬路徑與總成本：\n")
                for step in path:
                    f.write(f"{step}\n")
                f.write(f"總成本 = {total_cost:.2f} 楓點，破壞次數 = {destroy_count} 次\n")
    
    avg_cost = sum(total_costs) / simulations
    avg_destroys = sum(total_destroys) / simulations
    percentiles = {
        '10%': np.percentile(all_costs, 10),
        '25%': np.percentile(all_costs, 25),
        '50%': np.percentile(all_costs, 50),
        '75%': np.percentile(all_costs, 75),
        '90%': np.percentile(all_costs, 90)
    }
    return avg_cost, avg_destroys, percentiles, log_file

# 模擬所有策略
results = {}
protect_options = [None, 15, 16, 17, 18, 19]

for start_star in [15, 16, 17, 18, 19]:
    buy_back_options = [None] + list(range(15, start_star))
    for protect_start in protect_options:
        for buy_back_threshold in buy_back_options:
            strategy_key = f"{start_star}_protect_{protect_start if protect_start is not None else 'none'}_buyback_{buy_back_threshold if buy_back_threshold is not None else 'none'}"
            if strategy_key in results:
                continue
            
            print(f"\n模擬策略：起始買{start_star}星卷，若破壞後買{start_star}星卷" + 
                  (f"，從{protect_start}星開始防破壞" if protect_start is not None else "（無防破壞）") + 
                  (f"，下降到{buy_back_threshold}星買回{start_star}星" if buy_back_threshold is not None else ""))
            avg_cost, avg_destroys, percentiles, log_file = simulate_from_start(start_star, start_star, protect_start, buy_back_threshold, target, simulations)
            results[strategy_key] = (avg_cost, avg_destroys, percentiles, log_file)
            print(f"平均成本 = {avg_cost:.2f} 楓點")
            print(f"平均破壞次數 = {avg_destroys:.2f} 次")
            print(f"模擬路徑已寫入檔案：{log_file}")

# 直接買20星
print(f"\n模擬策略：起始買20星卷，若破壞後買20星卷（無防破壞）")
avg_cost = scroll_costs[20]
avg_destroys = 0
percentiles = {'10%': avg_cost, '25%': avg_cost, '50%': avg_cost, '75%': avg_cost, '90%': avg_cost}
results["20_protect_none_buyback_none"] = (avg_cost, avg_destroys, percentiles, "log_start_20.txt")
log_file = "log_start_20.txt"
with open(log_file, 'w', encoding='utf-8') as f:
    f.write("模擬策略：起始買20星卷，若破壞後買20星卷（無防破壞）\n\n")
    f.write("單次模擬路徑與總成本：\n")
    f.write(f"初始購買星力20強化卷 (成本: {scroll_costs[20]:.2f} 楓點, 目前總成本: {scroll_costs[20]:.2f})\n")
    f.write(f"總成本 = {scroll_costs[20]:.2f} 楓點，破壞次數 = 0 次\n")
print(f"平均成本 = {avg_cost:.2f} 楓點")
print(f"平均破壞次數 = {avg_destroys:.2f} 次")
print(f"模擬路徑已寫入檔案：{log_file}")

# 整理所有模擬情境（按層次排序）
print("\n=== 所有模擬情境 ===")
def sort_key(item):
    strategy_key = item[0]
    parts = strategy_key.split('_protect_')
    start_star = int(parts[0])
    rest = parts[1].split('_buyback_')
    protect_part = rest[0]
    protect_value = -1 if protect_part == 'none' else int(protect_part)
    buy_back_part = rest[1]
    buy_back_value = -1 if buy_back_part == 'none' else int(buy_back_part)
    return (start_star, protect_value, buy_back_value, item[1][0])

for strategy_key, (avg_cost, avg_destroys, percentiles, log_file) in sorted(results.items(), key=sort_key):
    parts = strategy_key.split('_protect_')
    start_star = parts[0]
    rest = parts[1].split('_buyback_')
    protect_part = rest[0]
    buy_back_part = rest[1]
    desc = f"起始買{start_star}星卷，若破壞後買{start_star}星卷" + \
           (f"，從{protect_part}星開始防破壞" if protect_part != 'none' else "（無防破壞）") + \
           (f"，下降到{buy_back_part}星買回{start_star}星" if buy_back_part != 'none' else "")
    print(f"{desc}：平均成本 = {avg_cost:.2f} 楓點，平均破壞次數 = {avg_destroys:.2f} 次")

# 前三佳策略
print("\n=== 前三佳策略 ===")
top_strategies = sorted(results.items(), key=lambda x: x[1][0])[:3]
for strategy_key, (avg_cost, avg_destroys, percentiles, log_file) in top_strategies:
    parts = strategy_key.split('_protect_')
    start_star = parts[0]
    rest = parts[1].split('_buyback_')
    protect_part = rest[0]
    buy_back_part = rest[1]
    desc = f"起始買{start_star}星卷，若破壞後買{start_star}星卷" + \
           (f"，從{protect_part}星開始防破壞" if protect_part != 'none' else "（無防破壞）") + \
           (f"，下降到{buy_back_part}星買回{start_star}星" if buy_back_part != 'none' else "")
    print(f"最佳策略：{desc}")
    print(f"平均成本 = {avg_cost:.2f} 楓點")
    print(f"平均破壞次數 = {avg_destroys:.2f} 次")
    print(f"  前10% = {percentiles['10%']:.2f} 楓點")
    print(f"  前25% = {percentiles['25%']:.2f} 楓點")
    print(f"  中位數 = {percentiles['50%']:.2f} 楓點")
    print(f"  後75% = {percentiles['75%']:.2f} 楓點")
    print(f"  後90% = {percentiles['90%']:.2f} 楓點")
    print()
