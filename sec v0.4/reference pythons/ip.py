import socket


urls=["https://www.sec.gov/Archives/edgar/data/910638/0000950144-08-000385-index.htm","https://www.sec.gov/Archives/edgar/data/1427189/9999999997-08-006296-index.htm",
"https://www.sec.gov/Archives/edgar/data/1413898/0001193125-08-001741-index.htm","https://www.sec.gov/Archives/edgar/data/815094/0001193125-08-011558-index.htm",
"https://www.sec.gov/Archives/edgar/data/815094/000119312508011558/d8k.htm", "https://www.sec.gov/Archives/edgar/data/815094/000119312508011558/dex991.htm"]
 
# [print (socket.gethostbyname("url")) for url in urls]

print (socket.gethostbyname_ex("www.sec.gov")) 


('e9076.dscb.akamaiedge.net', ['www.sec.gov', 'www.sec.gov.edgekey.net'], ['104.116.20.86'])
