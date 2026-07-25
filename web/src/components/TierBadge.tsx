import { TIER_COLOR } from '@/constants'

interface TierBadgeProps {
  tier: string
}

export function TierBadge({ tier }: TierBadgeProps) {
  return (
    <span
      className="px-3 py-1 rounded-full text-xs font-bold text-midnight"
      style={{ background: TIER_COLOR[tier] }}
    >
      {tier}
    </span>
  )
}
