import { DxcLogo } from './DxcLogo'

interface WordmarkProps {
  onDark?: boolean
}

export function Wordmark({ onDark = false }: WordmarkProps) {
  return (
    <div className={`flex items-center gap-2.5 ${onDark ? 'text-white' : 'text-midnight'}`}>
      <DxcLogo h={20} />
      <span className="w-px h-4 bg-current opacity-25"></span>
      <span className={`text-sm font-semibold ${onDark ? 'text-white/80' : 'text-ink'}`}>
        AdvisoryX
      </span>
    </div>
  )
}
