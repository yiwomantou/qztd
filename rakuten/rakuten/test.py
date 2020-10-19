# 目标怎么深入的了解一些知识，我现在感觉是高不成低不就，基础知识我看了好几遍，高等级的知识我有认真不下去学，真的矛盾
# 首先应该定一个方向，往这哪个方向走，要不然就像无头苍蝇一样不知道在干什么
# 我在干后端的时候明确知道我以后是想去学习数据分析，所以我会去找一些数据分析的数据来学习
# s = ['\n    ', '\n（40代／男性）    \xa0']
# print(s[-1].split('／'))
# print(s[-1].split('／')[0].split('（')[-1])
# print(s[-1].split('／')[1].split('）')[0])

# s = '1件〜5件 (全 5件)'
# print(s.split('(')[-1].split(')')[0])

# s = 'https://review.rakuten.co.jp/my/NmZlMDY5YzEwMGQyNmU_/1.0.0.1/'
# print(s.split('/')[-3])

s = 'https://item.rakuten.co.jp/zestnationjapan-2/zc0039/'
print(s.split('/')[-2])
