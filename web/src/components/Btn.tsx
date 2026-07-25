import { ReactNode } from 'react'

interface BtnProps {
  children: ReactNode
  onClick?: () => void
  kind?: 'primary' | 'ghost' | 'light'
  className?: string
  disabled?: boolean
}

export function Btn({
  children,
  onClick,
  kind = 'primary',
  className = '',
  disabled = false,
}: BtnProps) {
  const base =
    'px-6 py-3 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-royal/40'
  const kinds = {
    primary: 'bg-royal text-white hover:bg-[#003a86]',
    ghost: 'bg-transparent text-midnight border border-midnight/20 hover:border-midnight/50',
    light: 'bg-white text-midnight border border-black/10 hover:border-black/30',
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${kinds[kind]} ${className}`}
    >
      {children}
    </button>
  )
}
