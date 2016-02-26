crypto=require"crypto"
math.randomseed(os.clock() * 1e6)
function a_rand()
	return crypto.evp.new("sha1"):digest(math.random())
end
total_keys = tonumber(arg[1]) or 10
size=arg[2] or "16"
host = arg[3] or os.getenv("PROXY_PORT_3000_TCP_ADDR") .. ":" .. os.getenv("PROXY_PORT_3000_TCP_PORT")
for i=1,total_keys do
	--print("Putting data of size:",#v,misc.bitcalc(v).megabytes.." MB")
	local next_key=a_rand()
	local p = "wget -q -O/dev/null  --method=PUT --body-file=random"..size..".dat "..host.."/"..next_key
	local p_short = "wget -q -O/dev/null  --method=PUT --body-file=random"..size..".dat "..host.."/"..next_key
	print(i ,p_short)
	os.execute(p)
end
