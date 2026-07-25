import { DXC_PATH } from '@/constants'

interface DxcLogoProps {
  h?: number
  className?: string
}

export function DxcLogo({ h = 22, className = '' }: DxcLogoProps) {
  return (
    <svg
      viewBox="0 0 860 240"
      height={h}
      style={{ width: (860 / 240) * h, display: 'block' }}
      className={className}
      role="img"
      aria-label="DXC"
    >
      <path d={DXC_PATH} fill="currentColor" />
    </svg>
  )
}
