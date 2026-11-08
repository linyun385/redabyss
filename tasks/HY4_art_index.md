# HY4 任务：维护者卡图索引

**目的**：把 47 张维护者卡图逐张翻译成一句文字描述，做成索引表。
之后定稿新卡时，照这张表挑图，不用重新看图。

## 边界（先读这段）

| 允许 | 禁止 |
|---|---|
| 读这些 webp，写一句描述 | 改任何文件（图片、json、html 都不许动）|
| 指出某张图看不清 | 判断「这张图该配哪张卡」——那是我的活 |
| 写「未识别」 | 编造图里没有的东西 |

## 输出格式

存成一份 CSV，UTF-8 无 BOM，两列，不要表头以外的多余列：

```
id,描述
anm_0001,"洞穴中一把红色工具，握把缠白色布条，插在地上"
```

描述规矩：

1. **只写图里看得见的**：主体是什么、材质、姿态/朝向、背景、光从哪来
2. 一句，不超过 40 字，不写形容词堆砌，不写寓意
3. 不出现「似乎」「可能」「象征着」这类猜测词
4. 看不清就说「画面模糊/抽象，仅见红色团块」——**别硬猜**

## 要处理的 47 张

目录：`C:\Users\Administrator\Desktop\杂七杂八\红渊\game\web\assets\art`

| # | id | 卡名 | 稀有度 | 主脉 |
|---|---|---|---|---|
| 1 | anm_0001 | 现场回收 | common | mineral |
| 2 | anm_0002 | 扳手规程 | common | mineral |
| 3 | anm_0003 | 备用照明电池 | common | light |
| 4 | anm_0004 | 例检条款 | common | mineral |
| 5 | anm_0006 | 库存盘点 | common | mineral |
| 6 | anm_0007 | 调节螺栓 | common | mineral |
| 7 | anm_0008 | 报废清单 | common | mineral |
| 8 | anm_0009 | 料仓取件 | common | mineral |
| 9 | anm_0010 | 应急照明协议 | uncommon | light |
| 10 | anm_0011 | 焊接臂·民用型 | uncommon | heat |
| 11 | anm_0012 | 维修凝胶 | uncommon | water |
| 12 | anm_0013 | 料径校准 | uncommon | mineral |
| 13 | anm_0014 | 巡逻体残骸 | uncommon | mineral |
| 14 | anm_0015 | 主控授权·工程线 | rare | mineral |
| 15 | anm_0016 | 主控授权·安全线 | rare | mineral |
| 16 | anm_0017 | 回收协议·总则 | rare | mineral |
| 17 | anm_0018 | 威胁等级·评估员 | rare | mineral |
| 18 | anm_0019 | 例检手套 | special | mineral |
| 19 | anm_0020 | 协议：静默段 | uncommon | mineral |
| 20 | anm_0021 | 协议：优先级翻转 | common | tremor |
| 21 | anm_0022 | 协议：保运行 | common | water |
| 22 | anm_0023 | 协议：信息隔离 | uncommon | light |
| 23 | anm_0024 | 协议：库存封存 | uncommon | mineral |
| 24 | anm_0025 | 协议：终端确认 | uncommon | mineral |
| 25 | anm_0026 | 协议：最小代价原则 | rare | water |
| 26 | anm_0027 | 协议：静默段·延长 | rare | mineral |
| 27 | anm_0028 | 协议：注销 | special | mineral |
| 28 | anm_0029 | 氧气核算 | common | water |
| 29 | anm_0030 | 运料车残骸 | common | mineral |
| 30 | anm_0031 | 缓冲库存 | common | water |
| 31 | anm_0032 | 闭环利用 | common | water |
| 32 | anm_0033 | 血统册摘录 | common | light |
| 33 | anm_0035 | 超频保养 | uncommon | heat |
| 34 | anm_0036 | 保运行批文 | uncommon | water |
| 35 | anm_0037 | 动用储备 | uncommon | mineral |
| 36 | anm_0039 | 菌婪者组织样本 | uncommon | water |
| 37 | anm_0040 | 协议：例外条款 | rare | water |
| 38 | anm_0041 | 保运行优先级 | rare | water |
| 39 | anm_0042 | 基因修复台 | rare | light |
| 40 | anm_0043 | 静默段徵章 | special | tremor |
| 41 | anm_0044 | 死者的工号牌 | common | mineral |
| 42 | anm_0045 | 读图纸的人 | common | light |
| 43 | anm_0046 | 例检清单（残） | common | mineral |
| 44 | anm_0047 | 通风守卫·代班 | common | tremor |
| 45 | anm_0048 | 运输井规程 | uncommon | tremor |
| 46 | anm_0049 | 撤销程序残片 | rare | light |
| 47 | anm_0050 | 主控密钥（烧毁） | special | light |

合计 **47** 张。

## 验收方式

我随机抽 3 张，自己看图对描述。任一条对不上（编造、张冠李戴），整批退回重做。

★ 卡名**只用于让你知道这批图属于哪个职业**，**不要**拿卡名去反推画面内容——
　旧卡的图和旧卡的机制本来就可能对不上，照着卡名描述等于没看。
