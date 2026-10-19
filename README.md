# CANN 竞赛 BatchMatmulMaxSum 算子

本仓库代码为 CANN 算子挑战赛-上合赛区 初赛 32 强代码及迭代过程。

## 竞赛背景与题目要求

题目要求将批量矩阵乘法、按行取最大值、按行求和融合为一次完整的算子计算。设逻辑输入为 $A \in \mathbb{R}^{B \times M \times K}$、 $X \in \mathbb{R}^{B \times K \times N}$，输出为 $y \in \mathbb{R}^{B}$：

$$
\begin{aligned}
C_{b,m,n} &= \sum_{k=0}^{K-1} A_{b,m,k}\,X_{b,k,n}, \\
r_{b,m} &= \max_{0 \le n < N} C_{b,m,n}, \\
y_b &= \sum_{m=0}^{M-1} r_{b,m}.
\end{aligned}
$$

这对应 `torch.bmm`、`torch.amax`、`torch.sum` 的组合。输入支持 FP16、BF16，输出为 FP32；转置参数描述输入张量的存储布局，逻辑计算关系不变。精度判定应以官方题目和校验器为准。

OJ 评测硬件为 **昇腾 910C**。

性能基线为拆分执行 BatchMatMul、ReduceMax、ReduceSum 的总耗时，评分考查融合实现相对基线的加速效果。优化围绕 Cube 与 Vector 协同、GM/L1/L0/UB 数据搬运和复用、多核分块、尾块处理、流水与双缓冲展开，同时关注小形状的初始化、同步和收尾开销。

Host 侧仅负责参数校验、shape 推导、tiling 和启动配置；Device 侧承担完整计算，单次算子调用通过一次 Kernel 启动完成。开发必须遵守赛事规则，包括禁止 Host 读取或重排输入参与计算、预存结果、按评测用例或数据规律跳算、复用旧输出、跨调用缓存结果，以及干扰校验或计时。通用分派条件应能解释其布局、容量或性能依据。

## 最终提交与成绩

| 项目 | 记录 |
| :--- | :--- |
| 最终版本 | `clean203` |
| 官方正确性结果 | **15/15 Pass** |
| 官方分数 | **63.72 分** |
