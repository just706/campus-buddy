/** Application-wide constants. */

/** Category configuration — maps to backend category enum values. */
export const CATEGORIES = [
  { value: 'study', label: '学习', color: '#409EFF', icon: 'Reading' },
  { value: 'sports', label: '运动', color: '#F56C6C', icon: 'Basketball' },
  { value: 'dining', label: '约饭', color: '#E6A23C', icon: 'ForkSpoon' },
  { value: 'travel', label: '出行', color: '#67C23A', icon: 'MapLocation' },
  { value: 'other', label: '其他', color: '#909399', icon: 'More' },
] as const

/** Category value → display config lookup. */
export const CATEGORY_MAP = Object.fromEntries(
  CATEGORIES.map((c) => [c.value, c]),
) as Record<string, (typeof CATEGORIES)[number]>

/** Grade options for registration form. */
export const GRADE_OPTIONS = [
  { value: '大一', label: '大一' },
  { value: '大二', label: '大二' },
  { value: '大三', label: '大三' },
  { value: '大四', label: '大四' },
  { value: '研一', label: '研一' },
  { value: '研二', label: '研二' },
  { value: '研三', label: '研三' },
  { value: '博士', label: '博士' },
]

/** Gender options. */
export const GENDER_OPTIONS = [
  { value: '男', label: '男' },
  { value: '女', label: '女' },
  { value: '其他', label: '其他' },
]

/** Post status display config. */
export const POST_STATUS_MAP: Record<string, { label: string; color: string }> = {
  active: { label: '进行中', color: '#67C23A' },
  closed: { label: '已关闭', color: '#909399' },
  cancelled: { label: '已取消', color: '#F56C6C' },
}

/** Match status display config. */
export const MATCH_STATUS_MAP: Record<string, { label: string; color: string }> = {
  pending: { label: '待确认', color: '#E6A23C' },
  accepted: { label: '已匹配', color: '#67C23A' },
  rejected: { label: '已拒绝', color: '#909399' },
}

/** Suggested interest tags — organized by category for quick selection. */
export const SUGGESTED_TAGS: Array<{ label: string; tags: string[] }> = [
  {
    label: '学习',
    tags: ['自习', '图书馆', '考研', '英语', '编程', '数学', '论文', '考证', '背单词', '网课'],
  },
  {
    label: '运动',
    tags: ['篮球', '足球', '羽毛球', '乒乓球', '跑步', '健身', '游泳', '排球', '网球', '瑜伽'],
  },
  {
    label: '娱乐',
    tags: ['看电影', '追剧', '音乐', '唱歌', '游戏', '桌游', '剧本杀', '密室逃脱', '跳舞', '画画'],
  },
  {
    label: '美食',
    tags: ['探店', '火锅', '奶茶', '咖啡', '烧烤', '甜品', '小吃', '烘焙'],
  },
  {
    label: '出行',
    tags: ['爬山', '骑行', '露营', '旅游', '摄影', '逛街', '看展'],
  },
  {
    label: '其他',
    tags: ['志愿者', '实习', '创业', '辩论', '动漫', '追星', '养宠'],
  },
]

/** Flatten all suggested tags into a single array for validation/comparison. */
export const ALL_SUGGESTED_TAGS: string[] = SUGGESTED_TAGS.flatMap((g) => g.tags)

/** Match score color thresholds. */
export function getScoreColor(score: number): string {
  if (score >= 90) return '#67C23A'
  if (score >= 70) return '#409EFF'
  if (score >= 50) return '#E6A23C'
  return '#909399'
}
