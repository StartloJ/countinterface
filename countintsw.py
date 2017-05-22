from telnetlib import Telnet
from glob import glob
from base64 import b64decode
from time import sleep
import os

def get_id():
    f = open('identifier.base' , 'r')
    keep = f.read()
    '[+] Read Keys Identifier for media.'
    return keep.split('\n')

def countint(interfaces):
    utp = [0 , 0 , 0 , 0]
    fiber = [0 , 0 , 0 , 0]
    errorcase = []
    id_utp , id_fiber = get_id()
    id_utp = id_utp.split()
    id_fiber = id_fiber.split()
    for port in interfaces:
        score = ''
        idc = ''
        for item in port:
            if('connect' in item):
                score = item
            elif('disable' in item):
                score = item
            if('Base' in item):
                if(item[-2:] in id_utp):
                    idc = 'utp'
                if(item[-2:] in id_fiber):
                    idc = 'fiber'
            else:
                pass
        # !===============================================================================
        if(idc == 'utp'):
            utp[0] += 1
            if(score == 'connected'): utp[1] += 1
            elif(score == 'notconnect'): utp[2] += 1
            elif(score == 'disabled'): utp[3] += 1
        elif(idc == 'fiber'):
            fiber[0] += 1
            if(score == 'connected'): fiber[1] += 1
            elif(score == 'notconnect'): fiber[2] += 1
            elif(score == 'disabled'): fiber[3] += 1
        else:
            if(port[0][-2:].isdigit()):
                fiber[0] += 1
                if(score == 'connected'): fiber[1] += 1
                elif(score == 'notconnect'): fiber[2] += 1
                elif(score == 'disabled'): fiber[3] += 1
            errorcase.append(port)
            print '[-] ' + port[0] + ' can not detected for count in UTP or Fiber.'
    return utp , fiber , errorcase
        

def get_interface(text , hostlen=0):
    far = hostlen+7
    text = text[text.find('status')+8 : text.find('KickmeOff')-far]
    lines = text.split('\n')
    intf = [line.split() for line in lines if len(line.split()) > 1 and 'Gi' in line]
    print '[+] Get List of Interface.'
    return intf
 

def get_hostname(text):
    text = text[text.find('KickmeOn')+10 : text.find('#show')]
    print '[+] Get Hostname.'
    return text

def writefile(hostname , utp=[] , fiber=[] , err=[]):
    try:
        if not os.path.exists('Kitty/'):
            os.makedirs('Kitty')
        filer = open('Kitty/counter.txt' , 'a')
        filer.write(hostname + '\n')
        wrUTP = 'UTP Total : ' + str(utp[0]) + '\rUp : ' + str(utp[1]) + '\rDown : ' + str(utp[2]) + '\rDisabled : ' + str(utp[3])
        wrFIBER = 'Fiber Total : ' + str(fiber[0]) + '\rUp : ' + str(fiber[1]) + '\rDown : ' + str(fiber[2]) + '\rDisabled : ' + str(fiber[3])
        filer.write(wrUTP + '\n')
        filer.write(wrFIBER + '\n')
        er = ''
        for e in err:
            er += e[0] + ' , '
        filer.write('Cannot detect : ' + er + '\n')
        filer.write('!==========================================' + '\n')
    except IOError:
        print '[-] Error!! Can not write file.'
    print '[+] Write Anything to Resualt File.'

def callmebaby(ip, username, password):
    try:
        call = Telnet(ip)
        call.read_until("sername: ")
        call.write(username + '\n')
        call.read_until("assword: ")
        call.write(password + '\n')
        sleep(1)
        print '[+] Login Success.'
        if(call.read_until('>',2).find('>') != -1):
            call.write('aitadmin'+'\n')
        # !===================================================
        call.write('terminal length 0'+'\n')
        call.write('!==== KickmeOn'+'\n')
        call.write('show interface status'+'\n')
        call.write('!==== KickmeOff'+'\n')
        call.write('terminal length 24'+'\n')
        call.write('exit'+'\n')
        call.close
        print '[+] Execute Command Success.'
        plaintext = call.read_all()
        hostname = get_hostname(plaintext)
        lstint = get_interface(plaintext , hostlen=len(hostname))
        utp , fiber , err = countint(lstint)
        writefile(hostname , utp , fiber , err)
        print '[+] Analyze Log Success.'
    except IOError,ImportError:
        print '[-] Can not Telnet : ' + str(ip) + '.'
    


def get_ip():
    filesName = glob('*.txt')
    all_ip = []
    for fil in filesName:
        text = open(fil , 'r')
        device_ip = text.read().split('\r\n')
        if(len(device_ip) != 0):
            all_ip.append(device_ip)
        else:
            all_ip.append('Null')
    return all_ip

username = str(b64decode('c2FrcmFwZWU='))
password = str(b64decode('c2FrcmFwZWU0MQ=='))
if __name__ == '__main__':
    for ipl in get_ip():
        if(ipl is not 'Null'):
            for ip in ipl:
                callmebaby(ip, username, password)
