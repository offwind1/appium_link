#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:yjq
"""计算器"""

import re

def update_formula(calc_list,calc_operator_list):
    """通过拆分后的表达式列表与符号列表重新组合"""
    for index,item in enumerate(calc_list):
        if index == 0:
            formula = item
        elif index != 0:
            formula += calc_operator_list[index-1] + item
    return formula

def negative_start_issue(formula):
    """处理负数在括号内表达式开头的情形"""

    calc_list = re.split("[+-]",formula)    #通过+-符号将各个乘除运算分隔出来
    calc_operator_list = re.findall("[+-]",formula)

    for index,item in enumerate(calc_list):
        if index == 0 and item == '':    # 处理负号在开头的问题
            calc_list[index] = '0'
        else:
            calc_list[index] = item.strip()

    formula = update_formula(calc_list,calc_operator_list)
    return formula

def deal_unusual_issue(formula):
    """双加减符号处理"""
    formula = formula.replace(" ","") #去掉空格
    formula = formula.replace("++","+")
    formula = formula.replace("+-", "-")
    formula = formula.replace("-+", "-")
    formula = formula.replace("--", "+")
    return formula

def deal_negative_issue(formula):
    """处理乘除运算中负数的计算问题（分前后位置两种情况）"""

    # 1.负数在后
    m = re.search("[0-9]+[.]*[0-9]*[*|/][-][0-9]+[.]*[0-9]*",formula)
 #  minus_pre = re.search("[0-9]+[.]*[0-9]*[*|/][-][0-9]+[.]*[0-9]*",formula).group()
    # 注意匹配的必要项与非必要项，如："[0-9]+[.][0-9]+[*|/][-][0-9]+[.][0-9]+"误把非必要项当做必要项。
    if m:
        minus_pre = m.group()
        minus_pro = "-"+minus_pre.replace("-","")
        formula = formula.replace(minus_pre,minus_pro)
    if "*-" in formula or "/-" in formula:
        return deal_negative_issue(formula)

    # 2.负数在前
    formula = deal_unusual_issue(formula)

    return formula


def multiply_divide(formula):
    """乘除计算"""
    calc_list = re.split("[*/]", formula)
    operator_list = re.findall("[*/]", formula)  # 将乘号除号通过列表方式分隔出来

    res = 0
    for index2, i in enumerate(calc_list):
        # i = getRealVlue(item)

        if func(i) and func(res):
            """是变量是自然数"""
            if index2 == 0:
                res = int(i)
            else:
                if operator_list[index2 - 1] == '*':  # 通过sub_operator_list中的index判断到底是加法还是减法，
                    res *= int(i)
                elif operator_list[index2 - 1] == '/':
                    res /= int(i)
        else:
            """变量是字符串"""
            if index2 == 0:
                res = str(i)
            else:
                if operator_list[index2 - 1] == '*':  # 通过sub_operator_list中的index判断到底是加法还是减法，
                    res = str(res)+"*"+str(i) 
                elif operator_list[index2 - 1] == '/':
                    res = str(res)+"/"+str(i) 

    return res

def add_abstract(formula):
    """加减计算"""

    # 1.开头位置负数处理
    formula = negative_start_issue(formula)

    # 2.双加减符号处理
    formula = deal_unusual_issue(formula)

    # 3.加减逻辑运算
    calc_list = re.split("[+-]", formula)
    operator_list = re.findall("[+-]", formula)

    res = 0
    for index, i in enumerate(calc_list):
        if index == 0:
                res = i
        else:
            if func(i) and func(res):
                if operator_list[index-1] == '+':
                    res =int(res) + int(i)
                elif operator_list[index-1] == '-':
                    res = int(res) - int(i)
            else:
                if operator_list[index-1] == '+':
                    res += str(i)
                elif operator_list[index-1] == '-':
                    str(res).strip(str(i))
    return res


def elementary_arithmetic(formula):
    """
    四则混合运算主函数
    """
    # 负数处理
    formula = negative_start_issue(formula)
    formula = deal_negative_issue(formula)

    # 乘除运算
    calc_list = re.split("[+-]",formula)    # 通过+-符号将各个乘除运算分隔出来
    calc_operator_list = re.findall("[+-]",formula)

    for index1, item in enumerate(calc_list):
        calc_list[index1] = str(multiply_divide(item))  #数据类型的强制转换！！！
    formula = update_formula(calc_list,calc_operator_list)

    # 加减运算
    formula = add_abstract(formula)

    return formula


def calculator(formula):
    """
    括号运算
    """

    """数据预处理,将表达式内的空格全部取出"""
    formula = formula.replace(" ","")

    m = re.search("\([^()]*\)",formula)

    # 判断是否需要进行括号运算
    if m:
        # 括号运算
        # 提取最小括号运算式，计算结果，并返回。
        subformula = m.group().strip("()")  # 把找出来的括号剥离
        subres = elementary_arithmetic(subformula)  # 调用四则混合运算主函数
        formula = formula.replace(m.group(), str(subres))
        if "(" in formula:
            return calculator(formula)

        # 除去所有括号后可能出现：1-2*-312.8
        formula = elementary_arithmetic(formula)

        return formula
    else:
        return elementary_arithmetic(formula)



def calJudge(formula):
    """
    判断运算
    """

    """数据预处理,将表达式内的空格全部取出"""
    formula = formula.replace(" ","")

    m = re.search("\([^()]*\)",formula)

    if m:
        subformula = m.group().strip("()")  # 把找出来的括号剥离
        subres = logical_operation(subformula)
        formula = formula.replace(m.group(), str(subres))
        if "(" in formula:
            return calJudge(formula)
            
        formula = logical_operation(formula)

        return formula
    else:
        return logical_operation(formula)



def logical_operation(formula):
    """
        and or
    """

    # and or
    calc_list = re.split("and|or",formula)    # 通过+-符号将各个乘除运算分隔出来
    calc_operator_list = re.findall("and|or",formula)

    for index1, item in enumerate(calc_list):
        if "not" in item:
            spl_not = re.split("not", item)
            for spl in spl_not:
                if not spl=="":
                    s = comparison_operation(spl)
                    if str(s).lower() == 'ture':
                        s = True
                    elif str(s).lower() == 'false':
                        s = False
                    elif str(s).lower() == '0':
                        s = False
                    else:
                        s = True
                    calc_list[index1] = not s
        else:
            calc_list[index1] = str(comparison_operation(item))  #数据类型的强制转换！！！

    for index2, i in enumerate(calc_list):
        if str(i).lower() == 'ture':
            i = True
        elif str(i).lower() == 'false':
            i = False

        if index2 == 0:
            res = i
        else:
            if isinstance(res,bool) and isinstance(i,bool):
                if calc_operator_list[index2 - 1] == 'and':
                    res = bool(res) and bool(i)
                elif calc_operator_list[index2 - 1] == 'or':
                    res = bool(res) or bool(i)
            elif str(i).isdigit() and str(res).isdigit():
                    if calc_operator_list[index2 - 1] == 'and':  # 通过sub_operator_list中的index判断到底是加法还是减法，
                        res = int(res) and int(i)
                    elif calc_operator_list[index2 - 1] == 'or':
                        res = int(res) or int(i)
            else:
                if calc_operator_list[index2 - 1] == 'and':  # 通过sub_operator_list中的index判断到底是加法还是减法，
                    res = str(res) and str(i)
                elif calc_operator_list[index2 - 1] == 'or':
                    res = str(res) or str(i)

    # formula = update_formula(calc_list,calc_operator_list)

    # # 加减运算
    # formula = add_abstract(formula)

    return res

def comparison_operation(formula):
    """关系运算><=="""
    calc_list = re.split("<|>|==", formula)
    operator_list = re.findall("<|>|==", formula)  # 将乘号除号通过列表方式分隔出来

    for index1, item in enumerate(calc_list):
        calc_list[index1] = str(elementary_arithmetic(item))  #数据类型的强制转换！！！


    res = 0
    for index2, i in enumerate(calc_list):
        if str(i).lower() == 'ture':
            i = True
        elif str(i).lower() == 'false':
            i = False

        if index2 == 0:
            res = i
        else:
            if isinstance(res,bool) and isinstance(i,bool):
                if operator_list[index2 - 1] == '<':
                    res = bool(res) < bool(i)
                elif operator_list[index2 - 1] == '>':
                    res = bool(res) > bool(i)
                elif operator_list[index2 - 1] == '==':
                    res = bool(res) == bool(i)
            elif str(i).isdigit() and str(res).isdigit():
                    if operator_list[index2 - 1] == '<':  # 通过sub_operator_list中的index判断到底是加法还是减法，
                        res = int(res) < int(i)
                    elif operator_list[index2 - 1] == '>':
                        res = int(res) > int(i)
                    elif operator_list[index2 - 1] == '==':
                        res = int(res) == int(i)
            else:
                if operator_list[index2 - 1] == '<':  # 通过sub_operator_list中的index判断到底是加法还是减法，
                    res = str(res) < str(i)
                elif operator_list[index2 - 1] == '>':
                    res = str(res) > str(i)
                elif operator_list[index2 - 1] == '==':
                    res = str(res) == str(i)
    return res


def func(z):
     try:
         z=int(z)
         return isinstance(z,int)
     except ValueError:
         return False
