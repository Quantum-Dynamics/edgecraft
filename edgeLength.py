import numpy as np

def calculate_edge_length(edge:np.ndarray,pixelXsize=1,pixelYsize=1)->float:
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
        edgelength=edgelength+np.sqrt(pixelYsize**2+((centeredge[x]-centeredge[x+1])*pixelXsize)**2)
    #since there's 1 less tangent line than pixels
    edgelength=edgelength+1
    return edgelength