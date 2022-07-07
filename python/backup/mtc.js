//@version=3

study("MTC", shorttitle="MTC", overlay=true)


MFirst = input(1,title="M")
TFirst = input(1,title="T")
signal = input(11,title="Signal")




BRS = (((close[1] - sma(low, signal))/(sma(high, signal)-sma(low, signal)))*100)*1
M = 2.5 / 3 * MFirst + 0.5 / 3 * BRS
T = 2.5 / 3 * TFirst + 0.5 / 3 * M
C = 3 * M - 2 * T


plot(BRS, color=orange)
plot(M, color=lime)
plot(T, color=fuchsia)
plot(C, color=silver)


bgcolor(C>M? green : red, transp=70)
