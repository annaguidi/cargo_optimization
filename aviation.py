from gurobipy import *
import csv
import numpy as np

myModel = Model( "minCost" )

#dijt
demand = [[[0 for i in range (5)] for j in range (3)] for k in range(3)]

demand[0][1][0] = 10000
demand[0][1][1] = 20000
demand[0][1][2] = 10000
demand[0][1][3] = 40000
demand[0][1][4] = 30000

for x in range(5):
    demand[0][2][x] = 5000

for x in range(5):
    demand[1][0][x] = 2500

for x in range(5):
    demand[1][2][x] = 2500

for x in range(5):
    demand[2][0][x] = 4000


demand[2][1][0] = 40000
demand[2][1][1] = 20000
demand[2][1][2] = 30000
demand[2][1][3] = 20000
demand[2][1][4] = 40000

print(demand)

#make decision variables
#xijt
myVars = [[[0 for i in range (5)] for j in range (3)] for k in range(3)]

#yijt
emptyCargoVars = [[[0 for i in range (5)] for j in range (3)] for k in range(3)]

#uijt
undeliveredCargoVars = [[[0 for i in range (5)] for j in range (3)] for k in range(3)]

#yiit
empty_stay = [[[0 for i in range (5)] for j in range (3)] for k in range(3)]
print("empty stay")
print(empty_stay)

#initialize decision variables
#xijt
for i in range(3):
    for j in range(3):
        for k in range(5):
            if (i != j):
                myVars[i][j][k] = myModel.addVar(vtype = GRB.CONTINUOUS, name = 'x' + str(i) + "_" + str(j) + "_" + str(k))

myModel.update()

#yijt
for i in range(3):
    for j in range(3):
        for k in range(5):
            if (i != j):
                emptyCargoVars[i][j][k] = myModel.addVar(vtype = GRB.CONTINUOUS, name = 'y' + str(i) + "_" + str(j) + "_" + str(k))

myModel.update()

#uijt
for i in range(3):
    for j in range(3):
        for k in range(5):
            if (i != j):
                undeliveredCargoVars[i][j][k] = myModel.addVar(vtype = GRB.CONTINUOUS, name = 'u' + str(i) + "_" + str(j) + "_" + str(k))

myModel.update()

#yiit
for i in range(3):
    for j in range(3):
        for k in range(5):
            if (i == j):
                empty_stay[i][j][k] = myModel.addVar(vtype = GRB.CONTINUOUS, name = 'stay' + str(i) + "_" + str(i) + "_" + str(k))

myModel.update()

#cit
# c = [[0 for i in range (5)] for j in range (3)]
# print("THIS IS CAPACITY")
# print(c)
#
# for k in range(5):
#     for i in range(3):
#         for j in range(3):
#             if (i != j):
#                 c[i][k] += myVars[i][j][k]
#                 c[i][k] += emptyCargoVars[i][j][k]
#             else:
#                 c[i][k] += empty_stay[i][j][k]
#
# print(c)

#DO I PUT THIS IN GUROBI??????



#objectiveFunction
objExpr = LinExpr()
for x in range(5):
    objExpr += 3 * emptyCargoVars[0][2][x]
    objExpr += 3 * emptyCargoVars[2][0][x]

    myModel.setObjective( objExpr , GRB.MINIMIZE)

for x in range(5):
    objExpr += 7 * emptyCargoVars[0][1][x]
    objExpr += 7 * emptyCargoVars[1][0][x]

    myModel.setObjective( objExpr , GRB.MINIMIZE)

for x in range(5):
    objExpr += 6 * emptyCargoVars[2][1][x]
    objExpr += 6 * emptyCargoVars[1][2][x]

    myModel.setObjective( objExpr , GRB.MINIMIZE)

for i in range(3):
    for j in range(3):
        if (i != j):
            for x in range(5):
                objExpr += 10 * undeliveredCargoVars[i][j][x]

                myModel.setObjective( objExpr , GRB.MINIMIZE)

myModel.update()



#create constraints

#amt you ship
for i in range(3):
    for j in range(3):
        for k in range(5):
            if (k != 0):
                constExpr = LinExpr()
                constExpr += myVars[i][j][k]
                rhs = LinExpr()
                rhs += undeliveredCargoVars[i][j][k - 1]
                rhs += demand[i][j][k]
                myModel.addConstr(lhs = constExpr, sense = GRB.LESS_EQUAL, rhs = rhs , name = str(i) + str(j) + str(k) + "ship")
            else:
                constExpr = LinExpr()
                constExpr += myVars[i][j][k]
                rhs = LinExpr()
                rhs += undeliveredCargoVars[i][j][4]
                rhs += demand[i][j][k]
                myModel.addConstr(lhs = constExpr, sense = GRB.LESS_EQUAL, rhs = rhs , name = str(i) + str(j) + str(k) + "ship")


#how accumulation happens
for i in range(3):
    for j in range(3):
        for k in range(5):
            if (k == 0):
                constExpr = LinExpr()
                constExpr += demand[i][j][k]
                constExpr += undeliveredCargoVars[i][j][4]
                constExpr -= myVars[i][j][k]
                rhs = undeliveredCargoVars[i][j][k]
                myModel.addConstr(lhs = constExpr, sense = GRB.EQUAL, rhs = rhs , name = str(i) + str(j) + str(k) + "accumulation")
            else:
                constExpr = LinExpr()
                constExpr += demand[i][j][k]
                constExpr += undeliveredCargoVars[i][j][k - 1]
                constExpr -= myVars[i][j][k]
                rhs = undeliveredCargoVars[i][j][k]
                myModel.addConstr(lhs = constExpr, sense = GRB.EQUAL, rhs = rhs , name = str(i) + str(j) + str(k) + "accumulation")


#flow balance equations
for j in range(3):
    for k in range(5):
        constExpr = LinExpr()
        rhs = LinExpr()
        for i in range(3):
            if (k == 4):
                constExpr += myVars[i][j][k]
                constExpr += emptyCargoVars[i][j][k]
                constExpr += empty_stay[i][j][k]
                rhs += myVars[j][i][0]
                rhs += emptyCargoVars[j][i][0]
                rhs += empty_stay[j][i][0]
    # myModel.addConstr(lhs = constExpr, sense = GRB.EQUAL, rhs = rhs , name = str(i) + str(j) + str(k) + "flow")
            else:
                constExpr += myVars[i][j][k]
                constExpr += emptyCargoVars[i][j][k]
                constExpr += empty_stay[i][j][k]
                rhs += myVars[j][i][k + 1]
                rhs += emptyCargoVars[j][i][k + 1]
                rhs += empty_stay[j][i][k + 1]
        myModel.addConstr(lhs = constExpr, sense = GRB.EQUAL, rhs = rhs , name = str(i) + str(j) + str(k) + "flow")


#capacity restriction (120,000)

#Create constraint for not exceeding the cargo carrying capacity of 120000

for k in range(5):
    constExpr = LinExpr()
    for i in range(3):
        for j in range(3):
            constExpr += myVars[i][j][k]
            constExpr += emptyCargoVars[i][j][k]
            constExpr += empty_stay[i][j][k]
    myModel.addConstr(lhs = constExpr, sense = GRB.EQUAL, rhs = 120000 , name = str(i) + str(j) + str(k) + "capacityLimit")


myModel.update()

myModel.write( filename = "testOutput3.lp" )

myModel.optimize()

print( "\nOptimal Objective: " + str( myModel.ObjVal ) )
print( "\nOptimal Solution:" )
allVars = myModel.getVars()
for x in allVars:
    print(x.varName, x.X)
    print("\n")

print( "\nConstraints:" )
myConsts = myModel.getConstrs()

for x in myConsts:
    print(x.constrName, x.pi)


outFile = open( "solution.txt", "w" )
for curVar in allVars:
    outFile.write( curVar.varName + "," + str( curVar.x ) + "\n" )

for x in myConsts:
    outFile.write(x.constrName + "," + str(x.pi) + "\n")

outFile.write(str(myModel.ObjVal))

outFile.close()
