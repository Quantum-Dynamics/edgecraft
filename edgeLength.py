import numpy as np
import matplotlib.pyplot as plt

"""
def calculate_edge_length(edge:np.ndarray,pixelSize=1)->float:
    #at each row, find all the pixels that are in the edge
    #take the average of them to be the true edge point at that y index
    #connect them with tangent lines
    #spam the pythagorean theorem
    edgelength=0.0
    centeredge=[0.0]*len(edge)
    for y in range(len(edge)):
        if(np.sum(edge[y])==0):
            print("Error: no edge in this y column")
            return
        for x in range(len(edge[y])):
            centeredge[y]=centeredge[y]+x*edge[y][x]
        centeredge[y]=centeredge[y]/np.sum(edge[y])
        print(centeredge[y])
    for x in range (0,len(edge)-1):
        edgelength=edgelength+np.sqrt(1+(centeredge[x]-centeredge[x+1])**2)
    #since there's 1 less tangent line than pixels
    edgelength=edgelength+1
    return edgelength
"""
    
def calculate_edge_length(edge:np.ndarray,pixelSize=1)->float:
    #at each row, find all the pixels that are in the edge
    #take the average of them to be the true edge point at that y index
    #connect them with tangent lines
    #spam the pythagorean theorem
    edgelength=0.0
    centeredge=[0.0]*len(edge)
    for y in range(len(edge)):
        mindist=[0]*len(edge[y])
        if(np.sum(edge[y])==0):
            print("Error: no edge in this y column")
            return
        for x in range(len(edge[y])):
            if(edge[y][x]==0):
                pass
    for x in range (0,len(edge)-1):
        edgelength=edgelength+np.sqrt(1+(centeredge[x]-centeredge[x+1])**2)
    #since there's 1 less tangent line than pixels
    edgelength=edgelength+1
    return edgelength



x = np.arange(0, int(10000), 1)
y = np.arange(0, int(10000), 1)
X,Y = np.meshgrid(x, y)
space_matrix = (
    (X<=2*Y)
).astype(int)
space_matrix[np.where(X<Y)]=0
print("edgelength=",calculate_edge_length(space_matrix))
plt.imshow(space_matrix)
plt.title("space_matrix")
plt.colorbar()
plt.show()
print(np.where(space_matrix==0))