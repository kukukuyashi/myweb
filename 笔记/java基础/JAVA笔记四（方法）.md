# JAVA笔记四（方法）

## **1.方法的概念**

方法（method）是程序中最小的执行单元

**注意：**

- 方法必须先创建才可以使用，该过程成为方法定义
- 方法创建后并不是直接可以运行的，需要手动使用后，才执行，该过程成为方法调用



- 定义格式：

```Java
public static void 方法名 (   ) {
  // 方法体;
}
```



### 1.1**无参数方法的练习**

**需求：**设计一个方法用于打印两个数中的较大数 

```Java
public class MethodTest {
    public static void main(String[] args) {
        //在main()方法中调用定义好的方法
        getMax();
    }

    //定义一个方法，用于打印两个数字中的较大数，例如getMax()
    public static void getMax() {
        //方法中定义两个变量，用于保存两个数字
        int a = 10;
        int b = 20;

        //使用分支语句分两种情况对两个数字的大小关系进行处理
        if(a > b) {
            System.out.println(a);
        } else {
            System.out.println(b);
        }
    }
}
```



### 1.2**形参和实参**

1. **形参：**方法定义中的参数

等同于变量定义格式，例如：int number

1. **实参：**方法调用中的参数

等同于使用变量或常量，例如： 10  number

1. ### **带参数方法练习**

**需求：**设计一个方法用于打印两个数中的较大数，数据来自于方法参数 }

**思路：**

 ①定义一个方法，用于打印两个数字中的较大数，例如getMax() 

 ②为方法定义两个参数，用于接收两个数字 

 ③使用分支语句分两种情况对两个数字的大小关系进行处理 

 ④在main()方法中调用定义好的方法（使用常量）

 ⑤在main()方法中调用定义好的方法（使用变量） 

```Java
public class MethodTest {
    public static void main(String[] args) {
        //在main()方法中调用定义好的方法（使用常量）
        getMax(10,20);
        //调用方法的时候，人家要几个，你就给几个，人家要什么类型的，你就给什么类型的
        //getMax(30);
        //getMax(10.0,20.0);

        //在main()方法中调用定义好的方法（使用变量）
        int a = 10;
        int b = 20;
        getMax(a, b);
    }

    //定义一个方法，用于打印两个数字中的较大数，例如getMax()
    //为方法定义两个参数，用于接收两个数字
    public static void getMax(int a, int b) {
        //使用分支语句分两种情况对两个数字的大小关系进行处理
        if(a > b) {
            System.out.println(a);
        } else {
            System.out.println(b);
        }
    }
}
```



### 1.3**带返回值方法的定义和调用**

1. ### **带返回值方法定义和调用**

- 定义格式

```Java
public static 数据类型 方法名 ( 参数 ) {
        return 数据 ;
}
```

- 范例

```Java
public static boolean isEvenNumber( int number ) {

        return true ;
}
public static int getMax( int a, int b ) {
        return  100 ;
}
```

1. ### **带返回值方法练习**

**需求：**设计一个方法可以获取两个数的较大值，数据来自于参数

**思路：**

 ①定义一个方法，用于获取两个数字中的较大数 

 ②使用分支语句分两种情况对两个数字的大小关系进行处理 

 ③根据题设分别设置两种情况下对应的返回结果 

 ④在main()方法中调用定义好的方法并使用变量保存 

 ⑤在main()方法中调用定义好的方法并直接打印结果 

**代码：**

```Java
public class MethodTest {
    public static void main(String[] args) {
        //在main()方法中调用定义好的方法并使用变量保存
        int result = getMax(10,20);
        System.out.println(result);
        //在main()方法中调用定义好的方法并直接打印结果
        System.out.println(getMax(10,20));
    }
    //定义一个方法，用于获取两个数字中的较大数
    public static int getMax(int a, int b) {
        //使用分支语句分两种情况对两个数字的大小关系进行处理
        //根据题设分别设置两种情况下对应的返回结果
        if(a > b) {
            return a;
        } else {
            return b;
        }
    }
}
```



### 1.4**方法的注意事项**

1. ### **方法的注意事项**

- 方法不能嵌套定义
  -  **示例代码：**

  - ```Java
    public class MethodDemo {
        public static void main(String[] args) {
    
        }
    
        public static void methodOne() {
            public static void methodTwo() {
                // 这里会引发编译错误!!!
            }
        }
    }
    ```
- void表示无返回值，可以省略return，也可以单独的书写return，后面不加数据
  -  **示例代码：**

  - ```Java
    public class MethodDemo {
        public static void main(String[] args) {
    
        }
        public static void methodTwo() {
            //return 100; 编译错误，因为没有具体返回值类型
            return;        
            //System.out.println(100); return语句后面不能跟数据或代码
        }
    }
    ```

例如：

练习1:遍历数组定义一个方法遍历数组遍历格式如下:[1,2, 3,4, 5]

package com.itheima.test.array.method;

public class method3 {
    public static void main(String[] args) {
        int[] arr = {1,2,3,4,5,6,7,8,9,10};
        printArray(arr);
    }
    
```java
package com.itheima.test.array.method;

public class method3 {
    public static void main(String[] args) {
        int[] arr = {1,2,3,4,5};
        printArray(arr);
    }

    public static void printArray(int[] arr) {
        System.out.print("[");
        for (int i = 0; i < arr.length; i++) {
            if (i == arr.length - 1) {
                System.out.println(arr[i] + "]");
            } else {
                System.out.print(arr[i] + ", ");
            }
        }
    }
}
```


练习2
用方法打印九九乘法表

```java
package com.itheima.test.array.method;

public class method4 {
    static void main(String[] args) {
        gat9X9();
    }
    public static void gat9X9 () {
        for (int i = 1; i <= 9; i++) {
            for (int j = 1; j <= i; j++) {
                System.out.print(i + " * " + j + " = " + i * j +"\t");
            }
            System.out.println();
        }
    }
}
```



练习3

给定两个长方形，判断哪个长方形的面积更大?
如何定义方法?
小诀窍:
1.观察在大段的代码当中，反复使用的独立功能是什么?反复使用+独立功能
2.这个独立功能，需要什么才能完成?---形参 长宽
3.方法的调用处，是否需要这个独立功能的结果继续做其他事情? 必须要把面积返回

```java
package com.itheima.test.array.method;

public class method5 {
    static void main(String[] args) {
        double len1 = 10.0;
        double len2 = 20.0;

        double wigth1 = 10.0;
        double wigth2 = 7.0;

        double area1 = gatArea(len1, wigth1);
        double area2 = gatArea(len2, wigth2);

        if (area1 > area2) {
            System.out.println("第一个矩形面积大");
        } else if (area1 < area2) {
            System.out.println("第二个矩形面积大");
        } else {
            System.out.println("两个矩形面积相同");
        }

    }
    public static double gatArea(double len, double wigth) {
        return len * wigth;
    }
}

```



### 1.5**方法重载**

1. ### **方法重载**

- 概念：方法重载指同一个类中定义的多个方法之间的关系，满足下列条件的多个方法相互构成重载
  - 多个方法在同一个类中
  - 多个方法具有相同的方法名
  - 多个方法的参数不相同，类型不同或者数量不同

**注意：**

- 重载仅对应方法的定义，与方法的调用无关，调用方式参照标准格式
- 重载仅针对同一个类中方法的名称与参数进行识别，与返回值无关，换句话说不能通过返回值来判定两个方法是否相互构成重载



```Java
public class MethodDemo {
    public static void fn(int a) {
            //方法体
    }
    public static int fn(double a) {
            //方法体
    }
}
public class MethodDemo {
    public static float fn(int a) {
            //方法体
    }
    public static int fn(int a , int b) {
            //方法体
    }
}
```



**方法重载练习**

**需求：**使用方法重载的思想，设计比较两个整数是否相同的方法，兼容全整数类型（byte,short,int,long） 

**思路：**

 ①定义比较两个数字的是否相同的方法compare()方法，参数选择两个int型参数

 ②定义对应的重载方法，变更对应的参数类型，参数变更为两个long型参数

 ③定义所有的重载方法，两个byte类型与两个short类型参数 

 ④完成方法的调用，测试运行结果 

**代码：**

```Java
public class MethodTest {
    public static void main(String[] args) {
        //调用方法
        System.out.println(compare(10, 20));
        System.out.println(compare((byte) 10, (byte) 20));
        System.out.println(compare((short) 10, (short) 20));
        System.out.println(compare(10L, 20L));
    }
    //int
    public static boolean compare(int a, int b) {
        System.out.println("int");
        return a == b;
    }
    //byte
    public static boolean compare(byte a, byte b) {
        System.out.println("byte");
        return a == b;
    }
    //short
    public static boolean compare(short a, short b) {
        System.out.println("short");
        return a == b;
    }
    //long
    public static boolean compare(long a, long b) {
        System.out.println("long");
        return a == b;
    }
}
```



### 1.6方法的综合练习

**练习1：**

跳水比赛有五个评委打分，分数在0~100之间。最终得分会去掉一个最高分，去掉一个最低分，剩余的分数再求平均数，改平均数为选手最终得分。 

要求1:利用键盘录入5个整数存入数组当中，如果分数超出范围需要重新录入
要求2:定义方法分别求数组的最大值和最小值 
要求3:计算五名评委的总分 
要求4:总分-最大值-最小值，求选手最终平均分



```java
package com.itheima.test.array.method;

import java.util.Arrays;
import java.util.Scanner;

public class method6 {
    public static void main(String[] args) {
        int[] arr = new int[5];

        getArr(arr);
        System.out.println("总分："+getSum(arr) + "最小值：" + getMin(arr) + "最大值：" + getMax(arr) + "平均分：" + getAvg(arr));


    }
    public static void getArr (int[] arr) {
        Scanner sc = new Scanner(System.in);
        for (int i = 0; i < arr.length; i++) {
            boolean flag = true;
            System.out.println("请输入第" + (i + 1) + "个数字：");
            arr[i] = sc.nextInt();
            while (flag) {
                if (arr[i] > 100 || arr[i] < 0){
                    System.out.println("输入的数字有误，请重新输入：");
                    arr[i] = sc.nextInt();
                    continue;
                } else {
                    flag = false;
                }
            }
        }
        System.out.println(Arrays.toString(arr));
    };
    public static int getSum (int[] arr) {
        int sum = 0;
        for (int i = 0; i < arr.length; i++) {
            sum += arr[i];
        }
        return sum;
    }

    public static int getMin (int[] arr) {
        int min = arr[0];
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] < min) {
                min = arr[i];
            }
        }
        return min;
    }

    public static int getMax (int[] arr) {
        int max = arr[0];
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        return max;
    }

    public static double getAvg (int[] arr) {
        double sum = getSum(arr) - getMin(arr) - getMax(arr);
        return sum / (arr.length - 2);
    }
}
```





**练习2：**

班主任需要统计10名学生的数学成绩(0-100分)，
计算及格率，平均分，并找出最高分。

要求1:键盘录入10名学生的成绩，存入数组。超出范围，提示“成绩无效，请重新输入”要求2:定义方法，求及格人数，根据及格人数，求及格率。
要求3:定义方法求总分，根据总分求平均分
要求4:定义方法求最大值。

```java
package com.itheima.test.array.method;

import java.util.Scanner;
import java.util.Arrays;

public class method7 {
    static void main(String[] args) {
        int[] arr = new int[10];
        getArr(arr);
        System.out.println("通过人数为："+ getPass(arr));
        System.out.println("总分：" + getSum(arr));
        System.out.println("平均分：" + getAvg(arr));
        System.out.println("通过率：" + getPassRate(arr) + "%");
        System.out.println("最高分：" + getMax(arr));
    }
    public static void getArr(int[] arr) {
        Scanner sc = new Scanner(System.in);
        for (int i = 0; i < arr.length; i++) {
            System.out.println("请输入第" + (i + 1) + "个学生的成绩:");
            int num = sc.nextInt();
            boolean flag = true;
            while (flag) {
                if (num < 0 || num > 100) {
                    System.out.println("成绩无效，请重新输入:");
                    num = sc.nextInt();
                    continue;
                } else {
                    arr[i] = num;
                    flag = false;
                }
            }
        }
        System.out.println(Arrays.toString(arr));
    }
    public static int getPass (int[] arr) {
        int count = 0;
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] >= 60) {
                count++;
            }
        }
        return count;
    }
    public static int getSum (int[] arr) {
        int sum = 0;
        for (int i = 0; i < arr.length; i++) {
            sum += arr[i];
        }
        return sum;
    }

    public static int getAvg (int[] arr) {
        int sum = getSum(arr);
        return sum/arr.length;
    }

    public static int getPassRate (int[] arr) {

        return arr.length/getPass(arr);
    }

    public static int getMax (int[] arr) {
        int max = arr[0];
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        return max;
    }
}

```



练习3：

某快递公司的运费规则如下(首重1kg，超出部分按kg计算，不足1kg按1kg算):首重1kg:10元;
超出1-5kg:每kg加2元;
超出5kg以上:每kg加1.5元。
键盘录入小数，表示用户快递的重量，计算最终的结果
要求1:快递重量必须大于0，否则重新输入
要求2:不同价位的计算，单独定义一个方法

```java
package com.itheima.test.array.method;

import java.util.Scanner;

public class method8 {
    static void main(String[] args) {
        double weight = getweight();
        System.out.println("物品的运费为：" + weight);
    }
    public static double getweight () {
        Scanner sc = new Scanner(System.in);
        System.out.println("请输入物品的重量(kg)：");
        double weight = sc.nextDouble();
        while (weight <= 0) {
            System.out.println("输入的数字有误，请重新输入：");
            weight = sc.nextDouble();
        }
        double chaWeight = (int) Math.ceil(weight);
        if (chaWeight <= 1) {
            return 10;
        } else if (chaWeight <= 5) {
            return 10 + (chaWeight - 1) * 2;
        } else {
            return 10 + 8 + (chaWeight - 5) * 1.5;
        }
    }
}
```