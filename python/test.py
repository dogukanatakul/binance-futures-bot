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
    -5,
    0,
    1,
    3,
    -2,
    -3,
    -5,
    -5.1,
    60,
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

for profit in profits:
    if beforeProfit is not None:
        profitDiff.append(round(get_diff(profit, beforeProfit), 1))
        profitDiffAverage = abs(round(sum(profitDiff) / len(profitDiff), 1))
    if profit > 0:
        maxDamage = 0
        if profit > maxProfit:
            maxProfit = profit
        elif get_diff(profit, maxProfit) > profitDiffAverage and profit >= 5:
            turn = False
            trigger = "MaxTrigger"
        else:
            if profitDiffAverage and profit >= 5:
                currentDiff = get_diff(profit, beforeProfit)
                if currentDiff > profitDiffAverage:
                    turn = False
                    trigger = "AvarageTrigger"
        beforeProfit = profit
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

terminalTable(results)
