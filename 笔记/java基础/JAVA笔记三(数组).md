# JAVA笔记三（数组）

## 数组

### 1.数组的概念

**概念：**指的是一种容器，可以同来存储同种数据类型的多个值。但是数组容器在存储数据的时候，需要结合隐式转换考虑。

**比如：**定义了一个int类型的数组。那么boolean。double类型的数据是不能存到这个数组中的，但是byte类型，short类型，int类型的数据是可以存到这个数组里面的。

**举例：**

- 整数1 2 3 4 56 就可以使用int类型的数组来存储。
- 小数1.1 1.2 1.3 1.4 就可以使用double类型的数组来存储。
- 字符串"aaa"  "bbb"  "ccc" 就可以使用String类型的数组来存储。



### 2.**数组的静态初始化**

**完整格式：****数据类型[] 数组名 = new 数据类型[]{元素1，元素2，元素3，元素4...};**

```java
int[] nianArr  = {18,17,19};
double[] hightArr  = {180,179,169,182.2,132.4};
String[] nameArr  = {"xiaoming","xiaogao","xiaomei"};
```



### 3.**数组元素访问**

**格式：****数组名[索引];**

**作用：**

- 获取数组中对应索引上的值
- 修改数组中对应索引上的值
- 一旦修改之后，原来的值就会被覆盖了。

```Java
public class ArrDemo2 {
    /*
        数组中元素访问的格式：数组名[索引];
        作用：
          1.获取指定索引上对应的元素
          2.修改指定索引上对应的元素
    */
    public static void main(String[] args) {
       int[] arr = {1,2,3,4,5};
       //需求1：获取arr数组中，3索引上的值
        int number = arr[3];
        System.out.println(number);
        System.out.println(arr[3]);

       //需求2：将arr数组中，3索引上的值修改为10
            arr[3] = 10;
        System.out.println("修改之后为:" + arr[3]);
    }
}
```

### 4.**索引**

也叫角标、下标就是数组容器中每一个小格子对应的编号。

**索引的特点：**

- 索引一定是从0开始的。
- 连续不间断。
- 逐个+1增长。



### **5.数组的遍历**

**遍历：**就是把数组里面所有的内容一个一个全部取出来。

**数组的长度：**数组名.length;

**通用代码：**

```Java
for(int i = 0; i < arr.length; i++){
    //在循环的过程中，i依次表示数组中的每一个索引
    sout(arr[i]);//就可以把数组里面的每一个元素都获取出来，并打印在控制台上了。
}
```



### 6.**数组的动态初始化**

**数组的动态初始化**是指：在创建数组时，**只指定数组的长度**，而不显式指定数组元素的初始值，由系统为数组元素分配默认的初始值。

语法格式：

```java
// 一维数组
数据类型[] 数组名 = new 数据类型[长度];

// 例如
int[] arr = new int[5];     // 创建一个长度为5的int数组
String[] names = new String[3];  // 创建一个长度为3的String数组
```

**数组的默认初始化值：**

- 整数类型：0
- 小数类型：0.0
- 布尔类型：false
- 字符类型：'\u0000'
- 引用类型：null



**练习1：存储数据**
键盘录入5个的整数，存入数组当中，并进行遍历

```java
int[] arr = new int[5];
        Scanner sc = new Scanner(System.in);
        for (int i = 0; i < arr.length; i++) {
            System.out.println("请输入第" + (i+1) + "个数:");
            int num = sc.nextInt();
            arr[i] = num;
        }
        System.out.println(arr[1]);
```



**练习2：求最值**
已知数组元素为 {33,5,22,44,55}
请找出数组中最大值并打印在控制台

```java
int[] arr = {33,5,22,44,55};
int max = arr[0];  // 假设第一个数是最大值
for (int i = 1; i < arr.length; i++) {  // 从第二个数开始比较
    if (arr[i] > max) {
        max = arr[i];  // 更新最大值
    }
}
System.out.println(max);
```



**练习3：打乱数据** 
已知数组元素为 {1,2,3,4,5,6,7,8,9,10}
打乱数组中的数据，并且打印

```java
int[] arr = {1,2,3,4,5,6,7,8,9,10};
Random r = new Random();
for (int i = 0; i < arr.length - 1; i++) {
    int a = r.nextInt(0, arr.length);
    int b = 0;
    b = arr[a];
    arr[a] = arr[i];
    arr[i] = b;
}
System.out.println(Arrays.toString(arr));
```





**练习4：**
获取10个1-100之间的随机数并存入到数组当中，要求保证数据是唯一的

核心思路:
如果存在，就不存，继续生成下一个随机数:如果不存在，就存入到数组当中

```java
int[] arr = new int[10];
Random r = new Random();
for (int i = 0; i < arr.length; i++) { // 生成随机数
    int n = r.nextInt(0, 101); // 0-100的随机数
    while (true) { // 判断生成的随机数是否重复
        boolean flag = false; // 标记变量
        for (int j = 0; j < i; j++) {
            if (arr[j] == n) {
                flag = true;
                break;
            }
        }
        if (!flag) {
            break;
    }
        n = r.nextInt(0, 101);
    }
    arr[i] = n;
}
System.out.println(Arrays.toString(arr));
```





### 数组的力扣练习题

#### 练习1:两数之和(力扣算法)

给定一个整数数组nums和一个整数目标值target，请你在该数组中找出和为目标值target 的那两个整数，并输出它们的数组索引。

提示:先不用考虑效率问题，两层循环即可完成
要求1:只要输出第一对满足要求的情况
要求2:输出所有满足要求的情况

举例1:
输入:数组nums=[2,7,11,15] target=9
输出:0,1
解释:因为nums[0]+nums[1]==9，所以结果为0和1

```java
int[] nums = {2,7,3,6};
int target = 9;
for (int i = 0; i < nums.length - 1; i++) {
    for (int j = i + 1; j < nums.length; j++) {
        if (target == nums[i] + nums[j]) {
            System.out.println(i + " " + j);
        }
    }
}
```



#### 练习2：合并有序数组

给你两个有序数组arr1和arr2将两个数组中的数据合并到一个大数组中。要求:合并之后的大数组也是有序的

arr1:1 3 5 7 9 
arr2:2 4 6 8 10

```java
int[] arr1 = {1,3,5,7,9};
int[] arr2 = {2,4,6,8,10};
int[] arr3 = new int[arr1.length + arr2.length];
for (int i = 0; i < arr1.length; i++) {
    arr3[i] = arr1[i];
}
for (int i = 0; i < arr2.length; i++) {
    arr3[arr1.length + i] = arr2[i];
}
for (int i = 0; i < arr3.length; i++) {
    for (int j = i + 1; j < arr3.length; j++){
        if (arr3[i] > arr3[j]) {
            int temp = arr3[i];
            arr3[i] = arr3[j];
            arr3[j] = temp;
        }
    }
}
System.out.println(Arrays.toString(arr3));
```



#### 练习3:查找元素(力扣算法)

给定一个递增的有序数组和一个目标值，在数组中找到目标值，打印其索引。如果目标值不存在于数组中，打印应插入的位置举例1:
数据:nums=[1,3,5,6];target=5
输出:2
举例2:
数据:nums=[1,3,5,6],target=2
输出:1

```java
int[] arr = {1, 3, 5, 6};
int target = 5;
boolean flag = false;
for (int i = 0; i < arr.length; i++) {
    if (arr[i] == target) {
        System.out.println(i);
        flag = true;
        break;
    }
    if (arr[i] > target) {
        System.out.println(i);
        flag = true;
        break;
    }
}
if (!flag) {
    System.out.println(arr.length);
}
```

