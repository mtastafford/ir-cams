import numpy as np
dt=1.0
A=np.matrix([[1,dt],[0,1]])
uk=np.matrix([[-9.8106]])
Xkmin=np.matrix([[20],[0]])
Xk=np.matrix([[0],[0]])
B=np.matrix([[0.5*dt*dt],[dt]])
count=10
while(Xkmin.item((0,0))>0):
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
