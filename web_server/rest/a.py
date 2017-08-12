var = 'a'
s1 = locals()['var']
print(s1)

s2 = vars()['var']
print(s2)

a=3
eval(var)
print(s1, s2, var, a)

exec("b = '1'")
print(b)