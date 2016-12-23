import numpy as np
dt=1.0
A=np.matrix([[1,dt],[0,1]])
uk=np.matrix([[2]])
Xkmin=np.matrix([[50],[5]])
Xk=np.matrix([[0],[0]])
B=np.matrix([[0.5*dt*dt],[dt]])
C=([[1],[0]])
Yk=([[0],[0]])
count=8
while(count>0):
	print("A=")
	print(A)
	print("B=")
	print(B)
	print("Xkmin=")
	print(Xkmin)
	Xk=A*(Xkmin)+B*(uk)
	Xkmin=Xk
	print(Xk)
	count = count - 1
print("END?")
