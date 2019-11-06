from sieve import Sieve

a = [i for i in range(5)]
b = [i for i in range(5,10)]
c = [i for i in range(15,20)]
d = [i for i in range(25,30)]
e = [i for i in range(35,40)]
f = [i for i in range(36,41)]
# g = [i for i in range(36,26)]
g = [i for i in range(12,46)]

arrs = [a,b,c,d,e,f,g]


def all_even_index_even(arr):
    for i in range(len(arr)):
        if i % 2 == 0 and not arr[i] % 2 == 0:
            return False
    return True

def always_increasing(arr):
    for i in range(len(arr)-1):
        if not arr[i] < arr[i+1]:
            return False
    return True

my_sieve = Sieve(lambda arr: sum(arr) >= 100, all_even_index_even, always_increasing)
# watchlist = [arr for arr in arrs if my_filter(arr)]
watchlist = my_sieve.sift(arrs)
print(watchlist)

