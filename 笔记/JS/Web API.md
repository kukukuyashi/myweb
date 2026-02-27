# 1 Web API

## 1.1 API作用和分类

api分为 ==DOM== 和 ==BOM== 组成



DOM(Document Object Model--==文档对象模型==)是用来呈现以及与任意 HTML 或 XML文档交互的API

白话文:DOM是浏览器提供的一套专门用来 ==操作网页内容== 的功能



### DOM树

将 HTML 文档以==树状结构==直观的表现出来，我们称之为文档树或 DOM 树



### DOM对象

浏览器根据html标签生成的==JS对象==

​	所有的标签属性都可以在这个对象上面找到

​	修改这个对象的属性会自动映射到标签身上

 



### 小练习：

### 请控制台依次输出 以下 3个li 的 DOM对象



```javascript
<ul class="nav">
  <li>我的</li>
  <li>你的</li>
  <li>大家的</li>
</ul>
```

#### 答案：

```javascript
const lione = document.querySelectorAll('.nav li')
for (let i = 0; i < lione.length; i++) {
  console.log(lione[i])
}
```

### 总结：

1.获取页面中的标签我们最终常用那两种方式?

​	=> queryselectorAll()
​	=> querySelector()



2.他们两者的区别是什么?
	=> querySelector()只能选择一个元素，可以直接操作
	=> querySelectorAll()可以选择多个元素，得到的是伪数组，需要遍历得到每一个元素



3.他们两者小括号里面的参数有什么注意事项?
	=> 里面写css选择器
	=> ==必须是字符串，也就是必须加引号==







## 1.2 DOM修改元素内容

1.元素innerText 属性
	=> 将文本内容添加/更新到任意标签位置
	=> 显示纯文本，不解析标签

```javascript
<body>
  <h1>API1</h1>
  <script>
     const h1 = document.querySelector('h1')
     h1.innerText = '<strong>nihao</strong>'
  </script>
</body>
```



2.元素.innerHTML属性
	=> 将文本内容添加/更新到任意标签位置
	=> 会解析标签，多标签建议使用模板字符

```javascript
<body>
  <h1>API1</h1>
  <h1>API2</h1>
  <script>
     const h1 = document.querySelector('h1')
     const h2 = document.querySelector('h2')
     h1.innerText = '<strong>nihao</strong>'
     h2.innerText = '<strong>nihao</strong>'
  </script>
</body>
```





### 小练习：

从数组随机抽取一等奖、二等奖和三等奖，显示到对应的标签里面

数组名单：["白子", "星野", "野宫", "芹香"]

#### 答案：

```javascript
<body>
  <h1>成绩排名奖项</h1>
  <ul>
    <li><h2>一等奖：<span id="first"></span></h2></li>
    <li><h3>二等奖：<span id="second"></span></h3></li>
    <li><h4>三等奖：<span id="third"></span></h4></li>
    <li><h5>特等奖：<span id="fourth"></span></h5></li>
  </ul>
  <script>
    const arr = ["白子", "星野", "野宫", "芹香"]
    const ul = document.querySelectorAll("ul li span")
    
    for (let i = 0; i < ul.length; i++) {
      const ran = Math.floor(Math.random() * arr.length)
      ul[i].innerHTML = `${arr[ran]}`
      arr.splice(ran, 1)
    }
  </script>
</body>
```









## 1.3 DOM修改元素常见属性

### 常用属性

还可以通过JS设置/修改标签元素属性，比如通过src更换图片
href title src 等

语法：

==对象.属性 = 值==

```html
<body>
  <img src="./img/1 (1).jfif" alt="">
  <script>
    const img = document.querySelector("img")
    img.src = "./img/1 (2).jfif"
  </script>
</body>
```



### 小练习：页面刷新，图片随机更换

需求：当我们刷新页面，页面中的图片随机显示不同的图片

#### 答案:

```html
<body>
  <img src="img/1 (1).jfif" alt="">
  <script>
    function getrandom(N,M){
      return Math.floor(Math.random()*(M - N + 1)+ N)
    }
    const img = document.querySelector("img")
    img.src = `img/1 (${getrandom(1,10)}).jfif`
  </script>
</body>
```







## 1.4 通过style修改样式属性

语法：
==对象.style.样式属性 = “值”==

多组单词的采取 用小驼峰命名法

```html
<style>
  .box {
    width: 200px;
    height: 200px;
    background-color: pink;
  }
</style>
<body>
  <div class="box"></div>
  <script>
    const box = document.querySelector(".box")
    box.style.width = "300px"
    box.style.backgroundColor = "lightblue" // 小驼峰
  </script>
</body>
```



如果是修改body的样式
语法：
==document.body.style.样式属性 = “值”==

```html
<style>
  body {
    background: url(img/1.jfif) no-repeat center;
  }
</style>
<body>
  <script>
    function getRan(N,M) {
      return Math.floor(Math.random()* (M- N +1) + N)
    }
    const random = getRan(1,10);
    document.body.style.background = `url(img/${random}.jfif) no-repeat center`;
  </script>
</body>
```







## 1.5 通过类名修改样式属性

如果修改的样式比较多，直接通过style属性修改比较繁琐，我们可以通过借助于css类名的形式。

语法：

==元素.className = ‘active’==

```html
<style>
  .nav {
    width: 220px;
    height: 220px;
    background-color: pink;
  }
  .box {
    width: 500px;
    height: 500px;
    background-color: yellow;
    position: absolute;
  }
</style>
<body>
  <div>235623</div>
  <script>
    const box = document.querySelector('div')
    box.className = 'nav'
  </script>
</body>
```





## 1.6 通过classList修改样式

通过classList操作类控制CSS

语法：

```javascript
// 追加一个类
元素.classList.add('类名')

// 删除一个类
元素.classList.remove('类名')

// 切换一个类
元素.classList.toggle('类名')
```



```html
<style>
  .nav {
    width: 220px;
    height: 220px;
    background-color: pink;
  }
  .active {
    background-color: yellow;
    margin: 0px auto;
  }
</style>
<body>
  <div class="nav">235623</div>
  <script>
    const box = document.querySelector('div')
    box.classList.add('active')  // div里面有active nav
    box.classList.remove('nav') // div只剩下active
    box.classList.toggle('active') // div什么都没有了 切换类 有就删除 没有就加上
  </script>
</body>
```



### 练习：随机轮播图

需求:当我们刷新页面，页面中的轮播图会显示不同图片以及样式
模块:
1.图片晖随机变换
2.底部盒子背景颜色和文字内容会变换
3.小圆点随机一个高亮显示



```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  /* 设置所有元素的盒模型为border-box，使元素的宽度和高度包括内边距和边框 */
  * {
    box-sizing: border-box; 
  }
  
  /* 定义滑块容器的样式，包括宽度、高度和溢出处理 */
  .slider {
    width: 300px;
    height: 300px;
    overflow: hidden;
  }

  /* 定义滑块图片的样式，使其适应容器且保持宽高比 */
  .slider-wrapper img{
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
  }

  /* 定义滑块底部区域的样式，包括高度、背景颜色、内边距和相对定位 */
  .slider-footer {
    height: 80px ;
    background-color: #c56464;
    padding: 12px 12px 0px 12px;
    position: relative;
  }

  /* 定义控制按钮区域的样式，使其绝对定位在右上角 */
  .slider-footer .toggle {
    position: absolute;
    right: 0;
    top: 12px;
    display: flex;
  }

  /* 定义控制按钮的样式，包括大小、外观、背景颜色、文字颜色、圆角和鼠标样式 */
  .slider-footer .toggle button {
    margin-right: 12px;
    width: 28px;
    height: 28px;
    appearance: none;
    border: none;
    background-color: rgba(255, 255, 255, 0.3);
    color: white;
    border-radius: 5px;
    cursor: pointer;
  }

  /* 定义控制按钮在鼠标悬停时的背景颜色变化 */
  .slider-footer .toggle button:hover {
    background-color: rgba(255, 255, 255, 0.5);
  }

  /* 定义滑块底部文本的样式，包括颜色、字体大小和底部外边距 */
  .slider-footer p {
    margin: 0;
    color: #fff;
    font-size: 16px;
    margin-bottom: 10px;
  }

  /* 定义指示器列表的样式，移除默认样式并使其水平排列 */
  .slider-indicator {
    margin: 0;
    padding: 0;
    list-style: none;
    display: flex;
    align-items: center;
  }

  /* 定义指示器列表项的样式，包括大小、间距、形状、背景颜色、透明度和鼠标样式 */
  .slider-indicator li {
    width: 8px;
    height: 8px;
    margin: 4px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.5);  
    opacity: 0.5; 
    cursor: pointer;
  }

  /* 定义指示器列表项在激活状态时的样式变化，包括大小、透明度和背景颜色 */
  .slider-indicator li.active {
    width: 12px;
    height: 12px;
    opacity: 1; 
    background: #e0e0e0;
  }
</style>
<body>
  <!-- 滑块整体容器 -->
  <div class="slider">
    <!-- 滑块图片展示区域 -->
    <div class="slider-wrapper">
      <img src="img/1.jfif" alt="">
    </div>
    <!-- 滑块底部区域，包含标题和指示器 -->
    <div class="slider-footer">
      <!-- 滑块图片的标题 -->
      <p>阿达达瓦的大卫带</p>
      <!-- 滑块指示器列表 -->
      <ul class="slider-indicator">
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
      </ul>
      <!-- 滑块控制按钮区域 -->
      <div class="toggle">
        <!-- 上一张图片按钮 -->
        <button class="prev">&lt;</button>
        <!-- 下一张图片按钮 -->
        <button class="next">&gt;</button>
      </div>
    </div>
  </div>
  
  <script>
    // 定义图片数据数组，包含图片URL、标题和背景颜色
    const Data =  [
      { url: "img/1.jfif", title: "阿达达瓦的大卫带", color: "rgb(240, 128, 128)" },
      { url: "img/2.jfif", title: "分外附加赛", color: "rgb(135, 206, 250)" },
      { url: "img/3.jfif", title: "动物很费解啊我就", color: "rgb(144, 238, 144)" },
      { url: "img/4.jfif", title: "如图一哦请问你", color: "rgb(255, 182, 193)" },
      { url: "img/5.jfif", title: "挖到了叽歪了", color: "rgb(221, 160, 221)" },
      { url: "img/6.jfif", title: "提取哦i祭扫", color: "rgb(255, 228, 181)" },
      { url: "img/7.jfif", title: "期间地区建设的", color: "rgb(176, 224, 230)" },
      { url: "img/8.jfif", title: "纪念他们单位挖的", color: "rgb(152, 251, 152)" },
    ]

    // 生成一个随机数，用于选择一个随机的图片数据
    const random = parseInt(Math.random() * Data.length)

    // 获取滑块图片展示区域的img元素
    const sliderWrapper = document.querySelector('.slider-wrapper img')
    // 获取滑块底部区域的div元素
    const sliderFooter = document.querySelector('.slider-footer')
    // 获取滑块底部区域的p元素（用于显示图片标题）
    const sliderTitle = document.querySelector('.slider-footer p')

    // 设置滑块底部区域的背景颜色为随机选择的图片数据的颜色
    sliderFooter.style.backgroundColor = Data[random].color
    // 设置滑块底部文本内容为随机选择的图片数据的标题
    sliderTitle.innerHTML = Data[random].title
    // 设置滑块图片展示区域的图片源为随机选择的图片数据的URL
    sliderWrapper.src = Data[random].url

    // 获取滑块指示器的所有li元素
    const Indic = document.querySelectorAll('.slider-indicator li')
    // 将随机选择的指示器列表项标记为激活状态
    Indic[random].classList.toggle('active')
  </script>
</body>
</html>

```





## 1.7 获取设置表单的值

表单很多情况，也需要修改属性，比如点击眼睛，可以看到密码，本质是把表单类型转换为文本框
正常的有属性有取值的 跟其他的标签属性没有任何区别获取:



DOM对象.属性名
设置: DOM对象.属性名=新值

```html
<body>
  <input type="text" value="电脑">
  <script>
    const uname = document.querySelector("input")
    uname.value = "手机"
    console.log(uname.value)
    uname.type = "password"
  </script>
</body>
```





表单属性中添加就有效果,移除就没有效果,一律使用布尔值表示 如果为true 代表添加了该属性 如果是false 代表移除了该属性
比如:disabled、checked、selected

```html
<body>
  <input type="checkbox" name="" id="">
  <button disabled>点击</button>
  <script>
    const checkbox = document.querySelector('input')
    checkbox.checked = true

    const button = document.querySelector('button')
    button.disabled = false
  </script>
</body>
```







## 1.8 自定义属性

==标准属性==: 
标签天生自带的属性 比如class id title等,可以直接使用点语法操作比如: disabled、checked、selected



==自定义属性==：
在html5中推出来了专门的data-自定义属性
在标签上一律以data-开头
在DOM对象上一律以dataset对象方式获取



```html
<body>
  <div class="box" data-idddd="100"></div>
  <script>
    const box = document.querySelector('.box')
    console.log (box.dataset.idddd) // 100
  </script>
</body>
```







## 1.9 定时器-间歇函数

开启定时器 语法：

setInterval(函数，间隔时间)

```javascript
setInterval(function(){
  console.log("Hello, World!")
},1000)


function fn() {
  console.log("nihao")
}
setInterval(fn, 2000)  // fu不用加小括号
```



关闭定时器

```javascript
function fn() {
  console.log("nihao")
}
let n = setInterval(fn, 2000)
clearInterval(n)
```







## 1.10 用户倒计时效果 练习

### 案例：阅读注册协议

需求 按钮5秒之后才可以使用

```html
<body>
  <textarea name="" id="" cols="30" rows="10">dwajdlijwalidj</textarea><br>
  <button class="btn" type="text" disabled>我已经鱼肚(5)秒</button>
  <script>
    const button = document.querySelector('button.btn')
    let i = 5
    let n = setInterval(function(){ 
      i--
      button.innerText = `我已经鱼肚(${i})秒`
      if(i === 0){
        button.innerText = `我已经鱼肚了`
        button.disabled = false
        clearInterval(n)
      }
    }, 1000)
  </script>
</body>
```



## 1.11 综合案例 轮播图定时器版

### 案例 轮播图定时器

需求：每隔一秒钟切换一个图片

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  /* 设置所有元素的盒模型为border-box，使元素的宽度和高度包括内边距和边框 */
  * {
    box-sizing: border-box; 
  }
  
  /* 定义滑块容器的样式，包括宽度、高度和溢出处理 */
  .slider {
    width: 300px;
    height: 300px;
    overflow: hidden;
  }

  /* 定义滑块图片的样式，使其适应容器且保持宽高比 */
  .slider-wrapper img{
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
  }

  /* 定义滑块底部区域的样式，包括高度、背景颜色、内边距和相对定位 */
  .slider-footer {
    height: 80px ;
    background-color: #c56464;
    padding: 12px 12px 0px 12px;
    position: relative;
  }

  /* 定义控制按钮区域的样式，使其绝对定位在右上角 */
  .slider-footer .toggle {
    position: absolute;
    right: 0;
    top: 12px;
    display: flex;
  }

  /* 定义控制按钮的样式，包括大小、外观、背景颜色、文字颜色、圆角和鼠标样式 */
  .slider-footer .toggle button {
    margin-right: 12px;
    width: 28px;
    height: 28px;
    appearance: none;
    border: none;
    background-color: rgba(255, 255, 255, 0.3);
    color: white;
    border-radius: 5px;
    cursor: pointer;
  }

  /* 定义控制按钮在鼠标悬停时的背景颜色变化 */
  .slider-footer .toggle button:hover {
    background-color: rgba(255, 255, 255, 0.5);
  }

  /* 定义滑块底部文本的样式，包括颜色、字体大小和底部外边距 */
  .slider-footer p {
    margin: 0;
    color: #fff;
    font-size: 16px;
    margin-bottom: 10px;
  }

  /* 定义指示器列表的样式，移除默认样式并使其水平排列 */
  .slider-indicator {
    margin: 0;
    padding: 0;
    list-style: none;
    display: flex;
    align-items: center;
  }

  /* 定义指示器列表项的样式，包括大小、间距、形状、背景颜色、透明度和鼠标样式 */
  .slider-indicator li {
    width: 8px;
    height: 8px;
    margin: 4px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.5);  
    opacity: 0.5; 
    cursor: pointer;
  }

  /* 定义指示器列表项在激活状态时的样式变化，包括大小、透明度和背景颜色 */
  .slider-indicator li.active {
    width: 12px;
    height: 12px;
    opacity: 1; 
    background: #e0e0e0;
  }
</style>
<body>
  <!-- 滑块整体容器 -->
  <div class="slider">
    <!-- 滑块图片展示区域 -->
    <div class="slider-wrapper">
      <img src="img/1.jfif" alt="">
    </div>
    <!-- 滑块底部区域，包含标题和指示器 -->
    <div class="slider-footer">
      <!-- 滑块图片的标题 -->
      <p>阿达达瓦的大卫带</p>
      <!-- 滑块指示器列表 -->
      <ul class="slider-indicator">
        <li class="active"></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
      </ul>
      <!-- 滑块控制按钮区域 -->
      <div class="toggle">
        <!-- 上一张图片按钮 -->
        <button class="prev">&lt;</button>
        <!-- 下一张图片按钮 -->
        <button class="next">&gt;</button>
      </div>
    </div>
  </div>
  
  <script>
    // 定义图片数据数组，包含图片URL、标题和背景颜色
    const Data =  [
      { url: "img/1.jfif", title: "阿达达瓦的大卫带", color: "rgb(240, 128, 128)" },
      { url: "img/2.jfif", title: "分外附加赛", color: "rgb(135, 206, 250)" },
      { url: "img/3.jfif", title: "动物很费解啊我就", color: "rgb(144, 238, 144)" },
      { url: "img/4.jfif", title: "如图一哦请问你", color: "rgb(255, 182, 193)" },
      { url: "img/5.jfif", title: "挖到了叽歪了", color: "rgb(221, 160, 221)" },
      { url: "img/6.jfif", title: "提取哦i祭扫", color: "rgb(255, 228, 181)" },
      { url: "img/7.jfif", title: "期间地区建设的", color: "rgb(176, 224, 230)" },
      { url: "img/8.jfif", title: "纪念他们单位挖的", color: "rgb(152, 251, 152)" },
    ]

    // 生成一个随机数，用于选择一个随机的图片数据
    const img = document.querySelector('.slider-wrapper img')
    const title = document.querySelector('.slider-footer p')
    const indicator = document.querySelectorAll('.slider-indicator li')
    const color = document.querySelector('.slider-footer')

    let m = 0
    let i = setInterval(function() {
      m += 1
      if(m === Data.length){
        m = 0
      }
      img.src = Data[m].url
      title.innerHTML = Data[m].title
      color.style.backgroundColor = Data[m].color
      document.querySelector('.slider-indicator li.active').classList.remove('active')
      indicator[m].classList.toggle('active')
    },2000)
  </script>
</body>
</html>

```









#  2 Web API 事件

## 2.1 事件监听（绑定）

### 事件

事件是编程语言中的术语，它是用来描述程序的行为或状态的，**一旦行为或状态发生改变，便立即调用一个函数。**

例如：用户使用【鼠标点击】网页中的一个按钮、用户使用【鼠标拖拽】网页中的一张图片

### 事件监听

结合 DOM 使用事件时，需要为 DOM 对象添加事件监听，等待事件发生（触发）时，便立即调用一个函数。

`addEventListener` 是 DOM 对象专门用来添加事件监听的方法，它的两个参数分别为【事件类型】和【事件回调】。

语法：

```html
<body>
  <button>按钮</button>
  <script>
    const button = document.queryselector('button')
    button.addEventListener('click',function() {
      alert('按钮被点击了')
    })
  </script>
</body>
```



### 网页中广告的写法

```html
<style>
  .box {
    width: 100px;
    height: 100px;
    background-color: rgb(248, 194, 194);
    position: relative;
    text-align: center;
    line-height: 100px;
    margin: 100px auto;
  }
  .box2 {
    width: 20px;
    height: 20px;
    background-color: #a59898;
    top: 0px;
    right: 0px;
    line-height: 20px;
    position: absolute;
    cursor: pointer;
  }
</style>
<body>
  <div class="box">
    广告
    <div class="box2">X</div>
  </div>
  <script>
    const close = document.querySelector('.box2')
    close.addEventListener('click',function(){
      document.querySelector(".box").style.display = "none" 
    })
  </script>
</body>
```









## 2.2 随机点名案例

### 练习：

![](D:\Typora笔记\JS的笔记\Web API img\随机图片.gif)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  .box {
    width: 300px;
    height: 300px;
    background-color: #ffffff;
    margin: 80px auto;
    position: relative;
    border: #c3c3c3 solid 1px;
  }
  .box span {
    display: block;
    text-align: center;
  }
  .box img {
    position: absolute;
    top: 40%;
    left: 50%;
    transform: translate(-50%, -50%);
    position: absolute;
    width: 40%;
  }
  .ks {
    position: absolute;
    top: 80%;
    left: 20%;
    background-color: #c8c8c8;
    border: #545050 solid 0.5px;
    padding: 5px 15px;
    border-radius: 5px;
    cursor: pointer;
  }
  .js { 
    position: absolute;
    top: 80%;
    right: 20%;
    padding: 5px 15px;
    background-color: #c8c8c8;
    border: #545050 solid 0.5px;
    border-radius: 5px;
    cursor: pointer;
  }
</style>
<body>
  <div class="box">
    <span>随机图片</span>
    <img src="img/1.jfif" alt="">
    <div class="ks">开始</div>
    <div class="js">结束</div>
  </div>
  <script>
    const Data =  [
      { url: "img/1.jfif"},
      { url: "img/2.jfif"},
      { url: "img/3.jfif"},
      { url: "img/4.jfif"},
      { url: "img/5.jfif"},
      { url: "img/6.jfif"},
      { url: "img/7.jfif"},
      { url: "img/8.jfif"}
    ]
    const ks = document.querySelector('.ks')
    const js = document.querySelector('.js')
    const img = document.querySelector('div img')
    let time = 0
    let ran = 0
    ks.addEventListener("click",function() {
      
      time = setInterval(function() {
        ran = parseInt(Math.random() * Data.length)
        img.src = Data[ran].url
      }, 100)

      if (Data.length === 1) {
        ks.disabled = js.disabled = true
      }
      
    })
    js.addEventListener("click",function() {
        clearInterval(time)
        Data.splice(ran, 1)
        console.log(ran)
        console.log(Data)
      })
  </script>
</body>
</html>
```

完成事件监听分成3个步骤：

1. 获取 DOM 元素
2. 通过 `addEventListener` 方法为 DOM 节点添加事件监听
3. 等待事件触发，如用户点击了某个按钮时便会触发 `click` 事件类型
4. 事件触发后，相对应的回调函数会被执行

大白话描述：所谓的事件无非就是找个机会（事件触发）调用一个函数（回调函数）。

### 事件类型

`click` 译成中文是【点击】的意思，它的含义是监听（等着）用户鼠标的单击操作，除了【单击】还有【双击】`dblclick`

```html
<script>
  // 双击事件类型
  btn.addEventListener('dblclick', function () {
    console.log('等待事件被触发...');
    // 改变 p 标签的文字颜色
    const text = document.querySelector('.text')
    text.style.color = 'red'
  })

  // 只要用户双击击了按钮，事件便触发了！！！
</script>
```

结论：【事件类型】决定了事件被触发的方式，如 `click` 代表鼠标单击，`dblclick` 代表鼠标双击。





### 鼠标经过，鼠标离开 事件

语法如下：

```html
<style>
  .box {
    width: 200px;
    height: 200px;
    background-color: pink;
  }
</style>
<body>
  <div class="box"></div>
  <script>
    const box = document.querySelector('.box');
    box.addEventListener('mouseleave',function() {
      console.log('鼠标离开了盒子')
    })
    box.addEventListener('mouseenter',function() {
      console.log('鼠标进入了盒子')
    })
  </script>
</body>
```





### 案例 轮播图点击切换

需求:当点击左右的按钮，可以切换轮播图
如下：

![](D:\Typora笔记\JS的笔记\Web API img\轮播图完整版.gif)

分析:
①:右侧按钮点击，变量++，如果大于等于8，则复原0左侧按钮点击，变量--，如果小于0，则复原最后一张
鼠标经过暂停定时器
鼠标离开开启定时器

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  /* 设置所有元素的盒模型为border-box，使元素的宽度和高度包括内边距和边框 */
  * {
    box-sizing: border-box; 
  }
  
  /* 定义滑块容器的样式，包括宽度、高度和溢出处理 */
  .slider {
    width: 300px;
    height: 300px;
    overflow: hidden;
  }

  /* 定义滑块图片的样式，使其适应容器且保持宽高比 */
  .slider-wrapper img{
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
  }

  /* 定义滑块底部区域的样式，包括高度、背景颜色、内边距和相对定位 */
  .slider-footer {
    height: 80px ;
    background-color: #c56464;
    padding: 12px 12px 0px 12px;
    position: relative;
  }

  /* 定义控制按钮区域的样式，使其绝对定位在右上角 */
  .slider-footer .toggle {
    position: absolute;
    right: 0;
    top: 12px;
    display: flex;
  }

  /* 定义控制按钮的样式，包括大小、外观、背景颜色、文字颜色、圆角和鼠标样式 */
  .slider-footer .toggle button {
    margin-right: 12px;
    width: 28px;
    height: 28px;
    appearance: none;
    border: none;
    background-color: rgba(255, 255, 255, 0.3);
    color: white;
    border-radius: 5px;
    cursor: pointer;
  }

  /* 定义控制按钮在鼠标悬停时的背景颜色变化 */
  .slider-footer .toggle button:hover {
    background-color: rgba(255, 255, 255, 0.5);
  }

  /* 定义滑块底部文本的样式，包括颜色、字体大小和底部外边距 */
  .slider-footer p {
    margin: 0;
    color: #fff;
    font-size: 16px;
    margin-bottom: 10px;
  }

  /* 定义指示器列表的样式，移除默认样式并使其水平排列 */
  .slider-indicator {
    margin: 0;
    padding: 0;
    list-style: none;
    display: flex;
    align-items: center;
  }

  /* 定义指示器列表项的样式，包括大小、间距、形状、背景颜色、透明度和鼠标样式 */
  .slider-indicator li {
    width: 8px;
    height: 8px;
    margin: 4px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.5);  
    opacity: 0.5; 
    cursor: pointer;
  }

  /* 定义指示器列表项在激活状态时的样式变化，包括大小、透明度和背景颜色 */
  .slider-indicator li.active {
    width: 12px;
    height: 12px;
    opacity: 1; 
    background: #e0e0e0;
  }
</style>
<body>
  <!-- 滑块整体容器 -->
  <div class="slider">
    <!-- 滑块图片展示区域 -->
    <div class="slider-wrapper">
      <img src="img/1.jfif" alt="">
    </div>
    <!-- 滑块底部区域，包含标题和指示器 -->
    <div class="slider-footer">
      <!-- 滑块图片的标题 -->
      <p>阿达达瓦的大卫带</p>
      <!-- 滑块指示器列表 -->
      <ul class="slider-indicator">
        <li class="active"></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
      </ul>
      <!-- 滑块控制按钮区域 -->
      <div class="toggle">
        <!-- 上一张图片按钮 -->
        <button class="prev">&lt;</button>
        <!-- 下一张图片按钮 -->
        <button class="next">&gt;</button>
      </div>
    </div>
  </div>
  
  <script>
    // 定义图片数据数组，包含图片URL、标题和背景颜色
    const Data =  [
      { url: "img/1.jfif", title: "阿达达瓦的大卫带", color: "rgb(240, 128, 128)" },
      { url: "img/2.jfif", title: "分外附加赛", color: "rgb(135, 206, 250)" },
      { url: "img/3.jfif", title: "动物很费解啊我就", color: "rgb(144, 238, 144)" },
      { url: "img/4.jfif", title: "如图一哦请问你", color: "rgb(255, 182, 193)" },
      { url: "img/5.jfif", title: "挖到了叽歪了", color: "rgb(221, 160, 221)" },
      { url: "img/6.jfif", title: "提取哦i祭扫", color: "rgb(255, 228, 181)" },
      { url: "img/7.jfif", title: "期间地区建设的", color: "rgb(176, 224, 230)" },
      { url: "img/8.jfif", title: "纪念他们单位挖的", color: "rgb(152, 251, 152)" },
    ]

    // 生成一个随机数，用于选择一个随机的图片数据
    const slider = document.querySelector('.slider')
    const img = document.querySelector('.slider-wrapper img')
    const title = document.querySelector('.slider-footer p')
    const indicator = document.querySelectorAll('.slider-indicator li')
    const color = document.querySelector('.slider-footer')
    const prev = document.querySelector('.prev')
    const next = document.querySelector('.next')

    function getranyuan( ) {
      document.querySelector('.slider-indicator li.active').classList.remove('active')
      indicator[m].classList.toggle('active')
      img.src = Data[m].url
      title.innerHTML = Data[m].title
      color.style.backgroundColor = Data[m].color
    }

    let m = 0
    let i = 0
    prev.addEventListener('click', function() {
      m -= 1
      if(m < 0){
        m = Data.length - 1
      }
      getranyuan()
      
    })
    next.addEventListener('click',function() {
      m += 1
      if(m === Data.length) {
        m = 0
      }
      getranyuan()
    })

    function getks () {
      i = setInterval(function() {
        m += 1
        if(m === Data.length){
          m = 0
        }
        getranyuan()
      },1000)
    }
    getks()
    slider.addEventListener('mouseenter',function() {
      clearInterval(i)
      console.log('鼠标进入了盒子')
      
    }) 
    slider.addEventListener('mouseleave',function() {
      getks()
      console.log('鼠标离开了盒子')
    })
  </script>
</body>
</html>

```







## 2.3 焦点事件

### 焦点事件

focus  获得焦点

blur 失去焦点

```html
<body>
  <input type="text">
  <script>
    const input = document.querySelector ('input')
    input.addEventListener ('focus', function () {
      console.log("有焦点触发")
    })
    input.addEventListener ('blur', function () {
      console.log("失焦点触发")
    })
  </script>
</body>
```





### 案例：小米搜索框

小米搜索框案例
需求:当表单得到焦点，显示下拉菜单，失去焦点隐藏下来菜单



```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  ul {
    list-style: none;
  }
  .mi {
    width: 230px;
    margin: 100px auto;
  }

  .mi input {
    width: 230px;
    height: 40px;
    padding: 0 10px;
    border: 1px solid rgb(18, 18, 18);
  }
  .result-list {
    position: absolute;
    display: block;
    padding: 6px 15px;
    color: rgb(234, 245, 255);

    outline: none;
    border-top: 0px;
    background: #ffffff;
    display: none;
  }
  .result-list a {
    display: block;
    padding: 6px 15px;
    font-size: 12px;
    text-decoration: none;
    color: #424242;
    cursor: pointer;
  }
  .result-list a:hover { 
    background-color: rgb(250, 177, 138);
  }

  .active {
    position: relative;
    border: 1px solid rgb(250, 177, 138);
  }
  input:focus {
    outline:none;
  }

</style>
<body>
  <div class="mi">
    <input type="search" class="input" placeholder="小米笔记本">
    <ul class="result-list">
      <li><a href="#">全部商品</a></li>
      <li><a href="#">小米11</a></li>
      <li><a href="#">小米11 Pro</a></li>
      <li><a href="#">小米11 Ultra</a></li>
      <li><a href="#">小米11 Pro Max</a></li>
      <li><a href="#">小米11 Ultra Max</a></li>
      <li><a href="#">小米11 SE</a></li>
    </ul>
  </div>
  <script>
    const input = document.querySelector("[type='search']")
    const caidan = document.querySelector(".result-list")
    
    input.addEventListener("focus",function(){
      caidan.style.display = "block"
      input.style.border = "1px solid rgb(250, 177, 138)"
      caidan.classList.add("active")     
      
    })

    input.addEventListener("blur",function(){
      input.style.border = "1px solid #484747"
      caidan.classList.remove("active")
      caidan.style.display = "none"
    })
    
    
  </script>
</body>
</html>
```

[^浏览器默认焦点样式覆盖]: 浏览器（如 Chrome）为 &lt;input&gt; 的 :focus 状态默认添加了 outline（轮廓线）和边框颜色，若未覆盖这些样式，自定义边框颜色会被遮盖 ==看完 一定要重视==





## 2.4 键盘事件

keydown   键盘按下触发
keyup   键盘抬起触发

```html
<body>
  <input type="text">
  <script>
    const input = document.querySelector ('input')
    input.addEventListener ('keydown', function () {
      console.log("键盘按下了")
    })
    input.addEventListener ('keyup', function () {
      console.log("键盘松开了")
    })
  </script>
</body>
```

### 文本框输入事件

input  用户输入什么就能检测到什么

```html
<body>
  <input type="text">
  <script>
    const input = document.querySelector('input')
    input.addEventListener('input',function() {
      console.log(input.value);
    })
  </script>
</body>
```





### 案例：评论字数统计

需求：用户输入文字，可以计算用户输入的字数

1：判断用输入事件input
2：不断取得文本框里面的字符长度，文本域.value.length
3：把获得数字给下面文本框



```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  .box{
    position: relative;
    width: 240px;
  }
  .box input{ 
    border-radius: 3px;
    height: 50px;
    border: 1px solid #c9c9c9;
    outline: none;
    font-size: 12px;
  }
  .Anniu{
    width: 50px;
    height: 54px;
    background-color: #7ec3f8;
    color:rgb(239, 255, 254);
    border: 1px solid #7ec3f8;
    font-size: 12px;
    border-radius: 3px;
  }
  span {
    position: absolute;
    font-size: 11px;
    color: #959595;
    right: 73px;
    bottom: -14px;
  }
</style>
<body>
  <div class="box">
    <input type="text" placeholder="发布一条新动态">
    <button class="Anniu">发布</button>
    <span></span>
    
  </div>
  <script>
    const input = document.querySelector('input')
    const button = document.querySelector('.Anniu')
    const zi = document.querySelector('span')
    input.addEventListener('input', function() {
      zi.innerHTML = input.value.length + '/200字'
    })
    
    input.addEventListener('focus', function() {
      zi.style.opacity = 1
    })
    
    input.addEventListener('blur', function() {
      if (input.value.length === 0) {
        zi.style.opacity = 0
      }
    })
  </script>
</body>
</html>
```





## 2.5 事件对象

任意事件类型被触发时与事件相关的信息会被以对象的形式记录下来，我们称这个对象为事件对象。

```html
<body>
  <h3>事件对象</h3>
  <p>任意事件类型被触发时与事件相关的信息会被以对象的形式记录下来，我们称这个对象为事件对象。</p>
  <hr>
  <div class="box"></div>
  <script>
    // 获取 .box 元素
    const box = document.querySelector('.box')

    // 添加事件监听
    box.addEventListener('click', function (e) {
      console.log('任意事件类型被触发后，相关信息会以对象形式被记录下来...');

      // 事件回调函数的第1个参数即所谓的事件对象
      console.log(e)
    })
  </script>
</body>
```

事件回调函数的【第1个参数】即所谓的事件对象，通常习惯性的将这个对数命名为 `event`、`evt` 、`e` 

```html
<body>
  <input type="text">
  <script>
    const input = document.querySelector('input')
    input.addEventListener('keyup', function(e) {
      if (e.key === 'Enter') {
        console.log('按下了回车键')
      }
    })
  </script>
</body>
```

接下来简单看一下事件对象中包含了哪些有用的信息：

1. `e.type` 当前事件的类型
2. `e.clientX/Y` 光标相对浏览器窗口的位置
3. `e.offsetX/Y` 光标相于当前 DOM 元素的位置

注：在事件回调函数内部通过 window.event 同样可以获取事件对象。



### 练习：评论回车发布（可以发布信息）

需求：按下回车键盘，可以发布信息
分析：
1：用到按下键盘事件 keydown 或者keyup 都可以
2：如果用户按下的是回车键盘，则发布信息
3：让留言信息模块显示，把拿到的数据渲染到对应标签内部



```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>评论回车发布</title>
  <style>
    .wrapper {
      min-width: 400px;
      max-width: 800px;
      display: flex;
      justify-content: flex-end;
    }

    .avatar {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      overflow: hidden;
      background: url(img/1.jfif) no-repeat center / cover;
      margin-right: 20px;
    }

    .wrapper textarea {
      outline: none;
      border-color: transparent;
      resize: none;
      background: #f5f5f5;
      border-radius: 4px;
      flex: 1;
      padding: 10px;
      transition: all 0.5s;
      height: 30px;
    }

    .wrapper textarea:focus {
      border-color: #e4e4e4;
      background: #fff;
      height: 50px;
    }

    .wrapper button {
      background: #00aeec;
      color: #fff;
      border: none;
      border-radius: 4px;
      margin-left: 10px;
      width: 70px;
      cursor: pointer;
    }

    .wrapper .total {
      margin-right: 80px;
      color: #999;
      margin-top: 5px;
      opacity: 0;
      transition: all 0.5s;
    }

    .list {
      min-width: 400px;
      max-width: 800px;
      display: flex;
    }

    .list .item {
      width: 100%;
      display: flex;
    }

    .list .item .info {
      flex: 1;
      border-bottom: 1px dashed #e4e4e4;
      padding-bottom: 10px;
    }

    .list .item p {
      margin: 0;
    }

    .list .item .name {
      color: #FB7299;
      font-size: 14px;
      font-weight: bold;
    }

    .list .item .text {
      color: #333;
      padding: 10px 0;
    }

    .list .item .time {
      color: #999;
      font-size: 12px;
    }
  </style>
</head>

<body>
  <div class="wrapper">
    <i class="avatar"></i>
    <textarea id="tx" placeholder="发一条友善的评论" rows="2" maxlength="200"></textarea>
    <button>发布</button>
  </div>
  <div class="wrapper">
    <span class="total">0/200字</span>
  </div>
  <div class="list">
    <div class="item" style="display: none;">
      <i class="avatar"></i>
      <div class="info">
        <p class="name">开开心心</p>
        <p class="text"></p>
        <p class="time">2022-10-10 20:29:21</p>
      </div>
    </div>
  </div>

</body>
  <script>
    const input = document.querySelector('#tx')
    const total = document.querySelector('.total')
    const p = document.querySelector('.info p.text')
    const item = document.querySelector('.item')
    input.addEventListener('input',function(){
      total.innerHTML = `${input.value.length +'/ 200字'}`
    })
    
    input.addEventListener('keyup', function(e) {
      console.log(e.key)
      console.log(input.value)
      if (e.key ==='Enter') {
        if (input.value.trim() !== "" ) {
          item.style.display = 'block'
          p.innerHTML = input.value
        }
        input.value = ''
        total.innerHTML = `0/200字`
      }
      
    })
    input.addEventListener('focus', function() {
      total.style.opacity = 1
    })

    input.addEventListener('blur', function() {
      total.style.opacity = 0
    })
  </script>
</html>
```







## 2.6 环境对象

> 能够分析判断函数运行在不同环境中 this 所指代的对象。

环境对象指的是函数内部特殊的变量 `this` ，它代表着当前函数运行时所处的环境。

```html
<script>
  // 声明函数
  function sayHi() {
    // this 是一个变量
    console.log(this);
  }

  // 声明一个对象
  let user = {
    name: '张三',
    sayHi: sayHi // 此处把 sayHi 函数，赋值给 sayHi 属性
  }
  
  let person = {
    name: '李四',
    sayHi: sayHi
  }

  // 直接调用
  sayHi() // window
  window.sayHi() // window

  // 做为对象方法调用
  user.sayHi()// user
	person.sayHi()// person
</script>
```

结论：

1. `this` 本质上是一个变量，数据类型为对象
2. 函数的调用方式不同 `this` 变量的值也不同
3. 【谁调用 `this` 就是谁】是判断 `this` 值的粗略规则
4. 函数直接调用时实际上 `window.sayHi()` 所以 `this` 的值为 `window`



## 2.7 综合案例 TAB切换

需求：鼠标经过不同的选项卡，底部可以显示 不同的内容



```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>tab栏切换</title>
  <style>
    * {
      margin: 0;
      padding: 0;
    }

    .tab {
      width: 590px;
      height: 340px;
      margin: 20px;
      border: 1px solid #e4e4e4;
    }

    .tab-nav {
      width: 100%;
      height: 60px;
      line-height: 60px;
      display: flex;
      justify-content: space-between;
    }

    .tab-nav h3 {
      font-size: 24px;
      font-weight: normal;
      margin-left: 20px;
    }

    .tab-nav ul {
      list-style: none;
      display: flex;
      justify-content: flex-end;
    }

    .tab-nav ul li {
      margin: 0 20px;
      font-size: 14px;
    }

    .tab-nav ul li a {
      text-decoration: none;
      border-bottom: 2px solid transparent;
      color: #333;
    }

    .tab-nav ul li a.active {
      border-color: #e1251b;
      color: #e1251b;
    }

    .tab-content {
      padding: 0 16px;
    }

    .tab-content .item {
      display: none;
    }

    .tab-content .item.active {
      display: block; 
    }

    .tab-content img {
      width: 240px;
      height: 270px;
    }
  </style>
</head>

<body>
  <div class="tab">
    <div class="tab-nav">
      <h3>每日特价</h3>
      <ul>
        <li><a class="active" href="javascript:;">精选</a></li>
        <li><a href="javascript:;">美食</a></li>
        <li><a href="javascript:;">百货</a></li>
        <li><a href="javascript:;">个护</a></li>
        <li><a href="javascript:;">预告</a></li>
      </ul>
    </div>
    <div class="tab-content">
      <div class="item active"><img src="img/1.jfif" alt="" /></div>
      <div class="item"><img src="img/2.jfif" alt="" /></div>
      <div class="item"><img src="img/3.jfif" alt="" /></div>
      <div class="item"><img src="img/4.jfif" alt="" /></div>
      <div class="item"><img src="img/5.jfif" alt="" /></div>
    </div>
  </div>
  <script>
    const as = document.querySelectorAll('.tab-nav a')
    const tab = document.querySelector('.tab-nav')
    const item = document.querySelectorAll('.tab-content .item')
    
    for (let i = 0; i < as.length; i++) { 
      as[i].addEventListener('mouseover' ,function() {
        document.querySelector('.tab-nav a.active').classList.remove('active')
        document.querySelector('.tab-content .active').classList.remove('active')
        document.querySelector(`.tab-content .item:nth-child(${i+1})`).classList.add('active')
        as[i].classList.add('active') 
      })
    }
  </script>
</body>

</html>
```







# 3 Wed API 事件案例

## 3.1 表单全选反选

需求:用户点击全选，则下面复选框全部选择，取消全选则全部取消
分析:
1：全选复选框点击，可以得到当前按钮的 checked
2:把下面所有的小复选框状态checked，改为和全选复选框一致

![](D:\Typora笔记\JS的笔记\Web API img\表单全选反选.gif)

```HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  table { 
    width: 500px;
    height: 300px;
    border: 1px solid #373737;
  }
  .allCheck { 
    text-align: left;
  }

  td:first-child {
    
    width: 80px;
  }
  td {
    border: 1px solid #373737;
    color: rgb(33, 33, 33);
    text-align: center
  }
  th {
    background-color: #9a9a9a;
    border: 1px solid #373737;
  }
</style>
<body>
  <table>
    <tr>
      <th class="allCheck">
        <input type="checkbox" name="" id="allCheck"> <span class="all">全选</span>
      </th>
      <th>商品</th>
      <th>商家</th>
      <th>价格</th>
    </tr>
    <tr>
      <td>
        <input type="checkbox" name="check" class="ck">
      </td>
      <td>小米手机</td>
      <td>小米</td>
      <td>￥1999</td>
    </tr>
    <tr>
      <td>
        <input type="checkbox" name="check" class="ck" >
      </td>
      <td>小米电视</td>
      <td>小米</td>
      <td>￥2999</td>
    </tr>
    <tr>
      <td>
        <input type="checkbox" name="check" class="ck">
      </td>
      <td>小米净水器</td>
      <td>小米</td>
      <td>￥4999</td>
    </tr>
  </table>
  <script>
    const allCheck = document.querySelector('#allCheck');
    const ck = document.querySelectorAll('.ck')

    allCheck.addEventListener('click', function() {
      if (this.checked === true) {
        for (let i = 0; i < ck.length; i++) {
          ck[i].checked = true
        }
      }
      if (this.checked === false) {
        for (let i = 0; i < ck.length; i++) {
          ck[i].checked = false
        }
      }

    })

    for (let i = 0; i < ck.length; i++) {
      ck[i].addEventListener('click', function() {
        if (document.querySelectorAll(".ck:checked").length ===  ck.length) {
          allCheck.checked = true
        }
        else {
          allCheck.checked = false
        }
      })
    }
      

  </script>
</body>
</html>
```





## 3.2 事件流

事件流是对事件执行过程的描述，了解事件的执行过程有助于加深对事件的理解，提升开发实践中对事件运用的灵活度。

![](D:\Typora笔记\JS的笔记\Web API img\事件流.png)

如上图所示，任意事件被触发时总会经历两个阶段：【捕获阶段】和【冒泡阶段】。

简言之，捕获阶段是【从父到子】的传导过程，冒泡阶段是【从子向父】的传导过程。

### 



### 捕获和冒泡

了解了什么是事件流之后，我们来看事件流是如何影响事件执行的：

```html
<body>
  <h3>事件流</h3>
  <p>事件流是事件在执行时的底层机制，主要体现在父子盒子之间事件的执行上。</p>
  <div class="outer">
    <div class="inner">
      <div class="child"></div>
    </div>
  </div>
  <script>
    // 获取嵌套的3个节点
    const outer = document.querySelector('.outer');
    const inner = document.querySelector('.inner');
    const child = document.querySelector('.child');
		
    // html 元素添加事件
    document.documentElement.addEventListener('click', function () {
      console.log('html...')
    })
		
    // body 元素添加事件
    document.body.addEventListener('click', function () {
      console.log('body...')
    })

    // 外层的盒子添加事件
    outer.addEventListener('click', function () {
      console.log('outer...')
    })
    
    // 中间的盒子添加事件
    outer.addEventListener('click', function () {
      console.log('inner...')
    })
    
    // 内层的盒子添加事件
    outer.addEventListener('click', function () {
      console.log('child...')
    })
  </script>
</body>
```

执行上述代码后发现，当单击事件触发时，其祖先元素的单击事件也【相继触发】，这是为什么呢？

结合事件流的特征，我们知道当某个元素的事件被触发时，事件总是会先经过其祖先才能到达当前元素，然后再由当前元素向祖先传递，事件在流动的过程中遇到相同的事件便会被触发。

再来关注一个细节就是事件相继触发的【执行顺序】，事件的执行顺序是可控制的，即可以在捕获阶段被执行，也可以在冒泡阶段被执行。

如果事件是在冒泡阶段执行的，我们称为冒泡模式，它会先执行子盒子事件再去执行父盒子事件，默认是冒泡模式。

如果事件是在捕获阶段执行的，我们称为捕获模式，它会先执行父盒子事件再去执行子盒子事件。

```html
<body>
  <h3>事件流</h3>
  <p>事件流是事件在执行时的底层机制，主要体现在父子盒子之间事件的执行上。</p>
  <div class="outer">
    <div class="inner"></div>
  </div>
  <script>
    // 获取嵌套的3个节点
    const outer = document.querySelector('.outer')
    const inner = document.querySelector('.inner')

    // 外层的盒子
    outer.addEventListener('click', function () {
      console.log('outer...')
    }, true) // true 表示在捕获阶段执行事件
    
    // 中间的盒子
    outer.addEventListener('click', function () {
      console.log('inner...')
    }, true)
  </script>
</body>
```

结论：

1. `addEventListener` 第3个参数决定了事件是在捕获阶段触发还是在冒泡阶段触发
2. `addEventListener` 第3个参数为  `true` 表示捕获阶段触发，`false` 表示冒泡阶段触发，默认值为 `false`
3. 事件流只会在父子元素具有相同事件类型时才会产生影响
4. 绝大部分场景都采用默认的冒泡模式（其中一个原因是早期 IE 不支持捕获）



### 阻止冒泡

阻止冒泡是指阻断事件的流动，保证事件只在当前元素被执行，而不再去影响到其对应的祖先元素。

```html
<body>
  <h3>阻止冒泡</h3>
  <p>阻止冒泡是指阻断事件的流动，保证事件只在当前元素被执行，而不再去影响到其对应的祖先元素。</p>
  <div class="outer">
    <div class="inner">
      <div class="child"></div>
    </div>
  </div>
  <script>
    // 获取嵌套的3个节点
    const outer = document.querySelector('.outer')
    const inner = document.querySelector('.inner')
    const child = document.querySelector('.child')

    // 外层的盒子
    outer.addEventListener('click', function () {
      console.log('outer...')
    })

    // 中间的盒子
    inner.addEventListener('click', function (e) {
      console.log('inner...')

      // 阻止事件冒泡
      e.stopPropagation()
    })

    // 内层的盒子
    child.addEventListener('click', function (e) {
      console.log('child...')

      // 借助事件对象，阻止事件向上冒泡
      e.stopPropagation()
    })
  </script>
</body>
```

结论：事件对象中的 `e.stopPropagation` 方法，专门用来阻止事件冒泡。

> 鼠标经过事件：
>
> mouseover 和 mouseout 会有冒泡效果
>
> mouseenter  和 mouseleave   没有冒泡效果 (推荐)





## 3.3 事件解绑

语法:removeEventListener(事件类型,事件处理函数，[获取捕获或者冒泡阶段])

```html
<body>
  <button>按钮</button>
  <script>
    const button = document.querySelector('button')
    function fn() {
      console.log('按钮被点击了')
    }
    button.addEventListener('click', fn)
    // button.removeEventListener('click', fn)
  </script>
</body>
```



### 两种注册事件的区别

![](D:\Typora笔记\JS的笔记\Web API img\两种注册事件的区别.png)







## 3.4 事件委托

事件委托是利用事件流的特征解决一些现实开发需求的知识技巧，主要的作用是提升程序效率。

大量的事件监听是比较耗费性能的，如下代码所示

```html
<script>
  // 假设页面中有 10000 个 button 元素
  const buttons = document.querySelectorAll('table button');

  for(let i = 0; i <= buttons.length; i++) {
    // 为 10000 个 button 元素添加了事件
    buttons.addEventListener('click', function () {
      // 省略具体执行逻辑...
    })
  }
</script>
```

利用事件流的特征，可以对上述的代码进行优化，事件的的冒泡模式总是会将事件流向其父元素的，如果父元素监听了相同的事件类型，那么父元素的事件就会被触发并执行，正是利用这一特征对上述代码进行优化，如下代码所示：

```html
<script>
  // 假设页面中有 10000 个 button 元素
  let buttons = document.querySelectorAll('table button');
  
  // 假设上述的 10000 个 buttom 元素共同的祖先元素是 table
  let parents = document.querySelector('table');
  parents.addEventListener('click', function () {
    console.log('点击任意子元素都会触发事件...');
  })
</script>
```



```html
<body>
  <ul>
    <li>1</li>
    <li>2</li>
    <li>3</li>
    <li>4</li>
    <p>p</p>
  </ul>
  <script>
    const ul = document.querySelector('ul')
    ul.addEventListener('click', function(e) {
      if (e.target.tagName === 'LI') {
        e.target.style.color = 'blue'
      }
    })
  </script>
</body>
```





## 3.5 事件委托版tab切换

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>tab栏切换</title>
  <style>
    * {
      margin: 0;
      padding: 0;
    }

    .tab {
      width: 590px;
      height: 340px;
      margin: 20px;
      border: 1px solid #e4e4e4;
    }

    .tab-nav {
      width: 100%;
      height: 60px;
      line-height: 60px;
      display: flex;
      justify-content: space-between;
    }

    .tab-nav h3 {
      font-size: 24px;
      font-weight: normal;
      margin-left: 20px;
    }

    .tab-nav ul {
      list-style: none;
      display: flex;
      justify-content: flex-end;
    }

    .tab-nav ul li {
      margin: 0 20px;
      font-size: 14px;
    }

    .tab-nav ul li a {
      text-decoration: none;
      border-bottom: 2px solid transparent;
      color: #333;
    }

    .tab-nav ul li a.active {
      border-color: #e1251b;
      color: #e1251b;
    }

    .tab-content {
      padding: 0 16px;
    }

    .tab-content .item {
      display: none;
    }

    .tab-content .item.active {
      display: block; 
    }

    .tab-content img {
      width: 240px;
      height: 270px;
    }
  </style>
</head>

<body>
  <div class="tab">
    <div class="tab-nav">
      <h3>每日特价</h3>
      <ul>
        <li><a class="active" href="javascript:;" data-id="0">精选</a></li>
        <li><a href="javascript:;" data-id="1">美食</a></li>
        <li><a href="javascript:;" data-id="2">百货</a></li>
        <li><a href="javascript:;" data-id="3">个护</a></li>
        <li><a href="javascript:;" data-id="4">预告</a></li>
      </ul>
    </div>
    <div class="tab-content">
      <div class="item active"><img src="img/1.jfif" alt="" /></div>
      <div class="item"><img src="img/2.jfif" alt="" /></div>
      <div class="item"><img src="img/3.jfif" alt="" /></div>
      <div class="item"><img src="img/4.jfif" alt="" /></div>
      <div class="item"><img src="img/5.jfif" alt="" /></div>
    </div>
  </div>
  <script>
    const ul = document.querySelector('.tab-nav ul')
    
    ul.addEventListener('click', function(e) {
      if (e.target.tagName === 'A') {
        
        document.querySelector(".tab-nav .active").classList.remove('active')
        e.target.classList.add('active')
        const i = +e.target.dataset.id
        document.querySelector(".tab-content .active").classList.remove('active')
        document.querySelector(`.tab-content .item:nth-child(${i+1})`).classList.add('active')
      }
      
    })
  </script>
</body>

</html>
```







## 3.6 阻止元素默认行为

在网站中的注册，就需要阻止元素的默认行为

```html
<body>
  <form action="https://www.bilibili.com/">
    <input type="submit" vlaue="提交">
  </form>
  <script>
    const form = document.querySelector('form')
    form.addEventListener('submit', function(e) {
      e.preventDefault()
    })
    
  </script>
</body>
```





## 3.7 页面加载事件

加载外部资源（如图片、外联CSS和JavaScript等）加载完毕时触发的事件

有些时候需要等页面资源全部处理完了做一些事情

**事件名：load**

监听页面所有资源加载完毕：

~~~javascript
window.addEventListener('load', function() {
    // xxxxx
})
~~~







## 3.8 元素滚动事件

很多网页需要检测用户把页面滚动到某个区域后做一些处理，比如固定导航栏，比如返回顶部

**事件名：scroll**

```javascript
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  body{
    height: 3000px;
  }
  div {
    margin: 200px;
    height: 200px;
    width: 200px;
    border: 1px solid #000;
    overflow: scroll;
  }
</style>
<body>
  <div>
    dwaldlwadjlwajdlwajddawd
    dwladjlawjddawdwadawda  
    dddddddddddddddwwwddwd
    dlawjdliaw
  </div>
  <script>
    const div = document.querySelector("div")
    window.addEventListener("scroll",function(){
      let i = document.documentElement.scrollTop
      if (i >= 100) {
        div.style.display = "block"
      } else {
        div.style.display = "none"
      }
      console.log(Math.floor(i))
    })
  </script>
</body>
</html>
```

开发中，我们经常检测页面滚动的距离，比如页面滚动100像素，就可以显示一个元素，或者固定一个元素







## 3.9 页面尺寸事件

获取宽高:
获取元素的可见部分宽高(不包含边框，margin，滚动条等)

![](D:\Typora笔记\JS的笔记\Web API img\页面尺寸.png)

offsetTop 是一个只读属性，返回当前元素相对于 offsetParent 节点顶部边界的偏移像素值

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<style>
  body {
    height: 3000px;
  }
  div {
    margin: 200px;
    height: 200px;
    width: 200px;
    
    background-color: pink;
    
  }
  .ll {
    padding: 30px;
    width: 50px;
    height: 20px;
    background-color: #0000ff;
    opacity: 0;
  }
  .nn {
    width: 200px;
    height: 200px;
    background-color: #599c5b;
    opacity: 0;
  }
</style>
<body>
  <div></div>
  <div class="ll"></div>
  <div class="nn"></div>
  <script>
    const div = document.querySelector('div')
    const ll = document.querySelector('.ll')
    const nn = document.querySelector('.nn')
    window.addEventListener('scroll',function(){
      const n = document.documentElement.scrollTop
      ll.style.opacity = n >= div.offsetTop ? 1 : 0
      nn.style.opacity = n >= ll.offsetHeight ? 1 : 0
      console.log(n+'A')
      console.log(div.offsetTop+'B')
      console.log(ll.offsetHeight+'C')
    })
  </script>
</body>
</html>
```

> 1.offsetWidth和offsetHeight是得到元素什么的宽高?
> 内容 + padding + border
>
> 2.offsetTop和offsetLeft 得到位置以谁为准?
> .带有定位的父级
> .如果都没有则以 文档左上角 为准











# 4 Wed API 节点

## 4.1 日期对象

掌握 Date 日期对象的使用，动态获取当前计算机的时间。


ECMAScript 中内置了获取系统时间的对象 Date，使用 Date 时与之前学习的内置对象 console 和 Math 不同，它需要借助 new 关键字才能使用。



### 实例化

```javascript
  // 1. 实例化
  // const date = new Date(); // 系统默认时间
  const date = new Date('2020-05-01') // 指定时间
  // date 变量即所谓的时间对象

  console.log(typeof date)

```



### 方法

```javascript
<script>
  const time = new Date("2002-08-08 12:00:00")
  console.log(time)
</script>
```

```javascript
  // 1. 实例化
 const date = new Date();
 // 2. 调用时间对象方法
 // 通过方法分别获取年、月、日，时、分、秒
 const year = date.getFullYear(); // 四位年份
 const month = date.getMonth(); // 0 ~ 11
```

1. getFullYear 获取四位年份
2. getMonth 获取月份，取值为 0 ~ 11

3. getDate 获取月份中的每一天，不同月份取值也不相同

4. getDay 获取星期，取值为 0 ~ 6

5. getHours 获取小时，取值为 0 ~ 23

6. getMinutes 获取分钟，取值为 0 ~ 59

7. getSeconds 获取秒，取值为 0 ~ 59





### 案例：页面显示时间

需求:
将当前时间以:YYYY-MM-DDHH:mm 形式显示在页面2008-08-0808:08

```html
<style>
  div {
    border: 1px solid black;
    padding: 10px;
  }
</style>
<body>
  <div></div>
  <script>
    const div = document.querySelector('div')
    setInterval(function() {
      const data = new Date()
      div.innerHTML = data.toLocaleString()
    },1000)
  </script>
</body>
```





### 时间戳

时间戳是指1970年01月01日00时00分00秒起至现在的总秒数或毫秒数，它是一种特殊的计量时间的方式。

// 注：ECMAScript 中时间戳是以毫秒计的。

```javascript
// 1. 实例化
const date = new Date()
// 2. 获取时间戳
console.log(date.getTime())
// 还有一种获取时间戳的方法
console.log(+new Date())
// 还有一种获取时间戳的方法
console.log(Date.now())
```

获取时间戳的方法，分别为 getTime 和 Date.now 和  +new Date()



## DOM节点 

> 掌握元素节点创建、复制、插入、删除等操作的方法，能够依据元素节点的结构关系查找节点

回顾之前 DOM 的操作都是针对元素节点的属性或文本的，除此之外也有专门针对元素节点本身的操作，如插入、复制、删除、替换等。



## 4.2 查找节点

### 父节点查找:

​	**parentNode**
​	返回最近一级的父节点 找不到返回为null

```javascript
<style>
  .box {
    width: 60px;
    height: 60px;
    padding: 10px;
    margin: 10px;
    background-color: #ea9696;
  }
</style>
<body>
  <div class="box">
    <div class="box1">X1</div>
  </div>
  <div class="box">
    <div class="box1">X2</div>
  </div>
  <div class="box">
    <div class="box1">X3</div>
  </div>
  <script>
    const box = document.querySelectorAll('.box1')
    for (let i = 0; i < box.length; i++) {
      box[i].addEventListener('click', function() {
        this.parentNode.style.display = 'none'
      })
    }
  </script>
</body>
```

### 子节点查找:

​	**childNodes**
​	获得所有子节点、包括文本节点(空格、换行)、注释节点等

==children 属性 (重点)==
	仅获得所有元素节点
	返回的还是一个伪数组

```javascript
const ul = document.querySelector('ul')
console.log(ul.children)
```



### 兄弟节点查找：

​	1.下一个兄弟节点
​		nextElementSibling 属性
​	2.上一个兄弟节点
​		previousElementSibling 属性

```html
<body>
  <ul>
    <li>1</li>
    <li>2</li>
    <li>3</li>
    <li>4</li>
    <li>5</li>
  </ul>
  <script>
    const li2 = document.querySelector('ul li:nth-child(2)')
    console.log(li2.nextElementSibling)
    console.log(li2.previousElementSibling)
  </script>
</body>
```









## 4.3 增加节点 

### 创建节点

即创造出一个新的网页元素，再添加到网页内，一般先创建节点，然后插入节点

```javascript
document.createElement("div")
```



### 追加节点

要想在界面看到，还得插入到某个父元素中

插入到父元素的最后一个子元素: 
**父元素.appendChild(要插入的元素)**

插入到父元素中某个子元素的前面：
**父元素.insertBefore(要插入的元素, 在哪个元素前面)**

```html
<body>
  <div>nihao</div>
  <script>
    const div = document.querySelector("div")
    const li1 = document.createElement("li")
    const li2 = document.createElement("li")
    li1.innerHTML = "Hello World1"
    li2.innerHTML = "Hello World2"
    div.insertBefore(li2, div.children[0])
    div.appendChild(li1)
  </script>
</body>
```





### 克隆节点

cloneNode会克隆出一个跟原标签一样的元素，括号内传入**布尔值**
	若为true，则代表克隆时会包含后代节点一起克隆
	若为false，则代表克隆时不包含后代节点
	默认为false

语法：

```javascript
元素.cloneNode(布尔值)
```

```html
<body>
  <ul>
    <li>1</li>
    <li>2</li>
    <li>3</li>
  </ul>
  <script>
    const ul = document.querySelector('ul')
    ul.appendChild(ul.children[0].cloneNode(true))
    ul.appendChild(ul.children[0].cloneNode())
  </script>
</body>
```





### 删除节点

在 JavaScript 原生DOM操作中，要删除元素必须通过**父元素删除**

语法：

```javascript
父元素.removeChild(要删除的元素)
```

> 注:
> 如不存在父子关系则删除不成功
> 删除节点和隐藏节点(display:none)有区别的: 隐藏节点还是存在的，但是删除，则从html中删除节点

```html
<body>
  <div>123</div>
  <ul>
    <li>1</li>
  </ul>
  <script>
    const div = document.querySelector('div')
    div.removeChild(div.firstChild)
  </script>
</body>
```









## 4.4 M端事件

移动端也有自己独特的地方。比如**触屏事件 touch**(也称触摸事件)，Android 和 I0S 都有

**触屏事件 touch**(也称触摸事件)，Android 和IOS 都有。touch 对象代表一个触摸点。**触摸点可能是一根手指，也可能是一根触摸笔。**触屏事件可响应用户手指(或触控笔)对屏幕或者触控板操作。



常见的触屏事件如下:

| 触屏touch事件 | 说明                            |
| ------------- | ------------------------------- |
| touchstart    | 手指触摸到一个 DOM 元素时触发   |
| touchmove     | 手指在一个 DOM 元素上滑动时触发 |
| touchend      | 手指从一个 DOM 元素上移开时触发 |



```html
<style>
  .box {
    width: 300px;
    height: 300px;
    background-color: pink;
  }
</style>
<body>
  <div class="box">123</div>
  <ul>
    <li>1</li>
  </ul>
  <script>
    const div = document.querySelector('div')
    div.addEventListener('touchstart' , function (){
      console.log('开始摸')
    })
    div.addEventListener('touchmove' , function (){
      console.log('滑动中')
    })    
    div.addEventListener('touchend' , function (){
      console.log('结束')
    })
  </script>
</body>
```





### 案例：学生信息表

说明:
本次案例，我们尽量减少dom操作，采取操作数据的形式增加和删除都是针对于数组的操作，然后根据数组数据渲染页面

核心思路:
1:声明一个空的数组
2:点击录入，根据相关数据，生成对象，追加到数组里面
3:根据数组数据渲染页面-表格的 行
4:点击删除按钮，删除的是对应数组里面的数据
5:再次根据数组的数据，渲染页面

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>新增学员与就业榜</title>
</head>
<style>
  h2 {
    text-align: center;
    font-size: 28px;
  }
  form {
    text-align: center;
    width: 100%;
    padding: 10px 20px;
    height: 60px;
    display: flex; 
    justify-content: space-between;
    align-items: center;
  }
  div {
    display: flex;
  }
  form input:focus {
    outline: none;
  }
  form label {
    margin-right: 10px;
    font-size: 14px;
    align-self: center;
    font-weight: bold;
  }
  form div input,
  form div select {
    padding: 0px;
    width: 100px;
    height: 30px;
    margin-right: 5px;
    border: 1.5px solid #363535;
    border-radius: 7px;
    padding: 0px 0px 0px 7px;
  }

  form button {
    background-color: cornflowerblue;
    border: 1.5px solid rgb(83, 133, 227);
    margin: 0 20px;
    color: white;
    width: 100px;
    height: 30px;
    border-radius: 7px;
    cursor: pointer;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    justify-content: center;
  }
  table th {
    background-color: cornflowerblue;
    color: white;
    padding: 10px;
  }
  table td {
    padding: 10px;
    text-align: center;
  }
</style>
<body>

<h2>新增学员</h2>
<form autocomplete="off" class="info">
    <div>
        <label for="name">姓名：</label>
        <input type="text" id="name" name="name" value="">
    </div>
    <div>
        <label for="age">年龄：</label>
        <input type="number" id="age" name="age" value="">
    </div>
    <div>
        <label for="gender">性别：</label>
        <select id="gender" name="gender">
            <option value="男" selected>男</option>
            <option value="女">女</option>
        </select>
    </div>
    <div>
        <label for="salary">薪资：</label>
        <input type="number" id="salary" name="salary" value="">
    </div>
    <div>
        <label for="city">就业城市：</label>
        <select id="city" name="city">
            <option value="曹县" selected>曹县</option>
            <!-- 其他城市选项 -->
        </select>
    </div>
    <button type="submit">录入</button>
</form>

<h2>就业榜</h2>
<table border="1">
    <thead>
        <tr>
            <th>学号</th>
            <th>姓名</th>
            <th>年龄</th>
            <th>性别</th>
            <th>薪资</th>
            <th>就业城市</th>
            <th>操作</th>
        </tr>
    </thead>
    <tbody>
        
    </tbody>
</table>
<script>
  const info = document.querySelector('.info')
  const name = document.querySelector('#name')
  const age = document.querySelector('#age')
  const gender = document.querySelector('#gender')
  const salary = document.querySelector('#salary')
  const city = document.querySelector('#city')
  const tbody = document.querySelector('tbody')
  const arr = []
  // const tr = document.createElement('tr')
  const btn = document.querySelector('button')

    
  
  info.addEventListener('submit', function(e){
    e.preventDefault()
    const obj = {
      stuID : arr.length + 1,
      name :  name.value ,
      age : age.value ,
      gender : gender.value ,
      salary : salary.value ,
      city : city.value 
    }

    if(name.value === '' || age.value === '' || salary.value === '' || city.value === '') {
      alert('请填写完整信息')
      return
    }

    arr.push(obj)
    this.reset()
    render()

    function render() {
      tbody.innerHTML = ''
      for (let i = 0; i < arr.length; i++) {
        const tr = document.createElement('tr')

        tr.innerHTML = `
          <td>${arr[i].stuID}</td>
          <td>${arr[i].name}</td>
          <td>${arr[i].age}</td>
          <td>${arr[i].gender}</td>
          <td>${arr[i].salary}</td>
          <td>${arr[i].city}</td>
          <td><button data-id="${i}">删除</button></td>
        `
        tbody.appendChild(tr)
      }
    }
  
    const deleteButtons = document.querySelectorAll('tbody button');
    deleteButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        const index = parseInt(this.getAttribute('data-id'));
        arr.splice(index, 1);
        render()
      })
    })
  })
</script>
</body>
</html>
```











# 5 Web API BOM

## 5.1 BOM

BOM(Browser Object Model)是浏览器对象模型

window对象是一个==全局对象==，也可以说是JavaScript中的顶级对象
像document、alert()、console.log()这些都是window的属性，基本BOM的属性和方法都是window的。



## 5.2 延时函数

JavaScript 内置的一个用来让==代码延迟执行的函数==，叫 setTimeout

setTimeout 仅仅==只执行一次==，所以可以理解为就是把一段代码延迟执行,平时省略window

语法：

**setTimeout(回调函数，等待的毫秒数)**

```html
<style>
  .box {
    width: 100px;
    height: 100px;
    background-color: pink;
  }
</style>
<body>
  <div class="box">广告</div>
  <script>
    const box = document.querySelector('.box')
    const time = setTimeout(function() {
      box.style.display = 'none'
    } , 5000)
  </script>
</body>
```



### 5.3 JS执行机制

JavaScript 语言的一大特点就是==单线程==，也就是说，==同一个时间只能做一件事==

为了解决这个问题，利用多核CPU的计算能力，HTML5 提出 Web Worker 标准，允许JavaScript 脚本创建多个线程。于是，JS 中出现了==同步==和==异步==。

### 同步

前一个任务结束后再执行后一个任务，程序的执行顺序与任务的排列顺序是一致的、同步的。比如做饭的同步做法:我们要烧水煮饭，等水开了(10分钟之后)，再去切菜，炒菜。

### 异步

你在做一件事情时，因为这件事情会花费很长时间，在做这件事的同时，你还可以去处理其他事情。比如做饭的异步做法，我们在烧水的同时，利用这10分钟，去切菜，炒菜。

### 事件循环

1.先执行==执行栈中的同步任务==
2.异步任务放入任务队列中。
3.一旦执行栈中的所有同步任务执行完毕，系统就会按次序读取任务队列中的异步任务，于是被读取的异步任务结束等待状态，进入执行栈，开始执行。

```html
<script>
  console.log(1)
  document.addEventListener('click',function(){
    console.log(4)
  })    
  console.log(2)
  setTimeout(function(){
    console.log(3)
  },3000)
</script>
```



## 5.3 location对面

location 的数据类型是对象，它拆分并保存了URL地址的各个组成部分

**常用属性和方法**:
search属性获取地址中携带的参数，符号?后面部分

```javascript
console.log(location.hash)
```

```html
<body>
    <a href="https://www.bilibili.com/">5秒后跳转到bilibili</a>
  <script>
    const a = document.querySelector('a')
    let num = 5
    let timeid = setInterval(function(){
      num--
      a.innerHTML = `${num}秒后跳转到bilibili`
      if(num === 0){
        clearInterval(timeid)
        location.href = 'https://www.bilibili.com/'
      }
    },1000)
  </script>
</body>
```

reload方法用来刷新当前页面，传入参数 true 时表示强制刷新

```html
<body>
  <button>按钮</button>
  <script>
    let btn = document.querySelector('button')
    btn.addEventListener('click', function() {
      location.reload(true)
    })
  </script>
</body>
```







## 5.4 navigator对象

navigator的数据类型是对象，该对象下记录了浏览器自身的相关信息

**应用场景**： 开发者可以通过解析 `userAgent` 来判断用户的浏览器类型或操作系统，并根据不同的设备环境做出相应的调整，例如为移动设备提供响应式界面，或为不同浏览器提供特定的样式和功能支持。

```javascript
!(function () {
      const userAgent = navigator.userAgent
      // 验证是否为Android或iPhone
      const android = userAgent.match(/(Android);?[\s\/]+([\d.]+)?/)
      const iphone = userAgent.match(/(iPhone\sOS)\s([\d_]+)/)
      // 如果是Android或iPhone，则跳转至移动站点
      if (android || iphone) {
        location.href = 'http://m.itcast.cn'
      }
    })();
```



## 5.5 histroy对象

history 的数据类型是对象，主要管理历史记录，该对象与浏览器地址栏的操作相对应，如前进、后退、历史记录等

| histroy对象方法 | 作用                                                     |
| --------------- | -------------------------------------------------------- |
| back()          | 可以后退功能                                             |
| forward()       | 前进功能                                                 |
| go(参数)        | 前进后退功能 参数如果是1前进1个页面 如果是-1 后退1个页面 |

```html
<body>
  <button>后退</button>
  <button>前进</button>
  <script>
    const back = document.querySelector('button:first-child')
    const forward = back.nextElementSibling

    back.addEventListener('click', function(){
      history.back()
      history.go(-1)
    })
    forward.addEventListener('click', function(){
      history.forward()
      history.go(1)
    })
  </script>
</body>
```





## 5.6 本地存储 

### 5.6.1 本地存储分类localStorage

目标:能够使用localStorage 把数据存储的浏览器中

作用:
可以将数据==永久==存储在本地(用户的电脑)，除非手动删除，否则关闭页面也会存在

特性:
可以多窗口(页面)共享(同一浏览器可以共享)以键值对的形式存储使用

语法：

存储数据：

```javascript
localStorage.setItem(key, value)
```

获取数据：

```javascript
localStorage.getItem(key)
```

删除数据：

```javascript
localStorage.removeItem(key)
```

更改数据：

```javascript
localStorage.setItem(key, value1)
localStorage.setItem(key, value2)
```



### 5.6.2 本地存储分类 sessionStorage

特性:
==生命周期为关闭浏览器窗口==
在同一个窗口(页面)下数据可以共享
以键值对的形式存储使用
用法跟localStorage 基本相同



### 5.6.3 存储复杂数据类型

本地只能存储字符串,无法存储复杂数据类型 并且无法直接使用 

使用方法
1.用==JSON.stringify==转换为 JSON字符串存储
2.用==JSON.parse==把IJSON字符串转换为 对象

```javascript
const arr = {
  name: '张三',
  age: 20,
  sex: '男'
}
localStorage.setItem('obj', JSON.stringify(arr))
console.log(JSON.parse(localStorage.getItem('obj')))
```







## 5.7 字符串拼接 新 （开发采用写法）

利用 ==map()==和==join()==数组方法实现字符串拼接





### 使用map的方法

map 可以遍历数组==处理数据==，并且==返回新的数组==

```javascript
const arr = ['red','green','blue']
const newArr = arr.map(function (ele , index) {
  return ele + '颜色'
})
console.log(newArr) // ['red颜色', 'green颜色', 'blue颜色']
```

map 也称为==映射==。映射是个术语，指两个元素的集之间元素相互“对应”的关系
map重点在于==有返回值==，forEach==没有返回值==



### 使用join的方法

join()方法用于把==数组==中的==所有元素转换一个字符串==

```javascript
const arr = ['red','green','blue']
const newArr = arr.map(function (ele , index) {
  return ele + '颜色'
})
console.log(newArr.join()) // red颜色,green颜色,blue颜色
console.log(newArr.join("")) // red颜色green颜色blue颜色
console.log(newArr.join("|")) // red颜色|green颜色|blue颜色
```

## 5.8 学生就业信息表 练习

根据以下gif 做出学生就业信息表 

核心步骤:
1:读取 localstorage 本地数据
	如果有数据则==转换为对象==放到变量里面一会使用它渲染页面
	如果没有则用默认==空数组[]==
	为了测试效果，咱们可以先把initData 存入本地存储看效果

2:根据数据==渲染页面==。遍历数组，根据数据生成 tr，里面填充数据，最后追加给 tbody

3.给form==注册提交事件==，要阻止默认提交事件(阻止默认行为)
	（非空判断）-- 如果年龄、性别、薪资有一个值为空，则return 返回'输入能为空' 中断程序 

4.给 arr 数组==追加对象==，里面存储表单获取过来的数据，渲染页面和重置表单(reset()方法)

5.采用==事件委托==形式，给 tbody 注册点击事件得到当前点击的索引号。
渲染数据的时候，动态给a链接==添加自定义属性== data-id=“0”

6.根据索引号，利用 splice 删除数组这条数据，重新渲染页面
把最新 arr 数组==存入本地存储==

7.关于stuld 的处理:
	新增加序号应该是==最后一条数据的stuld + 1==
	数组[数组的长度-1].stuld +1

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="X-UA-Compatible" content="ie=edge" />
  <title>学生就业统计表</title>
  <link rel="stylesheet" href="../iconfont/iconfont.css">
</head>

<style>
  * {
  margin: 0;
  padding: 0;
}

a {
  text-decoration: none;
  color: #721c24;
}

h1 {
  text-align: center;
  color: #333;
  margin: 20px 0;

}

.title {
  width: 933px;
  height: 50px;
  line-height: 50px;
  padding-right: 15px;
  border: 1px solid #ebebeb;
  margin: 10px auto;
  background-color: #f2f2f2;
  text-align: right;
}

.title span {
  display: inline-block;
  vertical-align: middle;
  height: 20px;
  margin: -3px 5px 0;
  text-align: center;
  line-height: 20px;
  color: #f26934;
  font-weight: 700;
}

table {
  margin: 0 auto;
  width: 950px;
  border-collapse: collapse;
  color: #3c3637;
}

th {
  padding: 10px;
  background: #f2f2f2;
  font-size: 18px;
  text-align: left;
}

td,
th {
  border: 1px solid #ebebeb;
  padding: 15px;
}

td {

  color: #666;
  font-size: 16px;

}

tbody tr {
  background: #fff;
}

tbody tr:hover {
  background: #fbfafa;
}

tbody a {
  display: inline-block;
  width: 80px;
  height: 30px;
  text-align: center;
  line-height: 30px;
  color: #fff;
  background-color: #f26934;
}

.info {
  width: 900px;
  margin: 50px auto;
  text-align: center;
}

.info input,
.info select {
  width: 100px;
  height: 30px;
  outline: none;
  border: 1px solid #ebebeb;
  padding-left: 5px;
  box-sizing: border-box;
  margin-right: 10px;
}

.info button {
  width: 70px;
  height: 30px;
  background-color: #5dbfd8;
  outline: none;
  border: 0;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
}

.info button:hover {
  background-color: #52abc1;
}
</style>
<body>
  <h1>学生就业统计表</h1>
  <form class="info" autocomplete="off">
    <input type="text" class="uname" name="uname" placeholder="姓名" />
    <input type="text" class="age" name="age" placeholder="年龄" />
    <input type="text" class="salary" name="salary" placeholder="薪资" />
    <select name="gender" class="gender">
      <option value="男">男</option>
      <option value="女">女</option>
    </select>
    <select name="city" class="city">
      <option value="北京">北京</option>
      <option value="上海">上海</option>
      <option value="广州">广州</option>
      <option value="深圳">深圳</option>
      <option value="曹县">曹县</option>
    </select>
    <button class="add">
      <i class="iconfont icon-tianjia"></i>添加
    </button>
  </form>

  <div class="title">共有数据<span>0</span>条</div>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>姓名</th>
        <th>年龄</th>
        <th>性别</th>
        <th>薪资</th>
        <th>就业城市</th>
        <th>录入时间</th>
        <th>操作</th>
      </tr>
    </thead>
    <tbody>
      <!-- <tr>
        <td>1</td>
        <td>迪丽热巴</td>
        <td>23</td>
        <td>女</td>
        <td>12000</td>
        <td>北京</td>
        <td>2099/9/9 08:08:08</td>
        <td>
          <a href="javascript:">
            <i class="iconfont icon-shanchu"></i>
            删除
          </a>
        </td>
      </tr> -->
    </tbody>
  </table>
<script>
  const initData = [
    {
      id: 1,
      name: '迪丽热巴',
      age: 23,
      gender: '女',
      salary: 12000,
      city: '北京',
      time: '2099/9/9 08:08:08'
    }
  ]
  // localStorage.setItem('data',JSON.stringify(initData))
  const arr = JSON.parse(localStorage.getItem('data')) || []
  const tbody = document.querySelector('tbody')
  const getspan = document.querySelector('.title span')
  function render() {
    const trArr = arr.map(function(ele ,index) {
      return `
        <tr>
          <td>${ele.id}</td>
          <td>${ele.name}</td>
          <td>${ele.age}</td>
          <td>${ele.gender}</td>
          <td>${ele.salary}</td>
          <td>${ele.city}</td>
          <td>${ele.time}</td>
          <td>
            <a href="javascript:" data-id="${index}">
              <i class="iconfont icon-shanchu"></i>
              删除
            </a>
          </td>
        </tr>
      `
    })
    console.log(trArr)
    tbody.innerHTML = trArr.join('')
    getspan.innerHTML = arr.length
  }
  
  render()

  const info = document.querySelector('.info')
  const uname = document.querySelector('.uname')
  const age = document.querySelector('.age')
  const salary = document.querySelector('.salary')
  const gender = document.querySelector('.gender')
  const city = document.querySelector('.city')
  
  info.addEventListener('submit', function(e) {
    e.preventDefault() // 阻止默认提交
    if(!uname.value || !age.value || !salary.value ) {
      return alert('请填写完整信息')
    }
    arr.push({
      id: arr.length ?arr[arr.length-1].id + 1 : 1,
      name: uname.value,
      age: age.value,
      gender: gender.value,
      salary: salary.value,
      salary: gender.value,
      city: city.value,
      time: new Date().toLocaleString()
    })
    render()
    info.reset()
    localStorage.setItem('data',JSON.stringify(arr))
  })

  
  tbody.addEventListener('click', function(e) {
    if(e.target.tagName === 'A'){
      if(confirm('确定删除吗?')) {
        arr.splice(e.target.dataset.id,1)
        render()
        localStorage.setItem('data',JSON.stringify(arr))
      }
    }
  })


</script>
</body>

</html>
```











# 6 Wed API 正则表达式

## 6.1 正则表达式的介绍和使用

正则表达式(Reqular Expression)是用于匹配字符串中字符组合的模式。在JavaScript中，正则表达式也是对象通常用来查找、替换那些符合正则表达式的文本，许多语言都支持正则表达式

### 正则表达式有什么作用？

表单验证(匹配)
过滤敏感词(替换)
字符串中提取我们想要的部分(提取)



### 语法

1.定义正则表达式语法:

```javascript
const reg = /World/
```



2.判断是否有符合规则的字符串:

test()方法 用来查看正则表达式与指定的字符串==是否匹配==

```javascript
const str = 'Hello World'
const reg = /World/
console.log(reg.test(str))
```



3.==检索(查找)符合规则==的字符串:
exec()方法 在一个指定字符串中执行一个搜索匹配

如果匹配==成功==，exec()方法==返回一个数组==，否则返回null

```javascript
const str = 'Hello World'
const reg = /World/
console.log(reg.exec(str))
```









## 6.2 元字符

### 普通字符

大多数的字符仅能够描述它们本身，这些字符称作普通字符，例如所有的字母和数字。
也就是说普通字符只能够匹配字符串中与它们相同的字符。

### 元字符(特殊字符)

是一些具有特殊含义的字符，可以极大提高了灵活性和强大的匹配功能。
比如，规定用户只能输入英文26个英文字母，普通字符的话 abcdefghijklm....
==但是换成元字符写法:[a-z]==

正则测试工具：https://tool.oschina.net/regex



### 边界符

| 边界符 | 说明                         |
| ------ | ---------------------------- |
| ^      | 表示匹配行首的文本(以谁开始) |
| $      | 表示匹配行尾的文本(以谁结束) |

如果^和$在==一起==，表示必须是==精确匹配==。

```JavaScript
console.log(/^哈/.test('哈'))  // true
console.log(/哈$/.test('一哈'))  // true
console.log(/^哈$/.test('哈'))   // true
console.log(/^哈哈$/.test('哈哈'))   // true
console.log(/^哈$/.test('哈哈'))     // false
```



### 量词

量词用来 ==设定某个模式出现的次数==

| 量词  | 说明             |
| ----- | ---------------- |
| *     | 重复零次或更多次 |
| +     | 重复一次或更多次 |
| ？    | 重复零次或一次   |
| {n}   | 重复n次          |
| {n,}  | 重复n次或更多次  |
| {n,m} | 重复n次到m次     |

```javascript
console.log(/^哈*$/.test('哈')) // true
console.log(/哈+$/.test('一哈')) // true
console.log(/^哈{2,3}$/.test('哈')) // false
console.log(/^哈哈{1,3}$/.test('哈哈')) // true
console.log(/^哈{1,2}$/.test('哈哈哈'))  // false
```



### 字符类

[]匹配字符集合
后面的字符串只要包含 abc 中任意一个字符，都返回 true

```javascript
console.log(/^[abc]$/.test('a'))
console.log(/^[abc]$/.test('b'))
console.log(/^[a-z]$/.test('ab'))
console.log(/^[abc]$/.test('abc'))
```

[]里面加上^==取反==符号

```javascript
console.log(/^[^abc]$/.test('d'))
```



### 预定义

指的是 某些常见模式的简写方式

| 预定类 | 说明                                                        |
| ------ | ----------------------------------------------------------- |
| \d     | 匹配0-9之间的任一数字，相当于[0-9]                          |
| \D     | 匹配所有0-9以外的字符，相当于==[^0-9]==                     |
| \w     | 匹配任意的字母、数字和下划线，相当于[A-Za-z0-9]             |
| \W     | 除所有字母、数字和下划线以外的字符，相当于==[^A-Za-z0-9_]== |
| \s     | 匹配空格(包括换行符、制表符、空格符等)，相等于[\t\r\n\v\f]  |
| \S     | 兀配非空格的字符，相当于==[^ \t\r\n\v\f]==                  |



### 修饰符

修饰符约束正则执行的某些细节行为，如是否区分大小写、是否支持多行匹配等

##### 语法：

```javascript
console.log(/a/i.test('a')) // true
console.log(/a/g.test('A')) // false
```

i 是单词 ignore 的缩写，正则匹配时字母不区分大小写

g 是单词 global的缩写，匹配所有满足正则表达式的结果



### 替换 replace 

##### 语法：

```javascript
//字符串.replace(/正则表达式/,'替换的文本')//

const str = 'hello java world'
console.log(str.replace(/java/i,"nihao")) // hello nihao world
```



### 案例：用户名验证案例

需求:用户名要求用户英文字母,数字,下划线或者短横线组成，并且用户名长度为 6~16位分析:
1:首先准备好这种正则表达式模式 /^[a-zA-Z0-9-]{6,16}$/
2:当表单失去焦点就开始验证，
3:如果符合正则规范,则让后面的span标签添加 right 类
4:如果不符合正则规范,则让后面的span标签添加 wrong 类





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
    width: 250px;
    height: 30px;
    vertical-align: middle;
    line-height: 30px;
    padding-left: 15px;
  }
  .error {
    color: red;
  }
  .right {
    color: green;
  }
</style>
<body>
  <input type="text">
  <span></span>
  <script>
    const input = document.querySelector('input')
    const span = document.querySelector('span')
    const Reg = /^[0-9a-zA-Z_]{6,16}$/
    input.addEventListener('blur', function() {
      if(Reg.test(input.value)) {
        span.classList.add('right')
        span.innerHTML = '正确'
      } else {
        span.classList.add('error')
        span.innerHTML = '请输入6-16位字母或数字或下划线'
      }  
    })
    input.addEventListener('focus', function() {
      span.classList.remove('right')
      span.classList.remove('error')
    })
  </script>
</body>
</html>
```







## 6.3 注册页面案例

![](D:\Typora笔记\JS的笔记\Web API img\注册页面案例.gif)

**需求1:发送验证码**
用户点击之后，显示 05秒后重新获取时间到了，自动改为 重新获取

**需求2:用户名验证(注意封装函数 verifyxxx)**,失去焦点触发
函数正则 /^[a-zA-Z0-9-_]{6,10}$/
如果不符合要求，则出现提示信息 并return false 中断程序否则 则返回return true
之所以返回 布尔值，是为了 最后的提交按钮做准备侦听使用change事件，当鼠标离开了表单，并且表单值发生了变化时触发(类似京东效果)

**需求3:获取手机号码表单**
函数正则 /^1[3-9]\d{9}$/

**需求4:获取验证码**
函数正则 /^\d{6}$/

**需求5:密码验证**
函数正则 /^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,20}$/

**需求6:我同意模块**
添加类 .icon-queren2 则是默认选中样式 可以使用 toggle切换类

**需求7: 表单提交模块**
使用 submit 提交事件
如果没有勾选同意协议，则提示 需要勾选
==classList.contains()看看有没有包含某个类，如果有则返回true，么有则返回false==
如果上面input表单 只要有模块，返回的是 false 则 阻止提交

**分析模块:**
1:发送验证码模块
2:各个表单验证模块
3:勾选已经阅读同意模块
4:下一步验证全部模块
5:只要上面有一个input验证不通过就不同意提交

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
    <meta charset="UTF-8">
    <title>新用户注册</title>
    <style>
        * {
            margin: 0;
            padding: 0;
        }
        h2 {
            text-align: center;
            padding: 0px 0px 20px;
        }
        .max {
            max-width: 800px;
            margin: 50px auto;
            background-color: #ffffff;
            border: 1px solid #dcdcdc;
        }
        .container {
            max-width: 400px;
            margin: 50px auto;
            padding: 20px 40px;
            background-color: #e1e1e1;
            border-radius: 5px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
        }
        .form-group input {
            /*  方框内文字向右偏移5px */
            width: 100%;
            padding: 8px 0px 5px 5px;
            border: 1px solid #ccc;
            border-radius: 3px;
        }
        .form-group button {
          margin: 5px 0px;
        }
        .error {
            color: red;
            font-size: 12px;
            margin-top: 5px;
        }
        .btn {
            width: 100%;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        .btn:hover {
            background-color: #45a049;
        }
        #xieyi {
          display: flex;
        }
    </style>
</head>
<body>
    <div class="max">
        <div class="container">
            <h2>新用户注册</h2>
            <form id="registerForm">
                <div class="form-group">
                    <label for="nickname">昵称</label>
                    <input type="text" id="nickname" name="nickname" placeholder="请输入昵称" required>
                    <span class="error" id="nicknameError"></span>
                </div>

                <div class="form-group">
                    <label for="phone">手机号码</label>
                    <input type="tel" id="phone" name="phone" placeholder="请输入手机号码" required>
                    <span class="error" id="phoneError"></span>
                </div>

                <div class="form-group">
                    <label for="verificationCode">短信验证码</label>
                    <input type="text" id="verificationCode" name="verificationCode" placeholder="请输入短信验证码" required>
                    <button type="button" id="sendCodeBtn">发送验证码</button>
                    <span class="error" id="codeError"></span>
                </div>

                <div class="form-group">
                    <label for="password">设置密码</label>
                    <input type="password" id="password" name="password" placeholder="设置6至20位字母、数字和符号组合" required>
                    <span class="error" id="passwordError"></span>
                </div>

                <div class="form-group">
                    <label for="confirmPassword">确认密码</label>
                    <input type="password" id="confirmPassword" name="confirmPassword" placeholder="请再次输入上面密码" required>
                    <span class="error" id="confirmPasswordError"></span>
                </div>

                <div  id="xieyi">
                    <input class="xieyi" type="checkbox" id="agreeTerms" name="agreeTerms" required >
                    <label class="xieyi" for="agreeTerms">已阅读并同意《用户服务协议》</label>
                </div>

                <button type="submit" class="btn">下一步</button>
            </form>
        </div>
    </div>

    <script>
      const container = document.querySelector('.container')
      // 1.发送验证码模块
      const sendCodeBtn = document.querySelector('#sendCodeBtn')
      let flag = true // 防止用户多次点击按钮，导致发送验证码频繁 节流阀
      sendCodeBtn.addEventListener('click', function() {
        // 1.1 点击发送验证码按钮，禁用按钮，显示倒计时
        if(flag){
            flag = false
            let i = 5
            let timer = setInterval(function() {
                i--
                sendCodeBtn.innerHTML = i + '秒后重新获取验证码'
                if(i === 0) {
                    clearInterval(timer)
                    sendCodeBtn.innerHTML = '重新获取验证码'
                    flag = true
                }
            },1000)}  
        })
        
        // 2.验证模块
        // 2.1 获取用户名表单
        const nickName = document.querySelector('#nickname')
        // 2.2 使用change事件
        nickName.addEventListener('change', verifyName)
        // 2.3 封装verifyName函数
        function verifyName() {
            //2.3.1 定正则表达式
            const reg = /^[a-zA-Z0-9-_]{6,10}$/
            //2.3.2 获取span元素
            const span = document.querySelector('#nicknameError')
            //2.3.3 验证用户名是否符合规则
            if(!reg.test(nickName.value)) {
                span.innerHTML = '昵称必须是6-10位字母、数字、下划线、减号'
            } else {
                span.innerHTML = ''
            }
        }

        // 2.4 获取手机号码表单
        const phone = document.querySelector('#phone')
        // 2.5 使用change事件
        phone.addEventListener('change', verifyPhone)
        // 2.6 封装verifyPhone函数
        function verifyPhone() {
            //2.6.1 定正则表达式
            const reg = /^1[3-9]\d{9}$/
            //2.6.2 获取span元素
            const span = document.querySelector('#phoneError')
            //2.6.3 验证手机号码是否符合规则
            if(!reg.test(phone.value)) {
                span.innerHTML = '手机号码格式不正确'
            } else {
                span.innerHTML = ''
            }
        }

        // 2.7 获取验证码表单
        const verificationCode = document.querySelector('#verificationCode')
        // 2.8 使用change事件
        verificationCode.addEventListener('change',verifyCode)
        // 2.9 封装verifyCode函数
        function verifyCode() {
            // 2.9.1 定正则表达式
            const reg = /^\d{6}$/
            // 2.9.2 获取span元素
            const span = document.querySelector('#codeError')
            // 2.9.3 验证验证码是否符合规则
            if(!reg.test(verificationCode.value)) {
                span.innerHTML = '验证码格式不正确'
            } else {
                span.innerHTML = ''
            }
        }

        // 2.10 获取密码表单
        const password = document.querySelector('#password')
        const confirmPassword = document.querySelector('#confirmPassword')
        // 2.11 使用change事件
        container.addEventListener('change', verifyPassword)
        // 2.12 封装verifyPassword函数
        function verifyPassword() {
            // 2.12.1 定正则表达式
            const reg = /^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,20}$/
            // 2.12.2 获取span元素
            const span = document.querySelector('#passwordError')
            const confirmSpan = document.querySelector('#confirmPasswordError')
            // 2.12.3 验证密码是否符合规则
            if(!reg.test(password.value)) {
                span.innerHTML = '密码必须是6-20位字母、数字和符号组合'
            } else {
                span.innerHTML = ''
            }
            // 2.12.4 验证确认密码是否一致
            if(confirmPassword.value !== password.value) {
                confirmSpan.innerHTML = '密码不一致'
            } else {
                confirmSpan.innerHTML = ''
            }
        }

        // 3 我同意协议模块
        const agree = document.querySelector('#agreeTerms')
        const btn = document.querySelector('.btn')
        // 4 提交表单模块
        const form = document.querySelector('#registerForm')
        // 4.1 使用submit事件
        form.addEventListener('submit', function(e) {
            // 4.1.1 阻止默认提交事件
            e.preventDefault()
            // 4.1.2 验证表单
            if(!agree.checked) {
                alert('请阅读并同意用户服务协议')
                return false
            }
            // 4.1.3 验证成功，保存用户信息到本地存储
            localStorage.setItem('nickname', nickName.value)
            localStorage.setItem('phone', phone.value)
            localStorage.setItem('password', password.value)
            alert('注册成功')
            window.location.href = 'https://www.bilibili.com/'
        })
    </script>
</body>
</html>
```







# 7 Wed API 放大镜 

参考效果如下地址：

http://erabbit.itheima.net/#/

## 顶部导航模块

![](D:\Typora笔记\JS的笔记\Web API img\assets\444.gif)

需求：

1. 顶部导航开始不显示
2. 等页面滑到主导航栏，这个**新顶部导航栏滑动下拉显示**，并且改为固定定位
3. 等页面滑到上面，新顶部导航栏隐藏

## 图片切换模块

![](D:\Typora笔记\JS的笔记\Web API img\assets\111.gif)



## 放大镜效果

![](D:\Typora笔记\JS的笔记\Web API img\assets\555.gif)

业务分析：

①：鼠标经过对应小盒子，左侧中等盒子显示对应中等图片

②： 鼠标经过中盒子，右侧会显示放大镜效果的大盒子

③： 黑色遮罩盒子跟着鼠标来移动

④： 鼠标在中等盒子上移动，大盒子的图片跟着显示对应位置





思路分析：

①：鼠标经过小盒子，左侧中等盒子显示对应中等图片

1. 获取对应的元素
2. 采取事件委托的形式，监听鼠标经过小盒子里面的图片， 注意此时需要使用 `mouseover` 事件，因为需要事件冒泡触发small 
3. 让鼠标经过小图片的爸爸li盒子，添加类，其余的li移除类（注意先移除，后添加）
4. 鼠标经过小图片，可以拿到小图片的src， 可以做两件事
   - 让中等盒子的图片换成这个 这个小图片的src
   - 让大盒子的背景图片，也换成这个小图片的 src （稍后做）





②： 鼠标经过中等盒子，右侧大盒子显示

1. 用到鼠标经过和离开，鼠标经过中盒子，大盒子 利用 display 来显示和隐藏

2. 鼠标离开不会立马消失，而是有200ms的延时，用户体验更好，所以尽量使用定时器做个延时 setTimeout

3. 显示和隐藏也尽量定义一个函数，因为鼠标经过离开中等盒子，会显示隐藏，同时，**鼠标经过大盒子，也会显示和隐藏**

4. 给大盒子里面的背景图片一个默认的第一张图片

   

③： 黑色遮罩盒子跟着鼠标来移动

1. 先做鼠标经过 中等盒子，显示隐藏 黑色遮罩 的盒子

2. 让黑色遮罩跟着鼠标来走, 需要用到鼠标移动事件  mousemove  

3. 让黑色盒子的移动的核心思想：不断把鼠标在中等盒子内的坐标给黑色遮罩层 let  top 值，这样遮罩层就可以跟着移动了

   - 需求

     - 我们要的是 鼠标在 中等盒子内的坐标， 没有办法直接得到
     - 得到1：  鼠标在页面中的坐标
     - 得到2：  中等盒子在页面中的坐标

   - 算法

     - 得到鼠标在页面中的坐标    利用事件对象的  pageX  
     - 得到middle中等盒子在页面中的坐标   middle.getBoundingClientRect()
     - 鼠标在middle 盒子里面的坐标   =   鼠标在页面中的坐标  -   middle 中等盒子的坐标
     - 黑色遮罩层不断得到       鼠标在middle 盒子中的坐标 就可以移动起来了

     >注意 y坐标特殊，需要减去 页面被卷去的头部 
     >
     >为什么不用 box.offsetLet 和 box.offsetTop  因为这俩属性跟带有定位的父级有关系，很容被父级影响，而getBoundingClientRect() 不受定位的父元素的影响

   - 限定遮罩的盒子只能在middle 内部移动，需要添加判断

     - 限定水平方向 大于等于0 并且小于等于 400
     - 限定垂直方向 大于等于0 并且小于等于 400

   - 遮罩盒子移动的坐标： 

     - 声明一个 mx 作为移动的距离
     - 水平坐标 x 如果 小于等于100 ，则移动的距离 mx 就是  0  不应该移动
     - 水平坐标 如果 大于等于100 并且小于300，移动的距离就是  mx - 100 （100是遮罩盒子自身宽度的一半）
     - 水平坐标 如果 大于等于300，移动的距离就是  mx   就是200  不应该在移动了
     - 其实我们发现水平移动， 就在 100 ~ 200 之间移动的
     - 垂直同理

   ~~~javascript
   let mx = 0, my = 0;
   if (x <= 100) mx = 0
   if (x > 100 && x < 300) mx = x - 100
   if (x >= 300) mx = 200
   
   if (y <= 100) my = 0
   if (y > 100 && y < 300) my = y - 100
   if (y >= 300) my = 200
   ~~~

   - 大盒子图片移动的计算方法：
     - 中等盒子是 400px  大盒子 是 800px 的图片
     - 中等盒子移动1px， 大盒子就应该移动2px， 只不过是负值

   ~~~JavaScript
   large.style.backgroundPositionX = - 2 * mx + 'px'
   large.style.backgroundPositionY = - 2 * my + 'px'
   
   //或者写出
   large.style.backgroundPosition = `-${mx * 2}px -${my * 2}px`
   ~~~

   #### 放大镜完整代码：

   ```HTML
   <!DOCTYPE html>
   <html lang="en">
   
   <head>
     <meta charset="UTF-8">
     <title>小兔鲜儿 - 新鲜 惠民 快捷!</title>
     <meta http-equiv="X-UA-Compatible" content="IE=edge">
     <meta name="renderer" content="webkit">
     <!-- <link rel="stylesheet" href="//at.alicdn.com/t/font_1939705_bgtmkonu28.css"> -->
     <link rel="stylesheet" href="./css/common.css">
     <link rel="stylesheet" href="./css/product.css">
   </head>
   
   <body>
     <!-- 项部导航 -->
     <div class="xtx_topnav">
       <div class="wrapper">
         <!-- 顶部导航 -->
         <ul class="xtx_navs">
           <li>
             <a href="javascript:;">请先登录</a>
           </li>
           <li>
             <a href="javascript:;">免费注册</a>
           </li>
           <li>
             <a href=".javascript:;">我的订单</a>
           </li>
           <li>
             <a href="javascript:;">会员中心</a>
           </li>
           <li>
             <a href="javascript:;">帮助中心</a>
           </li>
           <li>
             <a href="javascript:;">在线客服</a>
           </li>
           <li>
             <a href="javascript:;">
               <i class="mobile sprites"></i>
               手机版
             </a>
           </li>
         </ul>
       </div>
     </div>
     <!-- 头部 -->
     <div class="xtx_header">
       <div class="wrapper">
         <!-- 网站Logo -->
         <h1 class="xtx_logo"><a href="/">小兔鲜儿</a></h1>
         <!-- 主导航 -->
         <div class="xtx_navs">
           <ul class="clearfix">
             <li>
               <a href="javascript:;">首页</a>
             </li>
             <li>
               <a href="javascript:;">生鲜</a>
             </li>
             <li>
               <a href="javascript:;">美食</a>
             </li>
             <li>
               <a href="javascript:;">餐厨</a>
             </li>
             <li>
               <a href="javascript:;">电器</a>
             </li>
             <li>
               <a href="javascript:;">居家</a>
             </li>
             <li>
               <a href="javascript:;">洗护</a>
             </li>
             <li>
               <a href="javascript:;">孕婴</a>
             </li>
             <li>
               <a href="javascript:;">服装</a>
             </li>
           </ul>
         </div>
         <!-- 站内搜索 -->
         <div class="xtx_search clearfix">
           <!-- 购物车 -->
           <a href="javascript:;" class="xtx_search_cart sprites">
             <i>2</i>
           </a>
           <!-- 搜索框 -->
           <div class="xtx_search_wrapper">
             <input type="text" placeholder="搜一搜" onclick="location.href='./search.html'">
           </div>
         </div>
       </div>
     </div>
     <div class="xtx-wrapper">
       <div class="container">
         <!-- 面包屑 -->
         <div class="xtx-bread">
           <a href="javascript:;"> 首页 > </a>
           <a href="javascript:;"> 电子产品 > </a>
           <a href="javascript:;"> 电视 > </a>
           <span>小米电视4A 32英寸</span>
         </div>
         <!-- 商品信息 -->
         <div class="xtx-product-info">
           <div class="left">
             <div class="pictrue">
               <div class="middle">
                 <img src="./images/1.jfif" alt="">
                 <div class="layer"></div>
               </div>
               <div class="small">
                 <ul>
                   <li class="active"><img src="./images/1.jfif" alt=""></li>
                   <li><img src="./images/2.jfif" alt=""></li>
                   <li><img src="./images/3.jfif" alt=""></li>
                   <li><img src="./images/4.jfif" alt=""></li>
                   <li><img src="./images/5.jfif" alt=""></li>
                 </ul>
               </div>
               <div class="large"></div>
             </div>
             <div class="other">
               <ul>
                 <li>
                   <p>销量人气</p>
                   <p>1999+</p>
                   <p>销量人气</p>
                 </li>
                 <li>
                   <p>商品评价</p>
                   <p>999+</p>
                   <p>查看评价</p>
                 </li>
                 <li>
                   <p>收藏人气</p>
                   <p>299+</p>
                   <p><a href="javascript:;">收藏商品</a></p>
                 </li>
                 <li>
                   <p>品牌信息</p>
                   <p>小米</p>
                   <p><a href="javascript:;">品牌主页</a></p>
                 </li>
               </ul>
             </div>
           </div>
           <div class="right">
             <h3 class="name">小米电视4A 32英寸</h3>
             <p class="desc">全面屏设计 / 高清分辨率 / 海量内容 / 1G+4G大内存 / 多核处理器</p>
             <p class="price"><span class="now">¥1899</span><span class="old">¥2999</span></p>
             <div class="address">
               <div class="item">
                 <div class="dt">促销</div>
                 <div class="dd">12月好物放送，App领券购买直降120元</div>
               </div>
               <div class="item">
                 <div class="dt">配送</div>
                 <div class="dd">至
                   <div class="box">
                     <span>陕西 西安 <i></i></span>
                   </div>
                 </div>
               </div>
               <div class="item">
                 <div class="dt">服务</div>
                 <div class="dd">
                   <span class="fw">无忧退货</span>
                   <span class="fw">快速退款</span>
                   <span class="fw">免费包邮</span>
                   <a href="#" class="lj">了解详情</a>
                 </div>
               </div>
             </div>
             <div class="attrs">
               <div class="item">
                 <div class="dt">颜色</div>
                 <div class="dd">
                   <img src="./uploads/img/cate-06.png" alt="">
                   <img src="./uploads/img/cate-07.png" alt="">
                 </div>
               </div>
               <div class="item">
                 <div class="dt">颜色</div>
                 <div class="dd">
                   <span class="size">22英寸</span>
                   <span class="size">42英寸</span>
                   <span class="size">52英寸</span>
                   <span class="size">62英寸</span>
                 </div>
               </div>
               <div class="item">
                 <div class="dt">数量</div>
                 <div class="dd">
                   <div class="num">
                     <a href="javascript:;">-</a>
                     <input type="text" value="1">
                     <a href="javascript:;">+</a>
                   </div>
                 </div>
               </div>
               <div class="item">
                 <a class="buy" href="javascript:;">立即购买</a>
               </div>
             </div>
           </div>
         </div>
         <!-- 同类产品推荐 -->
         <div class="xtx-relevant-product">
           <h3>同类产品推荐</h3>
           <ul>
             <li>
               <a href="#">
                 <img src="./uploads/history_goods_1.jpg" alt="">
                 <p class="name">USB Type C数据线</p>
                 <p class="desc">快速充电，稳定传输</p>
                 <p class="price">¥39</p>
               </a>
             </li>
             <li>
               <a href="#">
                 <img src="./uploads/history_goods_2.jpg" alt="">
                 <p class="name">红米Note 5A 高配版</p>
                 <p class="desc">1600万像素柔光自拍</p>
                 <p class="price">¥1899</p>
               </a>
             </li>
             <li>
               <a href="#">
                 <img src="./uploads/history_goods_3.jpg" alt="">
                 <p class="name">VGA网口多功能转接器</p>
                 <p class="desc">小巧便携，节省桌面空间</p>
                 <p class="price">¥19</p>
               </a>
             </li>
             <li>
               <a href="#">
                 <img src="./uploads/history_goods_4.jpg" alt="">
                 <p class="name">笔记本Pro 15.6"</p>
                 <p class="desc">全金属强化机身搭配独显</p>
                 <p class="price">¥4899</p>
               </a>
             </li>
           </ul>
           <a href="javascript:;" class="prev"><span class="iconfont icon-angle-left"></span></a>
           <a href="javascript:;" class="next"><span class="iconfont icon-angle-right"></span></a>
         </div>
         <!-- 商品详情 -->
         <div class="xtx-product-detail">
           <div class="main">
             <div class="cont">
               <div class="tab-head">
                 <a href="javascript:;">商品详情</a>
                 <a href="javascript:;">商品评价<span>（998+）</span></a>
               </div>
               <div class="tab-pane">
                 <!-- 静态属性 -->
                 <div class="attrs">
                   <div class="item"><span>商品名称：</span><span>小米L32M5-AZ </span></div>
                   <div class="item"><span>商品编号：</span><span>4620979 </span></div>
                   <div class="item"><span>商品毛重：</span><span>8.0kg </span></div>
                   <div class="item"><span>商品产地：</span><span>中国大陆 </span></div>
                   <div class="item"><span>屏幕尺寸：</span><span>32英寸及以下 </span></div>
                   <div class="item"><span>能效等级：</span><span>三级能效 </span></div>
                   <div class="item"><span>电视类型：</span><span>人工智能 </span></div>
                   <div class="item"><span>选购指数：</span><span>6.9-6.0 </span></div>
                   <div class="item"><span>观看距离：</span><span>2m以下（≤32英寸）</span></div>
                 </div>
                 <!-- 详情内容 -->
                 <div class="detail">
                   <img src="https://yanxuan-item.nosdn.127.net/39d7f2407c90d0442566a719146ee9c1.jpg" alt=""
                     data-v-2c43c764=""><img src="https://yanxuan-item.nosdn.127.net/7dfee58e7c6b3996badf368610ed62b1.jpg"
                     alt="" data-v-2c43c764=""><img
                     src="https://yanxuan-item.nosdn.127.net/d1acff1a29bddd21c2ad337d892a9f7c.jpg" alt=""
                     data-v-2c43c764=""><img src="https://yanxuan-item.nosdn.127.net/ac722b04b2014ac337d8db695ee46f0c.jpg"
                     alt="" data-v-2c43c764=""><img
                     src="https://yanxuan-item.nosdn.127.net/c63e36faa0848ee37c825897f5cec179.jpg" alt=""
                     data-v-2c43c764=""><img src="https://yanxuan-item.nosdn.127.net/e0f13dbf14c8a2f07e86bf3df3ca002b.jpg"
                     alt="" data-v-2c43c764="">
                 </div>
               </div>
               <div class="tab-pane" style="display: none;">评价</div>
             </div>
             <!-- 注意事项 -->
             <div class="warn">
               <h3>注意事项</h3>
               <p class="tit">• 购买运费如何收取？ </p>
               <p>单笔订单金额(不含运费)满88元免邮费；不满88元，每单收取10元运费。（港澳台地区需满500元免邮费；不满500元，每单收取30元运费) </p>
               <br>
               <br>
               <p class="tit">• 使用什么快递发货? </p>
               <p>默认使用顺丰快递发货(个别商品使用其他快递） </p>
               <p>配送范围覆盖全国大部分地区(港澳台地区除外）。 </p>
               <br>
               <br>
               <p class="tit">• 如何申请退货? </p>
               <p>1.自收到商品之日起30日内，顾客可申请无忧退货，退款将原路返还，不同的银行处理时间不同，预计1-5个工作日到账； </p>
               <p>2.内裤和食品等特殊商品无质量问题不支持退货； </p>
               <p>3.退货流程： 确认收货-申请退货-客服审核通过-用户寄回商品-仓库签收验货-退款审核-退款完成； </p>
               <p>4.因小兔鲜儿产生的退货，如质量问题，退货邮费由小兔鲜儿承担，退款完成后会以现金券的形式报销。因客户个人原因产生的退货，购买和寄回运费由客户个人承担。</p>
             </div>
           </div>
           <div class="aside">
             <div class="tit">24小时热销榜</div>
             <div class="product">
               <img src="./uploads/fresh_goods_3.jpg" alt="">
               <p class="name">USB Type C数据线</p>
               <p class="desc">快速充电，稳定传输</p>
               <p class="price">¥29</p>
             </div>
             <div class="product">
               <img src="./uploads/fresh_goods_3.jpg" alt="">
               <p class="name">USB Type C数据线</p>
               <p class="desc">快速充电，稳定传输</p>
               <p class="price">¥29</p>
             </div>
             <div class="product">
               <img src="./uploads/fresh_goods_3.jpg" alt="">
               <p class="name">USB Type C数据线</p>
               <p class="desc">快速充电，稳定传输</p>
               <p class="price">¥29</p>
             </div>
             <div class="tit">专题推荐</div>
             <div class="special">
               <img src="./uploads/discuss_goods_1.jpg" alt="">
               <p class="name">一往无前，诞生于崛起</p>
             </div>
             <div class="special">
               <img src="./uploads/discuss_goods_1.jpg" alt="">
               <p class="name">一往无前，诞生于崛起</p>
             </div>
             <div class="special">
               <img src="./uploads/discuss_goods_1.jpg" alt="">
               <p class="name">一往无前，诞生于崛起</p>
             </div>
           </div>
         </div>
       </div>
     </div>
     <!-- 公共底部 -->
     <div class="xtx_footer clearfix">
       <div class="wrapper">
         <!-- 联系我们 -->
         <div class="contact clearfix">
           <dl>
             <dt>客户服务</dt>
             <dd class="chat">在线客服</dd>
             <dd class="feedback">问题反馈</dd>
           </dl>
           <dl>
             <dt>关注我们</dt>
             <dd class="weixin">公众号</dd>
             <dd class="weibo">微博</dd>
           </dl>
           <dl>
             <dt>下载APP</dt>
             <dd class="qrcode">
               <img src="./uploads/qrcode.jpg">
             </dd>
             <dd class="download">
               <span>扫描二维码</span>
               <span>立马下载APP</span>
               <a href="javascript:;">下载页面</a>
             </dd>
           </dl>
           <dl>
             <dt>服务热线</dt>
             <dd class="hotline">
               400-0000-000
               <small>周一至周日 8:00-18:00</small>
             </dd>
           </dl>
         </div>
       </div>
       <!-- 其它 -->
       <div class="extra">
         <div class="wrapper">
           <!-- 口号 -->
           <div class="slogan">
             <a href="javascript:;" class="price">价格亲民</a>
             <a href="javascript:;" class="express">物流快捷</a>
             <a href="javascript:;" class="quality">品质新鲜</a>
           </div>
           <!-- 版权信息 -->
           <div class="copyright">
             <p>
               <a href="javascript:;">关于我们</a>
               <a href="javascript:;">帮助中心</a>
               <a href="javascript:;">售后服务</a>
               <a href="javascript:;">配送与验收</a>
               <a href="javascript:;">商务合作</a>
               <a href="javascript:;">搜索推荐</a>
               <a href="javascript:;">友情链接</a>
             </p>
             <p>CopyRight &copy; 小兔鲜儿</p>
           </div>
         </div>
       </div>
     </div>
     <script>
       // 放大镜效果
       const small = document.querySelector('.small')
       const middle = document.querySelector('.middle')
       const large = document.querySelector('.large')
   
       small.addEventListener('mousemove', function(e) {
         if(e.target.nodeName === 'IMG'){
           this.querySelector('.active').classList.remove('active')
           e.target.classList.add('active')
           middle.querySelector('img').src = e.target.src
           large.style.backgroundImage = `url(${e.target.src})`
         }
       })
       middle.addEventListener('mouseenter', show)
       middle.addEventListener('mouseleave', hide)
       let timeId = 0
       function show() { 
         clearInterval(timeId)
         large.style.display = 'block'
       }
       function hide() {
         timeId = setTimeout(function(){
           large.style.display = 'none'
         }, 100)
       }
   
       large.addEventListener('mouseenter', show)
       large.addEventListener('mouseleave', hide)
   
       const layer = document.querySelector('.layer')
       middle.addEventListener('mouseenter', function() {
         layer.style.display = 'block'
       })
       middle.addEventListener('mouseleave', function() {
         layer.style.display = 'none'
       })
   
       middle.addEventListener('mousemove', function(e) {
         const x = e.clientX - middle.getBoundingClientRect().left
         const y = e.clientY - middle.getBoundingClientRect().top - document.documentElement.scrollTop
         
         if(x >= 0 && x <= 400 && y >= 0 && y <= 400){
           let mx = 0 , my = 0
           if(x < 100)  mx = 0 
           if(x >= 100 && x <= 300)  mx = x - 100
           if(x > 300)  mx = 200
   
           if(y < 100)  my = 0 
           if(y >= 100 && y <= 300)  my = y - 100
           if(y > 300)  my = 200
   
           layer.style.left = mx + 'px'
           layer.style.top = my + 'px'
           
           large.style.backgroundPosition = `-${mx * 2}px -${my * 2}px`
         }
       })
     </script>
   </body>
   </html>
   ```
   
   ```
   @charset "UTF-8";
   /*! normalize.css v8.0.1 | MIT License | github.com/necolas/normalize.css */
   /* Document
      ========================================================================== */
   /**
    * 1. Correct the line height in all browsers.
    * 2. Prevent adjustments of font size after orientation changes in iOS.
    */
   html {
     line-height: 1.15;
     /* 1 */
     -webkit-text-size-adjust: 100%;
     /* 2 */
   }
   
   /* Sections
      ========================================================================== */
   /**
    * Remove the margin in all browsers.
    */
   body {
     margin: 0;
   }
   
   /**
    * Render the `main` element consistently in IE.
    */
   main {
     display: block;
   }
   
   /**
    * Correct the font size and margin on `h1` elements within `section` and
    * `article` contexts in Chrome, Firefox, and Safari.
    */
   h1 {
     font-size: 2em;
     margin: 0.67em 0;
   }
   
   /* Grouping content
      ========================================================================== */
   /**
    * 1. Add the correct box sizing in Firefox.
    * 2. Show the overflow in Edge and IE.
    */
   hr {
     box-sizing: content-box;
     /* 1 */
     height: 0;
     /* 1 */
     overflow: visible;
     /* 2 */
   }
   
   /**
    * 1. Correct the inheritance and scaling of font size in all browsers.
    * 2. Correct the odd `em` font sizing in all browsers.
    */
   pre {
     font-family: monospace, monospace;
     /* 1 */
     font-size: 1em;
     /* 2 */
   }
   
   /* Text-level semantics
      ========================================================================== */
   /**
    * Remove the gray background on active links in IE 10.
    */
   a {
     background-color: transparent;
   }
   
   /**
    * 1. Remove the bottom border in Chrome 57-
    * 2. Add the correct text decoration in Chrome, Edge, IE, Opera, and Safari.
    */
   abbr[title] {
     border-bottom: none;
     /* 1 */
     text-decoration: underline;
     /* 2 */
     text-decoration: underline dotted;
     /* 2 */
   }
   
   /**
    * Add the correct font weight in Chrome, Edge, and Safari.
    */
   b,
   strong {
     font-weight: bolder;
   }
   
   /**
    * 1. Correct the inheritance and scaling of font size in all browsers.
    * 2. Correct the odd `em` font sizing in all browsers.
    */
   code,
   kbd,
   samp {
     font-family: monospace, monospace;
     /* 1 */
     font-size: 1em;
     /* 2 */
   }
   
   /**
    * Add the correct font size in all browsers.
    */
   small {
     font-size: 80%;
   }
   
   /**
    * Prevent `sub` and `sup` elements from affecting the line height in
    * all browsers.
    */
   sub,
   sup {
     font-size: 75%;
     line-height: 0;
     position: relative;
     vertical-align: baseline;
   }
   
   sub {
     bottom: -0.25em;
   }
   
   sup {
     top: -0.5em;
   }
   
   /* Embedded content
      ========================================================================== */
   /**
    * Remove the border on images inside links in IE 10.
    */
   img {
     border-style: none;
   }
   
   /* Forms
      ========================================================================== */
   /**
    * 1. Change the font styles in all browsers.
    * 2. Remove the margin in Firefox and Safari.
    */
   button,
   input,
   optgroup,
   select,
   textarea {
     font-family: inherit;
     /* 1 */
     font-size: 100%;
     /* 1 */
     line-height: 1.15;
     /* 1 */
     margin: 0;
     /* 2 */
   }
   
   /**
    * Show the overflow in IE.
    * 1. Show the overflow in Edge.
    */
   button,
   input {
     /* 1 */
     overflow: visible;
   }
   
   /**
    * Remove the inheritance of text transform in Edge, Firefox, and IE.
    * 1. Remove the inheritance of text transform in Firefox.
    */
   button,
   select {
     /* 1 */
     text-transform: none;
   }
   
   /**
    * Correct the inability to style clickable types in iOS and Safari.
    */
   button,
   [type="button"],
   [type="reset"],
   [type="submit"] {
   webkit-appearance: button;
   }
   
   /**
    * Remove the inner border and padding in Firefox.
    */
   button::-moz-focus-inner,
   [type="button"]::-moz-focus-inner,
   [type="reset"]::-moz-focus-inner,
   [type="submit"]::-moz-focus-inner {
     border-style: none;
     padding: 0;
   }
   
   /**
    * Restore the focus styles unset by the previous rule.
    */
   button:-moz-focusring,
   [type="button"]:-moz-focusring,
   [type="reset"]:-moz-focusring,
   [type="submit"]:-moz-focusring {
     outline: 1px dotted ButtonText;
   }
   
   /**
    * Correct the padding in Firefox.
    */
   fieldset {
     padding: 0.35em 0.75em 0.625em;
   }
   
   /**
    * 1. Correct the text wrapping in Edge and IE.
    * 2. Correct the color inheritance from `fieldset` elements in IE.
    * 3. Remove the padding so developers are not caught out when they zero out
    *    `fieldset` elements in all browsers.
    */
   legend {
     box-sizing: border-box;
     /* 1 */
     color: inherit;
     /* 2 */
     display: table;
     /* 1 */
     max-width: 100%;
     /* 1 */
     padding: 0;
     /* 3 */
     white-space: normal;
     /* 1 */
   }
   
   /**
    * Add the correct vertical alignment in Chrome, Firefox, and Opera.
    */
   progress {
     vertical-align: baseline;
   }
   
   /**
    * Remove the default vertical scrollbar in IE 10+.
    */
   textarea {
     overflow: auto;
   }
   
   /**
    * 1. Add the correct box sizing in IE 10.
    * 2. Remove the padding in IE 10.
    */
   [type="checkbox"],
   [type="radio"] {
     box-sizing: border-box;
     /* 1 */
     padding: 0;
     /* 2 */
   }
   
   /**
    * Correct the cursor style of increment and decrement buttons in Chrome.
    */
   [type="number"]::-webkit-inner-spin-button,
   [type="number"]::-webkit-outer-spin-button {
     height: auto;
   }
   
   /**
    * 1. Correct the odd appearance in Chrome and Safari.
    * 2. Correct the outline style in Safari.
    */
   [type="search"] {
     -webkit-appearance: textfield;
     /* 1 */
     outline-offset: -2px;
     /* 2 */
   }
   
   /**
    * Remove the inner padding in Chrome and Safari on macOS.
    */
   [type="search"]::-webkit-search-decoration {
     -webkit-appearance: none;
   }
   
   /**
    * 1. Correct the inability to style clickable types in iOS and Safari.
    * 2. Change font properties to `inherit` in Safari.
    */
   ::-webkit-file-upload-button {
     -webkit-appearance: button;
     /* 1 */
     font: inherit;
     /* 2 */
   }
   
   /* Interactive
      ========================================================================== */
   /*
    * Add the correct display in Edge, IE 10+, and Firefox.
    */
   details {
     display: block;
   }
   
   /*
    * Add the correct display in all browsers.
    */
   summary {
     display: list-item;
   }
   
   /* Misc
      ========================================================================== */
   /**
    * Add the correct display in IE 10+.
    */
   template {
     display: none;
   }
   
   /**
    * Add the correct display in IE 10.
    */
   [hidden] {
     display: none;
   }
   
   * {
     box-sizing: border-box;
   }
   
   body {
     color: #333;
     font: 14px/1.4 "Helvetica Neue", Helvetica, Arial, "Microsoft Yahei", "Hiragino Sans GB", "Heiti SC", "WenQuanYi Micro Hei", sans-serif;
   }
   
   ul, h1, h3, h4, p, dl, dd {
     padding: 0;
     margin: 0;
   }
   
   a {
     text-decoration: none;
     color: #333;
   }
   
   i {
     font-style: normal;
   }
   
   input {
     outline: none;
     padding: 0;
     border: none;
   }
   
   img {
     max-width: 100%;
     max-height: 100%;
     vertical-align: middle;
   }
   
   ul {
     list-style: none;
   }
   
   .clearfix:before,
   .clearfix:after {
     content: " ";
     display: table;
   }
   
   .clearfix:after {
     clear: both;
   }
   
   .clearfix {
     zoom: 1;
   }
   
   .wrapper {
     width: 1240px;
     margin: 0 auto;
   }
   
   .sprites {
     background-image: url(../images/sprites.png);
     background-size: 400px 400px;
     background-repeat: no-repeat;
   }
   
   .fl {
     float: left;
   }
   
   .fr {
     float: right;
   }
   
   .tc {
     text-align: center;
   }
   
   .green {
     color: #27BA9B;
   }
   
   .red {
     color: #CF4444;
   }
   
   .mb10 {
     margin-bottom: 10px;
   }
   
   .fz20 {
     font-size: 20px;
   }
   
   .fz18 {
     font-size: 18px;
   }
   
   .fz16 {
     font-size: 16px;
   }
   
   .xtx-bread {
     padding: 10px 0 25px 25px;
   }
   
   .xtx-bread a {
     color: #999;
     padding-right: 5px;
   }
   
   .xtx-bread a:hover {
     color: #27BA9B;
   }
   
   .xtx-common-btn {
     width: 180px;
     height: 50px;
     border-radius: 4px;
     text-align: center;
     line-height: 48px;
     font-size: 16px;
     color: #FFFFFF;
     display: inline-block;
   }
   
   .xtx-common-btn[type="primary"] {
     background: #27BA9B;
   }
   
   .xtx-common-btn[type="info"] {
     background: #CCCCCC;
   }
   
   .xtx-check {
     color: #999;
     line-height: 30px;
     cursor: pointer;
   }
   
   .xtx-check i {
     vertical-align: middle;
   }
   
   .xtx-check i.icon-yixuanze {
     color: #27BA9B;
     display: none;
   }
   
   .xtx-check i.icon-weixuanze {
     color: #999;
   }
   
   .xtx-check span {
     vertical-align: middle;
   }
   
   .xtx-check input {
     display: none;
   }
   
   .xtx-check input:checked ~ span {
     color: #27BA9B;
   }
   
   .xtx-check input:checked ~ i.icon-yixuanze {
     display: inline-block;
   }
   
   .xtx-check input:checked ~ i.icon-weixuanze {
     display: none;
   }
   
   /** 顶部导航 **/
   .xtx_topnav {
     background-color: #333;
   }
   
   .xtx_topnav .xtx_navs {
     height: 53px;
     text-align: right;
     line-height: 53px;
     font-size: 0;
   }
   
   .xtx_topnav .xtx_navs li {
     display: inline-block;
     font-size: 14px;
   }
   
   .xtx_topnav .xtx_navs li:last-child a {
     border-right: none;
   }
   
   .xtx_topnav .xtx_navs .mobile {
     display: inline-block;
     width: 20px;
     height: 16px;
     position: relative;
     top: 3px;
     background-position: -160px -70px;
   }
   
   .xtx_topnav .xtx_navs a {
     display: inline-block;
     line-height: 1;
     padding: 0 15px;
     border-right: 2px solid #666666;
     color: #dcdcdc;
   }
   
   .xtx_topnav .xtx_navs a:hover {
     color: #27BA9B;
   }
   
   /** 主导航及Logo **/
   .xtx_header .wrapper {
     display: flex;
     align-items: center;
   }
   
   .xtx_header .xtx_logo {
     width: 200px;
     height: 132px;
     text-indent: -999px;
     background-image: url(../images/logo.png);
     background-size: contain;
     background-repeat: no-repeat;
     background-position-x: center;
     background-position-y: 20px;
   }
   
   .xtx_header .xtx_navs {
     padding-left: 50px;
   }
   
   .xtx_header .xtx_navs li {
     line-height: 1;
     font-size: 16px;
     margin-right: 50px;
     position: relative;
     float: left;
   }
   
   .xtx_header .xtx_navs li:after {
     content: '';
     display: none;
     width: 30px;
     height: 2px;
     background-color: #27BA9B;
     position: absolute;
     left: 1px;
     bottom: -7px;
   }
   
   .xtx_header .xtx_navs li:hover a, .xtx_header .xtx_navs li.active a {
     color: #27BA9B;
   }
   
   .xtx_header .xtx_navs li:hover:after, .xtx_header .xtx_navs li.active:after {
     display: block;
   }
   
   .xtx_header .xtx_search {
     height: 38px;
     padding-left: 20px;
   }
   
   .xtx_header .xtx_search_wrapper {
     width: 175px;
     height: 38px;
     padding-left: 39px;
     border-bottom: 1px solid #e7e7e7;
     position: relative;
     float: right;
   }
   
   .xtx_header .xtx_search_wrapper:before {
     content: '';
     display: block;
     width: 17px;
     height: 17px;
     position: absolute;
     left: 5px;
     top: 10px;
     background-image: url(../images/sprites.png);
     background-size: 400px 400px;
     background-position: -80px -70px;
   }
   
   .xtx_header .xtx_search_wrapper input {
     width: 100%;
     height: 100%;
     font-size: 15px;
     color: #999;
   }
   
   .xtx_header .xtx_search_wrapper input::-webkit-input-placeholder {
     color: #ccc;
   }
   
   .xtx_header .xtx_search_cart {
     display: block;
     width: 22px;
     height: 22px;
     position: relative;
     margin: 8px 12px 0 12px;
     float: right;
     background-position: -120px -70px;
   }
   
   .xtx_header .xtx_search_cart i {
     position: absolute;
     top: -5px;
     left: 16px;
     line-height: 1;
     padding: 1px 6px;
     font-style: normal;
     font-size: 13px;
     background-color: #E26237;
     border-radius: 15px;
     color: #fff;
   }
   
   /** 公共底部 **/
   .xtx_footer .contact {
     padding: 60px 0 40px 25px;
   }
   
   .xtx_footer .contact dl {
     height: 190px;
     text-align: center;
     padding: 0 72px;
     border-right: 1px solid #f2f2f2;
     color: #999;
     float: left;
   }
   
   .xtx_footer .contact dl:first-child {
     padding-left: 0;
   }
   
   .xtx_footer .contact dl:last-child {
     border-right: none;
     padding-right: 0;
   }
   
   .xtx_footer .contact dt {
     line-height: 1;
     font-size: 18px;
   }
   
   .xtx_footer .contact dd {
     margin: 36px 12px 0 0;
     float: left;
   }
   
   .xtx_footer .contact dd:last-child {
     margin-right: 0;
   }
   
   .xtx_footer .contact .chat, .xtx_footer .contact .feedback, .xtx_footer .contact .weixin, .xtx_footer .contact .weibo {
     width: 92px;
     height: 92px;
     padding-top: 20px;
     border: 1px solid #ededed;
   }
   
   .xtx_footer .contact .chat:before, .xtx_footer .contact .feedback:before, .xtx_footer .contact .weixin:before, .xtx_footer .contact .weibo:before {
     content: '';
     display: block;
     width: 40px;
     height: 30px;
     margin: 0 auto 8px;
     background-image: url(../images/sprites.png);
     background-size: 400px 400px;
   }
   
   .xtx_footer .contact .chat:before {
     background-position: -245px -70px;
   }
   
   .xtx_footer .contact .chat:hover:before {
     background-position: -200px -70px;
   }
   
   .xtx_footer .contact .feedback:before {
     background-position: -345px -70px;
   }
   
   .xtx_footer .contact .feedback:hover:before {
     background-position: -295px -70px;
   }
   
   .xtx_footer .contact .weixin:before {
     background-position: -247px -15px;
   }
   
   .xtx_footer .contact .weixin:hover:before {
     background-position: -202px -15px;
   }
   
   .xtx_footer .contact .weibo:before {
     background-position: -347px -15px;
   }
   
   .xtx_footer .contact .weibo:hover:before {
     background-position: -297px -15px;
   }
   
   .xtx_footer .contact .qrcode {
     width: 92px;
     height: 92px;
     padding: 7px;
     border: 1px solid #ededed;
   }
   
   .xtx_footer .contact .download {
     padding-top: 5px;
     font-size: 14px;
   }
   
   .xtx_footer .contact .download span {
     display: block;
   }
   
   .xtx_footer .contact .download a {
     display: block;
     line-height: 1;
     padding: 10px 25px;
     margin-top: 5px;
     color: #fff;
     border-radius: 2px;
     background-color: #27BA9B;
   }
   
   .xtx_footer .contact .hotline {
     padding-top: 20px;
     font-size: 22px;
     color: #666;
   }
   
   .xtx_footer .contact .hotline small {
     display: block;
     font-size: 15px;
     color: #999;
   }
   
   .xtx_footer .extra {
     background-color: #333;
   }
   
   .xtx_footer .slogan {
     height: 178px;
     line-height: 58px;
     padding: 60px 100px;
     border-bottom: 1px solid #434343;
     text-align: justify;
   }
   
   .xtx_footer .slogan:after {
     content: '';
     display: inline-block;
     width: 100%;
     height: 0;
   }
   
   .xtx_footer .slogan a {
     display: inline-block;
     height: 58px;
     line-height: 58px;
     color: #fff;
     font-size: 28px;
   }
   
   .xtx_footer .slogan a:before {
     content: '';
     width: 58px;
     height: 58px;
     margin-right: 10px;
     float: left;
     background-image: url(../images/sprites.png);
     background-size: 400px 400px;
   }
   
   .xtx_footer .slogan .price:before {
     background-position: 0 0;
   }
   
   .xtx_footer .slogan .express:before {
     background-position: -65px 0;
   }
   
   .xtx_footer .slogan .quality:before {
     background-position: -130px 0;
   }
   
   .xtx_footer .copyright {
     height: 170px;
     padding-top: 40px;
     text-align: center;
     color: #999;
     font-size: 15px;
   }
   
   .xtx_footer .copyright p {
     line-height: 1;
     margin-bottom: 20px;
   }
   
   .xtx_footer .copyright a {
     color: #999;
     line-height: 1;
     padding: 0 10px 0 6px;
     border-right: 1px solid #999;
   }
   
   .xtx_footer .copyright a:last-child {
     border-right: none;
   }
   
   ```
   
   以下是common.css的代码
   
   ```css
   @charset "UTF-8";
   /*! normalize.css v8.0.1 | MIT License | github.com/necolas/normalize.css */
   /* Document
      ========================================================================== */
   /**
    * 1. Correct the line height in all browsers.
    * 2. Prevent adjustments of font size after orientation changes in iOS.
    */
   html {
     line-height: 1.15;
     /* 1 */
     -webkit-text-size-adjust: 100%;
     /* 2 */
   }
   
   /* Sections
      ========================================================================== */
   /**
    * Remove the margin in all browsers.
    */
   body {
     margin: 0;
   }
   
   /**
    * Render the `main` element consistently in IE.
    */
   main {
     display: block;
   }
   
   /**
    * Correct the font size and margin on `h1` elements within `section` and
    * `article` contexts in Chrome, Firefox, and Safari.
    */
   h1 {
     font-size: 2em;
     margin: 0.67em 0;
   }
   
   /* Grouping content
      ========================================================================== */
   /**
    * 1. Add the correct box sizing in Firefox.
    * 2. Show the overflow in Edge and IE.
    */
   hr {
     box-sizing: content-box;
     /* 1 */
     height: 0;
     /* 1 */
     overflow: visible;
     /* 2 */
   }
   
   /**
    * 1. Correct the inheritance and scaling of font size in all browsers.
    * 2. Correct the odd `em` font sizing in all browsers.
    */
   pre {
     font-family: monospace, monospace;
     /* 1 */
     font-size: 1em;
     /* 2 */
   }
   
   /* Text-level semantics
      ========================================================================== */
   /**
    * Remove the gray background on active links in IE 10.
    */
   a {
     background-color: transparent;
   }
   
   /**
    * 1. Remove the bottom border in Chrome 57-
    * 2. Add the correct text decoration in Chrome, Edge, IE, Opera, and Safari.
    */
   abbr[title] {
     border-bottom: none;
     /* 1 */
     text-decoration: underline;
     /* 2 */
     text-decoration: underline dotted;
     /* 2 */
   }
   
   /**
    * Add the correct font weight in Chrome, Edge, and Safari.
    */
   b,
   strong {
     font-weight: bolder;
   }
   
   /**
    * 1. Correct the inheritance and scaling of font size in all browsers.
    * 2. Correct the odd `em` font sizing in all browsers.
    */
   code,
   kbd,
   samp {
     font-family: monospace, monospace;
     /* 1 */
     font-size: 1em;
     /* 2 */
   }
   
   /**
    * Add the correct font size in all browsers.
    */
   small {
     font-size: 80%;
   }
   
   /**
    * Prevent `sub` and `sup` elements from affecting the line height in
    * all browsers.
    */
   sub,
   sup {
     font-size: 75%;
     line-height: 0;
     position: relative;
     vertical-align: baseline;
   }
   
   sub {
     bottom: -0.25em;
   }
   
   sup {
     top: -0.5em;
   }
   
   /* Embedded content
      ========================================================================== */
   /**
    * Remove the border on images inside links in IE 10.
    */
   img {
     border-style: none;
   }
   
   /* Forms
      ========================================================================== */
   /**
    * 1. Change the font styles in all browsers.
    * 2. Remove the margin in Firefox and Safari.
    */
   button,
   input,
   optgroup,
   select,
   textarea {
     font-family: inherit;
     /* 1 */
     font-size: 100%;
     /* 1 */
     line-height: 1.15;
     /* 1 */
     margin: 0;
     /* 2 */
   }
   
   /**
    * Show the overflow in IE.
    * 1. Show the overflow in Edge.
    */
   button,
   input {
     /* 1 */
     overflow: visible;
   }
   
   /**
    * Remove the inheritance of text transform in Edge, Firefox, and IE.
    * 1. Remove the inheritance of text transform in Firefox.
    */
   button,
   select {
     /* 1 */
     text-transform: none;
   }
   
   /**
    * Correct the inability to style clickable types in iOS and Safari.
    */
   button,
   [type="button"],
   [type="reset"],
   [type="submit"] {
   webkit-appearance: button;
   }
   
   /**
    * Remove the inner border and padding in Firefox.
    */
   button::-moz-focus-inner,
   [type="button"]::-moz-focus-inner,
   [type="reset"]::-moz-focus-inner,
   [type="submit"]::-moz-focus-inner {
     border-style: none;
     padding: 0;
   }
   
   /**
    * Restore the focus styles unset by the previous rule.
    */
   button:-moz-focusring,
   [type="button"]:-moz-focusring,
   [type="reset"]:-moz-focusring,
   [type="submit"]:-moz-focusring {
     outline: 1px dotted ButtonText;
   }
   
   /**
    * Correct the padding in Firefox.
    */
   fieldset {
     padding: 0.35em 0.75em 0.625em;
   }
   
   /**
    * 1. Correct the text wrapping in Edge and IE.
    * 2. Correct the color inheritance from `fieldset` elements in IE.
    * 3. Remove the padding so developers are not caught out when they zero out
    *    `fieldset` elements in all browsers.
    */
   legend {
     box-sizing: border-box;
     /* 1 */
     color: inherit;
     /* 2 */
     display: table;
     /* 1 */
     max-width: 100%;
     /* 1 */
     padding: 0;
     /* 3 */
     white-space: normal;
     /* 1 */
   }
   
   /**
    * Add the correct vertical alignment in Chrome, Firefox, and Opera.
    */
   progress {
     vertical-align: baseline;
   }
   
   /**
    * Remove the default vertical scrollbar in IE 10+.
    */
   textarea {
     overflow: auto;
   }
   
   /**
    * 1. Add the correct box sizing in IE 10.
    * 2. Remove the padding in IE 10.
    */
   [type="checkbox"],
   [type="radio"] {
     box-sizing: border-box;
     /* 1 */
     padding: 0;
     /* 2 */
   }
   
   /**
    * Correct the cursor style of increment and decrement buttons in Chrome.
    */
   [type="number"]::-webkit-inner-spin-button,
   [type="number"]::-webkit-outer-spin-button {
     height: auto;
   }
   
   /**
    * 1. Correct the odd appearance in Chrome and Safari.
    * 2. Correct the outline style in Safari.
    */
   [type="search"] {
     -webkit-appearance: textfield;
     /* 1 */
     outline-offset: -2px;
     /* 2 */
   }
   
   /**
    * Remove the inner padding in Chrome and Safari on macOS.
    */
   [type="search"]::-webkit-search-decoration {
     -webkit-appearance: none;
   }
   
   /**
    * 1. Correct the inability to style clickable types in iOS and Safari.
    * 2. Change font properties to `inherit` in Safari.
    */
   ::-webkit-file-upload-button {
     -webkit-appearance: button;
     /* 1 */
     font: inherit;
     /* 2 */
   }
   
   /* Interactive
      ========================================================================== */
   /*
    * Add the correct display in Edge, IE 10+, and Firefox.
    */
   details {
     display: block;
   }
   
   /*
    * Add the correct display in all browsers.
    */
   summary {
     display: list-item;
   }
   
   /* Misc
      ========================================================================== */
   /**
    * Add the correct display in IE 10+.
    */
   template {
     display: none;
   }
   
   /**
    * Add the correct display in IE 10.
    */
   [hidden] {
     display: none;
   }
   
   * {
     box-sizing: border-box;
   }
   
   body {
     color: #333;
     font: 14px/1.4 "Helvetica Neue", Helvetica, Arial, "Microsoft Yahei", "Hiragino Sans GB", "Heiti SC", "WenQuanYi Micro Hei", sans-serif;
   }
   
   ul, h1, h3, h4, p, dl, dd {
     padding: 0;
     margin: 0;
   }
   
   a {
     text-decoration: none;
     color: #333;
   }
   
   i {
     font-style: normal;
   }
   
   input {
     outline: none;
     padding: 0;
     border: none;
   }
   
   img {
     max-width: 100%;
     max-height: 100%;
     vertical-align: middle;
   }
   
   ul {
     list-style: none;
   }
   
   .clearfix:before,
   .clearfix:after {
     content: " ";
     display: table;
   }
   
   .clearfix:after {
     clear: both;
   }
   
   .clearfix {
     zoom: 1;
   }
   
   .wrapper {
     width: 1240px;
     margin: 0 auto;
   }
   
   .sprites {
     background-image: url(../images/sprites.png);
     background-size: 400px 400px;
     background-repeat: no-repeat;
   }
   
   .fl {
     float: left;
   }
   
   .fr {
     float: right;
   }
   
   .tc {
     text-align: center;
   }
   
   .green {
     color: #27BA9B;
   }
   
   .red {
     color: #CF4444;
   }
   
   .mb10 {
     margin-bottom: 10px;
   }
   
   .fz20 {
     font-size: 20px;
   }
   
   .fz18 {
     font-size: 18px;
   }
   
   .fz16 {
     font-size: 16px;
   }
   
   .xtx-bread {
     padding: 10px 0 25px 25px;
   }
   
   .xtx-bread a {
     color: #999;
     padding-right: 5px;
   }
   
   .xtx-bread a:hover {
     color: #27BA9B;
   }
   
   .xtx-common-btn {
     width: 180px;
     height: 50px;
     border-radius: 4px;
     text-align: center;
     line-height: 48px;
     font-size: 16px;
     color: #FFFFFF;
     display: inline-block;
   }
   
   .xtx-common-btn[type="primary"] {
     background: #27BA9B;
   }
   
   .xtx-common-btn[type="info"] {
     background: #CCCCCC;
   }
   
   .xtx-check {
     color: #999;
     line-height: 30px;
     cursor: pointer;
   }
   
   .xtx-check i {
     vertical-align: middle;
   }
   
   .xtx-check i.icon-yixuanze {
     color: #27BA9B;
     display: none;
   }
   
   .xtx-check i.icon-weixuanze {
     color: #999;
   }
   
   .xtx-check span {
     vertical-align: middle;
   }
   
   .xtx-check input {
     display: none;
   }
   
   .xtx-check input:checked ~ span {
     color: #27BA9B;
   }
   
   .xtx-check input:checked ~ i.icon-yixuanze {
     display: inline-block;
   }
   
   .xtx-check input:checked ~ i.icon-weixuanze {
     display: none;
   }
   
   /** 顶部导航 **/
   .xtx_topnav {
     background-color: #333;
   }
   
   .xtx_topnav .xtx_navs {
     height: 53px;
     text-align: right;
     line-height: 53px;
     font-size: 0;
   }
   
   .xtx_topnav .xtx_navs li {
     display: inline-block;
     font-size: 14px;
   }
   
   .xtx_topnav .xtx_navs li:last-child a {
     border-right: none;
   }
   
   .xtx_topnav .xtx_navs .mobile {
     display: inline-block;
     width: 20px;
     height: 16px;
     position: relative;
     top: 3px;
     background-position: -160px -70px;
   }
   
   .xtx_topnav .xtx_navs a {
     display: inline-block;
     line-height: 1;
     padding: 0 15px;
     border-right: 2px solid #666666;
     color: #dcdcdc;
   }
   
   .xtx_topnav .xtx_navs a:hover {
     color: #27BA9B;
   }
   
   /** 主导航及Logo **/
   .xtx_header .wrapper {
     display: flex;
     align-items: center;
   }
   
   .xtx_header .xtx_logo {
     width: 200px;
     height: 132px;
     text-indent: -999px;
     background-image: url(../images/logo.png);
     background-size: contain;
     background-repeat: no-repeat;
     background-position-x: center;
     background-position-y: 20px;
   }
   
   .xtx_header .xtx_navs {
     padding-left: 50px;
   }
   
   .xtx_header .xtx_navs li {
     line-height: 1;
     font-size: 16px;
     margin-right: 50px;
     position: relative;
     float: left;
   }
   
   .xtx_header .xtx_navs li:after {
     content: '';
     display: none;
     width: 30px;
     height: 2px;
     background-color: #27BA9B;
     position: absolute;
     left: 1px;
     bottom: -7px;
   }
   
   .xtx_header .xtx_navs li:hover a, .xtx_header .xtx_navs li.active a {
     color: #27BA9B;
   }
   
   .xtx_header .xtx_navs li:hover:after, .xtx_header .xtx_navs li.active:after {
     display: block;
   }
   
   .xtx_header .xtx_search {
     height: 38px;
     padding-left: 20px;
   }
   
   .xtx_header .xtx_search_wrapper {
     width: 175px;
     height: 38px;
     padding-left: 39px;
     border-bottom: 1px solid #e7e7e7;
     position: relative;
     float: right;
   }
   
   .xtx_header .xtx_search_wrapper:before {
     content: '';
     display: block;
     width: 17px;
     height: 17px;
     position: absolute;
     left: 5px;
     top: 10px;
     background-image: url(../images/sprites.png);
     background-size: 400px 400px;
     background-position: -80px -70px;
   }
   
   .xtx_header .xtx_search_wrapper input {
     width: 100%;
     height: 100%;
     font-size: 15px;
     color: #999;
   }
   
   .xtx_header .xtx_search_wrapper input::-webkit-input-placeholder {
     color: #ccc;
   }
   
   .xtx_header .xtx_search_cart {
     display: block;
     width: 22px;
     height: 22px;
     position: relative;
     margin: 8px 12px 0 12px;
     float: right;
     background-position: -120px -70px;
   }
   
   .xtx_header .xtx_search_cart i {
     position: absolute;
     top: -5px;
     left: 16px;
     line-height: 1;
     padding: 1px 6px;
     font-style: normal;
     font-size: 13px;
     background-color: #E26237;
     border-radius: 15px;
     color: #fff;
   }
   
   /** 公共底部 **/
   .xtx_footer .contact {
     padding: 60px 0 40px 25px;
   }
   
   .xtx_footer .contact dl {
     height: 190px;
     text-align: center;
     padding: 0 72px;
     border-right: 1px solid #f2f2f2;
     color: #999;
     float: left;
   }
   
   .xtx_footer .contact dl:first-child {
     padding-left: 0;
   }
   
   .xtx_footer .contact dl:last-child {
     border-right: none;
     padding-right: 0;
   }
   
   .xtx_footer .contact dt {
     line-height: 1;
     font-size: 18px;
   }
   
   .xtx_footer .contact dd {
     margin: 36px 12px 0 0;
     float: left;
   }
   
   .xtx_footer .contact dd:last-child {
     margin-right: 0;
   }
   
   .xtx_footer .contact .chat, .xtx_footer .contact .feedback, .xtx_footer .contact .weixin, .xtx_footer .contact .weibo {
     width: 92px;
     height: 92px;
     padding-top: 20px;
     border: 1px solid #ededed;
   }
   
   .xtx_footer .contact .chat:before, .xtx_footer .contact .feedback:before, .xtx_footer .contact .weixin:before, .xtx_footer .contact .weibo:before {
     content: '';
     display: block;
     width: 40px;
     height: 30px;
     margin: 0 auto 8px;
     background-image: url(../images/sprites.png);
     background-size: 400px 400px;
   }
   
   .xtx_footer .contact .chat:before {
     background-position: -245px -70px;
   }
   
   .xtx_footer .contact .chat:hover:before {
     background-position: -200px -70px;
   }
   
   .xtx_footer .contact .feedback:before {
     background-position: -345px -70px;
   }
   
   .xtx_footer .contact .feedback:hover:before {
     background-position: -295px -70px;
   }
   
   .xtx_footer .contact .weixin:before {
     background-position: -247px -15px;
   }
   
   .xtx_footer .contact .weixin:hover:before {
     background-position: -202px -15px;
   }
   
   .xtx_footer .contact .weibo:before {
     background-position: -347px -15px;
   }
   
   .xtx_footer .contact .weibo:hover:before {
     background-position: -297px -15px;
   }
   
   .xtx_footer .contact .qrcode {
     width: 92px;
     height: 92px;
     padding: 7px;
     border: 1px solid #ededed;
   }
   
   .xtx_footer .contact .download {
     padding-top: 5px;
     font-size: 14px;
   }
   
   .xtx_footer .contact .download span {
     display: block;
   }
   
   .xtx_footer .contact .download a {
     display: block;
     line-height: 1;
     padding: 10px 25px;
     margin-top: 5px;
     color: #fff;
     border-radius: 2px;
     background-color: #27BA9B;
   }
   
   .xtx_footer .contact .hotline {
     padding-top: 20px;
     font-size: 22px;
     color: #666;
   }
   
   .xtx_footer .contact .hotline small {
     display: block;
     font-size: 15px;
     color: #999;
   }
   
   .xtx_footer .extra {
     background-color: #333;
   }
   
   .xtx_footer .slogan {
     height: 178px;
     line-height: 58px;
     padding: 60px 100px;
     border-bottom: 1px solid #434343;
     text-align: justify;
   }
   
   .xtx_footer .slogan:after {
     content: '';
     display: inline-block;
     width: 100%;
     height: 0;
   }
   
   .xtx_footer .slogan a {
     display: inline-block;
     height: 58px;
     line-height: 58px;
     color: #fff;
     font-size: 28px;
   }
   
   .xtx_footer .slogan a:before {
     content: '';
     width: 58px;
     height: 58px;
     margin-right: 10px;
     float: left;
     background-image: url(../images/sprites.png);
     background-size: 400px 400px;
   }
   
   .xtx_footer .slogan .price:before {
     background-position: 0 0;
   }
   
   .xtx_footer .slogan .express:before {
     background-position: -65px 0;
   }
   
   .xtx_footer .slogan .quality:before {
     background-position: -130px 0;
   }
   
   .xtx_footer .copyright {
     height: 170px;
     padding-top: 40px;
     text-align: center;
     color: #999;
     font-size: 15px;
   }
   
   .xtx_footer .copyright p {
     line-height: 1;
     margin-bottom: 20px;
   }
   
   .xtx_footer .copyright a {
     color: #999;
     line-height: 1;
     padding: 0 10px 0 6px;
     border-right: 1px solid #999;
   }
   
   .xtx_footer .copyright a:last-child {
     border-right: none;
   }
   
   ```
   
   以下是product.css的代码：
   
   ```
   .xtx-wrapper {
     background: #f5f5f5;
     line-height: 1.4;
   }
   
   .xtx-wrapper .container {
     width: 1240px;
     margin: 0 auto;
     padding: 20px 0 40px;
   }
   
   .xtx-bread {
     padding: 10px 0 25px 25px;
   }
   
   .xtx-bread a {
     color: #999;
     padding-right: 5px;
   }
   
   .xtx-bread a:hover {
     color: #27BA9B;
   }
   
   .xtx-product-info {
     background: #fff;
     display: flex;
     min-height: 580px;
   }
   
   .xtx-product-info .left {
     width: 580px;
     padding: 30px 50px;
   }
   
   .xtx-product-info .left .pictrue {
     width: 480px;
     height: 400px;
     display: flex;
     position: relative;
   }
   
   .xtx-product-info .left .pictrue .middle {
     width: 400px;
     height: 400px;
     position: relative;
   }
   
   .xtx-product-info .left .pictrue .middle .layer {
     display: none;
     width: 200px;
     height: 200px;
     background-color: rgba(0, 0, 0, 0.3);
     position: absolute;
     left: 0;
     top: 0;
     cursor: move;
   }
   
   .xtx-product-info .left .pictrue .large {
     width: 400px;
     height: 400px;
     box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
     position: absolute;
     left: 412px;
     top: 0;
     z-index: 999;
     background-color: #fff;
     display: none;
     background-image: url(../images/1.jfif);
     background-size: 800px 800px;
   }
   
   .xtx-product-info .left .pictrue .middle img {
     width: 100%;
     height: 100%;
   }
   
   .xtx-product-info .left .pictrue .small {
     width: 80px;
     height: 400px;
   }
   
   .xtx-product-info .left .pictrue .small ul li {
     width: 68px;
     height: 68px;
     margin-bottom: 15px;
     margin-left: 12px;
     border: 2px solid transparent;
   }
   
   .xtx-product-info .left .pictrue .small ul li img {
     width: 100%;
     height: 100%;
   }
   
   .xtx-product-info .left .pictrue .small ul li.active,
   .xtx-product-info .left .pictrue .small ul li:hover {
     border-color: #27BA9B;
   }
   
   .xtx-product-info .left .other {
     margin-top: 20px;
   }
   
   .xtx-product-info .left .other ul {
     display: flex;
     width: 400px;
   }
   
   .xtx-product-info .left .other ul li {
     flex: 1;
     text-align: center;
     position: relative;
     line-height: 32px;
   }
   
   .xtx-product-info .left .other ul li::before {
     content: "";
     position: absolute;
     top: 15px;
     right: 0;
     height: 70px;
     border-right: 1px solid #e4e4e4;
   }
   
   .xtx-product-info .left .other ul li:last-child::before {
     display: none;
   }
   
   .xtx-product-info .left .other ul li p:first-child {
     color: #999;
   }
   
   .xtx-product-info .left .other ul li p:nth-child(2) {
     color: #CF4444;
   }
   
   .xtx-product-info .right {
     width: 660px;
     padding-top: 30px;
   }
   
   .xtx-product-info .right h3 {
     font-size: 22px;
     font-weight: normal;
   }
   
   .xtx-product-info .right .desc {
     padding-top: 10px;
     color: #999;
   }
   
   .xtx-product-info .right .price {
     padding: 10px 0;
   }
   
   .xtx-product-info .right .price .now {
     color: #CF4444;
     margin-right: 5px;
     font-size: 22px;
   }
   
   .xtx-product-info .right .price .old {
     color: #999;
     text-decoration: line-through;
     font-size: 18px;
   }
   
   .xtx-product-info .right .address {
     width: 510px;
     background: #f9f9f9;
     padding: 0 10px 20px;
   }
   
   .xtx-product-info .right .address .fw {
     position: relative;
     padding: 0 15px 0 10px;
   }
   
   .xtx-product-info .right .address .fw::before {
     content: "";
     position: absolute;
     left: 0;
     top: 6px;
     width: 3px;
     height: 3px;
     border-radius: 50%;
     background: #27BA9B;
   }
   
   .xtx-product-info .right .address .lj {
     color: #27BA9B;
   }
   
   .xtx-product-info .right .address .box {
     width: 150px;
     height: 28px;
     border: 1px solid #e4e4e4;
     display: inline-block;
     line-height: 26px;
     text-align: center;
     margin-left: 10px;
     background: #fff;
   }
   
   .xtx-product-info .right .attrs {
     padding: 0 10px;
   }
   
   .xtx-product-info .right .attrs img {
     width: 50px;
     height: 50px;
     margin-right: 10px;
     border: 1px dashed transparent;
     cursor: pointer;
   }
   
   .xtx-product-info .right .attrs img.active,
   .xtx-product-info .right .attrs img:hover {
     border-color: #27BA9B;
   }
   
   .xtx-product-info .right .attrs .size {
     border: 1px solid #e4e4e4;
     padding: 5px 25px;
     display: inline-block;
     margin-right: 6px;
     cursor: pointer;
   }
   
   .xtx-product-info .right .attrs .size.active,
   .xtx-product-info .right .attrs .size:hover {
     border-color: #27BA9B;
   }
   
   .xtx-product-info .right .attrs .num {
     width: 116px;
     height: 28px;
     border: 1px solid #e4e4e4;
     display: flex;
   }
   
   .xtx-product-info .right .attrs .num input {
     border-left: 1px solid #e4e4e4;
     border-right: 1px solid #e4e4e4;
     width: 60px;
     line-height: 26px;
     text-align: center;
     color: #979797;
   }
   
   .xtx-product-info .right .attrs .num a {
     width: 28px;
     text-align: center;
     line-height: 26px;
     color: #979797;
   }
   
   .xtx-product-info .right .item {
     color: #999;
     display: flex;
     padding-top: 20px;
     align-items: center;
   }
   
   .xtx-product-info .right .item .dt {
     width: 50px;
   }
   
   .xtx-product-info .right .item .dd {
     flex: 1;
     color: #666;
   }
   
   .xtx-product-info .right .buy {
     width: 220px;
     height: 50px;
     background: #27BA9B;
     border-radius: 4px;
     display: block;
     color: #fff;
     font-size: 16px;
     text-align: center;
     line-height: 50px;
   }
   
   .xtx-relevant-product {
     background: #fff;
     margin: 20px 0;
     padding: 30px 28px;
     position: relative;
   }
   
   .xtx-relevant-product h3 {
     font-weight: normal;
     font-size: 20px;
     padding-bottom: 8px;
     padding-left: 25px;
   }
   
   .xtx-relevant-product .prev,
   .xtx-relevant-product .next {
     position: absolute;
     top: 200px;
     width: 40px;
     height: 40px;
     line-height: 40px;
     text-align: center;
     color: #dbdbdb;
   }
   
   .xtx-relevant-product .prev span,
   .xtx-relevant-product .next span {
     font-size: 30px;
   }
   
   .xtx-relevant-product .prev {
     left: 0;
   }
   
   .xtx-relevant-product .next {
     right: 0;
   }
   
   .xtx-relevant-product ul {
     display: flex;
     justify-content: space-between;
   }
   
   .xtx-relevant-product ul li {
     width: 278px;
     height: 360px;
     text-align: center;
   }
   
   .xtx-relevant-product ul li img {
     width: 190px;
     height: 190px;
     margin-top: 25px;
   }
   
   .xtx-relevant-product ul li .name {
     font-size: 16px;
     line-height: 40px;
   }
   
   .xtx-relevant-product ul li .desc {
     color: #999;
     line-height: 50px;
   }
   
   .xtx-relevant-product ul li .price {
     color: #CF4444;
     font-size: 18px;
     line-height: 50px;
   }
   
   .xtx-product-detail {
     display: flex;
     justify-content: space-between;
   }
   
   .xtx-product-detail .main {
     width: 942px;
   }
   
   .xtx-product-detail .main .cont {
     background: #fff;
   }
   
   .xtx-product-detail .main .cont .tab-head {
     height: 70px;
     line-height: 70px;
     border-bottom: 1px solid #f5f5f5;
     font-size: 18px;
     padding: 0 20px;
     position: relative;
   }
   
   .xtx-product-detail .main .cont .tab-head a {
     margin-right: 80px;
   }
   
   .xtx-product-detail .main .cont .tab-head a span {
     color: #CF4444;
   }
   
   .xtx-product-detail .main .cont .tab-head::before {
     content: "";
     position: absolute;
     height: 70px;
     width: 1px;
     background: #f5f5f5;
     top: 0;
     left: 135px;
   }
   
   .xtx-product-detail .main .cont .tab-pane .attrs {
     padding: 20px;
     display: flex;
     flex-wrap: wrap;
   }
   
   .xtx-product-detail .main .cont .tab-pane .attrs .item {
     width: 25%;
     display: flex;
     padding-bottom: 10px;
   }
   
   .xtx-product-detail .main .cont .tab-pane .attrs .item span:first-child {
     width: 75px;
     color: #999;
   }
   
   .xtx-product-detail .main .cont .tab-pane .attrs .item span:last-child {
     flex: 1;
     color: #666;
   }
   
   .xtx-product-detail .main .cont .tab-pane .detail {
     padding: 25px;
     text-align: center;
   }
   
   .xtx-product-detail .main .warn {
     margin-top: 20px;
     background: #fff;
     padding-bottom: 40px;
   }
   
   .xtx-product-detail .main .warn h3 {
     height: 80px;
     line-height: 80px;
     border-bottom: 1px solid #f5f5f5;
     padding-left: 50px;
     font-size: 18px;
     font-weight: normal;
     margin-bottom: 10px;
   }
   
   .xtx-product-detail .main .warn p {
     line-height: 40px;
     padding-left: 25px;
     color: #666;
   }
   
   .xtx-product-detail .main .warn p.tit {
     color: #333;
   }
   
   .xtx-product-detail .aside {
     width: 278px;
   }
   
   .xtx-product-detail .aside .tit {
     width: 278px;
     height: 70px;
     background: #E26237;
     color: #fff;
     font-size: 18px;
     line-height: 70px;
     padding-left: 25px;
     margin-bottom: 10px;
   }
   
   .xtx-product-detail .aside .product {
     margin-bottom: 10px;
     background: #fff;
     width: 278px;
     height: 360px;
     text-align: center;
   }
   
   .xtx-product-detail .aside .product img {
     width: 190px;
     height: 190px;
     margin-top: 25px;
   }
   
   .xtx-product-detail .aside .product .name {
     font-size: 16px;
     line-height: 40px;
   }
   
   .xtx-product-detail .aside .product .desc {
     color: #999;
     line-height: 50px;
   }
   
   .xtx-product-detail .aside .product .price {
     color: #CF4444;
     font-size: 18px;
     line-height: 50px;
   }
   
   .xtx-product-detail .aside .special {
     background: #fff;
     text-align: center;
     margin-bottom: 10px;
   }
   
   .xtx-product-detail .aside .special img {
     width: 278px;
     height: 212px;
   }
   
   .xtx-product-detail .aside .special .name {
     font-size: 18px;
     padding: 24px 0;
   }
   ```
   
   

