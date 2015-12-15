crypto=require"crypto"
math.randomseed(os.clock() * 1e6)
function a_rand()
	return crypto.evp.new("sha1"):digest(math.random())
end
total_keys = tonumber(arg[1]) or 10
size=arg[2] or "16"
host = arg[3] or "192.168.99.104:3000"
for i=1,total_keys do
	--print("Putting data of size:",#v,misc.bitcalc(v).megabytes.." MB")
	local next_key=a_rand()
	--local p = "wget -q -O/dev/null  --method=PUT --body-data=\""..v.."...\" http://127.0.0.1:30001/"..next_key
	local p = "wget -q -O/dev/null  --method=PUT --body-file=random"..size..".dat "..host.."/"..next_key
	local p_short = "wget -q -O/dev/null  --method=PUT --body-file=random"..size..".dat "..host.."/"..next_key
	print(i ,p_short)
	os.execute(p)
end

