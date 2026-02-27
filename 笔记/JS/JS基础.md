🖊 慢慢来，一步一步来。

# 1.JS 基础 认识数据

## 1.1 认识变量

### 重点 1：文档输出内容

```javascript
document.write("Hello World!")

document.write('<h1>你好，世界！</h1>') 
```



### 重点 2：控制台打印输出 给 程序员

```javascript
console.log('zaoshanghao')

console.log('rizhi') 
```



### 重点 3：输入语句

```javascript
prompt('请输入你的名字：')
```



### 重点 4：变量声明

```javascript
let age = 25  // 同时声明和赋值
```



### 变量声明练习

// 1.声明一个变量，用于存放用户购买的商品 数量(num)为 20 件

// 2.声明一个变量，用于存放用户的 姓名(uname)为'张三

// 3.依次控制台打印输出两个变量

#### 练习答案

```javascript
- let num = 20

- let uname = '张三'

- console.log(num)

- console.log(uname)
```

![image-20250913170131364](D:\Typora笔记\JS的笔记\img\image-20250913170131364.png)



## 1.2 JS 基础 变量

### 重点 1：用户输入

```javascript
prompt('请输入你的名字：')
```



### 重点 2：内部处理保存数据

```javascript
let uname = prompt('请输入你的姓名：')
```



### 重点 3：打印输出

```javascript
- let A = 10

- document.write(A)
```



### 练习 1：变量练习-弹出姓名

// 1.浏览器中弹出对话框: 请输入姓名

// 2.页面中输出: 刚才输入的姓名



#### 练习答案

```javascript
- let uname = prompt('请输入你的姓名：')

- document.write(uname)
```



### 练习 2：变量案例-交换变量的值

- ##### 需求:

- 有 2 个变量: num1 里面放的是 10，num2 里面放的是 20

- 最后变为 num1 里面放的是 20，num2 里面放的是 10

- ##### 目的:

- //1.练习变量的使用

- //2.为了后面冒泡排序做准备

  


#### 练习答案

- ```javascript
  - let num1 = 10
  
  - let num2 = 20
  
  - let temp
  
  - temp = num1
  
  - num1 = num2
  
  - num2 = temp
  
  - console.log(num1,num2)
  ```

  

## 1.3 JS 基础 变量命名的规则与规范

### 重点：变量命名的规则与规范

- ### 1.规则

  - ##### 关键字: 有特殊含义的字符，JavaScript 内置的一些英语词汇。例如: let、var、if、for 等

  - ##### 只能用下划线、字母、数字、$组成，且数字不能开头

  - ##### 字母严格区分大小写，如 Age 和 age 是不同的变量

- ### 2.规范

  - ##### 起名要有意义

  - ##### 小驼峰命名法
    
    - ##### 第一个单词首字母小写，后面每个单词首字母大写。例: userName

### 练习：变量练习-输出用户信息

- ##### javascript 需求: 让用户输入自己的名字、年龄、性别，再输出到网页

  

#### 练习答案

- ```javascript
  - let uname = prompt("请输入你的姓名：")
  
  - let age = prompt("请输入你的年龄：")
  
  - let gender = prompt("请输入你的性别：")
  
  - document.write(uname,age,gender)
  ```






## 1.4 JS 基础 var 和 let 的区别？

### var 声明:

- ##### 可以先使用 在声明(不合理)

- ##### var 声明过的变量可以重复声明(不合理)

- ##### 比如变量提升、全局变量、没有块级作用域等等

- ### 例如：

- ```javascript
  - var num = 10
  
  - var num = 20
  
  - console.log(num)
  
  //结果打印出来为20 
  ```

  

## 1.5 JS 基础 数组的基本使用

### 重点 1：声明数组

- ```javascript
  let arr = ["白子","星野","野宫"]
  ```

  


### 重点 2：使用数组  数组名 [索引号] 从 0 开始 以此类推

- ```javascript
  - console.log(arr)
  
  - console.log(arr[1])
  ```

  ![](D:\Typora笔记\JS的笔记\img\2.png)



### 练习：数组取值案例

- ##### 需求: 定义一个数组，里面存放星期一、星期二… 直到星期日(共 7 天)，在控制台输出: 星期日

#### 练习答案

- ```javascript
  - let arr = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
  
  - console.log(arr[6]) 
  ```

  

### 重点 3：数组的一些术语

- ##### 元素: 数组中保存的每个数据都叫数组元素

- ##### 下标: 数组中数据的编号

- ##### 长度: 数组中数据的个数，通过数组的 length 属性获得

- ###### 例如：

- ```javascript
  - let arr = ["白子","星野","野宫"]
  
  - console.log(arr.length)  // 打印台显示结果为3
  ```

  



## 1.6 JS 基础 认识常数

### 重点 1：常量 不允许更改值

- ```javascript
  - const PI = 3.14
  
  - console.log(PI)
  
  - PI = 3.15
  
  - console.log(PI)
  ```

  

- ![](D:\Typora笔记\JS的笔记\img\1.6.png)

### 重点 2：常量声明必须赋值

- ```javascript
  - const A = 9.9
  
  - 不可以写成const A
  ```

  


## 1.7 JS 基础 数据类型

### 重点 1：数字类型（Number）

- 可以是整数，小数，正数，负数

- 算术运算符 + - * / %


### 练习：计算圆的面积

- 需求: 对话框中输入圆的半径，算出圆的面积并显示到页面


#### 练习答案

- ```javascript
  - let r = prompt("请输入圆的半径：")
  
  - let re = 3.14*r*r
  
  - document.write(re)
  ```

  

### 重点 2：NaN 

- NaN 代表一个计算错误。

- 它是一个不正确的或者一个未定义的数学操作所得到的结果

- NaN 是粘性的。任何对 NaN 的操作都会返回 NaN

- ##### 甚至 NaN 不等于自己 打印结果会是 false
  
  // 逆天 NaN

### 重点 3：字符串类型

- ##### 知识 1.通过单引号(")、双引号(" ")或反引号(`)包裹的数据都叫字符串、单双引号没本质上的区别

- ##### 知识 2.单引号/双引号可以互相嵌套，但是不以自已嵌套自己(口诀: 外双内单，或者外单内双)

- ##### 知识 3.必要时可以使用转义符\，输出单引号或双引号

- ```javascript
  - let str = "白子"
  
  - let str1 = '黑子'
  
  - let str2 = '123'
    // 用引号包裹了就是字符串了
  ```

  

- ```javascript
  - let str3 = ""
   // 这种叫空字符串
  
  - console.log(str)
  
  - console.log(str1)
  
  - console.log(str2)
  
  - console.log('123')
  
  - console.log(str3)
  ```

  

- ![](D:\Typora笔记\JS的笔记\img\17.1.png)

- ### 知识 4.字符串拼接

  - 用法："字符串 1"+"字符串 2"

  - 例如：

    - ```javascript
      - document.write("你好"+"世界")
      
      - let uname = "碧蓝"
      
      - let uuname = "档案"
      
      - document.write(uname + uuname)
      ```

      

- ### 知识 5.模板字符串

  - 拼接字符串和变量

  - ```javascript
    document.write(`大家好，我叫`+ name +`,今年`+ age + `岁`)
    ```

    

  - 语法：

    - 内容拼接变量时，用 ${}包住变量

    - 例如：
      - ```javascript
        document.write("大家好，我叫${name},今年${age}岁")
        ```
      
        

  - // 相比于第一种字符串的拼接要方便很多 o.O

  -  


### 练习：页面输出用户信息

- 需求: 页面弹出对话框，输入名字和年龄，页面显示: 大家好，我叫 xxx，今年 xx 岁了


#### 练习答案：

- ```javascript
  - let uname = prompt("请输入你的姓名：")
  
  - let age = prompt("请输入你的年龄：")
  
  - document.write(`大家好，我叫${uname},今年${age}了`)
  ```

  

### 重点 4：布尔类型 

- 表示肯定或否定时在计算机中对应的是布尔类型数据

- 它有两个固定的值 true 和 false

- 表示肯定的数据用 true(真)，表示否定的数据用 false(假）

### 重点 5：未定义类型 undefined

- ##### 只声明变量，不赋值的情况下，变量的默认值为 undefined

- ```javascript
  - let num
  
  - console.log  // 打印结果为undefined
  ```

  

### 重点 6：空类型 null

- null 仅仅是一个代表“无”、“空”或“值未知”的特殊值

- #####  null 和 undefined 区别:

  - ##### undefined 表示没有赋值

  - ##### null 表示赋值了，但是内容为空

- ![img](D:\Typora笔记\JS的笔记\img\1.7.png)





## 1.8 JS 基础 数据类型检测

### 重点 1：通过 typeof 关键字检测数据类型

- typeof 运算符可以返回被检测的数据类型，它支持两种语法形式

  - 1.作为运算符： typeof x

  - 2.typeof(x)

- 例如：

- ```javascript
  - let num = 10 
  
  - console.log (typeof num) 打印结果为 number （数字型）
  
  - let str = "你好" 
  
  - console.log (typeof str) 打印结果为 string （字符型）
  ```

  


### 重点 2：通过 prompt()取过来的值默认是字符串类型

- ```javascript
  - let num1 = prompt("请输入一个数")
  
  - console.log(num1) // 打印结果是字符串类型
  ```

  

### 重点 3：隐式转换

- ##### 某些运算符被执行时，系统内部自动将数据类型进行转换，这种转换称为隐式转换

- 加号还可以让字符串转换成数字型 别的符号不行

- ```javascript
  - console.log("你好"+1)   ==》你好1
  
  - console.log("1"+1)  ==》11
  
  - console.log(2 - "2")  ==》0
  
  - console.log(+"123")  ==》转化成为数字型的123
  ```

  

### 重点 4：显示转换

- 自己写代码告诉系统该转成什么类型

- ##### 数字型：Number

  - ```javascript
    - let str = "123"
    
    - console.log(Number(str))
    
    - let num = +prompt("输入年薪")
    
    - console.log(num)f
    ```

    

- ##### 只保留整数：parseInt

  - ```javascript
    - console.log(parseInt("12px"))
    
    - console.log(parseInt("12.33px"))
    ```

    

- ##### 可以保留小数：parseFloat

- ```javascript
  - console.log(parseFloat("12px"))
  
  - console.log(parseFloat("12.33px"))
  ```

  

- 

### 练习：

- 输入 2 个数，计算两者的和，打印到页面中


#### 练习答案：

- ```javascript
  - let num1 = +prompt("第一个数：")
  
  - let num2 = +prompt("第二个数：")
  
  - let arr = num1 + num2 
  
  - alert(`答案结果为：${arr}`)
  ```

  



# 1 实战案例

### 案例 1：用户订单信息案例

- ##### 需求:

- 用户输入商品价格和商品数量，以及收货地址，可以自动打印订单信息

- ##### 分析:

- 需要输入 3 个数据，所以需要 3 个变量来存储 price num address

- 需要计算总的价格 total

- 页面打印生成表格，里面填充数据即可

- 记得最好使用模板字符串

- 

#### 练习答案：

```javascript
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  h2{
    text-align: center;
    
  }
  table {
    /* border-collapse: collapse ; */
    margin: 0 auto ;
    text-align: center;
  }
  th {
    padding: 5px 20px;
  }
  table ,th ,th {
    border: 1px solid #000
  }
</style>
<body>
  <h2>订单确认</h2>
  
 <script>
  // 1.用户输入
  let price = +prompt("商品价格：")
  let num = +prompt("商品数量：")
  let address = prompt("收获地址：")
  // 2.计算总额
  let total = price * num
  // 3.打印渲染
  document.write(`
    <table>
    <tr>
      <th>商品名称</th>
      <th>商品价格</th>
      <th>商品数量</th>
      <th>总价</th>
      <th>收获地址</th>
    </tr>
      <th>华为k70</th>
      <th>${price}元</th>
      <th>${num}</th>
      <th>${total}</th>
      <th>${address}</th>
    </table>
  `)
 </script> 
</body>
</html>
```





### 案例 2：获取用户信息

- 题目描述

  依次询问并获取用户的姓名、年龄、性别，收集数据之后在控制台依次打印出来。

  具体表现如下图：


![](D:\Typora笔记\JS的笔记\img\图片1.png)

![](D:\Typora笔记\JS的笔记\img\图片4.png)

- 题目提示
  - 通过 prompt 来弹出提示框，收集用户信息
  - 通过变量保存数据

#### 练习答案：

```javascript
let uname = prompt("请输入你的姓名：")
let age = prompt("请输入你的年龄：")
let xingbie = prompt("请输入你的性别：")
console.log (uname)
console.log (age)
console.log (xingbie)
```





### 案例 3：增加年龄

- 题目描述

  1、询问用户年龄，用户输入年龄后，把用户输入的年龄增加 5 岁

  2、增加 5 岁后，通过弹出框提示用户 “ 据我估计，五年后，你可能 XX 岁了”

  ![](D:\Typora笔记\JS的笔记\img\图片5.png)

  ![](D:\Typora笔记\JS的笔记\img\图片6.png)

- 题目提示

  - 通过 prompt 来弹出提示框，收集用户信息
  - 通过变量保存数据
  - 转换数据类型(需要预习第二天的数据类型转换哟)

#### 练习答案：

```javascript
	let age = +prompt("请输入你的年龄：")

    console.log(`五年后,你可能${age + 5}岁了`)
```





### 案例 4：计算银行卡余额案例

- 题目描述

  1、用户输入总的银行卡金额，依次输入本月花费的电费，水费，网费。

  2、页面打印一个表格，计算出本月银行卡还剩下的余额。

  ![](D:\Typora笔记\JS的笔记\img\111.gif)


- 题目提示

  - 思路：

    1.我们需要 5 个变量：银行卡总额、水费、电费、网费、银行卡余额

    2.银行卡余额 = 银行卡总额 – 水费 –电费  - 网费  

    3.第一步准备 5 个变量接受输入的数据

    4.第二步计算银行卡余额 

    5.第三步页面打印生成表格，里面填充数据即可。

    6.当然可以提前把 html 页面搭好。

#### 练习答案：

```javascript
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
  <style>
    h3{
      text-align: center;
    }
    table , th ,th {
      border: 1px solid #000;
      margin: 0 auto;
    }
    th {
      padding: 10px;
    }
  </style>
<body>
  <h3>支出表格</h3>
  
  <script>
    let shui = +prompt("请输入水费：")
    let dian = +prompt("请输入电费：")
    let wang = +prompt("请输入网费：")
    const zong = +1000
    let yuer = zong - shui - dian - wang
    document.write(`<table>
    <tr>
      <th>银行卡金额</th>
      <th>电费</th>
      <th>水费</th>
      <th>网费</th>
      <th>剩余余额</th>
    </tr>
      <th>1000</th>
      <th>${shui}</th>
      <th>${dian}</th>
      <th>${wang}</th>
      <th>${yuer}</th>
      </table>
      `)
  </script>
</body>
</html>
```





# 2.JS 基础 运算符和语句

## 2.1 赋值运算符  





### 重点 1：赋值运算符

等号 :

将等号右边的值赋予给左边，要求左边必须是一个容器

```javascript
let num = 1
// num = num + 1
num += 1
console.log(num)
```





### 重点 2：一元运算符

- 正号和负号 就是一元运算符

- ##### 前置自增：

- ```javascript
  let num = 1
  ++num  //让num的值加 1变2
  
  let i = 1
  console.log(++i + 2)  // 结果为4
  ```

  ==前置自增：先自加再使用==

- 后置自增：

- ```javascript
  let num = 1
  num++ //让num的值加 1变2
  
  let i = 1
  console.log(i++ + 2) // 结果为3 先用 i 和 2 相加 等于 3
  console.log(i) // 结果为2
  ```

  ==后置自增：先使用再自加==

​     ==前置自增和后置自增独立使用时二者并没有差别==





### 重点 3：比较运算符

- ![](D:\Typora笔记\JS的笔记\img\比较运算符.png)

```javascript
console.log(3 > 5) //false
console.log(2 == 2) // true
console.log(2 === "2") // false
console.log(NaN === NaN) // false

console.log("a" < "b") //true
console.log("aa" < "aac") //true
```





### 重点 4：逻辑运算符

- 使用场景: 逻辑运算符用来解决多重条件判断

- ```javascript
  num > 5 && num < 10
  ```

  | 符号 | 名称   | 日常读法 | 特点                             | 口诀           |
  | ---- | ------ | -------- | -------------------------------- | -------------- |
  | &&   | 逻辑与 | 并且     | 符号两边为 true<br />结果才为 true | 一假则假       |
  | \|\| | 逻辑或 | 或者     | 符号两边有一个 true<br />就为 true | 一真则真       |
  | ！   | 逻辑非 | 取反     | true 变 false<br />false 变 true | 真变假，假变真 |

  ```javascript
  console.log(true && true) //true
  console.log(true && false) //false
  console.log(3 < 5 && 3 > 2) //true
  
  console.log(true || true)  //true
  console.log(true || false) // false
  console.log(false || false) // false
  
  console.log(!true) // false
  console.log(!false) // true
  ```

  #### 练习：

  判断一个数是 4 的倍数，且不是 100 的倍数

  练习答案：

  ```javascript
  let num = prompt("请输入一个数字：")
  alert(num%4 === 0 && num%100 !== 0)
  ```

  ### 重点 5：

  | 优先级 | 运算符     | 顺序           |
  | ------ | ---------- | -------------- |
  | 1      | 小括号     | （）           |
  | 2      | 一元运算符 | ++ -- ！       |
  | 3      | 算术运算符 | 先* / % 后 + 1 |
  | 4      | 关系运算符 | > >= < <=      |
  | 5      | 想等运算符 | ！== == != === |
  | 6      | 逻辑运算符 | 先&& 后\|\|    |
  | 7      | 赋值运算符 | =              |
  | 8      | 逗号运算符 | ,              |





## 2.2 JS 基础 语句

- 语句是一段可以执行的代码

- ##### 表达式和语句的区别：

  - 表达式: 因为表达式可被求值，所以它可以写在赋值语句的右侧

  - ```javascript
    num = 3 + 4
    ```

  - 而语句不一定有值，所以比如 alert()for 和 break 等语句就不能被用于赋值

  - ```javascript
    alert() console.log()
    ```

程序三大流程控制语句

- 顺序结构
- 分支结构
  - if 分支语句
  - 三元运算符
  - switch 语句
- 循环结构

## if 分支语句

```javascript
if (false) {
console.log("执行语句1") 
} //不输出

if(3 < 5){
    console.log("执行语句2") 
} //输出

// 除了0 所用的数字都为真
if(0) {
    console.log("执行语句3")
} //不输出

// 除了空字符串 所用的字符串都为真
if("") {
    console.log("执行语句")
} //不输出
```





### 练习：==if== 语句 单分支

==需求==：单分支课堂案例 1: 用户输入高考成绩，如果分数大于 700，则提示恭喜

#### 练习答案：

```javascript
let num = + prompt("请输入高考成绩：")
    if (num > 700) {
      alert("恭喜")
    }
```





### 练习：if 语句 双分支

判断用户登录案例

==需求==: 用户输入，用户名: pink，密码: 123456，则提示登录成功，否则提示登录失败

==分析==:
①: 弹出输入框，分别输入用户名和密码
②: 通过 if 语句判断，如果用户名是 pink，并且密码是 123456，则执行 if 里面的语句，否则执行 else 里面的语句。

#### 练习答案：

```javascript
    let uname = prompt("输入用户名：")
    let password = prompt("输入密码：")
    if (uname === "pink" && password === "123456") {
      alert("恭喜成功登录")
    }
    else {
      alert("登录失败")
    }
```





### 练习：判断闰年案例

==需求==: 让用户输入年份，判断这一年是闰年还是平年并弹出对应的警示框

==分析==:
能被 4 整除但 ==不能被 100 整除==，或者 ==被 400 整除== 的年份是闰年，否则都是平年
需要逻辑运算符

#### 练习答案：

```javascript
let nian = prompt("请输入年份")
    if (nian%4 === 0 && nian%100 !== 0 || nian%400 === 0 ){
      alert(`${nian}年是闰年`)
    } else { 
      alert(`${nian}年是平年`)
    }
```





### 练习：多分支 if 语句

==需求==: 根据输入不同的成绩，反馈不同的评价
注:
1: 成绩 90 以上是 优秀
2: 成绩 70~90 是 良好
3: 成绩是 60~70 之间是 及格
4: 成绩 60 分以下是 不及格

#### 练习答案:

```javascript
let num = prompt("请输入你的成绩：")
    if (num >= 90){
      alert("优秀")
    } else if (num >= 70 && num < 90 ) {
      alert("良好")
    } else if (num >= 60 && num < 70 ) {
      alert("及格")
    } else {
      alert("不合格")
    }
```





## 三元运算符

==目标==:
能利用三元运算符执行满足条件的语句
==使用场景==:
其实是比 if 双分支 更简单的写法，可以使用 三元表达式
符号: ==?== 与 ==:== 配合使用

==语法==:
条件 ?满足条件执行的代码 : 不满足条件执行的代码

 

### 练习：判断 2 个数的最大值

==需求==:

用户输入 2 个数，控制台输出最大的值

#### 练习答案：

```javascript
let num1 = +prompt("第一个数:")
let num2 = +prompt("第二个数:") 
let end = num1 > num2 ? num1 : num2
alert(`最大值是${end}`)
```





### 练习：数字补 0 案例

==需求==: 用户输入 1 个数，如果数字小于 10，则前面进行补 0，比如 09 03 等

==分析==:
1: 为后期页面显示时间做铺垫
2: 利用三元运算符 补 0 计算



#### 练习答案：

```javascript
let num = +prompt("请输入一个数字：")
num = num < 10 ? "0" + num : num
alert(num)
```



## ==switch== 语句

### 练习：简单计算器

==需求==:
用户输入 2 个数字，然后输入+-*/任何一个，可以计算结果

####  练习答案：

```javascript
    let num1 = +prompt("请输入第一个数：")
    let num2 = +prompt("请输入第二个数：")
    let fuHao = prompt("请输入+-*/任何一个：")
    switch (fuHao) {
      case "+" :
        alert(`结果为${num1 + num2}`)
        break
      case "-" :
        alert(`结果为${num1 - num2}`)
        break
      case "*" :
        alert(`结果为${num1 * num2}`)
        break
      case "/" :
        alert(`结果为${num1 / num2}`)
        break
      default:
        alert("请正确输入")
    }
```





## 循环结构: ==while==

### 重点 1：断点调试

==作用==:
学习时可以帮助更好的理解代码运行，工作时可以更快找到 bug
==浏览器打开调试界面==
1.按 F12 打开开发者工具
2.点到 sources 一栏
3.选择代码文件



### ==while== 循环

循环: 重复执行一些操作 
while: 在...期间
所以 while 循环 就是在满足条件期间，重复执行某些代码



### while 循环基本语句：

```javascript
- while(循环条件) {
	要重复执行的代码(循环体)
- }
```



### 练习 1：在页面中打印输出 10 句“月薪过万”

==需求==:
使用 while 循环，页面中打印，可以添加换行效果

#### 练习答案：

```javascript
	let i = 1
    while (i <= 10) {
      document.write(`月薪过万<br>`)
      i++
    }
```



### 练习 2：页面输出 1-100

#### 练习答案：

```javascript
	let i = 1
    while (i <= 100) {
      document.write(`${i}<br>`)
      i++
    }
```



### 练习 3：计算从 1 加到 100 的总和并输出

#### 练习答案：

```javascript
	let sum = 0
    let i = 1
    while (i <= 100) {
      sum += i
      i++
    }
    document.write(sum)
```

### 练习 4：计算 1-100 之间的所有偶数和

#### 练习答案：

```javascript
	let sum = 0
    let i = 1
    while (i <= 100) {
      if (i % 2 === 0){
        sum+=i
      }
      i++
    }
    document.write(sum)
```



## 重点 2：循环退出

==循环结束==:
break: 退出循环
continue: 结束本次循环，继续下次循环

例如：==break==

```javascript
	let i =1 
    while (1 <= 5) {
      if(i === 3){
        break
      }
      console.log(`我要吃${i}个包子`)
    i++ 
    }
```

![](D:\Typora笔记\JS的笔记\img\2.2.2 (2).png)





例如：==continue==

```javascript
let i = 1
while (i <=5) {
if(i === 3) {
   i++
  }
console.log(`我要吃第${i}个包子`)
i++
}
```

![](D:\Typora笔记\JS的笔记\img\2.2.3.png)





### 逆天小练习：

==需求==:
页面弹出对话框，" 你爱我吗’，如果输入'爱’，则结束，否则一直弹出对话框
==分析==:
1: 循环条件永远为真，一直弹出对话框
2: 循环的时候，重新让用户输入
3.如果用户输入的是: 爱，则退出循环(break)

#### 练习答案：

```javascript
	let i 
    while (true) {
    if (prompt(`你爱我吗？`) === "爱") {
      break
      }
      else {
        continue
      }
    }
```





### 简易 ATM 取款机案例

==需求==：用户可以选择存钱、取钱、查看余额和退出功能

```javascript
let Q = 1000
while (true) {
    let i = prompt(`请选择您的操作：
      1.取钱
      2.取款
      3.查看余额
      4.退出`)
  switch (i) {
    case "1" :
      let qu = +prompt("请输入您要取钱的数目：")
      Q = Q - qu
      alert(`剩余余额：${Q}`)
      break
          
    case "2" :
      let qk = +prompt("请输入您要存款的数目：")
      Q = Q + qk
      alert(`剩余余额：${Q}`)
      break
          
    case "3" :
      alert(`剩余余额：${Q}`)
      break
    }
    
    if (i === "4" ) {
      alert("已退出") 
      break
    }
  }
```







# 2 实战案例

### 主观题

==输出星期练习（请使用 switch 分支语句来书写程序）==

题目描述：

请用户输入 1 个星期数. 就将对应的英文的星期打印出来. 

- 比如用户输入'星期一'， 则 页面可以打印  monday 
- 英文自己查有道。比如星期一是  monday  星期二是 tuesday 

```javascript
let i = prompt("输入星期一到星期日其中一个：")
switch (i) {
  case "星期一" :
  alert("monday")
  break
  case "星期二" :
  alert("tuesday")
  break
  case "星期三" :
  alert("wednesday")
  break
  case "星期四" :
  alert("thursday")
  break
  case "星期五" :
  alert("fiday")
  break
  case "星期六" :
  alert("saturday")
  break
  case "星期日" :
  alert("sunday")
  break
  default :
  alert("请正确输入")
}
```





**==用户登录验证 **==

题目描述：

接收用户输入的用户名和密码，若用户名为 “admin” , 且密码为 “123456” , 则提示用户登录成功!  否则，让用户一直输入。

```javascript
 while (true) {
  let uname = prompt("用户名：")
  let psw = prompt("密码：")
  if (uname === "admin" && psw === "123456") {
    alert("恭喜")
    break
  } else {
  alert("错误")
  }
  continue
}
```



### 综合案例变形

需求：根据用户选择计算两个数的结果：

**题目描述：**

打开页面出现一个提示框，注意是一直提示的，'请您选择 + - * / ，如果输入 q，则是退出结束程序

- 如果输入的是 + - * / 其中任何一个，比如用户输入是 + ，则是计算求和，如果用户输入是 *  则是计算乘积
  - 则提示第一个弹窗，提示用户：'请您输入第一个数字'
  - 输入完毕则继续提示第二个弹窗，提示用户：'请您输入第二个数字'
  - 都输入完毕，则通过警示框 alert 输出结果
- 如果输入是 q，则结束程序

提示：多分支请使用 if 多分支来完成

具体效果如图：

![](D:\Typora笔记\JS的笔记\img\2zui.gif)

```javascript
while (true) {
  let fuHao = prompt(`
1.请您选择 + - * / 
2.如果输入q,则是退出结束程序
`)
  let num1 = +prompt("第一个数：")
  let num2 = +prompt("第二个数：")
 if (fuHao === "+") {
  alert(`结果：${num1 + num2}`)
 } else if (fuHao === "-") {
  alert(`结果：${num1 - num2}`)
  
 } else if (fuHao === "*") {
  alert(`结果：${num1 * num2}`)
  
 } else if (fuHao === "/") {
  alert(`结果：${num1 / num2}`)
 } else if (fuHao === "q") {
  break
 }
}
```



## 排错题

### 排错题 1

~~~javascript
<!-- 请问以下代码会出现什么问题，如何解决？ -->
<script>
  // 需求： 求用户输入 2 个数字的和
  let num1 = prompt('请输入第一个值')
  let num2 = prompt('请输入第二个值')
  alert(num1 + num2)
</script>
~~~

#### 答案：

<details>
  <summary> 点击展开 </summary>
    prompt 前面没加 加号
</details>



### 排错题 2

~~~javascript
<!-- 请问下面代码会出现什么问题，怎么去解决？ -->
<script>
  // 判断用户名的案例，用户会输入用户名
  // 1. 如果用户名输入'迪丽热巴'，则页面弹出 '用户名输入正确'
  // 2. 如果用户名输入不是'迪丽热巴'，否则弹出'用户名输入不正确'

  let username = prompt('请输入用户名:')
  if (username = '迪丽热巴') {
    alert('用户名输入正确')
  } else {
    alert('用户名输入不正确')
  }
</script>
~~~

#### 答案：

<details>
  <summary> 点击展开 </summary>
    if (username = '迪丽热巴')  中的等号 要换成 ===
</details>



### 排错题 3

~~~html
<body>
  <!-- 请问以下代码会出什么问题？如何解决？ -->
  <script>
    // 需求，用户输入 1~10 之间的整数，则循环打印用户输入的次数
    // 注意此处有 2 个错误，找出并且修正

    let num = prompt('请输入一个 1~10 之间的整数')
    let i = 1
    while (i < num) {
      console.log(`我是第${i}句话`)
    }
  </script>
</body>
~~~

#### 答案：

<details>
  <summary> 点击展开/折叠内容 </summary>
  1.从 1 开始要小于等于， 从 0 开始 可以写小于 <br>
  2.while 循环里面要加 i++ 不然就死循环了
</details>

​    



### 排错题 4

~~~html
<body>
  <!-- bug:请你找到下面代码代码穿透的原因,并找到匹配不上case里面的值的问题进行修改 -->

  <script>
    // 需求： 用户输入 1~4 之间整数，对应输出 '春' '夏' '秋' '冬' 
    // 例如用户输入 1 则输出 '春' ，用户输入 2，则输出 '夏' 以此类推
    // 注意： 此处有 2 个错误，找出并且修正
    let num = +prompt('请你输入一个 1-4 之间的值')
    switch (num) {
      case '1':
        alert('春')
      case '2':
        alert('夏')
      case '3':
        alert('秋')
      case '4':
        alert('冬')
      default:
        alert('请输入 1~4 之间整数')
        break
    }

  </script>
~~~

#### 答案：

<details>
  <summary> 点击展开/折叠内容 </summary>
    1.pormpt 要去掉 +号 <br>
    2.落下了 break ，case 都落下了
</details>











# 3.JS 基础 循环

## 3.1 ==for== 循环语法

==作用==: 重复执行代码
==好处==: 把声明起始值、循环条件、变化值写到一起，让人一目了然，它是最常使用的循环形式

```javascript
for (let i = 0; i <= 3; i++) {
    document.write("你好,js")
}
```





### 循环练习 1：

利用 for 循环输出 1~100 岁

#### 练习答案：

```javascript
for (let i = 1; i <= 100; i++) {
    document.write(`${i}岁<br>`)
}
```



### 循环练习 2：

求 1-100 之间所有的偶数和

#### 练习答案：

```javascript
let sum = 0
for (let i = 1; i <= 100; i++) {
    
    if (i % 2 === 0) {
        sum = i +sum
    }
}                
document.write(sum)
```



### 循环练习 2：

页面中打印 5 个小星星

#### 练习答案：

```javascript
for (let i = 1; i<=5; i++) {
    document.write("☆")
}
```





## 3.2 for 循环的最大价值: 循环数组

### 练习：

请将 ==数组== ["小白", "小黑", "小红", "小蓝", "小绿"] ==依次打印== 出来

#### 练习答案：

```javascript
let arr = ["小白","小黑","小红","小蓝","小绿"]
for (let i = 0;i <= arr.length - 1; i++) {
  document.write(`${arr[i]}<br>`)
}
```







## 3.3 for 循环—基本使用

### 退出循环

==continue== ：退出本次循环，一般用于排除或者跳过某一个选项的时候，可以使用 continue

==break== ：退出整个 for 循环，一般用于结果已经得到, 后续的循环不需要的时候可以使用





#### 例如 continue：

```javascript
for(let i = 1; i <= 5; i++) {
  if (i === 3) {
      continue
  }
  console.log(i)
}  // i 等于3的时候 3不会在控制台打印出来
```





#### 例如 break：

```javascript
for(let i = 1; i <= 5; i++) {
  if (i === 3) {
      break
  }
  console.log(i)
}  // i 等于3的时候  剩下的都不打印了 包括3
```



> for 循环和 while 循环有什么区别呢:
> 当如果明确了循环的次数的时候推荐使用 for 循环当不明确循环的次数的时候推荐使用 while 循环







## 3.4 for 循环嵌套

循环嵌套就是 for 里面有个 for

```javascript
for (let i = 1;i <= 3 ;i++) {
  document.write(`你好啊，${i}<br>`)
  for (let j = 1; j<= 5;j++)
  document.write(`谢谢，${j}<br>`)
}
```









### 练习：打印 5 行 5 列的星星

#### 答案：

```javascript
for (let i = 0;i <= 4 ;i++) {
  document.write(`<br>`)
  for (let j = 1; j<= 5;j++)
  document.write(`⭐`)
}
```



### 练习：打印倒三角形星星

如图所示：

![](D:\Typora笔记\JS的笔记\img\daosanj.png)

#### 答案：

```javascript
for (let i = 0;i <= 4 ;i++) {
    document.write(`<br>`)
  for (let j = 0;j <= i ;j++) {
    document.write(`⭐`)
  }
}
```





### 练习：九九乘法表

```html
<style>
    span {
      display: inline-block;
      text-align: center;
      padding: 5px 10px;
      border : 1px solid pink;
      width: 60px;
      margin: 0px 2px ; 
      border-radius: 5px;
      box-shadow: 2px 2px 2px rgba(250, 198, 207, 0.859);
      background-color: rgba(255, 96, 122, 0.117);
    }
  </style>
  <script>
    for (let i = 1;i <= 9 ;i++) {
        document.write(`<br>`)

      for (let j = 1;j <= i ;j++) {
        document.write(`<span>${j}*${i}=${j*i}</span>`)
      }
    }
  </script>
```







## 3.5 数组

### 数组：Array

是一种可以按顺序保存数据的数据类型

==声明语法：==

let 数组名 = [数据 1，数据 2，数据 3，……, 数据 n]



```html
let arr = [1,2,“ping”,true]
// 计算机中的编号从0开始，所以1的编号为0，2编号为1，以此类推
```







### 练习：求和以及平均值

==需求==:

求数组 [2,6,1,7,4] 里面所有元素的和以及平均值

#### 练习答案：

```javascript
let sum = 0
let ave = 0
let arr = [2,6,1,7,4]
for (let i = 0;i <= arr.length-1; i++) {
  sum = sum + arr[i]
  ave = sum/arr.length
}
alert(`和为：${sum}`)
alert(`平均值：${ave}`)
```







### 练习：求最大值最小值

==需求:==

求数组 [2,6,1,77,52,25,7] 中的最大值

最大值：

```javascript
let max = 0
let arr = [2,6,1,77,52,25,7]
for (let i = 1;i <= arr.length;i++)  {
  max = max > arr[i-1] ? max : arr[i-1]  
}
alert(`最大值为：${max}`)
```

最小值：

```javascript
let arr = [2,6,1,77,52,25,7]
let min = arr[0]
for (let i = 1;i <= arr.length;i++)  {
  
  min = min < arr[i-1] ? min : arr[i-1]  
}
alert(`最小值为：${min}`)
```



## 3.6 数值操作 —— 修改

数组本质是 ==数据集合==，操作数据无非就是 ==增 删 改 查== 语法:

### 数组的增：

==数组名字.push()== 方法将一个或多个元素添加到数组的 ==末尾==，并返回该数组的新长度

```javascript
let arr = ["pink","red"]
arr.push("green")
arr.push("1","2")
console.log(arr)
```


==数组名字.unshift== 方法将一个或多个元素添加到数组的 ==开头==，并返回该数组的新长度

```javascript
let arr = ["pink","red"]
arr.unshift("green")
arr.unshift("1","2")
console.log(arr)
```





### 数组的删：

==数组.pop()== 方法 从数组中 ==删除最后一个元素==，并返回该元素的值

==数组.shift()== 方法 从数组中 ==删除第一个元素==，并返回该元素的值

```javascript
let arr = [2,0,6,1,77,0,52,0,25,7]
arr.pop()
arr.shift()
console.log(arr)
```





#### 数组 splice

> ==语法：==
>
> arr.splice(start, deleteCount)
>
> solice(起始位置，删除几个)

```javascript
let arr = [2,0,6,1,7]
arr.splice(1,2)
console.log(arr) // 剩下2，1，7
```



### 数组的改：

```javascript
let arr = ['pink','red','green']
for (let i = 0; i < arr.length; i++) {
  arr[i] = arr[i] + '劳斯' //改值了
}
console.log(arr)
```





### 数组的查：

```javascript
let arr = ['pink','red','green']
console.log(arr[1])
console.log(arr)
```









### 练习：数组筛选

==需求==:

将数组 [2,0,6,1,77,0,52,0,25,7] 中大于等于 10 的元素选出来，放入新数组

#### 答案：

```javascript
let arr = [2,0,6,1,77,0,52,0,25,7]
let arr2 = []
for (let i = 0; i < arr.length; i++) {
  if (arr[i] >= 10) {
    arr2.push(arr[i])
  }
}
console.log(arr2)
```







### 练习：数组去 0 案例

==需求==:
将数组 [2,0,6,1,77,0,52,0,25,7] 中的 0 去掉后，形成一个不包含 0 的新数组分析:

#### 答案：

```javascript
let arr = [2,0,6,1,77,0,52,0,25,7]
let arr2 = []
for (let i = 0; i < arr.length; i++) {
  if (arr[i] !== 0) {
    arr2.push(arr[i])
  }
}
console.log(arr2)
```







### 冒泡排序

冒泡排序是一种简单的排序算法。
它重复地走访过要排序的数列，一次比较两个元素，如果他们的顺序错误就把他们交换过来。走访数列的工作是重复地进行直到没有再需要交换，也就是说该数列已经排序完成。
这个算法的名字由来是 ==因为越小的元素会经由交换慢慢“浮”到数列的顶端。==
比如数组 [2,3,1,4,5] 经过排序成为了 [1,2,3,4,5] 或者 [5,4,3,2,1]

==第一种==

```javascript
let arr = [1,4,3,5,2]
for (let i = 0; i < arr.length-1; i++) {
  for (let j = 0; j < arr.length -i-1; j++) {
    if (arr[j] > arr[j+1]) {
      let temp = arr[j]
      arr[j] = arr[j+1]
      arr[j+1] = temp
    }
  }
}
document.write(arr) // 1,2,3,4,5
```

==第二种==

用 sort()可以代替第一种的手写排序

```javascript
let arr = [1,4,3,5,2]
arr.sort(function(a,b) { 
  return a - b  //升序 从小到大
})
document.write(arr) 
===========================================
let arr = [1,4,3,5,2]
arr.sort(function(a,b) {
  return b - a  //降序 从大到小
})
document.write(arr)
```













# 3 实战案例

### 练习 1：根据数据生成柱形图

==需求：==
用户输入四个季度的数据，可以生成柱形图

==分析:==
1: 需要输入 4 次，所以可以把 4 个数据放到一个数组里面
   利用循环，弹出 4 次框，同时存到数组里面

2: 遍历改数组，根据数据生成 4 个柱形图，渲染打印到页面中
   柱形图就是 div 盒子，设置宽度固定，高度是用户输入的数据
   div 里面包含显示的数字和 第 n 季度



答案：

```javascript
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        * {
            margin: 0;
            padding: 0;
        }

        .box {
            display: flex;
            width: 700px;
            height: 300px;
            border-left: 1px solid pink;
            border-bottom: 1px solid pink;
            margin: 50px auto;
            justify-content: space-around;
            align-items: flex-end;
            text-align: center;
        }

        .box>div {
            display: flex;
            width: 50px;
            background-color: pink;
            flex-direction: column;
            justify-content: space-between;
        }

        .box div span {

            margin-top: -20px;
        }

        .box div h4 {
            margin-bottom: -35px;
            width: 70px;
            margin-left: -10px;
        }
    </style>
</head>

<body>
    <script>
      let arr = []
      for (let i = 1; i <= 4; i++) {
        arr.push(prompt(`请输入第${i}季度的数据：`))
      }
      // console.log(arr)
      document.write(`<div class="box">`)
      for (let i = 0;i < arr.length;i++) {
        document.write(`
        <div style="height: ${arr[i]}px;">
          <span>${arr[i]}</span>
          <h4>第${i+1}季度</h4>
        </div>
        `)
      }

      document.write(`</div>`)

    </script>
</body>

</html>
```





## 主观题

### 综合大练习：

写一个程序，要求如下（★★） 

* 需求 1：让用户输入五个有效年龄（0-100 之间），**放入数组中**

  * 必须输入五个有效年龄年龄，如果是无效年龄，则不能放入数组中
* 需求 2：打印出所有成年人的年龄 (数组筛选)
* 需求 3：打印出所有人总年龄 （累加）
* 需求 4：打印出所有人的平均年龄 （累加）
* 需求 5：打印出最大年龄和最小年龄 （最大值）



#### 答案：

~~~javascript
  /* 1.让用户输入五个有效年龄（0-100 之间），放入数组中 */
//1.声明累加数组
let arr = []
//2.循环遍历
while( arr.length < 5 ){
    //输入年龄
    let num = +prompt(`请输入第${arr.length+1}个人有效年龄`)
    //判断是否有效
    if( num > 0 && num < 100){
        //添加到数组
        arr.push(num)
    }
}
   console.log(arr)
    // 2. 打印输出成人的年龄  年龄 > 18 
    for (let i = 0; i < arr.length; i++) {
      if (arr [i] >= 18) {
        document.write(`已经成人的年龄是: ${arr[i]} <br>`)
      }
    }
    //  需求 3：打印出所有人总年龄 （累加）
    let sum = 0
    for (let i = 0; i < arr.length; i++) {
      sum += arr [i]
    }
    document.write(`所有人的年龄是: ${sum} <br>`)
    // 需求 4：打印出所有人的平均年龄 （累加）
    let average = 0
    average = sum / arr.length
    document.write(`所有人的年龄是: ${average} <br>`)
    // 需求 5：打印出最大年龄和最小年龄 （最大值）   假设法
    let max = arr [0]
    let min = arr [0]
    for (let i = 1; i < arr.length; i++) {
      if (max < arr [i]) {
        max = arr [i]
      }
      if (min > arr [i]) {
        min = arr [i]
      }
    }
    document.write(`最大值是: ${max} <br>`)
    document.write(`最小值是: ${min} <br>`)
   // 需求 5：打印出最大年龄和最小年龄 （最大值）   排序法
     arr.sort(function (a, b) {
      return a - b;
    }) // 升序
    let min = arr [0]  // 
    let max = arr [arr.length - 1]  // 56
~~~







### 练习题 2：

找出数组中 元素为 10 的下标，有则打印该下标，没有则打印-1

* 例如: [88,20,10,100,50]  打印 2
* 例如: [88,20,30,100,50]  打印-1

~~~javascript
// 找出数组中 元素为 10 的下标，有则打印该下标，没有则打印 - 1
let arr = [88, 20, 10, 100, 50]
let re = -1  // 用于存储结果, 默认没有
for (let i = 0; i < arr.length; i++) {
    if (arr [i] === 10) {
        re = i  //如果找到则把当前索引号赋值给 re， 如果没有找到，则默认的是 -1
        break // 已经找到就退出
    }
}
console.log(re)
~~~







 ### 练习题 3: 

使用 for 循环 - 求出数组元素的和 [5, 8, 9, 2, 1, 5]
     

```javascript
 // 遇到数组 先把遍历写出来!!!!!!!!!!!!!!!=> 访问数组里面的单元的值

let arr = [5, 8, 9, 2, 1, 5]
let sum = 0
for (let i = 0; i < arr.length; i ++) {
    // sum = sum + item
    sum += item
}
console.log(sum) // 30
```







### 练习题 4: 

使用 for 循环 - 求出数组里大于 5 的 i 和 [4, 9, 5, 20, 3, 11]

```javascript
let arr =   [4, 9, 5, 20, 3, 11]
for (let i= 0; i < arr.length; i++) {
    if (arr[i] > 5) {
        sum += arr[i]
    }
}
console.log(sum) 

```







### 练习题 5: 

使用 for 循环 - 求出班级里同学们平均年龄 [16, 20, 21, 35, 18, 25]

```javascript
let arr = [16, 20, 21, 35, 18, 25]
let sum = 0
let ave = 0
for (let i = 0; i <= arr.length-1; i++) {
  sum = sum + arr[i]
}
ave = sum/(arr.length-1)
console.log(ave)
```



### 练习题 6: 

计算 [2, 6, 18, 15, 40] 中能被 3 整除的偶数的和

```javascript
let arr = [2, 6, 18, 15, 40]
let sum = 0
for (let i = 0; i <= arr.length-1; i++) {
  if (arr[i]%3 === 0 && arr[i]%2 === 0 ) {
    sum = sum + arr[i]
  }
}
console.log(sum)
```



### 练习题 7：

计算 [2, 6, 18, 15, 40] 中能被 3 整除的偶数的个数

```javascript
let arr = [2, 6, 18, 15, 40]
let sum = 0
for (let i = 0; i <= arr.length-1; i++) {
  if (arr[i]%3 === 0 && arr[i]%2 === 0 ) {
    sum++
  }
}
console.log(sum)
```



### 练习题 8：

给一个数字数组，该数组中有很多数字 0，将不为 0 的数据存入到一个新的数组中

```javascript
let arr = [2, 0, 18, 0, 40]
let arr2 = []
for (let i = 0; i <= arr.length-1; i++) {
  if (arr[i] !== 0) {
    arr2.push(arr[i])
  }
}
console.log(arr2)
```



###  核心练习题

需求：

根据用户输入的个数，页面可以渲染对应图片的个数

思路分析：

1. 渲染图片比较多，我们可以把图片地址放入数组中，
2. 图片名称是有序号排列的，比如 1.webp  2.webp 此处可以使用循环方式重复渲染图片
3. 渲染位置？ 可以考虑放到 box 盒子里写 script 即可

答案：

~~~html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title> Document </title>
</head>
<style>
    * {
      margin: 0;
      padding: 0;
    }

    li {
      list-style: none;
    }

    .box {
      display: flex;
      flex-wrap: wrap;
      width: 540px;
      margin: 20px auto;
    }



    .box li {
      width: 100px;
      height: 100px;
      margin: 0 10px 10px 0;
    }

    .box li: nth-child(5n+1) {
      margin-right: 0;
    }

    .box li img {
      width: 50%;
      height: 50%;
      border: 2px solid #258DF2;
      border-radius: 10px 0 10px 0;
    }
  </style>
<body>
  <script>
    let arr = []
    let j = prompt(`请输入显示的图片个数：`)
    document.write(`<ul class="box">`)
    for (let i = 1; i <= j; i++) {  
      document.write(`
      <li>
        <img src="/text/img/1 (${i}).jfif" alt="">
      </li>
      `)
    }
    document.write(`<ul>`)
  </script>
</body>
</html>
~~~



## 排错题

### 拍错题 1

~~~html
<body>
  <!-- 请问以下代码会出现什么问题，如何解决？ -->
  <script>
    // 需求： 求 1~100 之间的累加和
    // 注意： 此处有 3 个错误，找出并且修正
    let sum   //错误 1： sum 必须初始化为 0，如果默认是是 undefined，相加结果是 NaN
    for (let i = 1; i < 100; i++;) {  // 错误 2： 从 1 开始，是小于等于。 错误 3： i++ 后面不需要加分号
      sum += i
    }
    console.log(sum)
  </script>
</body>
~~~

### 排错题 2

~~~html
<!-- bug:请你找到下面代码的bug,把数字1打印出来 -->
<body>
  <script>
    let sum = 0
    let arr = [1, 2, 3, 4, 5]
    for (let i = 1; i < arr.length; i++) { // 错误： i 从 0 开始 
      console.log(arr [i])
    }
  </script>
</body>
~~~

### 排错题 3

~~~html
<!-- bug:找到下面代码死循环的原因,并修改为正确的代码 -->

<body>
  <script>
    for (let i = 1; i <= 5; i++) {
      for (let j = 1; j <= 5; i++) {  // 错误： 这里是 j++ 不是 i++ ，不是考察同学眼力，而是很多同学不小心就写这个了，要小心
        console.log(`这是双重for循环`);
      }
    }
  </script>
</body>
~~~













# 4.JS 基础 函数

### 函数的作用

函数可以把具有相同或相似逻辑的代码“包裹”起来，通过函数调用执行这些被“包裹”的代码逻辑，这么做的优势是有利于 ==精简代码方便复用==

比如我们前面使用的 alert()、prompt()和 console.log()都是一些 ==js 函数==，只不过已经封装好了，我们直接使用的

## 4.1 函数的用法

语法：

```
function 函数名() {
	函数体
}
```

```javascript
function sayHi() {
  console.log(`hi`)
}
sayHi() //调用才会执行
```



### 练习：

==需求:==
1.写一个打招呼的函数 hi~
2.把 99 乘法表封装到函数里面，重复调用 3 次

#### 答案：

```javascript
function sayHi() {
  console.log(`hi`)
}
sayHi()
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
  <style>
    span {
      display: inline-block;
      text-align: center;
      padding: 5px 10px;
      border : 1px solid pink;
      width: 60px;
      margin: 0px 2px ; 
      border-radius: 5px;
      box-shadow: 2px 2px 2px rgba(250, 198, 207, 0.859);
      background-color: rgba(255, 96, 122, 0.117);
    }
  </style>
<body>
  <script>
    function jiuJiu() {
    for (let i = 1;i <= 9 ;i++) {
        document.write(`<br>`)

      for (let j = 1;j <= i ;j++) {
        document.write(`<span>${j}*${i}=${j*i}</span>`)
        }
      }
    }
    jiuJiu()
    jiuJiu()
    jiuJiu()
  </script>
</body>
</html>
```



### 练习 2：

==需求:==
1.封装一个函数，计算两个数的和
2.封装一个函数，计算 1-100 之间所有数的和

#### 答案：

```javascript
function sum() {
  let num1 = +prompt(`第一个数：`)
  let num2 = +prompt(`第二个数：`)
  alert(num1 + num2)
}
sum()
```

```javascript
function sum() {
  let sum = 0
  for (let i = 1;i <= 100;i++) {
    sum = i + sum
  }
  alert(sum)
}
sum()
```









## 4.2 函数传参

上个知识点的函数是写死的，函数传参是可以让用户输入一定的值，让函数更灵活

```javascript
function sum(start，end) { // end叫 形参
  let sum = 0
  for (let i = start;i <= end;i++) {
    sum = i + sum
  }
  alert(sum) 
}
sum(1，50) // 50叫 实参 本质是和形参是一样的
```



## 4.3 函数传参-参数默认值

```javascript
function sum(start = 0,end = 0) { // 通常会给形参默认值
  let sum = 0
  for (let i = start;i <= end;i++) {
    sum = i + sum
  }
  console.log(sum)
}
sum()
sum(10,50)
```







## 4.4 函数的封装数组求和

### 练习 1：函数封装-求学生总分

需求: 学生的分数是一个数组, 计算每个学生的总分



#### 答案：

```javascript
function getArrSum (arr=[]) {
  let sum = 0
  for (let i = 0; i < arr.length;i++) {
    sum += arr[i]
  }
  console.log(sum);
  
}
getArrSum([1,2,3,4,5])
getArrSum()
```



实参可以是变量

```javascript
function getArrSum (n = 0,m = 0) {
  let sum = 0
  for (let i = n; i < m;i++) {
    sum += i
  }
  console.log(sum);
  
}
let num1 = +prompt(`请输入起始值：`)
let num2 = +prompt(`请输入结束值：`)
getArrSum(num1,num2)
```







## 4.5 函数的返回值

函数是被设计为 ==执行特定任务== 的代码块

执行完特定任务之后，应该把 ==任务的结果给我们==

```javascript
function fn() {
  return 20
}
let re = fn()
console.log(re)
```

返回值还有三个特点：

1.在函数体中使用 return 关键字能将内部的执行结果交给函数外部使用

2.==return 后面代码不会再被执行==，会立即结束当前函数，所以 return 后面的数据不要换行写

3.return 函数可以没有 return，这种情况函数默认返回值为 undefined



### 练习：函数返回值

1.求任意 2 个数中的最大值, 并返回

2.求任意数组中的最大值并返回这个最大值

3.求任意数组中的最小值并返回这个最小值

#### 答案：

1 两数比较最大值

```javascript
function getZmax (a,b) {
  let max = a > b ? a : b
  console.log(max)
  return max
}
let a = +prompt(`A的值是:`)
let b = +prompt(`B的值是:`)
getZmax(a,b)
```



2 最大值

```javascript
function getMax(arr=[]) {
  let max = 0
  for (let i = 0; i < arr.length-1;i++) {
    max = max > arr[i]? max : arr[i]
  }
  console.log(max);
  
  return max
}
let arr =[4,34,3,6,29,31]
getMax()
```



3 最小值

```javascript
function getMax(arr=[]) {
  let min = arr[0]
  for (let i = 0; i < arr.length-1;i++) {
    min = min < arr[i]? min : arr[i]
  }
  console.log(min);
  
  return min
}
let arr =[4,34,3,6,29,31]
getMin()
```









## 4.6 函数-作用域

通常来说，
一段程序代码中所用到的名字 ==并不总是有效和可用的==，而限定这个名字的 ==可用性的代码范围== 就是这个名
字的 ==作用域==。

### 全局作用域 和 局部作用域

全局作用域：

作用于所有代码执行的环境或者一个 ==独立的 js 文件==

局部作用域：

作用于函数内的代码环境，就是局部作用域。因为跟函数有关系所以也称为函数作用域。



### 匿名函数

函数可以分为具名函数和匿名函数

匿名函数：没有名字的函数, 无法直接使用。

#### 函数表达式

~~~javascript
// 声明
let fn = function() { 
   console.log('函数表达式')
}
// 调用
fn()
~~~

#### 立即执行函数

~~~javascript
(function(){ xxx  })();
(function(){xxxx}());
~~~

>无需调用，立即执行，其实本质已经调用了
>
>多个立即执行函数之间用分号隔开





### 练习：转换时间案例

==需求:==

用户输入秒数，可以自动转换为时分秒

#### 答案：

```javascript
	  // age = age + 1
     // 1. 用户输入
    let second = +prompt('请输入秒数:')
    // 2.封装函数
    function getTime(t) {
      // console.log(t)  // 总的秒数
      // 3. 转换
      // 小时：  h = parseInt(总秒数 / 60 / 60 % 24)
      // 分钟：  m = parseInt(总秒数 / 60 % 60)
      // 秒数: s = parseInt(总秒数 % 60) 
      let h = parseInt(t / 60 / 60 % 24)
      let m = parseInt(t / 60 % 60)
      let s = parseInt(t % 60)
      h = h < 10 ? '0' + h : h
      m = m < 10 ? '0' + m : m
      s = s < 10 ? '0' + s : s
      // console.log(h, m, s)
      return `转换完毕之后是${h}小时${m}分${s}秒`
    }
    let str = getTime(second)
    document.write(str)
    console.log(h)
```







## 4.7 转换为布尔型

### 1.显示转换:

==1.Boolean(内容)==
记忆:”、0、undefined、null、false、NaN 转换为布尔值后都是 false, ==其余则为 true==

```javascript
console.log(Boolean(null)) // false
console.log(Boolean("")) // f
console.log(Boolean(NaN)) // f 
console.log(Boolean(123)) // true
console.log(Boolean("123")) //t
```

```javascript
console.log (false && 20) // false
console.log(5 < 3 && 20)  // false
console.log(undefined && 20) // undefined 
console.log(null && 20) // null
console.log(0 && 20) // 0
console.log(10 && 20) // 20

console.log(false || 20) // 20
console.log(5 < 3 || 20) // 20
console.log(undefined || 20) //20
console.log(null || 20) //20
console.log(0 || 20) //20
console.log(10 || 20) //10
```



### 隐式转换:

1.有字符串的加法 “ ” + 1，结果是 “1” 
2.减法 - (像大多数数学运算一样)只能用于数字，它会使空字符串 " " 转换为 0
3.null 经过 ==数字转换之后== 会变为 0
4.undefined 经过数字转换之后会变为 NaN

```javascript
console.log("" - 1) // -1
console.log("pink老师" - 1) // NaN
console.log(null + 1) // 1
console.log(undefined + 1) // NaN
console.log(NaN + 1) // NaN
```









# 4 实战案例

## 主观题

### 练习题 1：

请看以下代码，并说出执行的流程~~~

```javascript
function printfInput(content) { 
    // 将用户输入的内容, 在页面中显示
    document.write(content)
}
let constr = prompt('请输入内容')
printfInput(constr)
```





### 练习题 2：

**目标：** 求和函数封装练习

**要求:**

1. 封装函数, 名字为 sum
2. 功能: 根据传入的两个数, 求和并且返回求和的结果（函数必须有 return 返回值）

```javascript
function getsum(a , b) {
  let sum = a + b
  return sum
}
let re = getsum(1,3)
document.write(`和为：${re}`)
```





### 练习题 3：

**目的:**  封装函数, 复习函数的基本写法。

**需求：** 实现两个数的值交换(函数版本)  

**分析:**

1. 函数名为 changeNum()
2. 调用函数时,  `changeNum(1，2)`
3. 经过函数内部处理后, 输出  `第一个值的结果是2  第二个值的结果是1`
4. 可以多调用两次

```javascript
function changeNum(a,b) {
  let c = a
  a = b
  b = c
  console.log(a,b)
}
changeNum(1,2)
```







### 练习题 4：

**目的:** 复习函数的声明与调用

**题目：** 封装余额函数

**要求:**

1. 运行程序后, 浏览器显示输入确认框(prompt)
2. 第一个输入确认框提示输入银行卡余额
3. 第二个输入确认框提示输入当月食宿消费金额
4. 第三个输入确认框提示输入当月生活消费金额
5. 输入完毕后, 在页面中显示银行卡剩余金额
6. 提示: 所有功能代码封装在函数内部（函数需要把余额返回）

```javascript
function getQian () {
  let yuEr = +prompt(`输入银行卡余额:`)
  let shiTang = +prompt(`当月食宿消费金额:`)
  let shangHou = +prompt(`当月生活消费金额:`)
  let re = yuEr - shiTang - shangHou
  return re
}
let money = getQian()
document.write(`我的银行卡余额还有${money}元`)
```







### 练习题 5:

**目标：** 封装一个函数, 可以求任意数组的和 或 平均值

**要求：**

- 函数可以传递 2 个参数，比如  handleData(arr, true)      `handleData 处理数据的意思`
  * 参数一： 接受实参传递过来的数组
  * 参数二:    布尔类型  如果是 true 或者不传递参数 是求和操作，   如果传递过来的参数是 false 则是求平均值



```javascript
function handleData (arr = [], buer = true) {
  let sum = 0
  for (let i = 0 ; i < arr.length ; i++) { 
    sum = arr[i] + sum
  }
  if (buer) { 
    return sum
  } else {
    return  sum / arr.length
  }}
console.log(handleData([2,3,5,2],true))
console.log(handleData([2,3,5,2],false))
```







### 拓展题 1

需求：  封装 some 函数查看数组是否存在某个元素  。

- 要传递 2 个参数 元素、数组
- 如果数组存在元素则返回 true，如果没有存在元素就返回 false

例如检测 香蕉  是否存在于  数组 ['苹果', '香蕉', '橘子', '荔枝', '梨子'] 中， 返回结果是 true

格式如下：

~~~javascript
function some (yuanShu, arr = []) {
  for (let i = 0 ; i < arr.length; i++) {
      if (arr [i] === yuanShu) {
        return true
      } else {
        continue
      }
  }
  return false
}
let re = some("星野", ["白子", "星野", "野宫", "芹香"])
let re2 = some("星野", ["白子", "野宫", "芹香"])
console.log(re)
console.log(re2)
~~~

### 拓展题 2 

需求：  封装 findeIndex 函数返回查找元素在数组中的索引号。

- 要传递 2 个参数 元素、数组
- 如果找到，则返回查找元素在数组中的索引号，如果查找不到，则返回 -1

例如检测 香蕉    数组 ['苹果', '香蕉', '橘子', '荔枝', '梨子'] 中， 返回结果是  1

格式如下：

~~~javascript
function findeIndex(yuanShu, arr = []) {
  for (let i = 0; i < arr.length ; i++) {
    if (arr [i] === yuanShu) {
      return 1
    } else {
      continue
    }
  }
  return -1
}
let re = findeIndex("星野", ["白子", "星野", "野宫", "芹香"])
let re1 = findeIndex("星野", ["白子", "野宫", "芹香"])
console.log(re)
console.log(re1)
~~~





## 排错题

### 排错题 1

~~~html
<!-- bug:请你找到代码返回NaN的原因,并进行修改 -->
<body>
  <script>
    // 请返回一个数字型的结果 可以使用默认参数或者逻辑中断都可以
    function fn(x, y) {  // 错误 因为 y 没有参数传递过来所以是 undefined 相加结果是 NaN 可以给 y 设置默认参数
      console.log(x + y)
    }
    fn(1)  
  </script>
</body>
~~~

### 排错题 2

~~~html
<!-- bug:请你找到下面代码的2处错误,并进行修改过来-->
<body>
  <script>
    // 任意数组求和案例
    function getsumArr(arr) {
      let sum = 0
      for (let i = 0; i < arr.legnth; i++) {  // 错误 1： length 写错了这是很多同学容易犯错误的地方
        sum + arr [i]  // 错误 2： 是 sum += arr [i]  很多同学不小心把 = 给丢了
      }
      return sum
    }
    console.log(getsumArr([10, 20, 30, 40]))
  </script>
</body>
~~~









# 5 对象

## 5.1 对象是什么？

对象(object): JavaScript 里的一种数据类型

可以理解为是一种 ==无序== 的数据集合，==注意== 数组是 ==有序== 的数据集合

用来描述某个事物，例如描述一个人 ：
人有姓名、年龄、性别等信息、还有吃饭睡觉打代码等功能



## 5.2 对象的使用

1.对象声明的语法

```javascript
let A = {}
```

2.对象有属性和方法组成

==属性==: 信息或叫特征(名词)。比如 手机尺寸、颜色、重量等..

```javascript
let obj = {
  uname:'pink老师' ,
  age: 18 ,
  gender : "男"
}
console.log(obj)
```

==方法==: 功能或叫行为(动词)。比如 手机打电话、发短信、玩游戏.



### 练习：声明一个产品对象

请声明一个产品对象，里面包如下信息:
要求:
商品对象名字: goods
商品名称命名为: name 商品编号: num
商品毛重: weight
商品产地: address

#### 答案:

```javascript
let obj = {
  goods:'xiaomi17',
  name: 'shouji' ,
  num: 18 ,
  weight : 100 ,
  address : "zhongshan" 
}
console.log(obj)
```



## 5.3 对象的增删改查

### 对象的 ==查找==

```javascript
let obj = {
  'get - name' :'nihao'
  goods:'xiaomi17',
  name: 'shouji' 
}
console.log(obj.goods) //
console.log(obj.['get - name'])
```



### 对象的 ==修改==

```javascript
let obj = {
  goods:'xiaomi17',
  name: 'shouji' ,
  num: 18 ,
  weight : 100 ,
  address : "zhongshan" 
}
obj.num = '20' //
obj.weight = '200' //
console.log(obj)
```



### 对象的 ==增加==

```javascript
let obj = {
  goods:'xiaomi17',
  name: 'shouji' ,
  num: 18 ,
  weight : 100 ,
  address : "zhongshan" 
}
obj.hobby = '篮球' //
console.log(obj)
```



### 对象的 ==删除==

```javascript
let obj = {
  goods:'xiaomi17',
  name: 'shouji' ,
  num: 18 ,
  weight : 100 ,
  address : "zhongshan" 
}
delete obj.goods //
console.log(obj)
```



### 练习：对产品对象进行操作

要求:
1.请将商品名称里面的值修改为: 小米 10 PLUS
2.新增一个属性颜色 color 为'粉色
3.请依次页面打印输出所有的属性值



#### 答案：

```javascript
let obj = {
  goods:'xiaomi',
  name: 'xiaomi 10' ,
  num: 1001212 ,
  weight : '0.55kg' ,
  address : "zhonggou" 
}
obj.name = 'xiaomi 10 PLUS'
obj.color = '粉色'
console.log(obj)
```







## 5.4 对象的方法和使用

方法就是 在对象里面写了个函数

```javascript
let obj = {
  goods: 'xiaomi',
  name: 'xiaomi 10',
  song: function(x,y) {
    console.log(x + y)
  }
}
obj.song(1,2)  // 3
console.log(obj)
```



### ==遍历对象==

for 遍历对象的问题:
对象没有像数组一样的 length 属性, 所以 ==无法确定长度==
对象里面是无序的键值对，==没有规律== 不像数组里面有规律的下标

```javascript
let obj = {
  goods: 'xiaomi',
  name: 'xiaomi 10',
  age : '18'
}
for (let k in obj) {
  console.log(k)
  console.log(obj[k])
}
// 打印结果：
 goods
 xiaomi
 name
 xiaomi 10
 age
 18
```



### 练习：遍历数组对象 1

需求: 请把下面数据中的对象打印出来

let students =[

   {name:'小明', age: 18, gender:'男', hometown:'河北省'},

   {name:'小红', age: 19, gender:'女', hometown:'河南省'},

   {name:'小刚', age: 17, gender:'男', hometown:'山西省'},

   {name:'小丽', age: 18, gender:'女', hometown:'山东省'}

#### 答案：

```javascript
let students =[
  {name:'小明',age:18, gender:'男',hometown:'河北省'},
  {name:'小红',age:19,gender:'女',hometown:'河南省'},
  {name:'小刚',age:17, gender:'男',hometown:'山西省'},
  {name:'小丽',age:18,gender:'女',hometown:'山东省'}
]
for (let i = 0 ; i < students.length ;i++) {
  console.log(i)
  console.log(students[i]) 
  // console.log(students[i].name)
}
```







### 练习 2：遍历数组对象 2

根据以下数据渲染生成表格

![](D:\Typora笔记\JS的笔记\img\bianliduixiang.png)

#### 答案：

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  th{
    width: 80px;
    height: 40px;
  }
  table,tr,th{
    border: 1px solid #000;
    border-collapse: collapse;
  }
  table tr:nth-child(1) {
    background-color: #888888;
  }

  table th:not(:first-child):hover {
    background-color: #888888;
  }
 
  caption {
    font-size: 18px;
    margin-bottom: 10px;
    font-weight: 700;
  }
</style>
  <table>
    <caption>列表</caption>
    <tr>
      <th>序号</th>
      <th>姓名</th>
      <th>年龄</th>
      <th>性别</th>
      <th>家乡</th>
    </tr>
    <script>
      let students =[
        {name:'小明',age:18, gender:'男',hometown:'河北省'},
        {name:'小红',age:19,gender:'女',hometown:'河南省'},
        {name:'小刚',age:17, gender:'男',hometown:'山西省'},
        {name:'小丽',age:18,gender:'女',hometown:'山东省'}
      ]
      for (let i = 0; i < students.length;i++) {
        document.write(`
        <tr>
          <th>${i + 1}</th>
          <th>${students[i].name}</th>
          <th>${students[i].age}</th>
          <th>${students[i].gender}</th>
          <th>${students[i].hometown}</th>
        </tr>
        `)
      }
    </script>
  </table>
<body>
</body>
</html>
```







## 5.5 内置对象

回想一下我们曾经使用过的 `console.log`，`console` 其实就是 JavaScript 中内置的对象，该对象中存在一个方法叫 `log`，然后调用 `log` 这个方法，即 `console.log()`。

除了 `console` 对象外，JavaScritp 还有其它的内置的对象

### Math

`Math` 是 JavaScript 中内置的对象，称为数学对象，这个对象下即包含了属性，也包含了许多的方法。

#### 属性

- Math.PI，获取圆周率

```javascript
// 圆周率
console.log(Math.PI);
```

#### 方法

- Math.random，生成 0 到 1 间的随机数

```javascript
// 0 ~ 1 之间的随机数, 包含 0 不包含 1
Math.random()
```

- Math.ceil，数字向上取整

```javascript
// 舍弃小数部分，整数部分加1
Math.ceil(3.4)
```

- Math.floor，数字向下取整

```javascript
// 舍弃小数部分，整数部分不变
Math.floor(4.68)
```

- Math.round，四舍五入取整

```javascript
// 取整，四舍五入原则
Math.round(5.46539)
Math.round(4.849)
```

- Math.max，在一组数中找出最大的

```javascript
// 找出最大值
Math.max(10, 21, 7, 24, 13)
```

- Math.min，在一组数中找出最小的

```javascript
// 找出最小值
Math.min(24, 18, 6, 19, 21)
```

- Math.pow，幂方法

```javascript
// 求某个数的多少次方
Math.pow(4, 2) // 求 4 的 2 次方
Math.pow(2, 3) // 求 2 的 3 次方
```

- Math.sqrt，平方根

```javascript
// 求某数的平方根
Math.sqrt(16)
```

数学对象提供了比较多的方法，这里不要求强记，通过演示数学对象的使用，加深对对象的理解。







## 5.6 随机数函数

如何生成 0-10 的随机数呢?

- ```javascript
  Math.floor(Math.random()*(10 + 1))
  ```



如何生成 5-10 的随机数?

- ```javascript
  Math.floor(Math.random()*(5 + 1)) + 5
  ```



==如何生成 N - M 之间的随机数?==

- ```javascript
  Math.floor(Math.random()*(M - N + 1)) + N
  ```

  



### 练习：随机点名案例

请把 ['白子','星野','野宫','芹香','绫音'] 随机显示一个名字到页面中

#### 答案：

```javascript
let arr = ['白子','星野','野宫','芹香','绫音']
let i = Math.floor(Math.random() * arr.length )
document.write(arr[i])
```





### 练习 2：随机点名案例 但是 ==不允许重复== 显示

请把 ['白子','星野','野宫','芹香','绫音'] 随机显示一个名字到页面中，==不允许重复== 显示

#### 答案：

```javascript
let arr = ['白子','星野','野宫','芹香','绫音']
let random = Math.floor(Math.random() * arr.length )
  document.write(arr[random])
  arr.splice(random , 1)
  console.log(arr)
```







### 练习 3：猜数字游戏

需求: 程序随机生成 1~10 之间的一个数字，用户输入一个数字

1.如果大于该数字，就提示，数字猜大了，继续猜
2.如果小于该数字，就提示，数字猜小了，继续猜
3.如果猜对了，就提示猜对了，程序结束

#### 答案：

```javascript
let num = +prompt("请输入一个数字：")
let random = Math.floor(Math.random() * (10 + 1) + 1)
while (true) {
  if (num === random) {
    alert(`对了`)
    break
  } else if (num < random) {
    alert(`小了`)
    num = +prompt("继续猜：")
    continue
  } else if (num > random) {
    alert(`大了`)
    num = +prompt("继续猜：")
    continue
  }
}
```









# 5 实战案例

## 主观题

### 练习题1：

点名: 每次刷新网页运行, 在控制台 随机输出一位同学的名字 ["老赵", "老李", "小传", "小黑"]，如果输出了，则数组中删除这个名字

~~~javascript
let arr = ["老赵", "老李", "小传", "小黑"]
let j = Math.floor(Math.random() * arr.length)
console.log(arr[j])
arr.splice(j, 1)
console.log(arr)
~~~





### 练习题2：

声明对象

目的: 复习对象的声明

要求:

1. 声明一个变量per, 类型为对象类型
2. 该对象的属性为性别,年龄,爱好(3个)
3. 该对象的方法有 说话, 吃饭(2个)
4. 在控制台分别调用该对象的属性和方法

```javascript
let per = {
  gat : "男",
  age : 25,
  hibbits : ['打游戏', '看电影', '旅游'],
  sayHello : function () {
    console.log('你好')
  },
  getEat : function () {
    console.log('吃饭')
  }
}
console.log(per.gat)
console.log(per.age)
console.log(per.hibbits)

per.sayHello()
per.getEat()
```







### 练习题3：

调用对象的方法

目的: 复习对象的使用

要求:

1. 对象声明完毕后, 调用对象中的吃饭的方法
2. 提示: 对象中的方法本质是函数, 调用需要加()
3. 方法也可以传递参数的

```javascript
let per = {
  sex: 'man', // 年龄,
  age: 18, // 性别,
  hobby: 'studyAndGame', // 爱好
  speak: function () {
    // 说话,
     document.write(`speak方法被调用了---<br>`)
   },
   eat: function (f) {
    // 吃饭
    document.write(`我今天吃的是${f}`)
   }
}
// 下面是调用部分
document.write(`姓名:${per.sex} <br>`)
document.write(`姓名:${per.age}<br>`)
document.write(`姓名:${per.hobby}<br>`)

// 调用方法
per.speak()
per.eat('苹果')
```







### 练习题4：

猜数字游戏，设定次数，最多猜8次

```javascript
let num = Math.floor(Math.random()* 10)
let guess = +prompt("请输入一个数字：")
for (let i = 0; i < 8; i++) {
  if (guess === num) {
  alert("恭喜你，猜对了！")
  break
  }  else if (guess < num) {
  alert("猜小了！")
  }  else if (guess > num) {
  alert("猜大了！")
  }
  guess = +prompt(`你剩下${8 - i}次机会，请输入一个数字：`)
  if (i === 7) {
  alert("很遗憾，你用完了8次机会，游戏结束！")
  }
}
```







### 拓展

**需求：** 利用对象数组渲染学生列表案例

**展示效果：**如下：

![](D:\Typora笔记\JS的笔记\img\学生放大缩小.png)

功能1：

1. 利用对象数组里面的数据来渲染页面，渲染多个数据
2. 鼠标经过停留会显示`学生名字`

```javascript
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  .box {
    height: 50px;
    display: flex;
    width: 50px;
    margin: 10px auto ;
    padding: 0px;
    justify-content: center;
  }
  img {
    height: 100px;
    padding: 0px;
    margin: 0px;
    transition: 0.3s ease;
  }
  img:hover {
    height: 125px;
  }
</style>
<body>
  <script>
    let datas = [
      { name: '日奈', imgSrc: '/text/img/10004.webp' },
      { name: '星野', imgSrc: '/text/img/10005.webp' },
      { name: '瞬', imgSrc: '/text/img/10011.webp' },
      { name: '泉奈', imgSrc: '/text/img/10014.webp' },
      { name: '野宫', imgSrc: '/text/img/13004.webp' },
      { name: '睦月', imgSrc: '/text/img/13006.webp' },
      { name: '纯子', imgSrc: '/text/img/13007.webp' },
      { name: '椿', imgSrc: '/text/img/13009.webp' },
      { name: '优香', imgSrc: '/text/img/13010.webp' },
      { name: '响', imgSrc: '/text/img/20000.webp' },
      { name: '真白', imgSrc: '/text/img/20003.webp' },
      { name: '晴', imgSrc: '/text/img/23003.webp' },
      { name: '绫音', imgSrc: '/text/img/23005.webp' }
    ]
    
      for(let i = 0; i < datas.length; i++){
        document.write(`
          <img src="${datas[i].imgSrc}" title="${datas[i].name}"></img>
        `)
      }
    
  </script>
</body>
</html>
```



### 排错题1

~~~html
<!-- bug:请你找到下面代码的2处BUG进行修改 -->

<body>
  <script>
    let obj = {
      name: '张三',
      age: 20,
      sex: '男',
      address: '中国人'
    }
    // 获取姓名
    console.log(obj.['name'])  // 错误1： 没有点

    // 获取地址
    console.log(obj.addres)  // 错误2： addres写错了，单词拼错
  </script>
</body>
~~~



### 排错题2

~~~html
<!-- 请你找到下面代码的3处bug进行修改 -->

<body>
  <script>
    let obj = {
      name: '张三',
      age: 20,
      sex: '男',
      address: '中国人',
      sing: function () {
        console.log('我会唱歌')
      }   // 错误3： 这里少了一个逗号
      sum: function (x, y) {
       return x + y
      }
    }

    console.log(obj.sing)   // 错误1： 方法调用是  obj.sing()
    console.log(obj.sum) // 错误2： 方法调用是  obj.sum()
  </script>
</body>
~~~





