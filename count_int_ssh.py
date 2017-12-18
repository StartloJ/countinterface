from netmiko import ConnectHandler
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
    utp = [0 , 0 , 0 , 0 , 0]
    fiber = [0 , 0 , 0 , 0 , 0]
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
            elif('inactive' in item):
                score = item

            if('Base' in item):
                if(item[-2:] in id_utp):
                    idc = 'utp'
                if(item[-2:] in id_fiber):
                    idc = 'fiber'
            elif('XCVR' in item or 'Gbic' in item):
                idc = 'fiber'
            else:
                pass
        # !===============================================================================
        if(idc == 'utp'):
            utp[0] += 1
            if(score == 'connected'): utp[1] += 1
            elif(score == 'notconnect'): utp[2] += 1
            elif(score == 'disabled'): utp[3] += 1
            elif(score == 'inactive'): utp[4] += 1
        elif(idc == 'fiber'):
            fiber[0] += 1
            if(score == 'connected'): fiber[1] += 1
            elif(score == 'notconnect'): fiber[2] += 1
            elif(score == 'disabled'): fiber[3] += 1
            elif(score == 'inactive'): fiber[4] += 1
        else:
            if(port[0][-2:].isdigit()):
                fiber[0] += 1
                if(score == 'connected'): fiber[1] += 1
                elif(score == 'notconnect'): fiber[2] += 1
                elif(score == 'disabled'): fiber[3] += 1
                elif(score == 'inactive'): fiber[4] += 1
            errorcase.append(port)
            print '[-] ' + port[0] + ' can not detected for count in UTP or Fiber.'
    return [utp , fiber , errorcase]
        
def select_version(vers , uptime):
    vers = vers[vers.find('Version')+8 : vers.find('RELEASE')-1]
    uptime = uptime[uptime.find('is')+3 :]
    uptime = uptime.replace('\r\n' , '')
    return vers , uptime

def only_integer(text):
    text = list(text)
    result = ''
    for let in text:
        if(let.isdigit()):
            result += let
        else:
            pass
    return result

def calc_process(hostname , cpu , mem):
    cpus = cpu.split('\n')
    cpus = [core for core in cpus if 'five minutes' in core]
    result = 0
    mem_use = str()
    for core in cpus:
        perc = core.split()[-1]
        perc = perc[:perc.find('%')]
        result += int(perc)
    result_cpu = result/len(cpus)
    if('DS' in hostname or 'ASS' in hostname or 'ASCS' in hostname):
        mem_use = mem[mem.find('total') : mem.find('used')]
        mem_use = only_integer(mem_use)
        mem_total = mem[mem.find('memory') : mem.find('total')]
        mem_total = only_integer(mem_total)
        mem_perc = float(mem_use) / int(mem_total)
        mem_perc = "%.2f" % mem_perc
    elif('CS' in hostname or 'AS' in hostname):
        mem_use = mem[mem.find('Used:') : mem.find('Free:')]
        mem_use = only_integer(mem_use)
        mem_total = mem[mem.find('Total:') : mem.find('Used:')]
        mem_total = only_integer(mem_total)
        mem_perc = float(mem_use) / int(mem_total)
        mem_perc = "%.2f" % mem_perc
    return str(result_cpu) , str(mem_perc)

def get_interface(text):

    all_int = text.split('!')
    all_int = all_int[0]
    lines = all_int.split('\n')
    intf = [line.split() for line in lines]
    intf = intf[2:-1]
    print '[+] Get List of Interface.'
    return intf
 

def get_hostname(text):
    pointer = 0
    find_status = True
    while(find_status):
        if(text[text.find('uptime is')-pointer] == '!'):
            text = text[text.find('uptime is')-(pointer-3): text.find('uptime is')]
            return text
        else:
            pointer += 1
    print '[+] Get Hostname.'
    

def get_version(text):
    texts = text.split('!')
    ios , uptime = select_version(texts[1] , texts[2])
    print '[+] Get IOS Version and Uptime.'
    return [ios , uptime]

def get_process(text , hostname):
    texts = text.split('!')
    texts = [let for let in texts if let != '\r\n\r\n']
    send_mem = texts[4]
    index = 4
    while(index < len(texts)):
        if(len(send_mem) > 10):
            send_mem = texts[index]
            break
        else:
            index += 1
    print send_mem
    cpu , mem = calc_process(hostname , texts[3] , send_mem)
    print '[+] Get CPU and Memory Process.'
    return [cpu , mem]

def writefile(ip , hostname , int_status=[] , version=[] , process=[]):
    try:
        if not os.path.exists('Kitty/'):
            os.makedirs('Kitty')
        filer = open('Kitty/counter.txt' , 'a')
        filer.write('Hostname: ' + hostname + '\n')
        filer.write('IP Address: ' + ip + '\n')
        filer.write('IOS Version: ' + version[0] + '\n')
        filer.write('Uptime: ' + version[1] + '\n')
        filer.write('CPU: ' + process[0] + '\n')
        filer.write('Memory Used: ' + process[1] + '\n')
        wrUTP = 'UTP Total : ' + str(int_status[0][0]) + ' \rUp : ' + str(int_status[0][1]) + ' \rDown : ' + str(int_status[0][2]) + ' \rDisabled : ' + str(int_status[0][3]) + ' \rInactive : ' + str(int_status[0][4])
        wrFIBER = 'Fiber Total : ' + str(int_status[1][0]) + ' \rUp : ' + str(int_status[1][1]) + ' \rDown : ' + str(int_status[1][2]) + ' \rDisabled : ' + str(int_status[1][3])  + ' \rInactive : ' + str(int_status[1][4])
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
    cisco_DS = {
        'device_type' : 'cisco_xe',
        'ip' : ip,
        'username' : username,
        'password' : password,
    }
    with open("command.base" , "r") as f:
        comms = f.read().split('\n')
    raw_text = str()

    try:
        ssh_connect = ConnectHandler(**cisco_DS)
        for com in comms:
            raw_text += ssh_connect.send_command(com)
            raw_text += '\r\n!\r\n'
        ssh_connect.disconnect()
    except IOError,ImportError:
        print '[-] Can not SSH : ' + str(ip) + '.'
    print raw_text
    hostname = get_hostname(raw_text)
    lstint = get_interface(raw_text)
    int_status = countint(lstint)
    vers = get_version(raw_text)
    process = get_process(raw_text , hostname)
    writefile(ip , hostname , int_status , vers , process)
    print '[+] Analyze Log Success.'

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


username = 'ait'
password = 'aitadmin'
if __name__ == '__main__':
    for ipl in get_ip():
        if(ipl is not 'Null'):
            print ipl
            for ip in ipl:
                callmebaby(ip, username, password)