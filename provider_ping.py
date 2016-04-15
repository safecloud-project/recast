import sys

filepath = sys.argv[1]


with open(filepath) as f:
    content = f.readlines()

content = content[0]

str_times = content.split(':')[1].split(' ')
str_times = str_times[1:len(str_times)-1]

int_times = map(lambda x: float(x), str_times)

total = 0
for i in int_times:
	total += i


print total/(len(int_times))