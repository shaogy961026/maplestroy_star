import random
import json
import os
from tqdm import tqdm

# 遊戲參數（楓幣換算成楓點）
scroll_costs_maple = {
    15: 81555555,   # 楓幣
    16: 244444444,
    17: 2396666666,
    18: 5466666666,
    19: 17776888888,
    20: 48888888888
}
equip_cost_maple = 30000000  # 裝備價格（楓幣）
conversion_rate = 6 / 100000000  # 1億楓幣 = 6楓點

scroll_costs = {star: cost * conversion_rate for star, cost in scroll_costs_maple.items()}
equip_compensation_cost = equip_cost_maple * conversion_rate
upgrade_cost = 9
protect_cost = 50

probabilities = {
    15: {"success": 1.0000, "destroy": 0.0000, "drop": 0.0000},
    16: {"success": 0.3000, "destroy": 0.1400, "drop": 0.5600},
    17: {"success": 0.3000, "destroy": 0.2100, "drop": 0.4900},
    18: {"success": 0.3000, "destroy": 0.2800, "drop": 0.4200},
    19: {"success": 0.3000, "destroy": 0.2800, "drop": 0.4200}
}
target = 20
MAX_STEPS = 1000

STRATEGY_FILE = "strategies.json"
BEST_HISTORY_FILE = "best_history.json"
LOG_FILE = "simulation_log.txt"

def simulate_game(strategy, log=False, sim_num=0):
    current_star = strategy.get("start_star", 15)
    total_cost = scroll_costs[current_star]  # 初始成本
    consecutive_drops = 0
    destroy_count = 0
    steps = 0
    log_entries = [f"模擬 #{sim_num} - 起始星級: {current_star}星, 初始成本: {total_cost:.2f}"]

    while current_star < target and steps < MAX_STEPS:
        steps += 1

        if consecutive_drops == 2:
            total_cost += upgrade_cost  # 連掉補償成本
            log_entries.append(f"Step {steps}: 連掉補償 (連掉={consecutive_drops}), {current_star} -> {current_star+1}, 成本: {upgrade_cost}, 總成本: {total_cost:.2f}")
            current_star += 1
            consecutive_drops = 0
            continue

        rule = strategy.get(str(current_star), {"base_action": "normal", "drop_threshold": 1, "rebuy_target": 15})
        action = rule["base_action"]
        if consecutive_drops >= rule["drop_threshold"]:
            action = f"rebuy_{rule['rebuy_target']}"

        old_star = current_star
        cost = 0

        if action.startswith("rebuy_"):
            new_star = int(action.split("_")[1])
            cost = scroll_costs[new_star]
            total_cost += cost  # 重買成本
            current_star = new_star
            consecutive_drops = 0
            log_entries.append(f"Step {steps}: {old_star}星 rebuy -> {new_star}星, 成本: {cost:.2f}, 總成本: {total_cost:.2f}, 連掉重置為0")
        else:
            cost = protect_cost if action == "protect" else upgrade_cost
            total_cost += cost  # 強化成本

            outcome = random.random()
            p_s = probabilities[current_star]["success"]
            p_d = probabilities[current_star]["destroy"]
            p_drop = probabilities[current_star]["drop"]

            if outcome < p_s:
                current_star += 1
                consecutive_drops = 0
                log_entries.append(f"Step {steps}: {old_star}星 {action} 成功 -> {current_star}星, 成本: {cost}, 總成本: {total_cost:.2f}, 連掉重置為0")
            elif outcome < p_s + p_d:
                if action == "protect":
                    current_star = max(current_star - 1, 15)
                    log_entries.append(f"Step {steps}: {old_star}星 {action} 失敗, 掉至 {current_star}星, 成本: {cost}, 總成本: {total_cost:.2f}, 連掉={consecutive_drops+1}")
                    consecutive_drops += 1
                else:
                    destroy_cost = equip_compensation_cost + scroll_costs[strategy.get("start_star", 15)]
                    total_cost += destroy_cost  # 破壞+重買成本
                    current_star = strategy.get("start_star", 15)
                    destroy_count += 1
                    log_entries.append(f"Step {steps}: {old_star}星 {action} 破壞, 重買 {current_star}星, 成本: {cost + destroy_cost:.2f}, 總成本: {total_cost:.2f}, 連掉重置為0")
                    consecutive_drops = 0
            elif outcome < p_s + p_d + p_drop:
                current_star = max(current_star - 1, 15)
                consecutive_drops += 1
                log_entries.append(f"Step {steps}: {old_star}星 {action} 失敗, 掉至 {current_star}星, 成本: {cost}, 總成本: {total_cost:.2f}, 連掉={consecutive_drops}")
            else:
                log_entries.append(f"Step {steps}: {old_star}星 {action} 失敗, 維持 {current_star}星, 成本: {cost}, 總成本: {total_cost:.2f}, 連掉={consecutive_drops}")
                consecutive_drops = 0

    if steps >= MAX_STEPS:
        total_cost += 9999999999  # 懲罰成本
        log_entries.append(f"Step {steps}: 超過步數限制, 懲罰成本 +100000, 總成本: {total_cost:.2f}")

    if log:
        log_entries.append(f"最終結果: 總成本={total_cost:.2f}, 破壞次數={destroy_count}")
        return {"total_cost": total_cost, "destroy_count": destroy_count, "log_entries": log_entries}
    return {"total_cost": total_cost, "destroy_count": destroy_count}

def generate_strategy():
    return {
        "start_star": random.randint(15, 19),
        **{str(star): {
            "base_action": random.choice(["normal", "protect"]),
            "drop_threshold": random.randint(0, 2),
            "rebuy_target": random.randint(15, 19)
        } for star in range(15, 20)}
    }

def load_strategies():
    if os.path.exists(STRATEGY_FILE):
        with open(STRATEGY_FILE, "r") as f:
            loaded = json.load(f)
            if len(loaded) == 100:
                return loaded
            else:
                print(f"載入的策略數量 ({len(loaded)}) 不符合要求，重新生成100個新策略...")
    else:
        print("未找到strategies.json，生成100個新策略...")
    return [{"strategy": generate_strategy(), "total_cost": 0, "count": 0} for _ in range(100)]

def save_strategies(strategies):
    with open(STRATEGY_FILE, "w") as f:
        json.dump(strategies, f, indent=4)

def load_best_history():
    if os.path.exists(BEST_HISTORY_FILE):
        with open(BEST_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"best_cost": float("inf"), "best_strategy": None, "history": []}

def save_best_history(best_cost, best_strategy, history):
    with open(BEST_HISTORY_FILE, "w") as f:
        json.dump({"best_cost": best_cost, "best_strategy": best_strategy, "history": history}, f, indent=4)

def run_simulation():
    num_strategies = 100
    sims_per_strategy = 100000

    strategies = load_strategies()
    print(f"當前策略數量: {len(strategies)}")

    best_history = load_best_history()
    global_best_cost = best_history["best_cost"]
    global_best_strategy = best_history["best_strategy"]
    history = best_history["history"]

    total_completed = 0
    all_strategies_avg_cost = 0
    log_data = []

    for i in range(num_strategies):
        strategy_cost = 0
        with tqdm(total=sims_per_strategy, desc=f"策略 {i+1}/{num_strategies}") as pbar:
            for j in range(sims_per_strategy):
                log = (i == 0 and j < 5)  # 前5筆LOG
                if log:
                    result = simulate_game(strategies[i]["strategy"], log=True, sim_num=j+1)
                    strategy_cost += result["total_cost"]
                    log_data.append(result["log_entries"])
                else:
                    result = simulate_game(strategies[i]["strategy"])
                    strategy_cost += result["total_cost"]
                total_completed += 1
                pbar.update(1)
                if total_completed % 1000000 == 0:
                    print(f"總進度: {total_completed}/{num_strategies * sims_per_strategy} ({(total_completed/(num_strategies * sims_per_strategy))*100:.2f}%)")
        strategies[i]["total_cost"] += strategy_cost
        strategies[i]["count"] += sims_per_strategy
        all_strategies_avg_cost += (strategy_cost / sims_per_strategy)

    overall_avg_cost = all_strategies_avg_cost / num_strategies
    print(f"本次100個策略的整體平均成本 (每個策略100,000次): {overall_avg_cost:.2f} 楓點")

    strategies.sort(key=lambda x: x["total_cost"] / x["count"])
    best_strategy = strategies[0]
    avg_cost = best_strategy["total_cost"] / best_strategy["count"]
    print(f"本次模擬完成！最佳平均成本 (基於100,000次): {avg_cost:.2f} 楓點")
    print("本次最佳策略：")
    print(f"起始星級: {best_strategy['strategy']['start_star']}")
    for star, rule in best_strategy["strategy"].items():
        if star != "start_star":
            print(f"{star}星: 基礎={rule['base_action']}, 連掉閾值={rule['drop_threshold']}, 重買目標={rule['rebuy_target']}")

    if avg_cost < global_best_cost:
        global_best_cost = avg_cost
        global_best_strategy = best_strategy["strategy"]
        print(f"發現新最佳！全局最佳平均成本更新為: {global_best_cost:.2f} 楓點")
    history.append({"run": len(history) + 1, "avg_cost": avg_cost})
    save_best_history(global_best_cost, global_best_strategy, history)

    top_strategies = strategies[:int(num_strategies * 0.2)]
    new_strategies = top_strategies.copy()
    while len(new_strategies) < num_strategies:
        parent = random.choice(top_strategies)
        new_strategy = {k: v.copy() if isinstance(v, dict) else v for k, v in parent["strategy"].items()}
        if random.random() < 0.1:
            new_strategy["start_star"] = random.randint(15, 19)
        for star in new_strategy:
            if star != "start_star" and random.random() < 0.1:
                if random.random() < 0.33:
                    new_strategy[star]["base_action"] = random.choice(["normal", "protect"])
                elif random.random() < 0.66:
                    new_strategy[star]["drop_threshold"] = random.randint(0, 2)
                else:
                    new_strategy[star]["rebuy_target"] = random.randint(15, 19)
        new_strategies.append({"strategy": new_strategy, "total_cost": 0, "count": 0})
    strategies = new_strategies

    save_strategies(strategies)
    with open(LOG_FILE, "w") as f:
        for log_entries in log_data:
            f.write("\n".join(log_entries) + "\n\n")
    print(f"已儲存 {len(strategies)} 個策略至 {STRATEGY_FILE}")
    print(f"前5筆模擬路徑已儲存至 {LOG_FILE}")

if __name__ == "__main__":
    run_simulation()
