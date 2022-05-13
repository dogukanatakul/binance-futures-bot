import time

import termtables as tt


def get_diff(previous, current):
    try:
        if previous == current:
            percentage = 0
        elif previous < 0 and current < 0:
            percentage = ((previous - current) / min(previous, current)) * 100
        elif previous < 0 and current > 0:
            percentage = (((max(previous, current) - min(previous, current)) / max(previous, current)) * 100)
        elif previous > 0 and current < 0:
            percentage = (((max(previous, current) - min(previous, current)) / max(previous, current)) * 100) * -1
        elif previous > current:
            percentage = (((previous - current) / previous) * 100) * -1
        else:
            percentage = ((current - previous) / current) * 100
    except ZeroDivisionError:
        percentage = float('inf')
    return percentage


def terminalTable(data):
    if len(data) > 0:
        header = list(data[0].keys())
        resultData = []
        for d in data:
            resultData.append(list(d.values()))
        tt.print(
            list(resultData),
            header=header,
        )



profits = [
    0.02,
    0.05,
    0.1,
    0.2,
    0.3,
    0.2,
    0.4,
    0.1,
    0.58,
    0.30,
    0.28,
    0.25,
    0.35,
    0.40,
    0.65,
    0.60,
    0.58,
    0.70,
    0.65,
    0.40,
    0.45,
    0.56,
    0.70,
    0.75,
    0.80,
    0.80,
    0.60,
]

profitDiff = []
profitDiffAverage = False

maxProfit = 0
minProfit = 0
beforeProfit = None
results = []
turn = True
trigger = None
maxDamage = 0
currentDiff = 0

for profit in profits:
    if beforeProfit is not None:
        if profit != beforeProfit:
            profitDiff.append(round(abs(get_diff(profit, beforeProfit)), 2))
            profitDiffAverage = abs(round(sum(profitDiff) / len(profitDiff), 2))
    if profit > 0:
        maxDamage = 0
        if profit > maxProfit:
            maxProfit = profit
        elif abs(get_diff(profit, maxProfit)) > profitDiffAverage and len(profitDiff) > 20:
            turn = False
            trigger = "MaxTrigger"
        else:
            if len(profitDiff) > 20:
                currentDiff = get_diff(profit, beforeProfit)
                if currentDiff > profitDiffAverage:
                    turn = False
                    trigger = "AvarageTrigger"

    elif profit <= -5:
        maxDamage += 1
        if maxDamage == 2:
            turn = False
            trigger = "DamageTrigger"
    results.append({
        'profit': profit,
        'maxProfit': maxProfit,
        'profitDiffAverage': profitDiffAverage,
        'currentDiff': currentDiff,
        'turn': turn,
        'trigger': trigger
    })
    beforeProfit = profit

terminalTable(results)
