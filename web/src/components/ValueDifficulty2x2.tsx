import { QUAD_LABEL } from '@/constants'
import { ValueDifficultyItem } from '@/types'

interface Vd2x2Props {
  items: ValueDifficultyItem[] | undefined
}

interface PointWithCoords extends ValueDifficultyItem {
  n: number
  key: string
  vx?: number
  vy?: number
}

export function ValueDifficulty2x2({ items }: Vd2x2Props) {
  if (!items || !items.length) return null

  const s = 320
  const pad = 58

  const counts: Record<string, number> = {}
  const idx: Record<string, number> = {}

  const pts = items.map((it, i) => ({
    ...it,
    n: i + 1,
    key:
      Math.round(it.difficulty_score * 10) + '_' + Math.round(it.value_score * 10),
  } as PointWithCoords))

  pts.forEach((p) => {
    counts[p.key] = (counts[p.key] || 0) + 1
  })

  pts.forEach((p) => {
    const m = counts[p.key]
    const k = (idx[p.key] = (idx[p.key] || 0) + 1)
    let dx = 0,
      dy = 0
    if (m > 1) {
      const a = (2 * Math.PI * (k - 1)) / m
      const r = 0.055
      dx = Math.cos(a) * r
      dy = Math.sin(a) * r
    }
    p.vx = Math.min(0.92, Math.max(0.08, p.difficulty_score + dx))
    p.vy = Math.min(0.92, Math.max(0.08, p.value_score + dy))
  })

  const X = (d: number) => pad + d * s
  const Y = (v: number) => pad + (1 - v) * s

  return (
    <div className="flex flex-col lg:flex-row gap-8 items-start">
      <svg
        width={s + pad * 1.3}
        height={s + pad * 1.4}
        viewBox={`0 0 ${s + pad * 1.3} ${s + pad * 1.4}`}
        className="flex-none"
        role="img"
        aria-label="Value versus difficulty map"
      >
        <rect x={pad} y={pad} width={s / 2} height={s / 2} fill="#EAF2FF" />
        <rect x={pad} y={pad} width={s} height={s} fill="none" stroke="#C9C4BC" />
        <line x1={pad + s / 2} y1={pad} x2={pad + s / 2} y2={pad + s} stroke="#E6E1DA" />
        <line x1={pad} y1={pad + s / 2} x2={pad + s} y2={pad + s / 2} stroke="#E6E1DA" />

        <text
          x={pad + 8}
          y={pad + 16}
          fontSize="10"
          fontWeight="700"
          fill="#004AAC"
        >
          QUICK WINS
        </text>
        <text
          x={pad + s - 8}
          y={pad + 16}
          fontSize="10"
          fontWeight="700"
          fill="#8A867E"
          textAnchor="end"
        >
          STRATEGIC BETS
        </text>
        <text
          x={pad + 8}
          y={pad + s - 8}
          fontSize="10"
          fontWeight="600"
          fill="#B7B1A8"
        >
          FILL-INS
        </text>
        <text
          x={pad + s - 8}
          y={pad + s - 8}
          fontSize="10"
          fontWeight="600"
          fill="#B7B1A8"
          textAnchor="end"
        >
          DEPRIORITIZE
        </text>

        <text
          x={pad + s / 2}
          y={pad + s + 26}
          fontSize="11"
          fontWeight="600"
          fill="#3D3F50"
          textAnchor="middle"
        >
          Implementation difficulty →
        </text>
        <text
          x={20}
          y={pad + s / 2}
          fontSize="11"
          fontWeight="600"
          fill="#3D3F50"
          textAnchor="middle"
          transform={`rotate(-90 20 ${pad + s / 2})`}
        >
          Business value →
        </text>

        {pts.map((p, i) => (
          <g key={i}>
            <circle cx={X(p.vx ?? 0)} cy={Y(p.vy ?? 0)} r="12" fill="#004AAC" />
            <text
              x={X(p.vx ?? 0)}
              y={(Y(p.vy ?? 0)) + 4}
              fontSize="12"
              fontWeight="700"
              fill="#fff"
              textAnchor="middle"
            >
              {p.n}
            </text>
          </g>
        ))}
      </svg>

      <div className="flex-1">
        <ol className="space-y-2">
          {pts.map((p, i) => (
            <li key={i} className="flex gap-3 text-sm items-start">
              <span className="flex-none w-6 h-6 rounded-full bg-royal text-white text-xs font-bold flex items-center justify-center">
                {p.n}
              </span>
              <span>
                <b>{p.opportunity}</b>{' '}
                <span className="text-ink">· {QUAD_LABEL[p.quadrant] || ''}</span>
              </span>
            </li>
          ))}
        </ol>
        <p className="text-xs text-ink mt-4 pt-3 border-t border-black/10">
          Upper-left quadrant = highest value for the least effort. Start there.
        </p>
      </div>
    </div>
  )
}
