import random  # 匯入 random 模組，用於模擬強化過程中的隨機結果

# 定義機率表函數，根據活動狀態返回不同星級的強化機率
def get_probabilities(event_active=False):
    # 基礎機率表，鍵為星級，值為字典，包含成功、下降和維持的機率
    base_probabilities = {
        15: {"success": 0.30, "drop": 0.00, "hold": 0.70},  # 15星：30%成功，0%下降，70%維持
        16: {"success": 0.30, "drop": 0.56, "hold": 0.14},  # 16星：30%成功，56%下降，14%維持
        17: {"success": 0.30, "drop": 0.49, "hold": 0.21},  # 17星：30%成功，49%下降，21%維持
        18: {"success": 0.30, "drop": 0.42, "hold": 0.28},  # 18星：30%成功，42%下降，28%維持
        19: {"success": 0.30, "drop": 0.42, "hold": 0.28},  # 19星：30%成功，42%下降，28%維持
    }
    # 若活動啟用，修改15星的機率為100%成功，無下降或維持
    if event_active:
        base_probabilities[15] = {"success": 1.00, "drop": 0.00, "hold": 0.00}
    return base_probabilities  # 返回機率表

# 定義星卷的基礎價格（單位：楓幣），鍵為星級，值為價格
scroll_prices = {
    15: 71888888,      # 15星卷價格
    16: 218888888,     # 16星卷價格
    17: 2388888888,    # 17星卷價格
    18: 6394500000,    # 18星卷價格
    19: 18555555555,   # 19星卷價格
    20: 50488888888    # 20星卷價格
}

# 設定換算比例，1億楓幣等於多少楓點，此處預設為6
points_per_billion = 6

# 將星卷價格從楓幣轉換為楓點，使用公式：價格 * points_per_billion / 10^8
scroll_costs = {star: price * points_per_billion / 10**8 for star, price in scroll_prices.items()}

# 定義基礎強化成本（非活動時，每次強化花費50楓點）
base_upgrade_cost = 50

# 定義活動強化成本（活動啟用時，15到16星每次強化花費9楓點）
event_upgrade_cost = 9

# 活動開關，True表示啟用活動，False表示不啟用
event_active = True  # 設為 True 啟用活動

# 根據活動狀態取得機率表
probabilities = get_probabilities(event_active)

# 輸出程式初始條件，顯示活動狀態、價格和換算結果
print("=== 程式輸入條件 ===")
print(f"活動狀態：{'啟用' if event_active else '未啟用'}（15星強化成功率100%，每次9楓點）")  # 顯示活動是否啟用
print("星卷價格（楓幣）：")  # 標題
for star, price in scroll_prices.items():
    print(f"{star}星：{price:,} 楓幣")  # 列出每個星級的楓幣價格，使用千分位分隔符
print("\n楓點與楓幣換算：")  # 換算說明標題
print(f"換算比例：1億楓幣 = {points_per_billion} 楓點")  # 顯示換算比例
print(f"轉換公式：價格(楓幣) * {points_per_billion} / 10^8")  # 顯示轉換公式
print("\n星卷價格（轉換後，楓點）：")  # 轉換後價格標題
for star, cost in scroll_costs.items():
    print(f"{star}星：{cost:.2f} 楓點")  # 列出每個星級的楓點價格，保留兩位小數
print(f"\n單次強化成本：{event_upgrade_cost} 楓點（15到16星，活動啟用時），其他星級或活動未啟用時為 {base_upgrade_cost} 楓點")  # 顯示強化成本說明
print("=================\n")  # 分隔線

# 計算從某星級到下一星級的單步最優成本
def calc_single_step_cost(start, prev_costs, event_active=False):
    # 若起始星級不在機率表中，返回0（例如20星無法再強化）
    if start not in probabilities:
        return 0
    buy_cost = scroll_costs[start + 1]  # 直接購買下一星卷的成本
    p_s = probabilities[start]["success"]  # 成功機率
    p_d = probabilities[start]["drop"]  # 下降機率
    p_h = probabilities[start]["hold"]  # 維持機率
    # 前一星級成本，若prev_costs中有則使用，否則用當前星級的購買成本
    C_prev = prev_costs[start - 1] if start - 1 in prev_costs else scroll_costs[start]
    # 根據活動狀態決定單次強化成本，15星活動時為9，其他為50
    current_upgrade_cost = event_upgrade_cost if event_active and start == 15 else base_upgrade_cost
    # 計算強化期望成本
    if event_active and start == 15:
        enhance_cost = current_upgrade_cost  # 活動時15星100%成功，直接用強化成本
    else:
        # 期望成本公式：(單次成本 * 總機率 + 下降時回補成本) / 成功機率
        enhance_cost = (current_upgrade_cost * (p_s + p_d + p_h) + p_d * C_prev) / p_s
    # 輸出計算過程
    print(f"計算 {start} 到 {start+1}：")
    print(f"  C_prev = {C_prev:.2f}")  # 前一星級成本
    print(f"  強化成本 = {enhance_cost:.2f} {'(活動：100%成功)' if event_active and start == 15 else ''}")  # 強化成本，若活動則標註
    print(f"  購買成本 = {buy_cost:.2f}")  # 購買成本
    print(f"  選擇：{'強化' if enhance_cost < buy_cost else '購買'}")  # 比較後選擇較便宜的策略
    return min(enhance_cost, buy_cost)  # 返回強化或購買中較低的成本

# 計算所有星級的單步最優成本
def calc_all_step_costs(event_active=False):
    costs = {}  # 儲存每步的最優成本
    optimal_costs = {}  # 儲存前一星級的最優成本，用於計算C_prev
    print("\n計算單步成本過程：")  # 標題
    # 從15星到19星逐一計算
    for star in range(15, 20):
        costs[star] = calc_single_step_cost(star, optimal_costs, event_active)  # 計算單步成本
        optimal_costs[star] = costs[star]  # 更新最優成本表
    return costs  # 返回所有單步成本

# 計算並儲存所有單步成本
step_costs = calc_all_step_costs(event_active)

# 儲存從1星到各目標星級的最優成本和起點
optimal_costs = {}

# 計算從1星到15星的最優成本（直接購買15星）
print("\n計算1到15的最優起始星卷：")
optimal_costs[15] = (scroll_costs[15], 15)  # 成本和起點設為15星
print(f"直接購買15星：總成本 = {scroll_costs[15]:.2f}")

# 動態規劃計算從1星到16-20星的最優成本和起點
for target in range(16, 21):
    print(f"\n計算1到{target}的最優起始星卷：")  # 標題
    prev_cost, prev_start = optimal_costs[target - 1]  # 前一階段的成本和起點
    total_from_prev = prev_cost + step_costs[target - 1]  # 從前一階段繼續的總成本
    print(f"  從 {prev_start} 星到 {target}：")
    print(f"    前一階段成本 = {prev_cost:.2f}")  # 前一階段成本
    print(f"    這一步成本 ({target-1} 到 {target}) = {step_costs[target-1]:.2f}")  # 單步成本
    print(f"    總成本 = {prev_cost:.2f} + {step_costs[target-1]:.2f} = {total_from_prev:.2f}")  # 總和
    direct_buy_cost = scroll_costs[target]  # 直接購買目標星級的成本
    print(f"  直接購買 {target} 星：總成本 = {direct_buy_cost:.2f}")
    # 比較從前一階段繼續 vs 直接購買，選擇較便宜的策略
    if total_from_prev < direct_buy_cost:
        best_cost = total_from_prev
        best_start = prev_start
        print(f"  選擇從 {prev_start} 星繼續，成本 = {best_cost:.2f}")
    else:
        best_cost = direct_buy_cost
        best_start = target
        print(f"  選擇直接購買 {target} 星，成本 = {best_cost:.2f}")
    optimal_costs[target] = (best_cost, best_start)  # 更新最優成本和起點

# 輸出從1星到各階段的最優結果
print("\n從1星到各階段的最優成本與起始星卷：")
for target, (cost, start) in optimal_costs.items():
    print(f"1星到{target}星：總成本 = {cost:.2f} 楓點，起始購買星力{start}強化卷")

# 模擬從1星到目標星級的強化過程，驗證平均成本
def simulate_upgrade(target=20, simulations=100000, event_active=False):
    total_costs = []  # 儲存每次模擬的總成本
    sample_path = None  # 儲存第一次模擬的路徑
    sample_cost = None  # 儲存第一次模擬的成本
    
    # 執行指定次數的模擬
    for sim in range(simulations):
        total_cost = 0  # 單次模擬的總成本
        path = ["初始1星"]  # 記錄本次模擬的路徑
        
        # 從最優起點開始
        _, best_start = optimal_costs[target]
        total_cost += scroll_costs[best_start]  # 加上購買起點星卷的成本
        current_star = best_start  # 當前星級設為起點
        path.append(f"購買星力{best_start}強化卷 (成本: {scroll_costs[best_start]:.2f} 楓點)")
        
        # 當前星級未達目標時，繼續強化或購買
        while current_star < target:
            enhance_cost = step_costs[current_star]  # 強化到下一星的期望成本
            buy_cost = scroll_costs[current_star + 1]  # 直接購買下一星的成本
            
            # 根據動態規劃結果選擇策略
            if enhance_cost < buy_cost:
                # 若選擇強化，根據活動狀態決定成本
                current_upgrade_cost = event_upgrade_cost if event_active and current_star == 15 else base_upgrade_cost
                total_cost += current_upgrade_cost  # 加上單次強化成本
                outcome = random.random()  # 隨機生成結果（0到1之間）
                p_s = probabilities[current_star]["success"]  # 成功機率
                p_d = probabilities[current_star]["drop"]  # 下降機率
                p_h = probabilities[current_star]["hold"]  # 維持機率
                
                # 根據隨機結果決定強化結局
                if outcome < p_s:
                    path.append(f"{current_star}升{current_star+1} 成功 (成本: {current_upgrade_cost} 楓點)")
                    current_star += 1  # 成功，星級加1
                elif outcome < p_s + p_d:
                    path.append(f"{current_star}升{current_star+1} 失敗，下滑至{current_star-1} (成本: {current_upgrade_cost} 楓點)")
                    current_star -= 1  # 下降，星級減1
                else:
                    path.append(f"{current_star}升{current_star+1} 失敗，維持 (成本: {current_upgrade_cost} 楓點)")  # 維持，星級不變
            else:
                total_cost += buy_cost  # 加上購買成本
                path.append(f"直接購買星力{current_star+1}強化卷 (成本: {buy_cost:.2f} 楓點)")
                current_star += 1  # 購買後星級加1
        
        total_costs.append(total_cost)  # 記錄本次總成本
        # 第一次模擬時，儲存路徑和成本作為範例
        if sim == 0:
            sample_path = path
            sample_cost = total_cost
    
    # 計算平均成本
    avg_cost = sum(total_costs) / simulations
    print(f"\n模擬 {simulations} 次，平均成本 = {avg_cost:.2f} 楓點")  # 輸出平均成本
    print("\n單次模擬路徑與總成本：")  # 範例路徑標題
    for step in sample_path:
        print(step)  # 輸出第一次模擬的每一步
    print(f"總成本 = {sample_cost:.2f} 楓點")  # 輸出第一次模擬的總成本

# 執行模擬，預設目標20星，10萬次模擬
simulate_upgrade(event_active=event_active)
