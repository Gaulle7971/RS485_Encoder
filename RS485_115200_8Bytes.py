import serial
import serial.tools.list_ports
import csv

##ser.close
length=50000
mulAngel=[0]*length
sinAngel=[0]*length
Angel=[0]*length
lastAngel=[0]*length
lastZone=[0]*length
yaw=[0]*length
w=[0]*length
rx_flag=0
save_flag=0
last_data=0
temp_mul=0
temp_angel=0
temp_high=0
last_yaw=0
# 帧读取
def process(com_data):
    global rx_flag
    global save_flag
    global last_data
    global temp_mul
    global temp_angel
    global temp_high

    if com_data==0xFF and rx_flag==0:
            rx_flag=1
            #print("1") 
            return  
    if com_data==0x81 and rx_flag==1:
            rx_flag=2
            #print("2")  
            return  
    if  rx_flag==2:
        #print("process begin")
        temp_mul=com_data
        #print("temp_mul is : ",temp_mul)
        rx_flag=3
        return  
    if  rx_flag==3:
        temp_high=com_data<<8
        ##print(temp_high)
        rx_flag=4
        return  
    if  rx_flag==4:
        temp_sinangel=temp_high|com_data
        #print("temp_sinangel is ",temp_sinangel)
        temp_angel=(temp_sinangel*360)/262144
        #print("temp_angel is ",temp_angel)
        save_flag=1
        ##print(com_data)
        ##print(temp_sinangel)
        ##print("data porcess sucessfully")
        rx_flag=0
        return  temp_mul,temp_angel
    #last_data=com_data
# 数据保存   
def save(mulAngel,Angel,yaw,w,flag):
        with open('save.csv', 'a', newline='\n') as s:
            # 2. 基于文件对象构建 csv写入对象
            csv_writer = csv.writer(s)
            # 3. 构建列表头
            if flag==0:
                csv_writer.writerow(["Zone", "Zone_Angle","Angle","w"])
            # 4. 写入csv文件内容
            if flag>0:
                csv_writer.writerow([mulAngel, Angel,yaw,w])
            # 5. 关闭文件
            s.close()
            #print("写入数据成功")
def str2int(a):
    return int(a,16)

def filter(x):
     if abs(x)>1.5:
        return x
     else:
        return 0

def yaw_w_process(mulAngel,Angel,lastZone,lastAngel):
    global last_yaw
    yaw=0
    w=0
    if mulAngel==lastZone:
            if  mulAngel==0:
               yaw=Angel
            if  mulAngel==1:
               yaw=Angel+90
            if  mulAngel==2:
               yaw=Angel+180
            if  mulAngel==3:
               yaw=Angel+270
            w=filter((Angel-lastAngel)/0.001)

    if abs(mulAngel-lastZone)==1 :
            if (mulAngel-lastZone)>0:
                if lastZone==0:
                    yaw=Angel+90
                    #print("Zone is 0 :",yaw)
                if lastZone==1:
                    yaw=Angel+180
                    #print(yaw)
                    #print("Zone is 1 :",yaw)
                if lastZone==2:
                    yaw=Angel+270
            else:
                 if lastZone==3:
                    yaw=Angel+180
                 if lastZone==2:
                    yaw=Angel+90
                 if lastZone==1:
                    yaw=Angel
            w=filter((yaw-last_yaw)/0.001)
    if abs(mulAngel-lastZone)==3 :
                if mulAngel-lastZone<0:#3to0
                    yaw=Angel
                    w=filter((yaw-last_yaw+360)/0.001)
                else:#0to3
                    yaw=Angel+270
                    w=filter((yaw-last_yaw-360)/0.001)
    last_yaw=yaw
    return yaw,w
flag = 0
if __name__=='__main__':
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) <= 0:
        print("无串口设备")
    else:
        print("可用的串口设备如下：")
        for i in ports_list:
            print(i)
        ser=serial.Serial("COM3",115200)
        if ser.isOpen():
            print("端口开启成功")
            while 1:
                com_read=ser.read().hex()
                com_data=str2int(com_read)
                #print(com_read)
                #print(com_data)
                #print(com_data<<8)
                #print(type(com_read))
                #print(int(com_read,16))
                res=process(com_data)
                #print(res[0])
                if save_flag==1:
                    mulAngel[flag]=res[0]
                    #print(mulAngel[flag])
                    #print(type(mulAngel[flag]))
                    Angel[flag]=res[1]
                    dev=yaw_w_process(mulAngel[flag],Angel[flag],lastZone[flag-1],lastAngel[flag-1])
                    yaw[flag]=dev[0]
                    w[flag]=dev[1]
                    save(mulAngel[flag],Angel[flag],yaw[flag],w[flag],flag)
                    lastAngel[flag]=Angel[flag]
                    lastZone[flag]=mulAngel[flag]
                    flag=flag+1
                    save_flag=0
        else:
            print("端口开启失败")