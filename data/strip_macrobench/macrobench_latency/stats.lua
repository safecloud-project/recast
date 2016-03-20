--Some statistical operations in tables of numbers

function mean( t )
  local sum = 0
  local count= 0
  for k,v in pairs(t) do
    --if type(v) == 'number' then
      sum = sum + v
      count = count + 1
   -- end
  end
  return (sum / count)
end

-- Get the standard deviation of a table
function standardDeviation( t )
  local m
  local vm
  local sum = 0
  local count = 0
  local result

  m = mean( t )

  for k,v in pairs(t) do
   -- if type(v) == 'number' then
      vm = v - m
      sum = sum + (vm * vm)
      count = count + 1
   -- end
  end

  result = math.sqrt(sum / (count-1))

  return result,m
end

function round(num, idp)
	local mult = 10^(idp or 0)
	return math.floor(num * mult + 0.5) / mult
end
function percentiles(requestedPercentiles , values)	
	local percs={}	
	local tempValues={}
	for i=1,#values do
		tempValues[i]=values[i]
	end
	table.sort(tempValues)
	for _,reqPerc in pairs(requestedPercentiles) do
		
		local p = tempValues[ round( reqPerc / 100 * #values+0.5) ]
		--print("INPUT VALUES:",table.concat(tempValues," "), "%th:", reqPerc, "ris:", p)
		table.insert(percs, p)
	end
	--table.insert(percs,tempValues[1])
	--table.insert(percs,tempValues[#tempValues])		
	return percs
end

lc=0
for l in io.lines() do
	local values_per_line={}
	for word in l:gmatch("%w+") do table.insert(values_per_line, word) end
	local stdev,mean = standardDeviation(values_per_line)
	print(lc,mean,stdev)
	lc=lc+1
end