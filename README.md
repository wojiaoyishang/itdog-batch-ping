# itdog 测速网站批量 Ping 节点爬虫脚本

#### 绪言
[itdog.cn](https://www.itdog.cn/) 是一个专注于网络测试与分析的在线工具网站，适合IT专业人员和网络管理员使用。该网站提供了一系列工具，如在线Ping和Tcping测试，支持IPv4和IPv6，帮助用户从不同地区和路线检测网络连接情况。此项目是在我在忙碌的学业之路上写的一个批量爬取 itdog 网站 Ping 数据的爬虫。也许这个是我高中写的最后一个项目了吧？

我原来打算的是使用这个测速网站来自选 Cloudflare 节点的，不知道还有没有时间将这个项目和 ddgth 大佬的项目 [cf2dns](https://github.com/ddgth/cf2dns) 联动起来。因为 ddgth 大佬的项目中的获取优质 Cloudflare 节点的算法是未开源的，而是通过请求网络 API 的方式从别的服务器获取 Cloudflare 节点。如果我学有余力，我会尝试去联动一下。ψ(*｀ー´)ψ

#### 爬虫分析

![输入图片说明](IMAGES/image1.png)

当用户请求 IP 测速的时候，网页会提交 POST 表单到当前网页 `https://www.itdog.cn/batch_ping/` 。随后，网页会请求 websocket 链接到服务器进行测速。

通过抓包，我们可以找出网页（客户端）与服务器的交互：

![输入图片说明](IMAGES/image2.png)

请求中的 `task_id` 我们是已知的，关键是要找出 `task_token` 的生成方式。略去过程， `task_token` 生成规则如下：

将提供的 `task_id` 加上一段不变的文本 `token_20230313000136kwyktxb0tgspm00yo5`，最后结果取 md5 16位小就是 `task_token` 了。下面是分析的过程：

网页创建 websocket 时会调用自定义函数 `create_websocket`，找出函数出自 js 文件 `https://www.itdog.cn/frame/js/pages/batch_ping.js`，通过浏览器的自动整理后如下：

![输入图片说明](IMAGES/image3.png)

`create_websocket` 函数被混淆了，不过我们还是可以看出一些端倪：

![输入图片说明](IMAGES/image4.png)

上述是与服务器通讯的主要地方，通过 Fiddler 抓包篡改代码，加入一段 `console.log` 看看到底通讯的什么，以便于我们定位函数。已知的坑如下：

+ 尝试将全部代码格式化并篡改，网页无法正常加载，已知卡在加载的时候，阻塞浏览器。*可以通过仅格式化函数 `create_websocket` 解决。*
+ 尝试使用 `console.log` 输出内容，结果发现 `console.log` 被重写了。*可以通过在代码最开头加上 window.console_log = console.log 提前保留输出函数。*

最后，是分析到请求时会将 `task_id` 加上一个固定字符串 `token_20230313000136kwyktxb0tgspm00yo5` 并取 `md5` 获取 `task_token`。

当然，这个 `task_token` 生成方法并非一直有效，依赖于固定字符串 `token_20230313000136kwyktxb0tgspm00yo5` 是否变化，因为这个字符串清晰标明了“token_2023”估计会在2024年重新设置。代码中定位 `token_2023` 你会找到：

![输入图片说明](IMAGES/image5.png)

这个至少当前是固定不变的。想研究的同学 `batch_ping.js` 样本已经放置在仓库的 `JavaScript_sample` 目录下。

***重要：batch_ping.js 在 2023/12/23 似乎重新混淆了代码，但是并不影响先前的爬虫算法。文章的配图是 2023/12/23 版本的代码。***
