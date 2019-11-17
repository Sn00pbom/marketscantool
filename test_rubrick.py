from valuehunter import grade
r = grade.Rubrick()

r.add_column('first',1,2,3)
r.add_column('second',1,2,3)
r.add_column('third',1,2,3)
for col in r:
    print(col)
print(r.keys())