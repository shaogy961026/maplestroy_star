import random

# 機率表
probabilities = {
    15: {"success": 0.30, "drop": 0.00, "hold": 0.70},
    16: {"success": 0.30, "drop": 0.56, "hold": 0.14},
    17: {"success": 0.30, "drop": 0.49, "hold": 0.21},
    18: {"success": 0.30, "drop": 0.42, "hold": 0.28},
    19: {"success": 0.30, "drop": 0.42, "hold": 0.28},
}

scroll_prices = {15: 71888888, 16: 218888888, 17: 2388888888, 18: 6394500000, 19: 18555555555, 20: 50488888888}
X = 6
scroll_costs = {star: price / (10**8 / X) for star, price in scroll_prices.items()}
upgrade_cost = 50

# 計算單步期望成本
def calc_single_step_cost(start, prev_costs):
    if start not in probabilities:
        return 0
    buy_cost = scroll_costs[start + 1]
    p_s = probabilities[start]["success"]
    p_d = probabilities[start]["drop"]
    p_h = probabilities[start]["hold"]
    C_prev = prev_costs[start - 1] if start - 1 in prev_costs else scroll_costs[start]
    enhance_cost = (50 * (p_s + p_d + p_h) + p_d * C_prev) / p_s
    print(f"計算 {start} 到 {start+1}：")
    print(f"  C_prev = {C_prev:.2f}")
    print(f"  強化成本 = (50 * ({p_s} + {p_d} + {p_h}) + {p_d} * {C_prev:.2f}) / {p_s} = {enhance_cost:.2f}")
    print(f"  購買成本 = {buy_cost:.2f}")
    print(f"  選擇：{'強化' if enhance_cost < buy_cost else '購買'}")
    return min(enhance_cost, buy_cost)

# 計算所有單步成本
def calc_all_step_costs():
    costs = {}
    optimal_costs = {}
    print("\n計算單步成本過程：")
    for star in range(15, 20):
        costs[star] = calc_single_step_cost(star, optimal_costs)
        optimal_costs[star] = costs[star]
    return costs

# 主計算邏輯（動態規劃）
step_costs = calc_all_step_costs()
optimal_costs = {}

# 1到15的起點
print("\n計算1到15的最優起始星卷：")
optimal_costs[15] = (scroll_costs[15], 15)
print(f"直接購買15星：總成本 = {scroll_costs[15]:.2f}")

# 從16到20逐步計算
for target in range(16, 21):
    print(f"\n計算1到{target}的最優起始星卷：")
    prev_cost, prev_start = optimal_costs[target - 1]
    total_from_prev = prev_cost + step_costs[target - 1]
    print(f"  從 {prev_start} 星到 {target}：")
    print(f"    前一階段成本 = {prev_cost:.2f}")
    print(f"    這一步成本 ({target-1} 到 {target}) = {step_costs[target-1]:.2f}")
    print(f"    總成本 = {prev_cost:.2f} + {step_costs[target-1]:.2f} = {total_from_prev:.2f}")
    
    direct_buy_cost = scroll_costs[target]
    print(f"  直接購買 {target} 星：總成本 = {direct_buy_cost:.2f}")
    
    if total_from_prev < direct_buy_cost:
        best_cost = total_from_prev
        best_start = prev_start
        print(f"  選擇從 {prev_start} 星繼續，成本 = {best_cost:.2f}")
    else:
        best_cost = direct_buy_cost
        best_start = target
        print(f"  選擇直接購買 {target} 星，成本 = {best_cost:.2f}")
    
    optimal_costs[target] = (best_cost, best_start)

print("\n從1星到各階段的最優成本與起始星卷：")
for target, (cost, start) in optimal_costs.items():
    print(f"1星到{target}星：總成本 = {cost:.2f} 楓點，起始購買星力{start}強化卷")

# 模擬（修正為期望成本一致）
def simulate_upgrade(target=20, simulations=100000):
    total_costs = []
    sample_path = None
    sample_cost = None
    
    for sim in range(simulations):
        total_cost = 0
        path = ["初始1星"]
        
        _, best_start = optimal_costs[target]
        total_cost += scroll_costs[best_start]
        current_star = best_start
        path.append(f"購買星力{best_start}強化卷 (成本: {scroll_costs[best_start]:.2f} 楓點)")
        
        while current_star < target:
            enhance_cost = step_costs[current_star]
            buy_cost = scroll_costs[current_star + 1]
            
            if enhance_cost < buy_cost:
                total_cost += upgrade_cost
                outcome = random.random()
                p_s = probabilities[current_star]["success"]
                p_d = probabilities[current_star]["drop"]
                p_h = probabilities[current_star]["hold"]
                
                if outcome < p_s:
                    path.append(f"{current_star}升{current_star+1} 成功 (成本: 50 楓點)")
                    current_star += 1
                elif outcome < p_s + p_d:
                    path.append(f"{current_star}升{current_star+1} 失敗，下滑至{current_star-1} (成本: 50 楓點)")
                    current_star -= 1
                else:
                    path.append(f"{current_star}升{current_star+1} 失敗，維持 (成本: 50 楓點)")
            else:
                total_cost += buy_cost
                path.append(f"直接購買星力{current_star+1}強化卷 (成本: {buy_cost:.2f} 楓點)")
                current_star += 1
        
        total_costs.append(total_cost)
        if sim == 0:
            sample_path = path
            sample_cost = total_cost
    
    avg_cost = sum(total_costs) / simulations
    print(f"\n模擬 {simulations} 次，平均成本 = {avg_cost:.2f} 楓點")
    print("\n單次模擬路徑與總成本：")
    for step in sample_path:
        print(step)
    print(f"總成本 = {sample_cost:.2f} 楓點")

simulate_upgrade()
