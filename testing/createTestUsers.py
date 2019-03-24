import sys

template='''
{
    "pushTokens" : [],
    "activated" : true,
    "email" : "t%d",
    "password" : "$2b$10$0NNUTnBOsvAmel.Rlmz.hucLGw5FjOJ6iMLoUhrJ.NlVPaOBobLB2",
    "nickname" : "Test user %d",
    "isDriver" : true,
    "carplate" : "12345",
    "contact" : "52252872"
}
'''
# password is 't'

def generateDocuments(n=1):
    doc = ''
    for i in range(1, n+1):
        doc += template%(i, i)
    return doc

if __name__ == "__main__":
    if(len(sys.argv)<2):
        print("Require 1 argument: N (number of test users to generate)")
        print("Example command: [python .\\createTestUsers.py 100 > testUsers.txt]")
        print("Then insert the content of testUsers.txt to Robo 3T")
    else:
        print(generateDocuments(int(sys.argv[1])))