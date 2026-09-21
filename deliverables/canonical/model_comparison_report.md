BUFN741 — Markowitz vs. Single-Index Model Comparison

Scope: dedicated cross-model comparison report. It complements `markowitz_report.md` and `sim_report.md` and does not replace either model-specific report.

Sample alignment

- Markowitz comparison sample: 2006-05 through 2026-07, N=243.
- SIM common sample: 2006-05 through 2026-07, N=243.
The direct comparison uses exactly the same observations for both models, so sample timing does not contaminate the model differences.

All portfolio calculations use monthly units. Displayed expected returns, volatilities and Sharpe ratios are annualized. CAL and tangency calculations use the configured fixed annual RF of 4.50%.

Experiment 1 — Covariance-model effect only

Markowitz and SIM use an exactly identical expected-return vector. Markowitz uses the full sample covariance matrix; SIM uses the single-index implied covariance matrix. Differences in this experiment therefore reflect covariance structure only.

### Specification A

**Markowitz**

- GMV annualized expected return: 2.4913%.
- GMV annualized volatility: 2.8333%.
- GMV gross exposure: 2.007606.
- GMV weights: SPY=3.50%, EFA=-12.50%, EEM=-2.75%, TLT=-32.49%, AGG=142.66%, GLD=-2.64%, USO=0.22%, DBC=4.00%.
- Tangency status: NONATTAINED.
- Tangency annualized expected return: not attained.
- Tangency annualized volatility: not attained.
- Annualized Sharpe supremum: 1.034731.
- Tangency gross exposure: no finite value.
- Tangency weights: none; no finite tangency portfolio or attained CAL exists.
- Weights at or near bounds: none.

**SIM**

- GMV annualized expected return: 3.6102%.
- GMV annualized volatility: 4.1558%.
- GMV gross exposure: 1.015161.
- GMV weights: SPY=-0.47%, EFA=0.74%, EEM=-0.28%, TLT=9.68%, AGG=81.98%, GLD=5.35%, USO=0.26%, DBC=2.76%.
- Tangency status: NONATTAINED.
- Tangency annualized expected return: not attained.
- Tangency annualized volatility: not attained.
- Annualized Sharpe supremum: 1.003635.
- Tangency gross exposure: no finite value.
- Tangency weights: none; no finite tangency portfolio or attained CAL exists.
- Weights at or near bounds: none.

**Common-target efficient-frontier comparison**

The overlapping efficient ranges contain 80 identical expected-return targets. The annual-SD tie tolerance is 1e-08.
- Minimum SIM-minus-Markowitz volatility difference: -0.326781%.
- Maximum SIM-minus-Markowitz volatility difference: 1.123051%.
- Mean absolute volatility difference: 0.328860%.
- MARKOWITZ: 33 targets (41.25%).
- SIM: 47 targets (58.75%).
- TIE: 0 targets (0.00%).
These are pointwise classifications; no overall winner is assigned.

| Target return | Markowitz volatility | SIM volatility | SIM − Markowitz | Lower volatility |
|---:|---:|---:|---:|:---:|
| 3.6102% | 3.0327% | 4.1558% | 1.1231% | MARKOWITZ |
| 3.7469% | 3.0823% | 4.1580% | 1.0757% | MARKOWITZ |
| 3.8836% | 3.1366% | 4.1647% | 1.0280% | MARKOWITZ |
| 4.0203% | 3.1955% | 4.1758% | 0.9803% | MARKOWITZ |
| 4.1570% | 3.2587% | 4.1913% | 0.9326% | MARKOWITZ |
| 4.2937% | 3.3260% | 4.2112% | 0.8852% | MARKOWITZ |
| 4.4303% | 3.3970% | 4.2353% | 0.8383% | MARKOWITZ |
| 4.5670% | 3.4716% | 4.2637% | 0.7921% | MARKOWITZ |
| 4.7037% | 3.5496% | 4.2962% | 0.7466% | MARKOWITZ |
| 4.8404% | 3.6307% | 4.3327% | 0.7020% | MARKOWITZ |
| 4.9771% | 3.7147% | 4.3732% | 0.6585% | MARKOWITZ |
| 5.1138% | 3.8015% | 4.4175% | 0.6160% | MARKOWITZ |
| 5.2504% | 3.8908% | 4.4656% | 0.5747% | MARKOWITZ |
| 5.3871% | 3.9825% | 4.5172% | 0.5347% | MARKOWITZ |
| 5.5238% | 4.0764% | 4.5723% | 0.4958% | MARKOWITZ |
| 5.6605% | 4.1724% | 4.6307% | 0.4583% | MARKOWITZ |
| 5.7972% | 4.2703% | 4.6924% | 0.4221% | MARKOWITZ |
| 5.9339% | 4.3700% | 4.7572% | 0.3871% | MARKOWITZ |
| 6.0705% | 4.4714% | 4.8249% | 0.3535% | MARKOWITZ |
| 6.2072% | 4.5744% | 4.8955% | 0.3211% | MARKOWITZ |
| 6.3439% | 4.6788% | 4.9688% | 0.2900% | MARKOWITZ |
| 6.4806% | 4.7846% | 5.0448% | 0.2602% | MARKOWITZ |
| 6.6173% | 4.8917% | 5.1232% | 0.2316% | MARKOWITZ |
| 6.7540% | 4.9999% | 5.2040% | 0.2041% | MARKOWITZ |
| 6.8906% | 5.1093% | 5.2871% | 0.1778% | MARKOWITZ |
| 7.0273% | 5.2197% | 5.3724% | 0.1526% | MARKOWITZ |
| 7.1640% | 5.3312% | 5.4597% | 0.1285% | MARKOWITZ |
| 7.3007% | 5.4435% | 5.5490% | 0.1055% | MARKOWITZ |
| 7.4374% | 5.5567% | 5.6402% | 0.0834% | MARKOWITZ |
| 7.5741% | 5.6708% | 5.7331% | 0.0624% | MARKOWITZ |
| 7.7107% | 5.7856% | 5.8278% | 0.0422% | MARKOWITZ |
| 7.8474% | 5.9011% | 5.9240% | 0.0230% | MARKOWITZ |
| 7.9841% | 6.0173% | 6.0219% | 0.0046% | MARKOWITZ |
| 8.1208% | 6.1341% | 6.1211% | -0.0130% | SIM |
| 8.2575% | 6.2516% | 6.2218% | -0.0298% | SIM |
| 8.3942% | 6.3696% | 6.3238% | -0.0458% | SIM |
| 8.5308% | 6.4882% | 6.4271% | -0.0611% | SIM |
| 8.6675% | 6.6073% | 6.5316% | -0.0757% | SIM |
| 8.8042% | 6.7269% | 6.6372% | -0.0897% | SIM |
| 8.9409% | 6.8469% | 6.7439% | -0.1030% | SIM |
| 9.0776% | 6.9674% | 6.8517% | -0.1157% | SIM |
| 9.2143% | 7.0883% | 6.9605% | -0.1278% | SIM |
| 9.3510% | 7.2095% | 7.0702% | -0.1393% | SIM |
| 9.4876% | 7.3312% | 7.1808% | -0.1504% | SIM |
| 9.6243% | 7.4532% | 7.2923% | -0.1609% | SIM |
| 9.7610% | 7.5755% | 7.4046% | -0.1709% | SIM |
| 9.8977% | 7.6982% | 7.5177% | -0.1805% | SIM |
| 10.0344% | 7.8212% | 7.6316% | -0.1896% | SIM |
| 10.1711% | 7.9444% | 7.7462% | -0.1983% | SIM |
| 10.3077% | 8.0680% | 7.8615% | -0.2065% | SIM |
| 10.4444% | 8.1918% | 7.9774% | -0.2144% | SIM |
| 10.5811% | 8.3159% | 8.0939% | -0.2219% | SIM |
| 10.7178% | 8.4402% | 8.2111% | -0.2291% | SIM |
| 10.8545% | 8.5647% | 8.3289% | -0.2359% | SIM |
| 10.9912% | 8.6895% | 8.4471% | -0.2424% | SIM |
| 11.1278% | 8.8145% | 8.5660% | -0.2485% | SIM |
| 11.2645% | 8.9397% | 8.6853% | -0.2544% | SIM |
| 11.4012% | 9.0650% | 8.8051% | -0.2599% | SIM |
| 11.5379% | 9.1906% | 8.9254% | -0.2652% | SIM |
| 11.6746% | 9.3164% | 9.0462% | -0.2702% | SIM |
| 11.8113% | 9.4423% | 9.1674% | -0.2749% | SIM |
| 11.9479% | 9.5684% | 9.2890% | -0.2794% | SIM |
| 12.0846% | 9.6946% | 9.4110% | -0.2837% | SIM |
| 12.2213% | 9.8210% | 9.5333% | -0.2877% | SIM |
| 12.3580% | 9.9476% | 9.6561% | -0.2915% | SIM |
| 12.4947% | 10.0743% | 9.7792% | -0.2951% | SIM |
| 12.6314% | 10.2011% | 9.9026% | -0.2985% | SIM |
| 12.7680% | 10.3281% | 10.0264% | -0.3017% | SIM |
| 12.9047% | 10.4552% | 10.1505% | -0.3046% | SIM |
| 13.0414% | 10.5824% | 10.2749% | -0.3075% | SIM |
| 13.1781% | 10.7097% | 10.3996% | -0.3101% | SIM |
| 13.3148% | 10.8372% | 10.5246% | -0.3126% | SIM |
| 13.4515% | 10.9647% | 10.6499% | -0.3149% | SIM |
| 13.5881% | 11.0924% | 10.7754% | -0.3170% | SIM |
| 13.7248% | 11.2201% | 10.9012% | -0.3190% | SIM |
| 13.8615% | 11.3480% | 11.0272% | -0.3208% | SIM |
| 13.9982% | 11.4760% | 11.1535% | -0.3225% | SIM |
| 14.1349% | 11.6040% | 11.2800% | -0.3241% | SIM |
| 14.2716% | 11.7322% | 11.4067% | -0.3255% | SIM |
| 14.4082% | 11.8604% | 11.5336% | -0.3268% | SIM |

**GMV weight sensitivity**

| Asset | Markowitz | SIM | SIM − Markowitz | Absolute difference | Sign reversal | Bound status changed |
|---|---:|---:|---:|---:|:---:|:---:|
| SPY | 3.5032% | -0.4736% | -3.9767% | 3.9767% | YES | NO |
| EFA | -12.5024% | 0.7366% | 13.2389% | 13.2389% | YES | NO |
| EEM | -2.7483% | -0.2845% | 2.4638% | 2.4638% | NO | NO |
| TLT | -32.4856% | 9.6758% | 42.1613% | 42.1613% | YES | NO |
| AGG | 142.6584% | 81.9782% | -60.6802% | 60.6802% | NO | NO |
| GLD | -2.6441% | 5.3526% | 7.9967% | 7.9967% | YES | NO |
| USO | 0.2153% | 0.2551% | 0.0398% | 0.0398% | NO | NO |
| DBC | 4.0034% | 2.7597% | -1.2437% | 1.2437% | NO | NO |

- Largest changes: AGG=60.6802%, TLT=42.1613%, EFA=13.2389%.

**tangency weight sensitivity:** unavailable because at least one tangency is NONATTAINED.

- GMV gross-exposure difference (SIM − Markowitz): -0.992446.

### Specification B

**Markowitz**

- GMV annualized expected return: 3.1551%.
- GMV annualized volatility: 4.3020%.
- GMV gross exposure: 1.000000.
- GMV weights: SPY=0.00%, EFA=0.00%, EEM=0.00%, TLT=0.00%, AGG=93.93%, GLD=0.00%, USO=1.66%, DBC=4.41%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 11.0696%.
- Tangency annualized volatility: 11.9425%.
- Tangency annualized Sharpe ratio: 0.550100.
- Tangency gross exposure: 1.000000.
- Tangency weights: SPY=63.50%, EFA=0.00%, EEM=0.00%, TLT=0.00%, AGG=0.00%, GLD=36.50%, USO=0.00%, DBC=0.00%.
- Weights at or near bounds: GMV SPY=0.000000; GMV EFA=0.000000; GMV EEM=0.000000; GMV TLT=0.000000; GMV GLD=0.000000; tangency EFA=0.000000; tangency EEM=0.000000; tangency TLT=0.000000; tangency AGG=0.000000; tangency USO=0.000000; tangency DBC=0.000000.

**SIM**

- GMV annualized expected return: 3.6431%.
- GMV annualized volatility: 4.1563%.
- GMV gross exposure: 1.000000.
- GMV weights: SPY=0.00%, EFA=0.20%, EEM=0.00%, TLT=9.69%, AGG=81.85%, GLD=5.34%, USO=0.23%, DBC=2.68%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 11.0463%.
- Tangency annualized volatility: 11.8861%.
- Tangency annualized Sharpe ratio: 0.550749.
- Tangency gross exposure: 1.000000.
- Tangency weights: SPY=63.20%, EFA=0.00%, EEM=0.00%, TLT=0.31%, AGG=0.00%, GLD=36.49%, USO=0.00%, DBC=0.00%.
- Weights at or near bounds: GMV SPY=0.000000; GMV EEM=0.000000; tangency EFA=0.000000; tangency EEM=0.000000; tangency AGG=0.000000; tangency USO=0.000000; tangency DBC=0.000000.

**Common-target efficient-frontier comparison**

The overlapping efficient ranges contain 80 identical expected-return targets. The annual-SD tie tolerance is 1e-08.
- Minimum SIM-minus-Markowitz volatility difference: -0.702496%.
- Maximum SIM-minus-Markowitz volatility difference: 0.005713%.
- Mean absolute volatility difference: 0.467911%.
- MARKOWITZ: 2 targets (2.50%).
- SIM: 78 targets (97.50%).
- TIE: 0 targets (0.00%).
These are pointwise classifications; no overall winner is assigned.

| Target return | Markowitz volatility | SIM volatility | SIM − Markowitz | Lower volatility |
|---:|---:|---:|---:|:---:|
| 3.6431% | 4.4399% | 4.1563% | -0.2836% | SIM |
| 3.7441% | 4.4835% | 4.1590% | -0.3245% | SIM |
| 3.8452% | 4.5299% | 4.1657% | -0.3642% | SIM |
| 3.9462% | 4.5789% | 4.1770% | -0.4019% | SIM |
| 4.0472% | 4.6304% | 4.1930% | -0.4374% | SIM |
| 4.1483% | 4.6842% | 4.2136% | -0.4706% | SIM |
| 4.2493% | 4.7403% | 4.2388% | -0.5016% | SIM |
| 4.3504% | 4.7987% | 4.2684% | -0.5302% | SIM |
| 4.4514% | 4.8592% | 4.3026% | -0.5566% | SIM |
| 4.5524% | 4.9217% | 4.3410% | -0.5808% | SIM |
| 4.6535% | 4.9863% | 4.3837% | -0.6026% | SIM |
| 4.7545% | 5.0527% | 4.4311% | -0.6216% | SIM |
| 4.8556% | 5.1210% | 4.4830% | -0.6380% | SIM |
| 4.9566% | 5.1915% | 4.5394% | -0.6520% | SIM |
| 5.0576% | 5.2639% | 4.6001% | -0.6638% | SIM |
| 5.1587% | 5.3383% | 4.6649% | -0.6734% | SIM |
| 5.2597% | 5.4147% | 4.7336% | -0.6811% | SIM |
| 5.3608% | 5.4934% | 4.8060% | -0.6874% | SIM |
| 5.4618% | 5.5746% | 4.8821% | -0.6925% | SIM |
| 5.5628% | 5.6581% | 4.9615% | -0.6965% | SIM |
| 5.6639% | 5.7438% | 5.0443% | -0.6995% | SIM |
| 5.7649% | 5.8316% | 5.1301% | -0.7014% | SIM |
| 5.8660% | 5.9214% | 5.2190% | -0.7024% | SIM |
| 5.9670% | 6.0131% | 5.3106% | -0.7025% | SIM |
| 6.0680% | 6.1066% | 5.4048% | -0.7018% | SIM |
| 6.1691% | 6.2019% | 5.5017% | -0.7003% | SIM |
| 6.2701% | 6.2989% | 5.6009% | -0.6980% | SIM |
| 6.3712% | 6.3974% | 5.7023% | -0.6951% | SIM |
| 6.4722% | 6.4975% | 5.8060% | -0.6916% | SIM |
| 6.5732% | 6.5991% | 5.9116% | -0.6875% | SIM |
| 6.6743% | 6.7020% | 6.0192% | -0.6828% | SIM |
| 6.7753% | 6.8063% | 6.1286% | -0.6776% | SIM |
| 6.8763% | 6.9118% | 6.2398% | -0.6720% | SIM |
| 6.9774% | 7.0185% | 6.3526% | -0.6659% | SIM |
| 7.0784% | 7.1264% | 6.4670% | -0.6594% | SIM |
| 7.1795% | 7.2354% | 6.5828% | -0.6526% | SIM |
| 7.2805% | 7.3454% | 6.7000% | -0.6454% | SIM |
| 7.3815% | 7.4564% | 6.8186% | -0.6378% | SIM |
| 7.4826% | 7.5684% | 6.9384% | -0.6300% | SIM |
| 7.5836% | 7.6813% | 7.0594% | -0.6219% | SIM |
| 7.6847% | 7.7951% | 7.1816% | -0.6136% | SIM |
| 7.7857% | 7.9098% | 7.3048% | -0.6050% | SIM |
| 7.8867% | 8.0251% | 7.4290% | -0.5960% | SIM |
| 7.9878% | 8.1407% | 7.5543% | -0.5864% | SIM |
| 8.0888% | 8.2565% | 7.6804% | -0.5761% | SIM |
| 8.1899% | 8.3727% | 7.8074% | -0.5653% | SIM |
| 8.2909% | 8.4891% | 7.9353% | -0.5538% | SIM |
| 8.3919% | 8.6058% | 8.0640% | -0.5418% | SIM |
| 8.4930% | 8.7227% | 8.1934% | -0.5293% | SIM |
| 8.5940% | 8.8398% | 8.3235% | -0.5163% | SIM |
| 8.6951% | 8.9572% | 8.4544% | -0.5028% | SIM |
| 8.7961% | 9.0748% | 8.5859% | -0.4889% | SIM |
| 8.8971% | 9.1925% | 8.7180% | -0.4745% | SIM |
| 8.9982% | 9.3105% | 8.8508% | -0.4598% | SIM |
| 9.0992% | 9.4287% | 8.9841% | -0.4446% | SIM |
| 9.2003% | 9.5470% | 9.1179% | -0.4291% | SIM |
| 9.3013% | 9.6656% | 9.2523% | -0.4133% | SIM |
| 9.4023% | 9.7843% | 9.3872% | -0.3971% | SIM |
| 9.5034% | 9.9031% | 9.5226% | -0.3806% | SIM |
| 9.6044% | 10.0222% | 9.6584% | -0.3637% | SIM |
| 9.7054% | 10.1413% | 9.7947% | -0.3466% | SIM |
| 9.8065% | 10.2606% | 9.9314% | -0.3292% | SIM |
| 9.9075% | 10.3801% | 10.0685% | -0.3116% | SIM |
| 10.0086% | 10.4997% | 10.2067% | -0.2930% | SIM |
| 10.1096% | 10.6194% | 10.3496% | -0.2699% | SIM |
| 10.2106% | 10.7413% | 10.4975% | -0.2438% | SIM |
| 10.3117% | 10.8676% | 10.6501% | -0.2175% | SIM |
| 10.4127% | 10.9981% | 10.8074% | -0.1907% | SIM |
| 10.5138% | 11.1328% | 10.9690% | -0.1637% | SIM |
| 10.6148% | 11.2713% | 11.1349% | -0.1365% | SIM |
| 10.7158% | 11.4138% | 11.3047% | -0.1090% | SIM |
| 10.8169% | 11.5598% | 11.4784% | -0.0814% | SIM |
| 10.9179% | 11.7094% | 11.6558% | -0.0537% | SIM |
| 11.0190% | 11.8625% | 11.8367% | -0.0258% | SIM |
| 11.1200% | 12.0559% | 12.0435% | -0.0125% | SIM |
| 11.2210% | 12.4100% | 12.4008% | -0.0092% | SIM |
| 11.3221% | 12.9209% | 12.9154% | -0.0055% | SIM |
| 11.4231% | 13.5710% | 13.5692% | -0.0018% | SIM |
| 11.5242% | 14.3413% | 14.3433% | 0.0020% | MARKOWITZ |
| 11.6252% | 15.2136% | 15.2193% | 0.0057% | MARKOWITZ |

**GMV weight sensitivity**

| Asset | Markowitz | SIM | SIM − Markowitz | Absolute difference | Sign reversal | Bound status changed |
|---|---:|---:|---:|---:|:---:|:---:|
| SPY | 0.0000% | 0.0000% | 0.0000% | 0.0000% | NO | NO |
| EFA | 0.0000% | 0.2028% | 0.2028% | 0.2028% | NO | YES |
| EEM | 0.0000% | 0.0000% | 0.0000% | 0.0000% | NO | NO |
| TLT | 0.0000% | 9.6936% | 9.6936% | 9.6936% | NO | YES |
| AGG | 93.9343% | 81.8480% | -12.0863% | 12.0863% | NO | NO |
| GLD | 0.0000% | 5.3420% | 5.3420% | 5.3420% | NO | YES |
| USO | 1.6556% | 0.2297% | -1.4260% | 1.4260% | NO | NO |
| DBC | 4.4101% | 2.6839% | -1.7262% | 1.7262% | NO | NO |

- Largest changes: AGG=12.0863%, TLT=9.6936%, GLD=5.3420%.

**tangency weight sensitivity**

| Asset | Markowitz | SIM | SIM − Markowitz | Absolute difference | Sign reversal | Bound status changed |
|---|---:|---:|---:|---:|:---:|:---:|
| SPY | 63.4994% | 63.1978% | -0.3016% | 0.3016% | NO | NO |
| EFA | 0.0000% | 0.0000% | -0.0000% | 0.0000% | NO | NO |
| EEM | 0.0000% | 0.0000% | -0.0000% | 0.0000% | NO | NO |
| TLT | 0.0000% | 0.3075% | 0.3075% | 0.3075% | NO | YES |
| AGG | 0.0000% | 0.0000% | -0.0000% | 0.0000% | NO | NO |
| GLD | 36.5006% | 36.4947% | -0.0059% | 0.0059% | NO | NO |
| USO | 0.0000% | 0.0000% | 0.0000% | 0.0000% | NO | NO |
| DBC | 0.0000% | 0.0000% | 0.0000% | 0.0000% | NO | NO |

- Largest changes: TLT=0.3075%, SPY=0.3016%, GLD=0.0059%.

- GMV gross-exposure difference (SIM − Markowitz): 0.000000.

### Specification C

**Markowitz**

- GMV annualized expected return: 6.5045%.
- GMV annualized volatility: 7.9296%.
- GMV gross exposure: 1.391062.
- GMV weights: SPY=20.00%, EFA=20.00%, EEM=-17.69%, TLT=20.00%, AGG=20.00%, GLD=19.55%, USO=-1.87%, DBC=20.00%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 8.3374%.
- Tangency annualized volatility: 11.8126%.
- Tangency annualized Sharpe ratio: 0.324854.
- Tangency gross exposure: 1.388271.
- Tangency weights: SPY=20.00%, EFA=20.00%, EEM=15.16%, TLT=20.00%, AGG=4.25%, GLD=20.00%, USO=-19.41%, DBC=20.00%.
- Weights at or near bounds: GMV SPY=0.200000; GMV EFA=0.200000; GMV TLT=0.200000; GMV AGG=0.200000; GMV DBC=0.200000; tangency SPY=0.200000; tangency EFA=0.200000; tangency TLT=0.200000; tangency GLD=0.200000; tangency DBC=0.200000.

**SIM**

- GMV annualized expected return: 6.6200%.
- GMV annualized volatility: 7.3849%.
- GMV gross exposure: 1.010240.
- GMV weights: SPY=20.00%, EFA=5.63%, EEM=-0.51%, TLT=20.00%, AGG=20.00%, GLD=20.00%, USO=1.33%, DBC=13.56%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 7.9136%.
- Tangency annualized volatility: 9.3278%.
- Tangency annualized Sharpe ratio: 0.365959.
- Tangency gross exposure: 1.281516.
- Tangency weights: SPY=20.00%, EFA=20.00%, EEM=14.08%, TLT=20.00%, AGG=20.00%, GLD=20.00%, USO=-9.48%, DBC=-4.60%.
- Weights at or near bounds: GMV SPY=0.200000; GMV TLT=0.200000; GMV AGG=0.200000; GMV GLD=0.200000; tangency SPY=0.200000; tangency EFA=0.200000; tangency TLT=0.200000; tangency AGG=0.200000; tangency GLD=0.200000.

**Common-target efficient-frontier comparison**

The overlapping efficient ranges contain 80 identical expected-return targets. The annual-SD tie tolerance is 1e-08.
- Minimum SIM-minus-Markowitz volatility difference: -1.227987%.
- Maximum SIM-minus-Markowitz volatility difference: 0.275874%.
- Mean absolute volatility difference: 0.948989%.
- MARKOWITZ: 1 targets (1.25%).
- SIM: 79 targets (98.75%).
- TIE: 0 targets (0.00%).
These are pointwise classifications; no overall winner is assigned.

| Target return | Markowitz volatility | SIM volatility | SIM − Markowitz | Lower volatility |
|---:|---:|---:|---:|:---:|
| 6.6200% | 7.9487% | 7.3849% | -0.5638% | SIM |
| 6.6444% | 7.9586% | 7.3856% | -0.5730% | SIM |
| 6.6688% | 7.9708% | 7.3880% | -0.5828% | SIM |
| 6.6932% | 7.9850% | 7.3919% | -0.5931% | SIM |
| 6.7176% | 8.0014% | 7.3974% | -0.6040% | SIM |
| 6.7421% | 8.0198% | 7.4044% | -0.6154% | SIM |
| 6.7665% | 8.0404% | 7.4130% | -0.6274% | SIM |
| 6.7909% | 8.0630% | 7.4231% | -0.6399% | SIM |
| 6.8153% | 8.0877% | 7.4347% | -0.6529% | SIM |
| 6.8397% | 8.1144% | 7.4479% | -0.6665% | SIM |
| 6.8642% | 8.1431% | 7.4627% | -0.6805% | SIM |
| 6.8886% | 8.1739% | 7.4789% | -0.6950% | SIM |
| 6.9130% | 8.2066% | 7.4966% | -0.7100% | SIM |
| 6.9374% | 8.2413% | 7.5159% | -0.7254% | SIM |
| 6.9618% | 8.2778% | 7.5366% | -0.7412% | SIM |
| 6.9863% | 8.3163% | 7.5588% | -0.7575% | SIM |
| 7.0107% | 8.3567% | 7.5824% | -0.7742% | SIM |
| 7.0351% | 8.3987% | 7.6075% | -0.7912% | SIM |
| 7.0595% | 8.4420% | 7.6341% | -0.8079% | SIM |
| 7.0840% | 8.4863% | 7.6620% | -0.8243% | SIM |
| 7.1084% | 8.5316% | 7.6913% | -0.8403% | SIM |
| 7.1328% | 8.5780% | 7.7221% | -0.8559% | SIM |
| 7.1572% | 8.6254% | 7.7542% | -0.8712% | SIM |
| 7.1816% | 8.6738% | 7.7876% | -0.8862% | SIM |
| 7.2061% | 8.7232% | 7.8224% | -0.9008% | SIM |
| 7.2305% | 8.7737% | 7.8585% | -0.9152% | SIM |
| 7.2549% | 8.8252% | 7.8959% | -0.9294% | SIM |
| 7.2793% | 8.8778% | 7.9345% | -0.9432% | SIM |
| 7.3037% | 8.9313% | 7.9745% | -0.9569% | SIM |
| 7.3282% | 8.9859% | 8.0157% | -0.9702% | SIM |
| 7.3526% | 9.0414% | 8.0581% | -0.9833% | SIM |
| 7.3770% | 9.0978% | 8.1017% | -0.9961% | SIM |
| 7.4014% | 9.1552% | 8.1464% | -1.0087% | SIM |
| 7.4258% | 9.2135% | 8.1924% | -1.0211% | SIM |
| 7.4503% | 9.2726% | 8.2395% | -1.0331% | SIM |
| 7.4747% | 9.3327% | 8.2877% | -1.0450% | SIM |
| 7.4991% | 9.3936% | 8.3371% | -1.0565% | SIM |
| 7.5235% | 9.4554% | 8.3875% | -1.0679% | SIM |
| 7.5479% | 9.5179% | 8.4390% | -1.0790% | SIM |
| 7.5724% | 9.5813% | 8.4915% | -1.0898% | SIM |
| 7.5968% | 9.6455% | 8.5451% | -1.1005% | SIM |
| 7.6212% | 9.7105% | 8.5996% | -1.1109% | SIM |
| 7.6456% | 9.7762% | 8.6552% | -1.1210% | SIM |
| 7.6700% | 9.8427% | 8.7117% | -1.1310% | SIM |
| 7.6945% | 9.9099% | 8.7692% | -1.1407% | SIM |
| 7.7189% | 9.9779% | 8.8276% | -1.1502% | SIM |
| 7.7433% | 10.0465% | 8.8870% | -1.1595% | SIM |
| 7.7677% | 10.1158% | 8.9472% | -1.1686% | SIM |
| 7.7921% | 10.1858% | 9.0084% | -1.1775% | SIM |
| 7.8166% | 10.2563% | 9.0705% | -1.1858% | SIM |
| 7.8410% | 10.3271% | 9.1338% | -1.1933% | SIM |
| 7.8654% | 10.3981% | 9.1980% | -1.2001% | SIM |
| 7.8898% | 10.4693% | 9.2633% | -1.2060% | SIM |
| 7.9142% | 10.5408% | 9.3296% | -1.2112% | SIM |
| 7.9387% | 10.6125% | 9.3968% | -1.2157% | SIM |
| 7.9631% | 10.6845% | 9.4650% | -1.2195% | SIM |
| 7.9875% | 10.7567% | 9.5341% | -1.2225% | SIM |
| 8.0119% | 10.8290% | 9.6041% | -1.2249% | SIM |
| 8.0363% | 10.9016% | 9.6750% | -1.2266% | SIM |
| 8.0608% | 10.9744% | 9.7468% | -1.2276% | SIM |
| 8.0852% | 11.0474% | 9.8195% | -1.2280% | SIM |
| 8.1096% | 11.1206% | 9.8929% | -1.2277% | SIM |
| 8.1340% | 11.1941% | 9.9672% | -1.2269% | SIM |
| 8.1584% | 11.2677% | 10.0422% | -1.2254% | SIM |
| 8.1829% | 11.3414% | 10.1181% | -1.2233% | SIM |
| 8.2073% | 11.4154% | 10.1947% | -1.2207% | SIM |
| 8.2317% | 11.4896% | 10.2769% | -1.2126% | SIM |
| 8.2561% | 11.5639% | 10.3677% | -1.1962% | SIM |
| 8.2805% | 11.6384% | 10.4668% | -1.1716% | SIM |
| 8.3050% | 11.7131% | 10.5741% | -1.1390% | SIM |
| 8.3294% | 11.7880% | 10.6892% | -1.0988% | SIM |
| 8.3538% | 11.8632% | 10.8119% | -1.0513% | SIM |
| 8.3782% | 11.9387% | 10.9420% | -0.9967% | SIM |
| 8.4026% | 12.0145% | 11.0792% | -0.9353% | SIM |
| 8.4271% | 12.0906% | 11.2233% | -0.8673% | SIM |
| 8.4515% | 12.1671% | 11.3739% | -0.7932% | SIM |
| 8.4759% | 12.2444% | 11.5966% | -0.6479% | SIM |
| 8.5003% | 12.3224% | 11.9111% | -0.4113% | SIM |
| 8.5247% | 12.4011% | 12.3000% | -0.1011% | SIM |
| 8.5492% | 12.4805% | 12.7564% | 0.2759% | MARKOWITZ |

**GMV weight sensitivity**

| Asset | Markowitz | SIM | SIM − Markowitz | Absolute difference | Sign reversal | Bound status changed |
|---|---:|---:|---:|---:|:---:|:---:|
| SPY | 20.0000% | 20.0000% | -0.0000% | 0.0000% | NO | NO |
| EFA | 20.0000% | 5.6279% | -14.3721% | 14.3721% | NO | YES |
| EEM | -17.6873% | -0.5120% | 17.1753% | 17.1753% | NO | NO |
| TLT | 20.0000% | 20.0000% | -0.0000% | 0.0000% | NO | NO |
| AGG | 20.0000% | 20.0000% | -0.0000% | 0.0000% | NO | NO |
| GLD | 19.5531% | 20.0000% | 0.4469% | 0.4469% | NO | YES |
| USO | -1.8658% | 1.3255% | 3.1913% | 3.1913% | YES | NO |
| DBC | 20.0000% | 13.5586% | -6.4414% | 6.4414% | NO | YES |

- Largest changes: EEM=17.1753%, EFA=14.3721%, DBC=6.4414%.

**tangency weight sensitivity**

| Asset | Markowitz | SIM | SIM − Markowitz | Absolute difference | Sign reversal | Bound status changed |
|---|---:|---:|---:|---:|:---:|:---:|
| SPY | 20.0000% | 20.0000% | 0.0000% | 0.0000% | NO | NO |
| EFA | 20.0000% | 20.0000% | -0.0000% | 0.0000% | NO | NO |
| EEM | 15.1601% | 14.0758% | -1.0843% | 1.0843% | NO | NO |
| TLT | 20.0000% | 20.0000% | 0.0000% | 0.0000% | NO | NO |
| AGG | 4.2534% | 20.0000% | 15.7466% | 15.7466% | NO | YES |
| GLD | 20.0000% | 20.0000% | 0.0000% | 0.0000% | NO | NO |
| USO | -19.4136% | -9.4760% | 9.9376% | 9.9376% | NO | NO |
| DBC | 20.0000% | -4.5998% | -24.5998% | 24.5998% | YES | YES |

- Largest changes: DBC=24.5998%, AGG=15.7466%, USO=9.9376%.

- GMV gross-exposure difference (SIM − Markowitz): -0.380822.

Experiment 2 — Complete model comparison

Markowitz uses its sample mean vector and full covariance matrix. SIM uses its model-implied expected-return vector and SIM covariance matrix. Differences therefore combine expected-return and covariance assumptions.

### Specification A

**Markowitz**

- GMV annualized expected return: 2.4913%.
- GMV annualized volatility: 2.8333%.
- GMV gross exposure: 2.007606.
- GMV weights: SPY=3.50%, EFA=-12.50%, EEM=-2.75%, TLT=-32.49%, AGG=142.66%, GLD=-2.64%, USO=0.22%, DBC=4.00%.
- Tangency status: NONATTAINED.
- Tangency annualized expected return: not attained.
- Tangency annualized volatility: not attained.
- Annualized Sharpe supremum: 1.034731.
- Tangency gross exposure: no finite value.
- Tangency weights: none; no finite tangency portfolio or attained CAL exists.
- Weights at or near bounds: none.

**SIM**

- GMV annualized expected return: 6.1950%.
- GMV annualized volatility: 4.1558%.
- GMV gross exposure: 1.015161.
- GMV weights: SPY=-0.47%, EFA=0.74%, EEM=-0.28%, TLT=9.68%, AGG=81.98%, GLD=5.35%, USO=0.26%, DBC=2.76%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 14.2855%.
- Tangency annualized volatility: 9.9851%.
- Tangency annualized Sharpe ratio: 0.980009.
- Tangency gross exposure: 3.194688.
- Tangency weights: SPY=123.65%, EFA=-65.11%, EEM=-25.17%, TLT=16.61%, AGG=43.14%, GLD=26.34%, USO=-7.33%, DBC=-12.12%.
- Weights at or near bounds: none.

**Common-target efficient-frontier comparison**

The overlapping efficient ranges contain 80 identical expected-return targets. The annual-SD tie tolerance is 1e-08.
- Minimum SIM-minus-Markowitz volatility difference: -1.895491%.
- Maximum SIM-minus-Markowitz volatility difference: -0.409366%.
- Mean absolute volatility difference: 1.606283%.
- MARKOWITZ: 0 targets (0.00%).
- SIM: 80 targets (100.00%).
- TIE: 0 targets (0.00%).
These are pointwise classifications; no overall winner is assigned.

| Target return | Markowitz volatility | SIM volatility | SIM − Markowitz | Lower volatility |
|---:|---:|---:|---:|:---:|
| 6.1950% | 4.5651% | 4.1558% | -0.4094% | SIM |
| 6.2990% | 4.6443% | 4.1574% | -0.4869% | SIM |
| 6.4030% | 4.7243% | 4.1623% | -0.5620% | SIM |
| 6.5069% | 4.8051% | 4.1705% | -0.6346% | SIM |
| 6.6109% | 4.8866% | 4.1819% | -0.7047% | SIM |
| 6.7149% | 4.9688% | 4.1965% | -0.7723% | SIM |
| 6.8188% | 5.0517% | 4.2143% | -0.8374% | SIM |
| 6.9228% | 5.1352% | 4.2352% | -0.8999% | SIM |
| 7.0268% | 5.2193% | 4.2593% | -0.9600% | SIM |
| 7.1307% | 5.3039% | 4.2864% | -1.0176% | SIM |
| 7.2347% | 5.3891% | 4.3164% | -1.0727% | SIM |
| 7.3386% | 5.4749% | 4.3494% | -1.1254% | SIM |
| 7.4426% | 5.5611% | 4.3853% | -1.1758% | SIM |
| 7.5466% | 5.6478% | 4.4239% | -1.2239% | SIM |
| 7.6505% | 5.7349% | 4.4652% | -1.2697% | SIM |
| 7.7545% | 5.8225% | 4.5092% | -1.3133% | SIM |
| 7.8585% | 5.9105% | 4.5558% | -1.3547% | SIM |
| 7.9624% | 5.9988% | 4.6048% | -1.3940% | SIM |
| 8.0664% | 6.0876% | 4.6562% | -1.4313% | SIM |
| 8.1704% | 6.1767% | 4.7100% | -1.4667% | SIM |
| 8.2743% | 6.2661% | 4.7660% | -1.5001% | SIM |
| 8.3783% | 6.3559% | 4.8242% | -1.5317% | SIM |
| 8.4823% | 6.4460% | 4.8845% | -1.5615% | SIM |
| 8.5862% | 6.5364% | 4.9468% | -1.5896% | SIM |
| 8.6902% | 6.6271% | 5.0111% | -1.6160% | SIM |
| 8.7942% | 6.7181% | 5.0772% | -1.6409% | SIM |
| 8.8981% | 6.8093% | 5.1451% | -1.6642% | SIM |
| 9.0021% | 6.9008% | 5.2147% | -1.6860% | SIM |
| 9.1060% | 6.9925% | 5.2860% | -1.7065% | SIM |
| 9.2100% | 7.0845% | 5.3589% | -1.7256% | SIM |
| 9.3140% | 7.1767% | 5.4333% | -1.7434% | SIM |
| 9.4179% | 7.2691% | 5.5092% | -1.7599% | SIM |
| 9.5219% | 7.3617% | 5.5865% | -1.7752% | SIM |
| 9.6259% | 7.4546% | 5.6651% | -1.7894% | SIM |
| 9.7298% | 7.5476% | 5.7451% | -1.8025% | SIM |
| 9.8338% | 7.6408% | 5.8262% | -1.8146% | SIM |
| 9.9378% | 7.7342% | 5.9086% | -1.8256% | SIM |
| 10.0417% | 7.8278% | 5.9921% | -1.8357% | SIM |
| 10.1457% | 7.9216% | 6.0767% | -1.8449% | SIM |
| 10.2497% | 8.0155% | 6.1623% | -1.8531% | SIM |
| 10.3536% | 8.1095% | 6.2490% | -1.8606% | SIM |
| 10.4576% | 8.2037% | 6.3366% | -1.8672% | SIM |
| 10.5616% | 8.2981% | 6.4251% | -1.8730% | SIM |
| 10.6655% | 8.3926% | 6.5145% | -1.8781% | SIM |
| 10.7695% | 8.4873% | 6.6048% | -1.8825% | SIM |
| 10.8734% | 8.5820% | 6.6959% | -1.8862% | SIM |
| 10.9774% | 8.6769% | 6.7877% | -1.8892% | SIM |
| 11.0814% | 8.7720% | 6.8803% | -1.8916% | SIM |
| 11.1853% | 8.8671% | 6.9737% | -1.8934% | SIM |
| 11.2893% | 8.9624% | 7.0677% | -1.8947% | SIM |
| 11.3933% | 9.0578% | 7.1624% | -1.8953% | SIM |
| 11.4972% | 9.1533% | 7.2578% | -1.8955% | SIM |
| 11.6012% | 9.2488% | 7.3537% | -1.8951% | SIM |
| 11.7052% | 9.3445% | 7.4503% | -1.8943% | SIM |
| 11.8091% | 9.4403% | 7.5474% | -1.8930% | SIM |
| 11.9131% | 9.5362% | 7.6450% | -1.8912% | SIM |
| 12.0171% | 9.6322% | 7.7432% | -1.8890% | SIM |
| 12.1210% | 9.7283% | 7.8419% | -1.8864% | SIM |
| 12.2250% | 9.8244% | 7.9411% | -1.8833% | SIM |
| 12.3290% | 9.9207% | 8.0407% | -1.8799% | SIM |
| 12.4329% | 10.0170% | 8.1409% | -1.8762% | SIM |
| 12.5369% | 10.1134% | 8.2414% | -1.8720% | SIM |
| 12.6408% | 10.2099% | 8.3423% | -1.8676% | SIM |
| 12.7448% | 10.3065% | 8.4437% | -1.8628% | SIM |
| 12.8488% | 10.4031% | 8.5455% | -1.8577% | SIM |
| 12.9527% | 10.4998% | 8.6476% | -1.8522% | SIM |
| 13.0567% | 10.5966% | 8.7501% | -1.8465% | SIM |
| 13.1607% | 10.6935% | 8.8529% | -1.8405% | SIM |
| 13.2646% | 10.7904% | 8.9561% | -1.8343% | SIM |
| 13.3686% | 10.8874% | 9.0596% | -1.8277% | SIM |
| 13.4726% | 10.9844% | 9.1635% | -1.8210% | SIM |
| 13.5765% | 11.0815% | 9.2676% | -1.8139% | SIM |
| 13.6805% | 11.1787% | 9.3720% | -1.8067% | SIM |
| 13.7845% | 11.2759% | 9.4767% | -1.7992% | SIM |
| 13.8884% | 11.3732% | 9.5817% | -1.7915% | SIM |
| 13.9924% | 11.4705% | 9.6870% | -1.7835% | SIM |
| 14.0963% | 11.5679% | 9.7925% | -1.7754% | SIM |
| 14.2003% | 11.6654% | 9.8983% | -1.7671% | SIM |
| 14.3043% | 11.7628% | 10.0043% | -1.7586% | SIM |
| 14.4082% | 11.8604% | 10.1105% | -1.7499% | SIM |

**GMV weight sensitivity**

| Asset | Markowitz | SIM | SIM − Markowitz | Absolute difference | Sign reversal | Bound status changed |
|---|---:|---:|---:|---:|:---:|:---:|
| SPY | 3.5032% | -0.4736% | -3.9767% | 3.9767% | YES | NO |
| EFA | -12.5024% | 0.7366% | 13.2389% | 13.2389% | YES | NO |
| EEM | -2.7483% | -0.2845% | 2.4638% | 2.4638% | NO | NO |
| TLT | -32.4856% | 9.6758% | 42.1613% | 42.1613% | YES | NO |
| AGG | 142.6584% | 81.9782% | -60.6802% | 60.6802% | NO | NO |
| GLD | -2.6441% | 5.3526% | 7.9967% | 7.9967% | YES | NO |
| USO | 0.2153% | 0.2551% | 0.0398% | 0.0398% | NO | NO |
| DBC | 4.0034% | 2.7597% | -1.2437% | 1.2437% | NO | NO |

- Largest changes: AGG=60.6802%, TLT=42.1613%, EFA=13.2389%.

**tangency weight sensitivity:** unavailable because at least one tangency is NONATTAINED.

- GMV gross-exposure difference (SIM − Markowitz): -0.992446.

### Specification B

**Markowitz**

- GMV annualized expected return: 3.1551%.
- GMV annualized volatility: 4.3020%.
- GMV gross exposure: 1.000000.
- GMV weights: SPY=0.00%, EFA=0.00%, EEM=0.00%, TLT=0.00%, AGG=93.93%, GLD=0.00%, USO=1.66%, DBC=4.41%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 11.0696%.
- Tangency annualized volatility: 11.9425%.
- Tangency annualized Sharpe ratio: 0.550100.
- Tangency gross exposure: 1.000000.
- Tangency weights: SPY=63.50%, EFA=0.00%, EEM=0.00%, TLT=0.00%, AGG=0.00%, GLD=36.50%, USO=0.00%, DBC=0.00%.
- Weights at or near bounds: GMV SPY=0.000000; GMV EFA=0.000000; GMV EEM=0.000000; GMV TLT=0.000000; GMV GLD=0.000000; tangency EFA=0.000000; tangency EEM=0.000000; tangency TLT=0.000000; tangency AGG=0.000000; tangency USO=0.000000; tangency DBC=0.000000.

**SIM**

- GMV annualized expected return: 6.2208%.
- GMV annualized volatility: 4.1563%.
- GMV gross exposure: 1.000000.
- GMV weights: SPY=0.00%, EFA=0.20%, EEM=0.00%, TLT=9.69%, AGG=81.85%, GLD=5.34%, USO=0.23%, DBC=2.68%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 8.6236%.
- Tangency annualized volatility: 6.2319%.
- Tangency annualized Sharpe ratio: 0.661691.
- Tangency gross exposure: 1.000000.
- Tangency weights: SPY=20.43%, EFA=0.00%, EEM=0.00%, TLT=15.35%, AGG=39.88%, GLD=24.34%, USO=0.00%, DBC=0.00%.
- Weights at or near bounds: GMV SPY=0.000000; GMV EEM=0.000000; tangency EFA=0.000000; tangency EEM=0.000000; tangency USO=0.000000; tangency DBC=0.000000.

**Common-target efficient-frontier comparison**

The overlapping efficient ranges contain 80 identical expected-return targets. The annual-SD tie tolerance is 1e-08.
- Minimum SIM-minus-Markowitz volatility difference: -3.264217%.
- Maximum SIM-minus-Markowitz volatility difference: -1.389295%.
- Mean absolute volatility difference: 2.314345%.
- MARKOWITZ: 0 targets (0.00%).
- SIM: 80 targets (100.00%).
- TIE: 0 targets (0.00%).
These are pointwise classifications; no overall winner is assigned.

| Target return | Markowitz volatility | SIM volatility | SIM − Markowitz | Lower volatility |
|---:|---:|---:|---:|:---:|
| 6.2208% | 6.2514% | 4.1563% | -2.0950% | SIM |
| 6.2892% | 6.3174% | 4.1581% | -2.1593% | SIM |
| 6.3576% | 6.3842% | 4.1628% | -2.2214% | SIM |
| 6.4260% | 6.4516% | 4.1710% | -2.2807% | SIM |
| 6.4945% | 6.5198% | 4.1828% | -2.3370% | SIM |
| 6.5629% | 6.5886% | 4.1983% | -2.3903% | SIM |
| 6.6313% | 6.6580% | 4.2174% | -2.4406% | SIM |
| 6.6997% | 6.7281% | 4.2401% | -2.4880% | SIM |
| 6.7681% | 6.7988% | 4.2662% | -2.5325% | SIM |
| 6.8365% | 6.8700% | 4.2959% | -2.5741% | SIM |
| 6.9049% | 6.9418% | 4.3297% | -2.6121% | SIM |
| 6.9733% | 7.0142% | 4.3676% | -2.6465% | SIM |
| 7.0417% | 7.0871% | 4.4097% | -2.6774% | SIM |
| 7.1101% | 7.1605% | 4.4557% | -2.7047% | SIM |
| 7.1786% | 7.2344% | 4.5056% | -2.7287% | SIM |
| 7.2470% | 7.3087% | 4.5592% | -2.7495% | SIM |
| 7.3154% | 7.3836% | 4.6164% | -2.7672% | SIM |
| 7.3838% | 7.4589% | 4.6771% | -2.7818% | SIM |
| 7.4522% | 7.5346% | 4.7411% | -2.7936% | SIM |
| 7.5206% | 7.6108% | 4.8083% | -2.8025% | SIM |
| 7.5890% | 7.6874% | 4.8785% | -2.8089% | SIM |
| 7.6574% | 7.7644% | 4.9517% | -2.8127% | SIM |
| 7.7258% | 7.8417% | 5.0277% | -2.8141% | SIM |
| 7.7942% | 7.9195% | 5.1064% | -2.8131% | SIM |
| 7.8627% | 7.9975% | 5.1876% | -2.8099% | SIM |
| 7.9311% | 8.0757% | 5.2713% | -2.8045% | SIM |
| 7.9995% | 8.1541% | 5.3573% | -2.7968% | SIM |
| 8.0679% | 8.2325% | 5.4455% | -2.7870% | SIM |
| 8.1363% | 8.3111% | 5.5358% | -2.7753% | SIM |
| 8.2047% | 8.3898% | 5.6281% | -2.7616% | SIM |
| 8.2731% | 8.4686% | 5.7224% | -2.7462% | SIM |
| 8.3415% | 8.5475% | 5.8184% | -2.7291% | SIM |
| 8.4099% | 8.6266% | 5.9162% | -2.7103% | SIM |
| 8.4783% | 8.7057% | 6.0157% | -2.6901% | SIM |
| 8.5468% | 8.7850% | 6.1167% | -2.6683% | SIM |
| 8.6152% | 8.8644% | 6.2192% | -2.6452% | SIM |
| 8.6836% | 8.9438% | 6.3231% | -2.6208% | SIM |
| 8.7520% | 9.0234% | 6.4283% | -2.5951% | SIM |
| 8.8204% | 9.1031% | 6.5349% | -2.5682% | SIM |
| 8.8888% | 9.1828% | 6.6426% | -2.5402% | SIM |
| 8.9572% | 9.2627% | 6.7516% | -2.5111% | SIM |
| 9.0256% | 9.3426% | 6.8616% | -2.4810% | SIM |
| 9.0940% | 9.4226% | 6.9727% | -2.4500% | SIM |
| 9.1624% | 9.5027% | 7.0848% | -2.4180% | SIM |
| 9.2309% | 9.5829% | 7.1978% | -2.3851% | SIM |
| 9.2993% | 9.6632% | 7.3118% | -2.3514% | SIM |
| 9.3677% | 9.7435% | 7.4266% | -2.3169% | SIM |
| 9.4361% | 9.8240% | 7.5423% | -2.2817% | SIM |
| 9.5045% | 9.9045% | 7.6587% | -2.2457% | SIM |
| 9.5729% | 9.9850% | 7.7759% | -2.2091% | SIM |
| 9.6413% | 10.0657% | 7.8939% | -2.1718% | SIM |
| 9.7097% | 10.1464% | 8.0125% | -2.1338% | SIM |
| 9.7781% | 10.2271% | 8.1318% | -2.0953% | SIM |
| 9.8465% | 10.3080% | 8.2518% | -2.0562% | SIM |
| 9.9149% | 10.3889% | 8.3723% | -2.0166% | SIM |
| 9.9834% | 10.4699% | 8.4934% | -1.9764% | SIM |
| 10.0518% | 10.5509% | 8.6151% | -1.9358% | SIM |
| 10.1202% | 10.6320% | 8.7373% | -1.8947% | SIM |
| 10.1886% | 10.7143% | 8.8600% | -1.8543% | SIM |
| 10.2570% | 10.7987% | 8.9832% | -1.8155% | SIM |
| 10.3254% | 10.8851% | 9.1069% | -1.7782% | SIM |
| 10.3938% | 10.9734% | 9.2310% | -1.7424% | SIM |
| 10.4622% | 11.0636% | 9.3556% | -1.7080% | SIM |
| 10.5306% | 11.1556% | 9.4806% | -1.6751% | SIM |
| 10.5990% | 11.2495% | 9.6059% | -1.6435% | SIM |
| 10.6675% | 11.3451% | 9.7317% | -1.6134% | SIM |
| 10.7359% | 11.4424% | 9.8581% | -1.5843% | SIM |
| 10.8043% | 11.5414% | 9.9892% | -1.5522% | SIM |
| 10.8727% | 11.6420% | 10.1261% | -1.5159% | SIM |
| 10.9411% | 11.7443% | 10.2685% | -1.4757% | SIM |
| 11.0095% | 11.8480% | 10.4162% | -1.4318% | SIM |
| 11.0779% | 11.9583% | 10.5690% | -1.3893% | SIM |
| 11.1463% | 12.1322% | 10.7266% | -1.4056% | SIM |
| 11.2147% | 12.3831% | 10.8889% | -1.4942% | SIM |
| 11.2831% | 12.7065% | 11.0556% | -1.6509% | SIM |
| 11.3516% | 13.0970% | 11.2266% | -1.8704% | SIM |
| 11.4200% | 13.5488% | 11.4017% | -2.1471% | SIM |
| 11.4884% | 14.0559% | 11.5806% | -2.4753% | SIM |
| 11.5568% | 14.6127% | 11.7632% | -2.8494% | SIM |
| 11.6252% | 15.2136% | 11.9493% | -3.2642% | SIM |

**GMV weight sensitivity**

| Asset | Markowitz | SIM | SIM − Markowitz | Absolute difference | Sign reversal | Bound status changed |
|---|---:|---:|---:|---:|:---:|:---:|
| SPY | 0.0000% | 0.0000% | 0.0000% | 0.0000% | NO | NO |
| EFA | 0.0000% | 0.2028% | 0.2028% | 0.2028% | NO | YES |
| EEM | 0.0000% | 0.0000% | 0.0000% | 0.0000% | NO | NO |
| TLT | 0.0000% | 9.6936% | 9.6936% | 9.6936% | NO | YES |
| AGG | 93.9343% | 81.8480% | -12.0863% | 12.0863% | NO | NO |
| GLD | 0.0000% | 5.3420% | 5.3420% | 5.3420% | NO | YES |
| USO | 1.6556% | 0.2297% | -1.4260% | 1.4260% | NO | NO |
| DBC | 4.4101% | 2.6839% | -1.7262% | 1.7262% | NO | NO |

- Largest changes: AGG=12.0863%, TLT=9.6936%, GLD=5.3420%.

**tangency weight sensitivity**

| Asset | Markowitz | SIM | SIM − Markowitz | Absolute difference | Sign reversal | Bound status changed |
|---|---:|---:|---:|---:|:---:|:---:|
| SPY | 63.4994% | 20.4270% | -43.0724% | 43.0724% | NO | NO |
| EFA | 0.0000% | 0.0000% | 0.0000% | 0.0000% | NO | NO |
| EEM | 0.0000% | 0.0000% | -0.0000% | 0.0000% | NO | NO |
| TLT | 0.0000% | 15.3503% | 15.3503% | 15.3503% | NO | YES |
| AGG | 0.0000% | 39.8790% | 39.8790% | 39.8790% | NO | YES |
| GLD | 36.5006% | 24.3437% | -12.1569% | 12.1569% | NO | NO |
| USO | 0.0000% | 0.0000% | 0.0000% | 0.0000% | NO | NO |
| DBC | 0.0000% | 0.0000% | 0.0000% | 0.0000% | NO | NO |

- Largest changes: SPY=43.0724%, AGG=39.8790%, TLT=15.3503%.

- GMV gross-exposure difference (SIM − Markowitz): 0.000000.

### Specification C

**Markowitz**

- GMV annualized expected return: 6.5045%.
- GMV annualized volatility: 7.9296%.
- GMV gross exposure: 1.391062.
- GMV weights: SPY=20.00%, EFA=20.00%, EEM=-17.69%, TLT=20.00%, AGG=20.00%, GLD=19.55%, USO=-1.87%, DBC=20.00%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 8.3374%.
- Tangency annualized volatility: 11.8126%.
- Tangency annualized Sharpe ratio: 0.324854.
- Tangency gross exposure: 1.388271.
- Tangency weights: SPY=20.00%, EFA=20.00%, EEM=15.16%, TLT=20.00%, AGG=4.25%, GLD=20.00%, USO=-19.41%, DBC=20.00%.
- Weights at or near bounds: GMV SPY=0.200000; GMV EFA=0.200000; GMV TLT=0.200000; GMV AGG=0.200000; GMV DBC=0.200000; tangency SPY=0.200000; tangency EFA=0.200000; tangency TLT=0.200000; tangency GLD=0.200000; tangency DBC=0.200000.

**SIM**

- GMV annualized expected return: 8.0949%.
- GMV annualized volatility: 7.3849%.
- GMV gross exposure: 1.010240.
- GMV weights: SPY=20.00%, EFA=5.63%, EEM=-0.51%, TLT=20.00%, AGG=20.00%, GLD=20.00%, USO=1.33%, DBC=13.56%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 8.5016%.
- Tangency annualized volatility: 7.7914%.
- Tangency annualized Sharpe ratio: 0.513588.
- Tangency gross exposure: 1.095368.
- Tangency weights: SPY=20.00%, EFA=11.29%, EEM=4.21%, TLT=20.00%, AGG=20.00%, GLD=20.00%, USO=-4.77%, DBC=9.28%.
- Weights at or near bounds: GMV SPY=0.200000; GMV TLT=0.200000; GMV AGG=0.200000; GMV GLD=0.200000; tangency SPY=0.200000; tangency TLT=0.200000; tangency AGG=0.200000; tangency GLD=0.200000.

**Common-target efficient-frontier comparison**

The overlapping efficient ranges contain 80 identical expected-return targets. The annual-SD tie tolerance is 1e-08.
- Minimum SIM-minus-Markowitz volatility difference: -4.591589%.
- Maximum SIM-minus-Markowitz volatility difference: -3.691623%.
- Mean absolute volatility difference: 4.213380%.
- MARKOWITZ: 0 targets (0.00%).
- SIM: 80 targets (100.00%).
- TIE: 0 targets (0.00%).
These are pointwise classifications; no overall winner is assigned.

| Target return | Markowitz volatility | SIM volatility | SIM − Markowitz | Lower volatility |
|---:|---:|---:|---:|:---:|
| 8.0949% | 11.0765% | 7.3849% | -3.6916% | SIM |
| 8.1006% | 11.0937% | 7.3849% | -3.7088% | SIM |
| 8.1064% | 11.1110% | 7.3852% | -3.7258% | SIM |
| 8.1121% | 11.1282% | 7.3856% | -3.7426% | SIM |
| 8.1179% | 11.1455% | 7.3862% | -3.7593% | SIM |
| 8.1236% | 11.1628% | 7.3869% | -3.7758% | SIM |
| 8.1294% | 11.1801% | 7.3879% | -3.7922% | SIM |
| 8.1351% | 11.1974% | 7.3890% | -3.8084% | SIM |
| 8.1409% | 11.2147% | 7.3902% | -3.8245% | SIM |
| 8.1466% | 11.2320% | 7.3916% | -3.8404% | SIM |
| 8.1524% | 11.2494% | 7.3932% | -3.8562% | SIM |
| 8.1581% | 11.2667% | 7.3950% | -3.8718% | SIM |
| 8.1639% | 11.2841% | 7.3969% | -3.8872% | SIM |
| 8.1696% | 11.3014% | 7.3990% | -3.9025% | SIM |
| 8.1754% | 11.3188% | 7.4012% | -3.9176% | SIM |
| 8.1811% | 11.3362% | 7.4036% | -3.9326% | SIM |
| 8.1869% | 11.3536% | 7.4062% | -3.9474% | SIM |
| 8.1926% | 11.3710% | 7.4090% | -3.9621% | SIM |
| 8.1984% | 11.3884% | 7.4119% | -3.9766% | SIM |
| 8.2041% | 11.4059% | 7.4150% | -3.9909% | SIM |
| 8.2099% | 11.4233% | 7.4182% | -4.0051% | SIM |
| 8.2156% | 11.4408% | 7.4216% | -4.0192% | SIM |
| 8.2214% | 11.4582% | 7.4252% | -4.0330% | SIM |
| 8.2271% | 11.4757% | 7.4289% | -4.0468% | SIM |
| 8.2329% | 11.4932% | 7.4328% | -4.0604% | SIM |
| 8.2386% | 11.5107% | 7.4369% | -4.0738% | SIM |
| 8.2444% | 11.5282% | 7.4411% | -4.0871% | SIM |
| 8.2501% | 11.5457% | 7.4455% | -4.1002% | SIM |
| 8.2559% | 11.5632% | 7.4501% | -4.1131% | SIM |
| 8.2616% | 11.5807% | 7.4548% | -4.1259% | SIM |
| 8.2674% | 11.5983% | 7.4596% | -4.1386% | SIM |
| 8.2731% | 11.6158% | 7.4647% | -4.1511% | SIM |
| 8.2789% | 11.6334% | 7.4699% | -4.1635% | SIM |
| 8.2846% | 11.6509% | 7.4753% | -4.1757% | SIM |
| 8.2904% | 11.6685% | 7.4808% | -4.1877% | SIM |
| 8.2961% | 11.6861% | 7.4865% | -4.1996% | SIM |
| 8.3019% | 11.7037% | 7.4923% | -4.2114% | SIM |
| 8.3076% | 11.7213% | 7.4983% | -4.2230% | SIM |
| 8.3134% | 11.7389% | 7.5045% | -4.2344% | SIM |
| 8.3192% | 11.7566% | 7.5108% | -4.2458% | SIM |
| 8.3249% | 11.7742% | 7.5173% | -4.2569% | SIM |
| 8.3307% | 11.7919% | 7.5239% | -4.2680% | SIM |
| 8.3364% | 11.8096% | 7.5307% | -4.2789% | SIM |
| 8.3422% | 11.8273% | 7.5377% | -4.2896% | SIM |
| 8.3479% | 11.8450% | 7.5448% | -4.3002% | SIM |
| 8.3537% | 11.8628% | 7.5521% | -4.3107% | SIM |
| 8.3594% | 11.8805% | 7.5595% | -4.3210% | SIM |
| 8.3652% | 11.8983% | 7.5671% | -4.3312% | SIM |
| 8.3709% | 11.9161% | 7.5748% | -4.3412% | SIM |
| 8.3767% | 11.9339% | 7.5827% | -4.3511% | SIM |
| 8.3824% | 11.9517% | 7.5908% | -4.3609% | SIM |
| 8.3882% | 11.9695% | 7.5990% | -4.3705% | SIM |
| 8.3939% | 11.9874% | 7.6073% | -4.3800% | SIM |
| 8.3997% | 12.0052% | 7.6159% | -4.3894% | SIM |
| 8.4054% | 12.0231% | 7.6245% | -4.3986% | SIM |
| 8.4112% | 12.0410% | 7.6333% | -4.4077% | SIM |
| 8.4169% | 12.0589% | 7.6423% | -4.4166% | SIM |
| 8.4227% | 12.0768% | 7.6514% | -4.4254% | SIM |
| 8.4284% | 12.0947% | 7.6607% | -4.4341% | SIM |
| 8.4342% | 12.1127% | 7.6701% | -4.4426% | SIM |
| 8.4399% | 12.1307% | 7.6796% | -4.4511% | SIM |
| 8.4457% | 12.1488% | 7.6894% | -4.4594% | SIM |
| 8.4514% | 12.1669% | 7.6992% | -4.4677% | SIM |
| 8.4572% | 12.1850% | 7.7092% | -4.4758% | SIM |
| 8.4629% | 12.2032% | 7.7194% | -4.4838% | SIM |
| 8.4687% | 12.2214% | 7.7297% | -4.4917% | SIM |
| 8.4744% | 12.2397% | 7.7401% | -4.4996% | SIM |
| 8.4802% | 12.2580% | 7.7507% | -4.5073% | SIM |
| 8.4859% | 12.2763% | 7.7615% | -4.5149% | SIM |
| 8.4917% | 12.2947% | 7.7723% | -4.5223% | SIM |
| 8.4974% | 12.3131% | 7.7834% | -4.5297% | SIM |
| 8.5032% | 12.3315% | 7.7945% | -4.5370% | SIM |
| 8.5089% | 12.3500% | 7.8058% | -4.5442% | SIM |
| 8.5147% | 12.3686% | 7.8173% | -4.5513% | SIM |
| 8.5204% | 12.3871% | 7.8289% | -4.5582% | SIM |
| 8.5262% | 12.4057% | 7.8406% | -4.5651% | SIM |
| 8.5319% | 12.4244% | 7.8525% | -4.5719% | SIM |
| 8.5377% | 12.4430% | 7.8645% | -4.5786% | SIM |
| 8.5434% | 12.4617% | 7.8766% | -4.5851% | SIM |
| 8.5492% | 12.4805% | 7.8889% | -4.5916% | SIM |

**GMV weight sensitivity**

| Asset | Markowitz | SIM | SIM − Markowitz | Absolute difference | Sign reversal | Bound status changed |
|---|---:|---:|---:|---:|:---:|:---:|
| SPY | 20.0000% | 20.0000% | -0.0000% | 0.0000% | NO | NO |
| EFA | 20.0000% | 5.6279% | -14.3721% | 14.3721% | NO | YES |
| EEM | -17.6873% | -0.5120% | 17.1753% | 17.1753% | NO | NO |
| TLT | 20.0000% | 20.0000% | -0.0000% | 0.0000% | NO | NO |
| AGG | 20.0000% | 20.0000% | -0.0000% | 0.0000% | NO | NO |
| GLD | 19.5531% | 20.0000% | 0.4469% | 0.4469% | NO | YES |
| USO | -1.8658% | 1.3255% | 3.1913% | 3.1913% | YES | NO |
| DBC | 20.0000% | 13.5586% | -6.4414% | 6.4414% | NO | YES |

- Largest changes: EEM=17.1753%, EFA=14.3721%, DBC=6.4414%.

**tangency weight sensitivity**

| Asset | Markowitz | SIM | SIM − Markowitz | Absolute difference | Sign reversal | Bound status changed |
|---|---:|---:|---:|---:|:---:|:---:|
| SPY | 20.0000% | 20.0000% | 0.0000% | 0.0000% | NO | NO |
| EFA | 20.0000% | 11.2867% | -8.7133% | 8.7133% | NO | YES |
| EEM | 15.1601% | 4.2053% | -10.9548% | 10.9548% | NO | NO |
| TLT | 20.0000% | 20.0000% | 0.0000% | 0.0000% | NO | NO |
| AGG | 4.2534% | 20.0000% | 15.7466% | 15.7466% | NO | YES |
| GLD | 20.0000% | 20.0000% | -0.0000% | 0.0000% | NO | NO |
| USO | -19.4136% | -4.7684% | 14.6452% | 14.6452% | NO | NO |
| DBC | 20.0000% | 9.2764% | -10.7236% | 10.7236% | NO | YES |

- Largest changes: AGG=15.7466%, USO=14.6452%, EEM=10.9548%.

- GMV gross-exposure difference (SIM − Markowitz): -0.380822.

Covariance-structure comparison

The full Markowitz covariance matrix retains every sample covariance. The SIM-implied covariance generates cross-asset covariance only through common SPY exposure and assumes zero residual cross-covariances.
- Markowitz covariance condition number: 607.642792.
- SIM covariance condition number: 82.932790.
- Monthly covariance-difference Frobenius norm: 0.006871555546.
- Maximum absolute monthly covariance discrepancy: 0.004202446923.

**Full Markowitz covariance matrix (monthly)**

| Asset | SPY | EFA | EEM | TLT | AGG | GLD | USO | DBC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 0.00192877 | 0.00187120 | 0.00199391 | -0.00014159 | 0.00014119 | 0.00017615 | 0.00156977 | 0.00104728 |
| EFA | 0.00187120 | 0.00242362 | 0.00254960 | -0.00008586 | 0.00021083 | 0.00047300 | 0.00198012 | 0.00134898 |
| EEM | 0.00199391 | 0.00254960 | 0.00364331 | -0.00012331 | 0.00022894 | 0.00090781 | 0.00232354 | 0.00170546 |
| TLT | -0.00014159 | -0.00008586 | -0.00012331 | 0.00159541 | 0.00043539 | 0.00051570 | -0.00155474 | -0.00070268 |
| AGG | 0.00014119 | 0.00021083 | 0.00022894 | 0.00043539 | 0.00017214 | 0.00024186 | -0.00028320 | -0.00006316 |
| GLD | 0.00017615 | 0.00047300 | 0.00090781 | 0.00051570 | 0.00024186 | 0.00247068 | 0.00021283 | 0.00080387 |
| USO | 0.00156977 | 0.00198012 | 0.00232354 | -0.00155474 | -0.00028320 | 0.00021283 | 0.01192867 | 0.00505104 |
| DBC | 0.00104728 | 0.00134898 | 0.00170546 | -0.00070268 | -0.00006316 | 0.00080387 | 0.00505104 | 0.00294617 |

**SIM-implied covariance matrix (monthly)**

| Asset | SPY | EFA | EEM | TLT | AGG | GLD | USO | DBC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 0.00193022 | 0.00186990 | 0.00199084 | -0.00013941 | 0.00014206 | 0.00016996 | 0.00156437 | 0.00104705 |
| EFA | 0.00186990 | 0.00242210 | 0.00192862 | -0.00013505 | 0.00013762 | 0.00016464 | 0.00151548 | 0.00101433 |
| EEM | 0.00199084 | 0.00192862 | 0.00364228 | -0.00014379 | 0.00014652 | 0.00017529 | 0.00161350 | 0.00107993 |
| TLT | -0.00013941 | -0.00013505 | -0.00014379 | 0.00160492 | -0.00001026 | -0.00001227 | -0.00011299 | -0.00007562 |
| AGG | 0.00014206 | 0.00013762 | 0.00014652 | -0.00001026 | 0.00017309 | 0.00001251 | 0.00011513 | 0.00007706 |
| GLD | 0.00016996 | 0.00016464 | 0.00017529 | -0.00001227 | 0.00001251 | 0.00246698 | 0.00013774 | 0.00009219 |
| USO | 0.00156437 | 0.00151548 | 0.00161350 | -0.00011299 | 0.00011513 | 0.00013774 | 0.01196060 | 0.00084859 |
| DBC | 0.00104705 | 0.00101433 | 0.00107993 | -0.00007562 | 0.00007706 | 0.00009219 | 0.00084859 | 0.00295412 |

**Largest absolute covariance discrepancies (monthly covariance)**

| Asset i | Asset j | Markowitz | SIM | SIM − Markowitz |
|---|---|---:|---:|---:|
| USO | DBC | 0.0050510395 | 0.0008485926 | -0.0042024469 |
| TLT | USO | -0.0015547432 | -0.0001129857 | 0.0014417575 |
| EEM | GLD | 0.0009078135 | 0.0001752927 | -0.0007325207 |
| GLD | DBC | 0.0008038664 | 0.0000921921 | -0.0007116743 |
| EEM | USO | 0.0023235444 | 0.0016135011 | -0.0007100434 |
| TLT | DBC | -0.0007026807 | -0.0000756223 | 0.0006270583 |
| EEM | DBC | 0.0017054617 | 0.0010799305 | -0.0006255312 |
| EFA | EEM | 0.0025496024 | 0.0019286226 | -0.0006209798 |
| TLT | GLD | 0.0005157030 | -0.0000122749 | -0.0005279779 |
| EFA | USO | 0.0019801180 | 0.0015154817 | -0.0004646363 |

**Largest absolute correlation discrepancies**

| Asset i | Asset j | Markowitz | SIM | SIM − Markowitz |
|---|---|---:|---:|---:|
| TLT | AGG | 0.830810 | -0.019466 | -0.850276 |
| USO | DBC | 0.852031 | 0.142761 | -0.709270 |
| AGG | GLD | 0.370856 | 0.019141 | -0.351715 |
| TLT | USO | -0.356391 | -0.025788 | 0.330603 |
| TLT | DBC | -0.324111 | -0.034730 | 0.289380 |
| AGG | USO | -0.197631 | 0.080017 | 0.277648 |
| TLT | GLD | 0.259750 | -0.006169 | -0.265919 |
| GLD | DBC | 0.297952 | 0.034150 | -0.263801 |
| EEM | GLD | 0.302580 | 0.058478 | -0.244101 |
| EFA | EEM | 0.858009 | 0.649329 | -0.208680 |

Covariance Effect

- Specification A: MARKOWITZ 33, SIM 47, TIE 0 across 80 common targets; mean absolute annual-volatility difference 0.328860%.
- Specification B: MARKOWITZ 2, SIM 78, TIE 0 across 80 common targets; mean absolute annual-volatility difference 0.467911%.
- Specification C: MARKOWITZ 1, SIM 79, TIE 0 across 80 common targets; mean absolute annual-volatility difference 0.948989%.
These differences isolate the covariance model because the saved expected-return vectors are exactly identical. The SIM restriction removes residual cross-asset covariance and retains only covariance transmitted through SPY beta exposure.

Additional Expected-Return Effect

- Specification A: mean absolute frontier difference changes from 0.328860% in Experiment 1 to 1.606283% in Experiment 2; the complete-model counts are MARKOWITZ 0, SIM 80, TIE 0.
- Specification B: mean absolute frontier difference changes from 0.467911% in Experiment 1 to 2.314345% in Experiment 2; the complete-model counts are MARKOWITZ 0, SIM 80, TIE 0.
- Specification C: mean absolute frontier difference changes from 0.948989% in Experiment 1 to 4.213380% in Experiment 2; the complete-model counts are MARKOWITZ 0, SIM 80, TIE 0.
Experiment 2 changes the SIM expected-return vector in addition to its covariance matrix. Its increment relative to Experiment 1 is therefore the additional expected-return-model effect; it must not be interpreted as another covariance-only result.

Economic interpretation

- Assets least naturally represented by SPY as the sole factor, based on the lowest saved R² values: GLD=0.0061, TLT=0.0063, AGG=0.0606.
- The largest covariance and correlation discrepancies above identify the assets and pairs for which the single-index approximation departs most from the full sample covariance structure.
- Experiment 1 — Covariance-model effect only: the largest available portfolio weight L1 change is 1.318012 for Specification A GMV.
- Experiment 1 — Covariance-model effect only: the most sensitive individual saved allocation is AGG in the GMV comparison, with an absolute weight change of 60.6802%.
- Experiment 1 — Covariance-model effect only: GMV weight L1 differences by constraint are A=1.318012, B=0.304769, C=0.416270; B reduces the difference relative to A, C reduces the difference relative to A.
- Experiment 1 — Covariance-model effect only: for attained tangencies, C amplifies the difference relative to B.
- Experiment 2 — Complete model comparison: the largest available portfolio weight L1 change is 1.318012 for Specification A GMV.
- Experiment 2 — Complete model comparison: the most sensitive individual saved allocation is AGG in the GMV comparison, with an absolute weight change of 60.6802%.
- Experiment 2 — Complete model comparison: GMV weight L1 differences by constraint are A=1.318012, B=0.304769, C=0.416270; B reduces the difference relative to A, C reduces the difference relative to A.
- Experiment 2 — Complete model comparison: for attained tangencies, C reduces the difference relative to B.
Constraints can change which assets absorb covariance or mean-model differences. The bound-change columns and L1 distances above report that effect directly. Pointwise frontier crossings are retained, and the report deliberately assigns no overall model winner.
