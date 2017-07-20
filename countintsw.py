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

def split_lines(texts):
    texts = texts.split('\n')
    text_lst = []
    for rou in range(5):
        if(texts[rou].find('#') == -1):
            text_lst.append(texts[rou])
        else: pass
    text_lst = filter(None , text_lst)
    return text_lst

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
    return [utp , fiber , errorcase]
        
def select_version(textlst):
    vers , ios = textlst
    vers = vers[vers.find('Version')+8 : vers.find('RELEASE')-2]
    ios = ios[ios.find('is')+2 :]
    return vers , ios

def calc_process(lst):
    cpu , mem = lst
    cpu = cpu.split()
    cpu = cpu[-1]
    mem_total = mem[mem.find('Total:')+6 : mem.find('Used:')]
    mem_total = mem_total.replace(',' , '')
    mem_used = mem[mem.find('Used:')+6 : mem.find('Free:')]
    mem_used = mem_used.replace(',' , '')
    mem_avg = (float(mem_used) / int(mem_total)) * 100
    mem_avg = "{0:.2f}".format(mem_avg) + '%'
    return cpu , mem_avg

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

def get_version(text):
    try:
        texts = text[text.find('KickmeOff')+10 : text.find('HitmeOn')]
        cleantext = split_lines(texts)
        ios , uptime = select_version(cleantext)
        print '[+] Get IOS Version and Uptime.'
        return [ios , uptime]
    except ValueError:
        print '[-] Something with show version Error.'
        return ['' , '']
    

def get_process(text):
    try:
        texts = text[text.find('HitmeOn')+8 : text.find('HitmeOff')]
        cleantext = split_lines(texts)
        cpu , mem = calc_process(cleantext)
        print '[+] Get CPU and Memory Process.'
        return [cpu , mem]
    except ValueError:
        print '[-] Something with show process Error.'
        return ['' , '']
    

def writefile(ip , hostname , int_status=[] , version=[] , process=[]):
    try:
        if not os.path.exists('Kitty/'):
            os.makedirs('Kitty')
        filer = open('Kitty/'+ hostname +'.txt' , 'w')
        filer.write('Hostname: ' + hostname + '\n')
        filer.write('IP Address: ' + ip + '\n')
        filer.write('IOS Version: ' + version[0] + '\n')
        filer.write('Uptime: ' + version[1] + '\n')
        filer.write('CPU: ' + process[0] + '\n')
        filer.write('Memory Used: ' + process[1] + '\n')
        wrUTP = 'UTP Total : ' + str(int_status[0][0]) + ' \rUp : ' + str(int_status[0][1]) + ' \rDown : ' + str(int_status[0][2]) + ' \rDisabled : ' + str(int_status[0][3])
        wrFIBER = 'Fiber Total : ' + str(int_status[1][0]) + ' \rUp : ' + str(int_status[1][1]) + ' \rDown : ' + str(int_status[1][2]) + ' \rDisabled : ' + str(int_status[1][3])
        filer.write(wrUTP + '\n')
        filer.write(wrFIBER + '\n')
        er = ''
        for e in int_status[2]:
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
##        if(call.read_until('>',2).find('>') != -1):
##            call.write('aitadmin'+'\n')
##        # !===================================================
        call.write('terminal length 0'+'\n')
        call.write('!==== KickmeOn'+'\n')
        call.write('show interface status'+'\n')
        call.write('!==== KickmeOff'+'\n')
        call.write('show version | include Cisco IOS Software'+'\n')
        call.write('show version | include uptime is'+'\n')
        call.write('!==== HitmeOn'+'\n')
        call.write('show processes cpu | include CPU utilization'+'\n')
        call.write('show processes memory | include Total'+'\n')
        call.write('!==== HitmeOff'+'\n')
        call.write('terminal length 24'+'\n')
        call.write('exit'+'\n')
        call.close
        print '[+] Execute Command Success.'
        plaintext = call.read_all()
        hostname = get_hostname(plaintext)
        lstint = get_interface(plaintext , hostlen=len(hostname))
        int_status = countint(lstint)
        vers = get_version(plaintext)
        process = get_process(plaintext)
        writefile(ip , hostname , int_status , vers , process)
        print '[+] Analyze Log Success' + str(ip)
    except IOError,ImportError:
        print '[-] Can not Telnet : ' + str(ip)
    
def get_ip():
    filesName = glob('*.txt')
    all_ip = []
    for fil in filesName:
        text = open(fil , 'r')
        device_ip = text.read().split('\n')
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
            #======= End ip loop ========
    #======= End file loop ========
