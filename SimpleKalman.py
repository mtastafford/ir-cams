KG=0.0
Eest=2.0
Eestminus=2.0
Emea=4.0
MEA=[75.0,71,70,74]
ESTt=68.0
ESTtminus=68.0
for i in range(0,4):
	print("Measurement =")
	print(MEA[i])
	print("BEGIN KALMAN GAIN CALCULATION")
	KG=(Eest/(Eest+Emea))
	print(KG)
	print("BEGIN ESTIMATE UPDATE")
	ESTt=ESTtminus+KG*(MEA[i]-ESTtminus)
	print(ESTt)
	print("BEGIN ERROR ESTIMATE UPDATE")
	Eest=(1-KG)*Eestminus
	print(Eest)
	Eestminus=Eest
	ESTtminus=ESTt

print("does this happen at the end?")
