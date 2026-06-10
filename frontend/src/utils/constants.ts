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

/** Match score color thresholds. */
export function getScoreColor(score: number): string {
  if (score >= 90) return '#67C23A'
  if (score >= 70) return '#409EFF'
  if (score >= 50) return '#E6A23C'
  return '#909399'
}
