import time

import termtables as tt

print(round((5.32 / 100) * float(1.5), 2))
time.sleep(999)

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
    0.01,
    0.03,
    0.02,
    0.01,
    0.01,
    0.02,
    0.01,
    0.03,
    0.01,
    0.02,
    0.01,
    0.03,
    0.04,
    0.01,
    0.06,
    0.02,
    0.03,
    0.05,
    0.06,
    0.06,
    0.07,
    0.09,
    0.11,
    0.12,
    0.15,
    0.15,
    0.12,
    0.15,
    0.11,
    0.10,
    0.12,
    0.13,
    0.15,
    0.11,
    0.10,
    0.12,
    0.15,
    0.16,
    0.17,
    0.19,
    0.19,
    0.18,
    0.19,
    0.20,
    0.21,
    0.15,
    0.13,
    0.11,
    0.10,
    0.11,
    0.12,
    0.15,
    0.13,
    0.15,
    0.16,
    0.17,
    0.19,
    0.25,
    0.30,
    0.33,
    0.30,
    0.25,
    0.26,
    0.26,
    0.26,
    0.21,
    0.20,
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
maxTriggerCount = 0
profitss = []

for profit in profits:
    if beforeProfit is not None:
        if profit != beforeProfit:
            diffCurrent = round(abs(get_diff(profit, beforeProfit)), 2)
            if diffCurrent not in profitDiff:
                profitDiff.append(diffCurrent)
                profitDiffAverage = abs(round(sum(profitDiff) / len(profitDiff), 2))
    if profit > 0:
        if profit not in profitss:
            profitss.append(profit)

        maxDamage = 0
        if profit > maxProfit:
            maxProfit = profit
            maxTriggerCount = 0
        elif abs(get_diff(profit, maxProfit)) > profitDiffAverage and len(profitss) >= 15:
            maxTriggerCount += 1
            if maxTriggerCount >= 2:
                turn = False
                trigger = "MaxTrigger"
        else:
            maxTriggerCount = 0

    elif profit <= -5:
        maxDamage += 1
        if maxDamage == 2:
            turn = False
            trigger = "DamageTrigger"
    results.append({
        'profit': profit,
        'maxProfit': maxProfit,
        'profitDiffAverage': profitDiffAverage,
        'turn': turn,
        'trigger': trigger
    })
    beforeProfit = profit

terminalTable(results)
