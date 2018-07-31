#!/usr/bin/evn python
# -*- encoding:utf-8 -*-

import os
import sys
import time
import logging
import psutil

import lhb


def daemon_init(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    sys.stdin = open(stdin, 'r')
    sys.stdout = open(stdout, 'a+')
    sys.stderr = open(stderr, 'a+')
    try:
        pid = os.fork()
        if pid > 0:  # parrent
            os._exit(0)
    except OSError as e:
        sys.stderr.write("first fork failed!!" + e.strerror)
        os._exit(1)

    # 子进程， 由于父进程已经退出，所以子进程变为孤儿进程，由init收养
    # setsid使子进程成为新的会话首进程，和进程组的组长，与原来的进程组、控制终端和登录会话脱离。'''
    os.setsid()
    # 防止在类似于临时挂载的文件系统下运行，例如/mnt文件夹下，这样守护进程一旦运行，临时挂载的文件系统就无法卸载了，这里我们推荐把当前工作目录切换到根目录下'''
    os.chdir("/")
    # 设置用户创建文件的默认权限，设置的是权限“补码”，这里将文件权限掩码设为0，使得用户创建的文件具有最大的权限。否则，默认权限是从父进程继承得来的'''
    os.umask(0)

    try:
        pid = os.fork()  # 第二次进行fork,为了防止会话首进程意外获得控制终端
        if pid > 0:
            os._exit(0)  # 父进程退出
    except OSError as e:
        sys.stderr.write("second fork failed!!" + e.strerror)
        os._exit(1)

    # 孙进程
#   for i in range(3,64):  # 关闭所有可能打开的不需要的文件，UNP中这样处理，但是发现在python中实现不需要。
#       os.close(i)
    sys.stdout.write("Daemon has been created! with pid: %d\n" % os.getpid())
    # sys.stdout.flush()  # 由于这里我们使用的是标准IO，回顾APUE第五章，这里应该是行缓冲或全缓冲，因此要调用flush，从内存中刷入日志文件。

    logger = logging.getLogger(__name__)

    try:
        fs = open('/tmp/daemon_lhb.pid', 'w')
    except Exception as e:
        sys.stderr.write(e)
    else:
        fs.write('%d' % (os.getpid()))
        fs.flush()
        fs.close()

    # lhb task entry
    hDB = lhb.DB_Setup()
    lhb.LHB_Start(hDB)

    os.remove('/tmp/daemon_lhb.pid')


def main():
    # 在调用daemon_init函数前是可以使用print到标准输出的，调用之后就要用把提示信息通过stdout发送到日志系统中了
    # 调用之后，你的程序已经成为了一个守护进程，可以执行自己的程序入口了
    daemon_init('/dev/null', '/tmp/daemon.log', '/tmp/daemon.err')
    # time.sleep(10) #daemon化自己的程序之后，sleep 10秒，模拟阻塞


def daemon_start():
    print('daemon start....')
    if os.path.exists('/tmp/daemon_lhb.pid'):
        print('daemon is already running!')
        return

    daemon_init('/dev/null', '/tmp/daemon_lhb.log', '/tmp/daemon_lhb.err')


def daemon_stop():
    print('daemon stop....')

    try:
        fs = open('/tmp/daemon_lhb.pid', 'r')
    except Exception as e:
        print(
            'Daemon process may not running, please run \'daemon status\' command to check!')
        return
    else:
        pid = fs.readline()

    if pid != 0:
        try:
            pl = [proc.info for proc in psutil.process_iter(
                attrs=['pid']) if int(pid) == proc.info['pid']]
            # print pl
            if len(pl) > 0:
                os.system('kill -9 %s' % (pid))
            else:
                print(
                    'Daemon process may not running, please run \'daemon status\' command to check!')
                return
        except Exception as e:
            print(e)
        else:
            fs.close()
            os.remove('/tmp/daemon_lhb.pid')
            print('Daemon process is stopped!')


def daemon_status():
    print('daemon status:')
    try:
        fs = open('/tmp/daemon_lhb.pid', 'r')
    except Exception as e:
        print('Daemon process may not running!')
        return
    else:
        pid = int(fs.readline())
        #print('daemon process pid is %d'%(pid))

    if pid != 0:
        pl = [proc.info for proc in psutil.process_iter(
            attrs=['pid']) if int(pid) == proc.info['pid']]
        # print pl
        if len(pl) > 0:
            print('Daemon process is running with pid %d' % (pid))
        else:
            print('Daemon process is not running( not found process with pid %d)'%(pid))
    else:
        print('Daemon process is not running!')


if __name__ == '__main__':
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    # logging configuration
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fHandle = logging.FileHandler('./daemon_lhb.log', 'a', encoding='utf-8')
    fHandle.setFormatter(fmt)
    logger.addHandler(fHandle)

    #pl = [proc.info for proc in psutil.process_iter(attrs=['pid', 'name']) if 'python' in proc.info['name']]

    # fs = open('daemon.pid', 'w')
    # fs.write('26787')
    # fs.flush()
    # fs.close()

    # print(sys.argv)
    if len(sys.argv) == 1:
        daemon_start()
    elif len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon_start()
        elif 'stop' == sys.argv[1]:
            daemon_stop()
        elif 'restart' == sys.argv[1]:
            daemon_stop()
            daemon_start()
        elif 'status' == sys.argv[1]:
            daemon_status()
        else:
            print("command line not recognized!")
    else:
        print("command line not recognized!")
