import tkinter as tk
import time
from tkinter import messagebox as msg
m = 1
# S盒
s = [[9, 4, 10, 11],
     [13, 1, 8, 5],
     [6, 2, 0, 3],
     [12, 14, 15, 7]]
# 逆s盒
nis = [[10, 5, 9, 11],
       [1, 7, 8, 15],
       [6, 0, 2, 3],
       [12, 4, 13, 14]]
# 替换表
Replace = [[0, 0, 0, 0], [0, 0, 0, 1],
           [0, 0, 1, 0], [0, 0, 1, 1],
           [0, 1, 0, 0], [0, 1, 0, 1],
           [0, 1, 1, 0], [0, 1, 1, 1],
           [1, 0, 0, 0], [1, 0, 0, 1],
           [1, 0, 1, 0], [1, 0, 1, 1],
           [1, 1, 0, 0], [1, 1, 0, 1],
           [1, 1, 1, 0], [1, 1, 1, 1]]

# 轮常数
rcon1 = [1, 0, 0, 0, 0, 0, 0, 0]
rcon2 = [0, 0, 1, 1, 0, 0, 0, 0]


# 十进制转二进制(默认8位)
def tenTotwo(number, bit=8):
    # 定义栈
    s = []
    binstring = ''
    while number > 0:
        # 余数进栈
        rem = number % 2
        s.append(rem)
        number = number // 2
    while len(s) > 0:
        # 元素全部出栈即为所求二进制数
        binstring = binstring + str(s.pop())
    while len(binstring) < bit:
        binstring = '0' + binstring
    return binstring


def XR_8(a, b):
    # a、b 分别是两个长度为 8 的数组，返回一个长度也为 8 的数组
    t = [0] * 8  # 结果数组
    for i in range(8):
        t[i] = a[i] ^ b[i]
    return t


# 字节替换
def SubBytes(temp):
    # temp 是一个长度为8的数组，进行S盒替换
    # 先计算出需要进行S盒替换的四位二进制数
    t1 = 2 * temp[0] + temp[1]
    t2 = 2 * temp[2] + temp[3]
    t3 = 2 * temp[4] + temp[5]
    t4 = 2 * temp[6] + temp[7]
    # 进行 S 盒替换
    num1 = s[t1][t2]
    num2 = s[t3][t4]
    # 将替换后的结果按四位四位赋值给temp
    for i in range(4):
        temp[i] = Replace[num1][i]
    for i in range(4):
        temp[i + 4] = Replace[num2][i]


def niSubBytes(temp):
    # temp 是一个长度为8的数组，进行S盒替换
    # 先计算出需要进行S盒替换的四位二进制数
    t1 = 2 * temp[0] + temp[1]
    t2 = 2 * temp[2] + temp[3]
    t3 = 2 * temp[4] + temp[5]
    t4 = 2 * temp[6] + temp[7]
    # 进行 S 盒替换
    num1 = nis[t1][t2]
    num2 = nis[t3][t4]
    # 将替换后的结果按四位四位赋值给temp
    for i in range(4):
        temp[i] = Replace[num1][i]
    for i in range(4):
        temp[i + 4] = Replace[num2][i]


# g函数
def g(temp, rcon):
    # temp 是一个长度为8的数组，rcon是轮常数
    t = temp.copy()  # temp是密钥，不能改动，复制一个新的
    # 进行循环左移
    for i in range(4):
        tt = t[i + 4]
        t[i + 4] = t[i]
        t[i] = tt
    # 进行 S 盒替换
    SubBytes(t)
    # 进行轮常数异或
    return XR_8(t, rcon)


def nig(temp, rcon):
    # temp 是一个长度为8的数组，rcon是轮常数
    t = temp.copy()  # temp是密钥，不能改动，复制一个新的
    # 进行循环左移
    for i in range(4):
        tt = t[i + 4]
        t[i + 4] = t[i]
        t[i] = tt
    # 进行 S 盒替换
    niSubBytes(t)
    # 进行轮常数异或
    return XR_8(t, rcon)


# 轮密钥加
def AddRoundKey(plaintext, key):
    for i in range(2):
        for j in range(8):
            plaintext[i][j] ^= key[i][j]


# 行变换
def ShiftRows(temp):
    # 第一字节的右半部分和第二字节的右半部分进行替换
    for i in range(4, 8):
        t = temp[0][i]
        temp[0][i] = temp[1][i]
        temp[1][i] = t


# 4位的异或
def OR_4(a, b):
    # a、b 分别是两个长度为 4 的数组，返回一个长度也为 4 的数组
    t = [0] * 4  # 结果数组
    for i in range(4):
        t[i] = a[i] ^ b[i]
    return t


def x_fx(f, a):
    # 进行有限域上的多项式除法运算，用于求解一个元素的逆元
    if a[0] == 0:
        for i in range(3):  # 定义一个长度为4的数组f表示一个3次多项式
            f[i] = a[i + 1]
    else:
        f[1] = a[2]
        f[2] = 0 if a[3] == 1 else 1
        f[3] = 1


def multiply(a, b):
    # 在有限域 GF(2^4) 上的多项式乘法运算
    # 记录下f^n
    f = [0] * 4
    x_fx(f, a)
    f2 = [0] * 4
    x_fx(f2, f)
    f3 = [0] * 4
    x_fx(f3, f2)
    # 现在需要根据多项式a和b开始异或
    result = [0] * 4  # 储存结果的系数
    if b[0] == 1:
        for i in range(4):
            result[i] ^= f3[i]
    if b[1] == 1:
        for i in range(4):
            result[i] ^= f2[i]
    if b[2] == 1:
        for i in range(4):
            result[i] ^= f[i]
    if b[3] == 1:
        for i in range(4):
            result[i] ^= a[i]
    return result


# 列混淆
def MixColumns(plaintext):
    rule = [0, 1, 0, 0]
    m00 = plaintext[0][:4]
    m10 = plaintext[0][4:]
    m01 = plaintext[1][:4]
    m11 = plaintext[1][4:]

    n00 = OR_4(m00, multiply(rule, m10))  # 乘法结果是1011
    n10 = OR_4(multiply(rule, m00), m10)  # 0101
    n01 = OR_4(m01, multiply(rule, m11))  # 0100
    n11 = OR_4(multiply(rule, m01), m11)  # 0010

    plaintext[0][:4] = n00
    plaintext[0][4:] = n10
    plaintext[1][:4] = n01
    plaintext[1][4:] = n11


# 逆列混淆
def niMixColumns(plaintext):
    rule = [1, 0, 0, 1]
    rule2 = [0, 0, 1, 0]
    m00 = plaintext[0][:4]
    m10 = plaintext[0][4:]
    m01 = plaintext[1][:4]
    m11 = plaintext[1][4:]

    n00 = OR_4(multiply(rule, m00), multiply(rule2, m10))  # 乘法结果是1011
    n10 = OR_4(multiply(rule2, m00), multiply(rule, m10))  # 0101
    n01 = OR_4(multiply(rule, m01), multiply(rule2, m11))  # 0100
    n11 = OR_4(multiply(rule2, m01), multiply(rule, m11))  # 0010

    plaintext[0][:4] = n00
    plaintext[0][4:] = n10
    plaintext[1][:4] = n01
    plaintext[1][4:] = n11


def S_AES_EncryByte(mingwen_str, key_str):
    plaintext = [[int(mingwen_str[i * 8 + j]) for j in range(8)] for i in range(2)]
    key = [[int(key_str[i * 8 + j]) for j in range(8)] for i in range(2)]
    # print('明文', plaintext)
    # print('key', key)

    # 密钥扩展算法，由于只有三轮加密，第一轮只使用了原始key
    key1 = [[0] * 8 for _ in range(2)]
    key2 = [[0] * 8 for _ in range(2)]
    key1[0] = XR_8(key[0], g(key[1], rcon1))
    key1[1] = XR_8(key1[0], key[1])
    key2[0] = XR_8(key1[0], g(key1[1], rcon2))
    key2[1] = XR_8(key2[0], key1[1])

    # 第零轮
    # 轮密钥加
    AddRoundKey(plaintext, key)

    # 第一轮
    # 明文半字节代替
    SubBytes(plaintext[0])
    SubBytes(plaintext[1])
    # 明文的行移位
    ShiftRows(plaintext)
    # 明文的列混淆
    MixColumns(plaintext)
    # 明文的轮密钥加
    AddRoundKey(plaintext, key1)

    # 第二轮
    # 明文半字节代替
    SubBytes(plaintext[0])
    SubBytes(plaintext[1])
    # 明文的行移位
    ShiftRows(plaintext)
    # 明文的轮密钥加
    AddRoundKey(plaintext, key2)

    output = ''
    # 输出结果
    # print("密文为：")
    for i in range(2):
        for j in range(8):
            # print(plaintext[i][j], end=' ')
            output += str(plaintext[i][j])
    return output


def S_AES_DecryByte(miwen_str, key_str):
    ciphertext = [[int(miwen_str[i * 8 + j]) for j in range(8)] for i in range(2)]
    key = [[int(key_str[i * 8 + j]) for j in range(8)] for i in range(2)]
    # print('密文', ciphertext)
    # print('key', key)

    # 密钥扩展算法，由于只有三轮加密，第一轮只使用了原始key
    key1 = [[0] * 8 for _ in range(2)]
    key2 = [[0] * 8 for _ in range(2)]
    key1[0] = XR_8(key[0], g(key[1], rcon1))
    key1[1] = XR_8(key1[0], key[1])
    key2[0] = XR_8(key1[0], g(key1[1], rcon2))
    key2[1] = XR_8(key2[0], key1[1])

    # 第零轮
    # 轮密钥加
    AddRoundKey(ciphertext, key2)
    ShiftRows(ciphertext)
    niSubBytes(ciphertext[1])
    niSubBytes(ciphertext[0])
    AddRoundKey(ciphertext, key1)
    niMixColumns(ciphertext)
    ShiftRows(ciphertext)
    niSubBytes(ciphertext[1])
    niSubBytes(ciphertext[0])
    AddRoundKey(ciphertext, key)
    # 输出结果
    output = ''
    # print("明文为：")
    for i in range(2):
        for j in range(8):
            # print(ciphertext[i][j], end=' ')
            output += str(ciphertext[i][j])
    return output


def crashtext(plaintext, ciphertexts):
    output = ''
    key = 0
    for i in range(65536):
        key1 = tenTotwo(key, bit=16)
        ciphertext = S_AES_EncryByte(plaintext, key1)
        if ciphertext == ciphertexts:
            output += key1 + ' '
            key = key + 1
        else:
            key = key + 1
    print('密钥有', output)
    return output


root = tk.Tk()
root.title("计算界面")
root.geometry("380x200")
root.configure(bg="#F9F9F9")
# 创建标签和输入框
label1 = tk.Label(root, text="输入明文:", font=("微软雅黑", 12), bg="#F9F9F9")
entry1 = tk.Entry(root,  font=("微软雅黑", 12), width=20, bd=2)
label2 = tk.Label(root, text="输入密钥:", font=("微软雅黑", 12), bg="#F9F9F9")
entry2 = tk.Entry(root, font=("微软雅黑", 12), width=20, bd=2)
label3 = tk.Label(root, text="输入密文:", font=("微软雅黑", 12), bg="#F9F9F9")
entry3 = tk.Entry(root,  font=("微软雅黑", 12), width=20, bd=2)
label4 = tk.Label(root, text="输入密钥:", font=("微软雅黑", 12), bg="#F9F9F9")
entry4 = tk.Entry(root, font=("微软雅黑", 12), width=20, bd=2)
label5 = tk.Label(root, text="输入明文:", font=("微软雅黑", 12), bg="#F9F9F9")
entry5 = tk.Entry(root,  font=("微软雅黑", 12), width=20, bd=2)
label6 = tk.Label(root, text="输入密文:", font=("微软雅黑", 12), bg="#F9F9F9")
entry6 = tk.Entry(root, font=("微软雅黑", 12), width=20, bd=2)


def changeturn():
    global m
    if m == 0:
        m = 1
    else:
        m = 0


def encry_result():
    # 获取输入的参数值
    param1 = entry1.get()
    param2 = entry2.get()
    if m == 0:
        result = S_AES_EncryByte(param1, param2)
        encry_label.config(text=f"结果: {result}")
    else:
        # 初始化一个空的列表来存储二进制位
        param1_list = []

        # 处理字符串中的每个字符
        for char in param1:
            if char.isalpha():  # 如果字符是字母
                # 将字符转换为二进制
                param1_list.extend([int(bit) for bit in format(ord(char), '08b')])
            elif char.isdigit():  # 如果字符是数字
                # 将数字字符转换为整数，然后转换为二进制
                param1_list.extend([int(bit) for bit in format(int(char), '08b')])

        result0 = []
        for i in range(0, len(param1_list), 16):
            # 取出16位作为参数调用函数
            eight_bits = param1_list[i:i + 16]
            wm1 = "".join(eight_bits)
            result0.append(S_AES_EncryByte(wm1, param2))
        # 遍历每个子列表，将二进制数字转换为整数，并将整数解释为ASCII字符

        # ascii_characters = [chr(int("".join(map(str, sublist), 2)) for sublist in result0)]

        # 将ASCII字符连接成一个字符串0
        result = ''.join([chr(int(''.join(map(str, sublist)), 2)) for sublist in result0])

        # 显示结果
        encry_label.config(text=f"结果: {result}")


def decry_result():
    # 获取输入的参数值
    param1 = entry3.get()
    param2 = entry4.get()
    if m == 0:
        result = S_AES_DecryByte(param1, param2)
        encry_label.config(text=f"结果: {result}")
    else:
        # 初始化一个空的列表来存储二进制位
        param1_list = []

        # 处理字符串中的每个字符
        for char in param1:
            if char.isalpha():  # 如果字符是字母
                # 将字符转换为二进制
                param1_list.extend([int(bit) for bit in format(ord(char), '08b')])
            elif char.isdigit():  # 如果字符是数字
                # 将数字字符转换为整数，然后转换为二进制
                param1_list.extend([int(bit) for bit in format(int(char), '08b')])

        result0 = []
        for i in range(0, len(param1_list), 16):
            # 取出16位作为参数调用函数
            eight_bits = param1_list[i:i + 16]
            wm1 = "".join(eight_bits)
            result0.append(S_AES_DecryByte(wm1, param2))
        # 遍历每个子列表，将二进制数字转换为整数，并将整数解释为ASCII字符

        # ascii_characters = [chr(int("".join(map(str, sublist), 2)) for sublist in result0)]

        # 将ASCII字符连接成一个字符串0
        result = ''.join([chr(int(''.join(map(str, sublist)), 2)) for sublist in result0])

        # 显示结果
        decry_label.config(text=f"结果: {result}")


def vio_result():
    # 获取输入的参数值
    param5 = entry5.get()
    param6 = entry6.get()
    result = crashtext(param5, param6)
    break_label.config(text=f"结果: {result}")


encry_button = tk.Button(root, text="加密", font=(
    "微软雅黑", 12), bg="#000080", fg="#FFFFFF", command=encry_result)
encry_label = tk.Label(root, text="结果: ", font=("微软雅黑", 12), bg="#F9F9F9")
# 布局管理
label1.grid(row=0, column=0, padx=20, pady=10)
entry1.grid(row=0, column=1, padx=20, pady=10)
label2.grid(row=1, column=0, padx=20, pady=10)
entry2.grid(row=1, column=1, padx=20, pady=10)
encry_button.grid(row=2, column=0, padx=20, pady=10)
encry_label.grid(row=2, column=1, padx=20, pady=10)

# 解密
decry_button = tk.Button(root, text="解密", font=(
    "微软雅黑", 12), bg="#000080", fg="#FFFFFF", command=decry_result)
decry_label = tk.Label(root, text="结果: ", font=("微软雅黑", 12), bg="#F9F9F9")
# 布局管理
label3.grid(row=3, column=0, padx=20, pady=10)
entry3.grid(row=3, column=1, padx=20, pady=10)
label4.grid(row=4, column=0, padx=20, pady=10)
entry4.grid(row=4, column=1, padx=20, pady=10)
decry_button.grid(row=5, column=0, padx=20, pady=10)
decry_label.grid(row=5, column=1, padx=20, pady=10)


# 破解
break_button = tk.Button(root, text="破解", font=(
    "微软雅黑", 12), bg="#000080", fg="#FFFFFF", command=vio_result)
break_label = tk.Label(root, text="结果: ", font=("微软雅黑", 12), bg="#F9F9F9")

# 布局管理
label5.grid(row=6, column=0, padx=20, pady=10)
entry5.grid(row=6, column=1, padx=20, pady=10)
label6.grid(row=7, column=0, padx=20, pady=10)
entry6.grid(row=7, column=1, padx=20, pady=10)
break_button.grid(row=8, column=0, padx=20, pady=10)
# break_label.grid(row=8, column=1, padx=20, pady=10)

# 切换二进制输入和字符串输入
change_button = tk.Button(root, text="切换（二进制/字符串）", font=(
    "微软雅黑", 12), bg="#000080", fg="#FFFFFF", command=changeturn)
change_button.grid(row=9, column=0, padx=20, pady=10)

# 设置窗口大小和位置
window_width = 500
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# 启动主循环
root.mainloop()
