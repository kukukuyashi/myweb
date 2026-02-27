## 常见“看不见模型”的补充检查

如果修改完代码后，画面还是黑的或者没东西，请检查以下两点：

1.模型比例 (Scale)： Rhino 导出的模型如果单位是毫米，在 Three.js 里会变得巨大无比（你会发现自己在模型“肚子”里，四周都是黑的）。 尝试缩小模型： 在 scene.add(myModel); 前加上 myModel.scale.set(0.01, 0.01, 0.01);。**有可能是模型太小了，在 scene.add(myModel); 前加上 myModel.scale.set(50, 50, 50);**

2.相机位置： 你的相机在 z = 5。如果你的模型中心点不在 (0,0,0) 或者尺寸很大，相机可能拍不到它。 尝试后退相机： 将 camera.position.z = 5; 改成 50 或 100 看看。 **有可能是模型太小了，将 camera.position.z = 5; 改成 1 或 0.1 看看**

3.坐标轴转向： Rhino 是 Z 轴向上。加载后模型可能是躺着的。 尝试旋转： myModel.rotation.x = -Math.PI / 2;