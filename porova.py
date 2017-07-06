import random
from matplotlib import pyplot as plt
result = []
n = 100000
for x in xrange(n):
    r = sorted([random.randint(1,6) for l in xrange(4)])
    result.append(sum(r[1:]))
   
x = xrange(20)
y = [100.*result.count(i)/n for i in x]

print sum([i* y[i] for i in x])
#n, bins, patches = plt.hist(y, 50, normed=1, facecolor='green', alpha=0.75)
plt.scatter(x, y)

plt.show()
